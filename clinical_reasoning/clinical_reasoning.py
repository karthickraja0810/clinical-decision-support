from typing import override
from clinical_reasoning.rules import (
    thyroid_logic,
    diabetes_logic,
    pcos_logic,
    adrenal_logic,
    # metabolic_syndrome_logic
)
from clinical_reasoning.retrieval import retrieve_guidelines
from clinical_reasoning.llm_layer import llm_explanation


def has_minimum_clinical_data(patient_data):
    labs = patient_data.get("labs", {})
    vitals = patient_data.get("vitals", {})
    symptoms = patient_data.get("symptoms", {})

    # Check if at least one meaningful value exists
    has_labs = any(value is not None for value in labs.values())
    has_vitals = any(
        isinstance(v, dict) and any(val is not None for val in v.values())
        or v is not None
        for v in vitals.values()
    )
    has_symptoms = any(symptoms.values())

    return has_labs or has_vitals or has_symptoms


def generate_diabetes_reasoning(labs, condition, risk, confidence):
    fbs = labs.get("fbs")
    hba1c = labs.get("hba1c")

    # Diagnostic thresholds
    fbs_diabetic = fbs is not None and fbs >= 126
    hba1c_diabetic = hba1c is not None and hba1c >= 6.5
    hba1c_prediabetic = hba1c is not None and 5.7 <= hba1c < 6.5

    if fbs_diabetic and not hba1c_diabetic:
        return (
            "A fasting plasma glucose value above the diagnostic threshold suggests "
            "a diabetes mellitus pattern. However, the HbA1c value remains below the "
            "diagnostic range, indicating discordant glycemic markers. Repeat "
            "confirmatory testing is recommended before establishing a definitive "
            "diagnosis."
        )

    if fbs_diabetic and hba1c_diabetic:
        return (
            "Both fasting plasma glucose and HbA1c values are within the diagnostic "
            "range for diabetes mellitus, providing strong biochemical evidence "
            "supporting the diagnosis."
        )

    if hba1c_prediabetic or (fbs is not None and 100 <= fbs < 126):
        return (
            "Glycemic values are within the prediabetic range, indicating impaired "
            "glucose regulation. Lifestyle modification and periodic monitoring are "
            "recommended to reduce progression risk."
        )

    return (
        "Glycemic parameters are within normal limits, with no biochemical evidence "
        "of impaired glucose regulation at this time."
    )


# ✅ CHANGE 1 — CLEANED (dead code removed, logic unchanged)
def critical_override(patient_data):
    labs = patient_data.get("labs", {})
    vitals = patient_data.get("vitals", {})

    alerts = []

    if labs.get("fbs") is not None and labs["fbs"] >= 300:
        alerts.append("Severe hyperglycemia detected (FBS ≥ 300 mg/dL)")

    if vitals.get("bp_systolic") is not None and vitals["bp_systolic"] >= 180:
        alerts.append("Hypertensive crisis (SBP ≥ 180 mmHg)")

    if vitals.get("bp_diastolic") is not None and vitals["bp_diastolic"] >= 120:
        alerts.append("Hypertensive crisis (DBP ≥ 120 mmHg)")

    if alerts:
        return {
            "primary": {
                "condition": "Medical Emergency",
                "risk_level": "Critical",
                "confidence": "High",
                "clinical_findings": alerts,
                "clinical_reasoning": (
                    "Critical values detected that require immediate medical attention. "
                    "Automated clinical reasoning has been halted."
                )
            },
            "secondary": []
        }

    return None


def normalize_risk(risk):
    if isinstance(risk, int):
        return {1: "Low", 2: "Moderate", 3: "High"}.get(risk, "Low")
    return risk


