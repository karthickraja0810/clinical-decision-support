from flask import Flask, render_template, request
import pprint
from clinical_reasoning.clinical_reasoning import run_clinical_reasoning

app = Flask(__name__)

# -----------------------------
# Helper functions (SAFE parsing)
# -----------------------------

def get_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def get_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def get_bool(value):
    return value == "on"

def calculate_bmi(weight, height_cm):
    if not weight or not height_cm:
        return None
    height_m = height_cm / 100
    return round(weight / (height_m ** 2), 1)



# -----------------------------
# Main Route
# -----------------------------

@app.route("/", methods=["GET", "POST"])
def clinical_workspace():

    assessment_result = None  # <-- THIS is what UI will read

    if request.method == "POST":

        # =========================
        # Patient Context
        # =========================
        patient_context = {
            "patient_id": request.form.get("patient_id"),
            "age": get_int(request.form.get("age")),
            "sex": request.form.get("sex"),
            "visit_date": request.form.get("visit_date")
        }


        age = patient_context["age"]
        sex = patient_context["sex"]


        # =========================
        # Vital Signs
        # =========================
        vitals = {
            "blood_pressure": {
                "systolic": get_int(request.form.get("bp_systolic")),
                "diastolic": get_int(request.form.get("bp_diastolic"))
            },
            "heart_rate": get_int(request.form.get("heart_rate")),
            "weight": get_float(request.form.get("weight")),
            "height": get_float(request.form.get("height"))
                }
        # -----------------------------
        # Backend-authoritative BMI
        # -----------------------------
        bmi = calculate_bmi(
            vitals["weight"],
            vitals["height"]
        )

        vitals["bmi"] = bmi


        # =========================
        # Laboratory Values
        # =========================
        labs = {
            "fbs": get_float(request.form.get("fbs")),
            "hba1c": get_float(request.form.get("hba1c")),
            "tsh": get_float(request.form.get("tsh")),
            "ft4": get_float(request.form.get("ft4"))
        }

        # =========================
        # Symptoms & History
        # =========================
        symptoms = {
            "fatigue": get_bool(request.form.get("fatigue")),
            "weight_gain": get_bool(request.form.get("weight_gain")),
            "menstrual_irregularity": get_bool(request.form.get("menstrual_irregularity")),
            "hirsutism": get_bool(request.form.get("hirsutism")),
            "acne_severity": request.form.get("acne_severity"),
            "family_history_diabetes": get_bool(request.form.get("family_history_diabetes"))
        }

        # =========================
        # Sex-based clinical filtering
        # =========================
        if sex != "female":
            symptoms["menstrual_irregularity"] = False
            symptoms["hirsutism"] = False

        # =========================
        # PCOS eligibility (clinical rule)
        # =========================
        pcos_eligible = (
            sex == "female" and
            patient_context["age"] is not None and
            patient_context["age"] >= 12
        )

        # =========================
        # Final Clinical Data Object
        # =========================
        patient_data = {
    "demographics": {
        "age": age,
        "sex": sex
    },
    "vitals": vitals,
    "labs": labs,
    "symptoms": symptoms
}

        # =========================
        # DEBUG OUTPUT (optional)
        # =========================
        print("\n====== STRUCTURED PATIENT DATA ======")
        pprint.pprint(patient_data)
        print("====================================\n")

        # =========================
        # Clinical Reasoning Engine
        # =========================
        assessment_result = run_clinical_reasoning(patient_data)

        print("\n--- SUPPORTING EVIDENCE PREVIEW ---")
        print(assessment_result.get("supporting_evidence", "")[:300])
        print("----------------------------------\n")


        print("\n====== CLINICAL ASSESSMENT RESULT ======")
        pprint.pprint(assessment_result)
        print("=======================================\n")

    # =========================
    # Render UI
    # =========================
    return render_template(
        "workspace.html",
        assessment=assessment_result
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
