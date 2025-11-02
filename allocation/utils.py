from .maxflow import maxflow
from core.models import Hospital, Patient, HospitalTransfer,Resource,Supply_center,Disaster_zone,TransportFlow
from django.db import transaction
from .knapsack import run_knapsack

def run_allocation():
    mf = maxflow()
    source = "S"
    sink = "T"

    patients = list(Patient.objects.filter(hospital_name__isnull=True))
    hospitals = list(Hospital.objects.all())
    hospital_t = list(HospitalTransfer.objects.all())

    priority_map = {1: "critical", 2: "top", 3: "mid", 4: "low"}

    for p in patients:
        patient_node = f"P{p.id}"
        mf.add_edge(source, patient_node, 1)

    for p in patients:
        patient_node = f"P{p.id}"
        bed_type = priority_map.get(p.priority_level)
        for h in hospitals:
            bed_count = getattr(h, f"{bed_type}_priority_avaiable_beds")
            if bed_count > 0:
                hospital_node = f"H{h.id}-{bed_type}"
                mf.add_edge(patient_node, hospital_node, 1)

    for t in hospital_t:
        hospital_A_node = f"H{t.from_hospital.id}"
        hospital_B_node = f"H{t.to_hospital.id}"
        mf.add_edge(hospital_A_node,hospital_B_node,t.capacity)

    for h in hospitals:
        for bed_type in ["critical", "top", "mid", "low"]:
            bed_count = getattr(h, f"{bed_type}_priority_avaiable_beds")
            if bed_count > 0:
                hospital_node = f"H{h.id}-{bed_type}"
                mf.add_edge(hospital_node, sink, bed_count)

    total_assigned = mf.mflow(source, sink)
    print("Total patients assigned:", total_assigned)

    assignments = mf.get_flow()  # check this returns [(u,v), ...]

    updated_patients = []
    hospital_bed_updates = {}

    for u, v ,f in assignments:
        if u.startswith("P") and v.startswith("H"):
            try:
                patient_id = int(u[1:])
                hospital_id_str, bed_type = v[1:].split("-")
                hospital_id = int(hospital_id_str)

                patient = next((p for p in patients if p.id == patient_id), None)
                hospital = next((h for h in hospitals if h.id == hospital_id), None)

                if patient and hospital:
                    patient.hospital_name = hospital
                    updated_patients.append(patient)

                    if hospital_id not in hospital_bed_updates:
                        hospital_bed_updates[hospital_id] = {
                            "critical": hospital.critical_priority_avaiable_beds,
                            "top": hospital.top_priority_avaiable_beds,
                            "mid": hospital.mid_priority_avaiable_beds,
                            "low": hospital.low_priority_avaiable_beds,
                        }

                    hospital_bed_updates[hospital_id][bed_type] -= 1

            except Exception as e:
                print("Error processing assignment:", e)

    with transaction.atomic():
        Patient.objects.bulk_update(updated_patients, ["hospital_name"])
        for h in hospitals:
            if h.id in hospital_bed_updates:
                beds = hospital_bed_updates[h.id]
                h.critical_priority_avaiable_beds = beds["critical"]
                h.top_priority_avaiable_beds = beds["top"]
                h.mid_priority_avaiable_beds = beds["mid"]
                h.low_priority_avaiable_beds = beds["low"]
                h.save()

    print("Allocation complete")

def run_transport_allocation():
    mf = maxflow()
    source = "S"
    sink = "T"

    center_list = list(Supply_center.objects.all())
    destination_list = list(Disaster_zone.objects.all())

    # Source -> centers
    for c in center_list:
        mf.add_edge(source, f"S{c.id}", c.total_stock)

    # Center -> Zone
    for t in TransportFlow.objects.all():
        mf.add_edge(f"S{t.center.id}", f"Z{t.zone.id}", t.amount_sent)

    # Zone -> Sink
    for z in destination_list:
        mf.add_edge(f"Z{z.id}", sink, z.demand)

    # Run maxflow
    total_flow = mf.mflow(source, sink)
    print("Total supplies transported:", total_flow)

    # Prepare dicts for updating stocks and demands
    center_updates = {c.id: c.total_stock for c in center_list}
    destination_updates = {z.id: z.demand for z in destination_list}

    assignments = mf.get_flow()  # returns [(u, v, flow), ...]

    # Print allocation and update dicts
    for u, v, flow in assignments:
        if u.startswith("S") and v.startswith("Z") and flow > 0:
            center_id = int(u[1:])
            zone_id = int(v[1:])
            center_updates[center_id] -= flow
            destination_updates[zone_id] -= flow
            print(f"Center {center_id} sent {flow} units → Zone {zone_id}")

    # Save updates in DB
    with transaction.atomic():
        for c in center_list:
            c.total_stock = center_updates[c.id]
            c.save()

        for z in destination_list:
            z.demand = destination_updates[z.id]
            z.save()

        # Save allocation for admin panel
        TransportFlow.objects.all().delete()  # optional: clear old data
        for u, v, flow in assignments:
            if u.startswith("S") and v.startswith("Z") and flow > 0:
                center_id = int(u[1:])
                zone_id = int(v[1:])
                center = next(c for c in center_list if c.id == center_id)
                zone = next(z for z in destination_list if z.id == zone_id)
                TransportFlow.objects.create(center=center, zone=zone, amount_sent=flow)

    print("\n✅ Transport allocation completed successfully!\n")


def run_supply_optimization(max_capacity=50):
    print("Running Knapsack optimization for medical supplies...")
    selected, total_value = run_knapsack(max_capacity)
    print("Optimization complete!")
    return selected, total_value
