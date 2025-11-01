from .maxflow import maxflow
from core.models import Hospital, Patient
from django.db import transaction
from .knapsack import run_knapsack

def run_allocation():
    mf = maxflow()
    source = "S"
    sink = "T"

    patients = list(Patient.objects.filter(hospital_name__isnull=True))
    hospitals = list(Hospital.objects.all())

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

    for u, v in assignments:
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


def run_supply_optimization(max_capacity=50):
    print("Running Knapsack optimization for medical supplies...")
    selected, total_value = run_knapsack(max_capacity)
    print("Optimization complete!")
    return selected, total_value
