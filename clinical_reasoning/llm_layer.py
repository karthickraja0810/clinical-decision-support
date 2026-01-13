# llm_layer.py

import subprocess


SYSTEM_PROMPT = """
You are a clinical decision support explanation assistant.

STRICT SAFETY RULES (MUST FOLLOW):
- You MUST NOT invent laboratory values, imaging findings, or measurements.
- You MUST NOT mention triglycerides, HDL, LDL, cholesterol, waist circumference, or imaging unless explicitly provided.
- If information is missing, state clearly: "Data not available".
- You MUST NOT diagnose or confirm a disease.
- You MUST NOT recommend medications or treatments.
- You MUST NOT suggest treatment initiation.
- You MUST use cautious language such as:
  "may be consistent with", "can be seen in", "suggests a possible pattern".

STYLE:
- Neutral, professional, clinician-facing language
- Brief (4–6 sentences max)
- Emphasize uncertainty and need for clinical correlation
- State that final decisions rest with the clinician
"""


def format_findings(findings):
    """
    Convert findings list into safe, explicit bullet points.
    """
    if not findings:
        return "No significant clinical findings were provided."

    return "\n".join(f"- {item}" for item in findings)


def llm_explanation(findings, guideline_text):
    formatted_findings = format_findings(findings)

    if not guideline_text:
        guideline_text = "No guideline evidence was available."

    prompt = f"""
{SYSTEM_PROMPT}

CLINICAL FINDINGS (ONLY THESE ARE AVAILABLE):
{formatted_findings}

GUIDELINE CONTEXT (REFERENCE ONLY):
{guideline_text}

TASK:
Provide a cautious clinical interpretation of the findings.
- Do NOT assume missing data
- Do NOT infer laboratory abnormalities not listed
- Explicitly mention uncertainty where applicable

OUTPUT:
A short explanation suitable for a physician.
"""

    result = subprocess.run(
        ["ollama", "run", "llama3:8b"],
        input=prompt,
        text=True,
        capture_output=True
    )

    return result.stdout.strip()