def run_clinical_reasoning(patient_data):

    # 🔴 STEP 1: SAFETY FIRST
    override = critical_override(patient_data)
    if override:
        return override

    # ✅ CHANGE 2 — DATA SUFFICIENCY CHECK (CRITICAL FIX)
    if not has_minimum_clinical_data(patient_data):
        return {
            "primary": {
                "condition": "Insufficient clinical data",
                "risk_level": "Not Applicable",
                "confidence": "Low",
                "clinical_findings": [],
                "clinical_reasoning": (
                    "No sufficient clinical parameters were provided to generate a "
                    "meaningful assessment. Please enter relevant laboratory values, "
                    "vital signs, or clinical symptoms."
                ),
            },
            "secondary": [],
            "disclaimer": (
                "This system provides clinical decision support and does not replace "
                "professional medical judgment."
            )
        }

    labs = patient_data.get("labs", {})
    vitals = patient_data.get("vitals", {})
    symptoms = patient_data.get("symptoms", {})
    demographics = patient_data.get("demographics", {})

    assessments = []
    borderline_findings = []

    # =========================
    # PCOS – PRIORITY CHECK
    # =========================
    pcos_result = pcos_logic(labs, symptoms, demographics)
    if pcos_result:
        assessments.append(("pcos", pcos_result))

    # =========================
    # Thyroid
    # =========================
    thyroid_result = thyroid_logic(labs, symptoms)
    if thyroid_result:
        assessments.append(("thyroid", thyroid_result))
        if thyroid_result["risk_level"] == "Moderate":
            borderline_findings.extend(thyroid_result["clinical_findings"])

    # =========================
    # Diabetes
    # =========================
    diabetes_result = diabetes_logic(labs)

    # ✅ CHANGE 3 — ignore NORMAL diabetes results
    if diabetes_result and diabetes_result["risk_level"] != "Low":
        assessments.append(("diabetes", diabetes_result))
        if diabetes_result["risk_level"] == "Moderate":
            borderline_findings.extend(diabetes_result["clinical_findings"])

    # =========================
    # Adrenal
    # =========================
    adrenal_result = adrenal_logic(labs)
    if adrenal_result:
        assessments.append(("adrenal", adrenal_result))

    # =========================
    # No dominant disorder
    # =========================
    if not assessments:
        return {
            "primary": {
                "condition": "No significant endocrine or metabolic disorder detected",
                "risk_level": "Low",
                "confidence": "High",
                "clinical_findings": [],
                "clinical_reasoning": (
                    "No dominant endocrine or metabolic syndrome is identified based "
                    "on the available clinical data. Clinical correlation is advised."
                ),
            },
            "borderline_findings": [],
            "explainability": {
                "triggered_rule": "None",
                "criteria_met": [],
                "criteria_missing": [],
                "confidence_basis": "All screening criteria were negative"
            },
            "secondary": [],
            "disclaimer": "This system provides clinical decision support and does not replace professional medical judgment."
        }

    # =========================
    # Sort by severity
    # =========================
    RISK_PRIORITY = {
        "High": 3,
        "Moderate": 2,
        "Low": 1
    }

    assessments.sort(
        key=lambda x: RISK_PRIORITY.get(x[1].get("risk_level", "Low"), 0),
        reverse=True
    )

    primary_domain, primary = assessments[0]
    secondary = assessments[1:]

    # =========================
    # Guideline retrieval (PRIMARY ONLY)
    # =========================
    guidelines = retrieve_guidelines(
        query=primary.get("condition", ""),
        domain=primary_domain
    )
    guideline_excerpt = guidelines[0].strip().split("\n\n")[0][:800] if guidelines else ""

    # =========================
    # Clinical Reasoning
    # =========================
    findings = primary.get("clinical_findings", [])
    confidence = primary.get("confidence", "Medium")

    if primary_domain == "diabetes":
        explanation = generate_diabetes_reasoning(
            labs=labs,
            condition=primary.get("condition"),
            risk=primary.get("risk_level"),
            confidence=confidence
        )
    else:
        try:
            explanation = llm_explanation(
                findings=findings,
                guideline_context=guideline_excerpt
            )
        except Exception:
            explanation = (
                "Clinical findings suggest a possible endocrine pattern. "
                "Further clinical correlation is advised."
            )

    # =========================
    # Final Output
    # =========================
    return {
        "primary": {
            "condition": primary.get("condition", "Unspecified condition"),
            "risk_level": normalize_risk(primary.get("risk_level", "Low")),
            "confidence": primary.get("confidence", "Medium"),
            "clinical_findings": primary.get("clinical_findings", []),
            "clinical_reasoning": explanation,
            "supporting_evidence": guideline_excerpt,
            "evidence_domain": primary_domain,
        },
        "borderline_findings": list(set(borderline_findings)),
        "secondary": [
            {
                "condition": sec.get("condition", "Unspecified condition"),
                "risk_level": normalize_risk(sec.get("risk_level", "Low")),
                "confidence": sec.get("confidence", "Medium")
            }
            for _, sec in secondary
        ],
        "disclaimer": "This system provides clinical decision support and does not replace professional medical judgment."
    }
