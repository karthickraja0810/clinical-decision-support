# rules.py

def thyroid_logic(labs, symptoms):
    score = 0
    findings = []

    tsh = labs.get("tsh")
    ft4 = labs.get("ft4")
    fatigue = symptoms.get("fatigue")
    weight_gain = symptoms.get("weight_gain")

    # -----------------------------
# Discordant thyroid pattern
# -----------------------------
    # Discordant thyroid pattern (safe check)
    if tsh is not None and ft4 is not None:
       if tsh <= 4.5 and ft4 > 1.8:
        findings.append(
            "Discordant thyroid function tests (normal TSH with elevated free T4)"
        )
        return {
            "condition": "Discordant thyroid function tests",
            "risk_level": "Low",
            "confidence": "Low",
            "clinical_findings": findings
        }


    if tsh is None or ft4 is None:
        return None

    # -----------------------------
    # TSH evaluation
    # -----------------------------
    if tsh > 4.5:
        score += 2
        findings.append("Elevated TSH level")

    elif tsh < 0.4:
        score += 2
        findings.append("Suppressed TSH level")

    # -----------------------------
    # Free T4 evaluation
    # -----------------------------
    if ft4 < 0.8:
        score += 2
        findings.append("Low free T4 level")

    elif ft4 > 1.8:
        score += 2
        findings.append("Elevated free T4 level")

    # -----------------------------
    # Symptom support
    # -----------------------------
    if fatigue:
        score += 1
        findings.append("Fatigue reported")

    if weight_gain:
        score += 1
        findings.append("Weight gain reported")

    # -----------------------------
    # Risk stratification
    # -----------------------------
    if score >= 5:
        condition = "Likely thyroid dysfunction"
        risk = "High"
        confidence = "High"

    elif score >= 3:
        condition = "Possible thyroid dysfunction"
        risk = "Moderate"
        confidence = "Medium"

    else:
        condition = "No significant thyroid abnormality"
        risk = "Low"
        confidence = "Low"
        
    return {
        "condition": condition,
        "risk_level": risk,
        "confidence": confidence,
        "clinical_findings": findings
    }


def diabetes_logic(labs):
    findings = []

    fbs = labs.get("fbs")      # mg/dL
    hba1c = labs.get("hba1c")  # %

    if fbs is None and hba1c is None:
        return None

    # -----------------------------
    # Flags
    # -----------------------------
    diabetic_flag = False
    prediabetic_flag = False

    # -----------------------------
    # Fasting Blood Glucose
    # -----------------------------
    if fbs is not None:
        if fbs >= 126:
            findings.append("Fasting glucose above diagnostic threshold (≥126 mg/dL)")
            diabetic_flag = True
        elif 100 <= fbs < 126:
            findings.append("Fasting glucose in impaired range (100–125 mg/dL)")
            prediabetic_flag = True

    # -----------------------------
    # HbA1c
    # -----------------------------
    if hba1c is not None:
        if hba1c >= 6.5:
            findings.append("HbA1c above diagnostic threshold (≥6.5%)")
            diabetic_flag = True
        elif 5.7 <= hba1c < 6.5:
            findings.append("HbA1c in prediabetic range (5.7–6.4%)")
            prediabetic_flag = True

    # -----------------------------
    # Final interpretation (PRIORITY-BASED)
    # -----------------------------
    if diabetic_flag:
        condition = "Diabetes mellitus pattern (confirmation required)"
        risk = "High"
        confidence = "Medium" if prediabetic_flag else "High"

    elif prediabetic_flag:
        condition = "Prediabetes pattern"
        risk = "Moderate"
        confidence = "Medium"

    else:
        condition = "Normal glycemic status"
        risk = "Low"
        confidence = "High"

    return {
        "condition": condition,
        "risk_level": risk,
        "confidence": confidence,
        "clinical_findings": findings
    }


def pcos_logic(labs, symptoms, demographics):
    if demographics.get("sex") != "female":
        return None

    age = demographics.get("age")
    if age is None or age < 12:
        return None

    findings = []

    if symptoms.get("menstrual_irregularity"):
        findings.append("Menstrual irregularity")

    if symptoms.get("hirsutism"):
        findings.append("Clinical hyperandrogenism (hirsutism)")

    # ✅ STRONG PCOS (≥2 criteria)
    if len(findings) >= 2:
        return {
            "condition": "Possible Polycystic Ovary Syndrome (PCOS)",
            "risk_level": "Moderate",
            "confidence": "Moderate",
            "clinical_findings": findings
        }

    # ✅ WEAK / SUSPICION PCOS (1 criterion)
    if len(findings) == 1:
        return {
            "condition": "PCOS (clinical suspicion)",
            "risk_level": "Low",
            "confidence": "Low",
            "clinical_findings": findings
        }

    return None


def adrenal_logic(labs):
    findings = []
    # Risk levels: 1=Low, 2=Moderate, 3=High
    risk = 1
    condition = "No significant adrenal abnormality"

    cortisol = labs.get("Cortisol_AM")

    if cortisol is None:
        return None

    if cortisol < 5:
        findings.append("Low morning cortisol level")
        condition = "Possible adrenal insufficiency pattern"
        risk = 3

    elif cortisol > 20:
        findings.append("Elevated morning cortisol level")
        condition = "Possible hypercortisol pattern"
        risk = 2

    return {
        "condition": condition,
        "risk_level": risk if risk == 3 else "Moderate",
        "confidence": "High",
        "clinical_findings": findings
    }
def metabolic_syndrome_logic(vitals, labs):
    findings = []
    # Risk levels: 1=Low, 2=Moderate, 3=High
    risk = 1
    condition = "No metabolic syndrome pattern detected"
    confidence = "High"

    waist = vitals.get("Waist_Circumference")
    bp_sys = vitals.get("BP_Systolic")
    triglycerides = labs.get("Triglycerides")
    hdl = labs.get("HDL")

    criteria_count = 0

    if waist and waist > 90:
        findings.append("Increased waist circumference")
        criteria_count += 1

    if bp_sys and bp_sys >= 130:
        findings.append("Elevated blood pressure")
        criteria_count += 1

    if triglycerides and triglycerides >= 150:
        findings.append("Elevated triglycerides")
        criteria_count += 1

    if hdl and hdl < 40:
        findings.append("Reduced HDL cholesterol")
        criteria_count += 1

    if criteria_count >= 3:
        condition = "Possible metabolic syndrome pattern"
        risk = 3

    return {
        "condition": condition,
        "risk_level": risk,
        "confidence": confidence,
        "clinical_findings": findings
    }
