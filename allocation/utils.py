from .maxflow import maxflow
from core.models import Hospital, Patient
from django.db import transaction

def run_allocation():
    mf = maxflow()
    source = "S"
    sink = "T"

    # Fetch patients without hospital
    patients = list(Patient.objects.filter(hospital_name__isnull=True))
    hospitals = list(Hospital.objects.all())

    # Map patient priority to hospital bed types
    priority_map = {
        1: "critical",
        2: "top",
        3: "mid",
        4: "low"
    }

    # Add edges from source to each patient
    for p in patients:
        patient_node = f"P{p.id}"
        mf.add_edge(source, patient_node, 1)

    # Add edges from patients to hospitals based on priority
    for p in patients:
        patient_node = f"P{p.id}"
        bed_type = priority_map.get(p.priority_level)
        for h in hospitals:
            # Only connect if hospital has available beds for that priority
            bed_count = getattr(h, f"{bed_type}_priority_avaiable_beds")
            if bed_count > 0:
                hospital_node = f"H{h.id}-{bed_type}"
                mf.add_edge(patient_node, hospital_node, 1)

    # Add edges from hospital priority nodes to sink
    for h in hospitals:
        for bed_type in ["critical", "top", "mid", "low"]:
            bed_count = getattr(h, f"{bed_type}_priority_avaiable_beds")
            if bed_count > 0:
                hospital_node = f"H{h.id}-{bed_type}"
                mf.add_edge(hospital_node, sink, bed_count)

    # Run max-flow algorithm
    total_assigned = mf.mflow(source, sink)
    print("Total patients assigned:", total_assigned)

    # Get assignments from max-flow
    assignments = mf.get_flow()  # Ensure this returns [(u,v), ...] for flow > 0

    updated_patients = []
    hospital_bed_updates = {}

    for u, v in assignments:
        if u.startswith("P") and v.startswith("H"):
            try:
                patient_id = int(u[1:])
                # v is like "H{id}-{bed_type}"
                hospital_id_str, bed_type = v[1:].split("-")
                hospital_id = int(hospital_id_str)

                patient = next((p for p in patients if p.id == patient_id), None)
                hospital = next((h for h in hospitals if h.id == hospital_id), None)

                if patient and hospital:
                    patient.hospital_name = hospital
                    updated_patients.append(patient)

                    # Track hospital bed updates
                    if hospital_id not in hospital_bed_updates:
                        hospital_bed_updates[hospital_id] = {
                            "critical": hospital.critical_priority_avaiable_beds,
                            "top": hospital.top_priority_avaiable_beds,
                            "mid": hospital.mid_priority_avaiable_beds,
                            "low": hospital.low_priority_avaiable_beds,
                        }

                    # Decrement assigned bed
                    hospital_bed_updates[hospital_id][bed_type] -= 1

            except Exception as e:
                print("Error processing assignment:", e)

    # Save updates to DB
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
