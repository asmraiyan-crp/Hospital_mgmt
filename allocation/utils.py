from .maxflow import maxflow
from core.models import Hospital , Patient

def run_allocation():
    mf = maxflow()
    source = "S"
    sink = "T"
    patients = list(Patient.objects.filter(hospital_name_isnull= True))
    hospitals = list( Hospital.objects.all)

    for p in patients:
        mf.add_edge(source,f"P{p.id}",1)
    for p in patients:
        for h in hospitals:
            if p.priority_level == 1 and h.critical_priority_top_priority_avaiable_beds >0:
                mf.add_edge(f"P{p.id}",f"H{h.id}",1)
            elif p.priority_level == 2 and h.top_priority_top_priority_avaiable_beds >0:
                mf.add_edge(f"P{p.id}",f"H{h.id}",1)
            elif p.priority_level == 3 and h.mid_priority_top_priority_avaiable_beds >0:
                mf.add_edge(f"P{p.id}",f"H{h.id}",1)
            elif p.priority_level == 4 and h.low_priority_top_priority_avaiable_beds >0:
                mf.add_edge(f"P{p.id}",f"H{h.id}",1)
    for h in hospitals:
        total_capacity = (
            h.critical_priority_avaiable_beds+
            h.top_priority_avaiable_beds +
            h.mid_priority_avaiable_beds +
            h.low_priority_avaiable_beds
        )
        mf.add_edge(f"H{h.id}",sink,total_capacity)
    total_assigned = mf.mflow(source,sink)
    print("total paitents assigned: ", total_assigned)
    
    assignments = mf.get_flow()

    for u, v in assignments:
        if u.startswith("P" and v.startswith("H")):
            patient_id = int(u[1:])
            hospital_id = int(v[1:])
        try:
            patient = Patient.objects.get(id = patient_id)
            hospital = Hospital.objects.get(id = hospital_id)

            patient.hospital_name = hospital
            patient.save()

            if patient.priority_level ==1:
                hospital.critical_priority_avaiable_beds -= 1
            elif patient.priority_level ==2:
                hospital.top_priority_avaiable_beds -= 1
            elif patient.priority_level ==3:
                hospital.mid_priority_avaiable_beds -= 1
            else:
                hospital.low_priority_avaiable_beds -= 1
            hospital.save()
        except Exception as e:
            print(e)
    print("allocation complete")
