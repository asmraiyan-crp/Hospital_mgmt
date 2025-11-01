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

    # Add edges from source to patients
    for p in patients:
        mf.add_edge(source, f"P{p.id}", 1)

    # Add edges from patients to hospitals based on priority
    for p in patients:
        for h in hospitals:
            if p.priority_level == 1 and h.critical_priority_avaiable_beds > 0:
                mf.add_edge(f"P{p.id}", f"H{h.id}", 1)
            elif p.priority_level == 2 and h.top_priority_avaiable_beds > 0:
                mf.add_edge(f"P{p.id}", f"H{h.id}", 1)
            elif p.priority_level == 3 and h.mid_priority_avaiable_beds > 0:
                mf.add_edge(f"P{p.id}", f"H{h.id}", 1)
            elif p.priority_level == 4 and h.low_priority_avaiable_beds > 0:
                mf.add_edge(f"P{p.id}", f"H{h.id}", 1)

    # Add edges from hospitals to sink
    for h in hospitals:
        total_capacity = (
            h.critical_priority_avaiable_beds +
            h.top_priority_avaiable_beds +
            h.mid_priority_avaiable_beds +
            h.low_priority_avaiable_beds
        )
        mf.add_edge(f"H{h.id}", sink, total_capacity)

    # Run max-flow
    total_assigned = mf.mflow(source, sink)
    print("Total patients assigned:", total_assigned)

    # Process assignments
    assignments = mf.get_flow()
    
    # Keep track of updated patients and hospitals
    updated_patients = []
    hospital_bed_updates = {}

    for u, v in assignments:
        if u.startswith("P") and v.startswith("H"):
            try:
                patient_id = int(u[1:])
                hospital_id = int(v[1:])
                
                patient = next((p for p in patients if p.id == patient_id), None)
                hospital = next((h for h in hospitals if h.id == hospital_id), None)

                if patient and hospital:
                    patient.hospital_name = hospital
                    updated_patients.append(patient)

                    # Update hospital beds in memory
                    if hospital_id not in hospital_bed_updates:
                        hospital_bed_updates[hospital_id] = {
                            "critical": hospital.critical_priority_avaiable_beds,
                            "top": hospital.top_priority_avaiable_beds,
                            "mid": hospital.mid_priority_avaiable_beds,
                            "low": hospital.low_priority_avaiable_beds,
                        }

                    if patient.priority_level == 1:
                        hospital_bed_updates[hospital_id]["critical"] -= 1
                    elif patient.priority_level == 2:
                        hospital_bed_updates[hospital_id]["top"] -= 1
                    elif patient.priority_level == 3:
                        hospital_bed_updates[hospital_id]["mid"] -= 1
                    else:
                        hospital_bed_updates[hospital_id]["low"] -= 1

            except Exception as e:
                print("Error processing assignment:", e)

    # Save updates to DB in bulk inside a transaction
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
