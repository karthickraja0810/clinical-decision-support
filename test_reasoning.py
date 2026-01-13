from clinical_reasoning.clinical_reasoning import run_clinical_reasoning

patient_data = {
    "labs": {
        "HbA1c": 6.8,
        "FBS": 140
    },
    "vitals": {
        "BP_Systolic": 138
    },
    "symptoms": {}
}

print(run_clinical_reasoning(patient_data))
