from . import models
from .maxflow import maxflow
from core.models import Hospital, Patient, HospitalTransfer,Resource,Supply_center,Disaster_zone,TransportFlow, supply_max_cap
from django.db import transaction
from django.db.models import F
from .knapsack import run_knapsack
from collections import defaultdict

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

    # Fetch all supply centers and disaster zones
    centers = list(Supply_center.objects.all())
    zones = list(Disaster_zone.objects.all())

    # Initialize nodes in the graph
    for c in centers:
        center_node = f"C{c.id}"
        mf.add_edge(source, center_node, c.total_stock)

    for z in zones:
        zone_node = f"Z{z.id}"
        mf.add_edge(zone_node, sink, z.demand)

    # Fetch all transport routes
    transport_routes = list(TransportFlow.objects.all())
    for t in transport_routes:
        c_node = f"C{t.center.id}"
        z_node = f"Z{t.zone.id}"
        mf.add_edge(c_node, z_node, t.amount_sent if t.amount_sent > 0 else t.send_limits)

    # Run max-flow
    total_flow = mf.mflow(source, sink)
    print(f"✅ Total supplies transported: {total_flow}")

    # Get the flow assignments
    assignments = mf.get_flow()  # should return [(u, v, flow), ...]

    # Prepare dicts to track remaining stock and demand
    center_updates = {c.id: c.total_stock for c in centers}
    zone_updates = {z.id: z.demand for z in zones}
    flow_map = {}  # key = (center_id, zone_id), value = flow_amount

    for u, v, flow in assignments:
        if u.startswith("C") and v.startswith("Z"):
            center_id = int(u[1:])
            zone_id = int(v[1:])
            center_updates[center_id] -= flow
            zone_updates[zone_id] -= flow
            flow_map[(center_id, zone_id)] = flow
            print(f"Center {center_id} sent {flow} units → Zone {zone_id}")

    # Save updates to DB
    with transaction.atomic():
        # Update stocks in supply centers
        for c in centers:
            c.total_stock = center_updates[c.id]
            c.save()

        # Update demand in disaster zones
        for z in zones:
            z.demand = zone_updates[z.id]
            z.save()

        # Update TransportFlow table for admin view
        for (center_id, zone_id), flow_amount in flow_map.items():
            tf = TransportFlow.objects.filter(center_id=center_id, zone_id=zone_id).first()
            if tf:
                tf.amount_sent = flow_amount
                tf.save()
            else:
                center = next(c for c in centers if c.id == center_id)
                zone = next(z for z in zones if z.id == zone_id)
                TransportFlow.objects.create(center=center, zone=zone, amount_sent=flow_amount)

    print("✅ Transport allocation completed and admin panel updated.")


def run_supply_optimization():
    print("Running Knapsack optimization for medical supplies...")
    s = supply_max_cap.objects.first()

    if s:
        mcapacity = s.max_capacity
    else:
        mcapacity = 100

    selected, total_value = run_knapsack(mcapacity)
    with transaction.atomic():
        # First, mark all resources as not allocated
        Resource.objects.update(quantity=F('volume'))

        for item in selected:
            # Suppose Resource model has 'quantity_available' field
            item.quantity= max(0, item.quantity- item.quantity)
            item.save()

    print("Optimization complete!")

    return selected, total_value
