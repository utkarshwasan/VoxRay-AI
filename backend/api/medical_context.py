"""
medical_context.py
Grounding data for VoxRay AI to prevent hallucinations.

Sources: 
- IDSA/ATS Community-Acquired Pneumonia Guidelines 2019
- Fleischner Society Guidelines for Pulmonary Nodules
- AO Foundation Fracture Classification
- Standard Radiology Reporting Criteria

Last Updated: 2024-01
Review Schedule: Every 6 months or when guidelines change
Version: 1.0.0

DISCLAIMER: This provides educational context only.
Always recommend professional consultation for clinical decisions.
"""

import re
from typing import Dict, Any

# Version tracking for maintenance
KNOWLEDGE_BASE_VERSION = "1.0.0"
LAST_UPDATED = "2024-01"

CONDITION_DETAILS: Dict[str, Dict[str, Any]] = {
    # Class 0: NORMAL_LUNG
    "NORMAL_LUNG": {
        "description": "No significant acute pulmonary abnormalities detected.",
        "radiological_features": [
            "Clear bilateral lung fields",
            "Sharp costophrenic angles",
            "Normal cardiac silhouette (CTR < 50%)",
            "Visible pulmonary vascular markings",
            "No focal consolidation or masses"
        ],
        "typical_location": "N/A - findings indicate normal anatomy",
        "severity": "None",
        "severity_level": 0,
        "next_steps": "No further imaging required unless clinical symptoms persist. Correlate with patient presentation.",
        "differential": [],
        "source": "Standard Chest X-Ray Normalcy Criteria",
        "common_symptoms": ["None (Asymptomatic regarding radiologic findings)"],
        "standard_treatment": "No medical intervention required."
    },
    
    # Class 1: NORMAL_BONE
    "NORMAL_BONE": {
        "description": "No evidence of acute fracture or dislocation.",
        "radiological_features": [
            "Intact cortical margins",
            "Normal trabecular bone pattern",
            "Preserved joint alignment",
            "No visible lucent fracture lines",
            "No periosteal reaction"
        ],
        "typical_location": "N/A - findings indicate normal anatomy",
        "severity": "None",
        "severity_level": 0,
        "next_steps": "If clinical suspicion for fracture remains high, consider CT or MRI for occult injuries. Correlate with mechanism of injury.",
        "differential": [],
        "source": "Standard Skeletal Trauma Protocols",
        "common_symptoms": ["None (Asymptomatic regarding radiologic findings)"],
        "standard_treatment": "No medical intervention required."
    },

    # Class 2: NORMAL_PNEUMONIA (Ambiguous class - requires special handling)
    "NORMAL_PNEUMONIA": {
        "description": "Classification shows mixed features. Image may represent transitional state (early or resolving infection) or require clarification.",
        "radiological_features": [
            "Features are equivocal (neither clearly normal nor clearly abnormal)",
            "May represent early/resolving disease process",
            "Subtle findings that require expert interpretation",
            "Requires manual radiologist review for definitive interpretation"
        ],
        "typical_location": "Unspecified - requires clinical correlation",
        "severity": "Indeterminate - Requires Review",
        "severity_level": 1,
        "next_steps": "Recommend radiologist review. Consider repeat imaging in 48-72 hours if clinically indicated. Correlate with symptoms, vital signs, and laboratory values.",
        "differential": ["Early pneumonia", "Resolving infection", "Atelectasis", "Artifact"],
        "source": "VoxRay Classification Uncertainty Protocol",
        "common_symptoms": ["Variable", "Mild cough", "Low-grade fever"],
        "standard_treatment": "Clinical correlation required to determine necessity of treatment."
    },

    # Class 3: LUNG_CANCER
    "LUNG_CANCER": {
        "description": "Suspicious pulmonary finding requiring urgent oncological workup.",
        "radiological_features": [
            "Solitary pulmonary nodule or mass (>3cm classified as mass)",
            "Spiculated or irregular margins (higher malignancy risk)",
            "Possible hilar or mediastinal lymphadenopathy",
            "May have associated pleural effusion",
            "Possible chest wall invasion"
        ],
        "typical_location": "Upper lobes more commonly affected; can present centrally (squamous) or peripherally (adenocarcinoma)",
        "severity": "HIGH - Urgent specialist referral required",
        "severity_level": 3,
        "next_steps": "Urgent: CT chest with contrast for characterization. PET-CT for staging if confirmed. Pulmonology/Oncology referral. Tissue biopsy for histological diagnosis. Smoking cessation counseling.",
        "differential": ["Primary lung cancer", "Metastatic disease", "Benign granuloma", "Hamartoma"],
        "source": "Fleischner Society Guidelines for Pulmonary Nodules; NCCN Lung Cancer Screening Guidelines",
        "common_symptoms": ["Persistent cough", "Hemoptysis (coughing up blood)", "Unexplained weight loss", "Chest pain", "Shortness of breath"],
        "standard_treatment": "Treatment is stage-dependent. Options typically include surgical resection, chemotherapy, radiation therapy, immunotherapy, and targeted drug therapy."
    },

    # Class 4: FRACTURED
    "FRACTURED": {
        "description": "Disruption of bone continuity consistent with acute fracture.",
        "radiological_features": [
            "Visible lucent fracture line traversing cortex",
            "Cortical step-off or discontinuity",
            "Displacement or angulation if present",
            "Associated soft tissue swelling",
            "Possible joint involvement or extension"
        ],
        "typical_location": "Location varies by mechanism - common sites include distal radius (Colles'), hip (femoral neck), ankle (malleoli), and clavicle",
        "severity": "Moderate to High - depends on location and displacement",
        "severity_level": 2,
        "next_steps": "Orthopedic consultation. Immobilization (splint/cast). CT if complex fracture pattern suspected. Assess for neurovascular compromise. Pain management.",
        "differential": ["Acute fracture", "Stress fracture", "Pathologic fracture"],
        "source": "AO Foundation Fracture Classification; Ottawa Ankle/Knee Rules",
        "common_symptoms": ["Immediate pain", "Swelling", "Bruising", "Inability to bear weight or move limb", "Deformity"],
        "standard_treatment": "Immobilization (splint/cast), pain management, and physical therapy. Complex fractures may require surgical fixation (ORIF)."
    },

    # Class 5: PNEUMONIA
    "PNEUMONIA": {
        "description": "Inflammatory consolidation of lung parenchyma consistent with infectious process.",
        "radiological_features": [
            "Airspace consolidation (areas of increased opacity)",
            "Air bronchograms (air-filled bronchi visible within consolidation)",
            "Silhouette sign (loss of normal cardiac or diaphragm border)",
            "Possible parapneumonic pleural effusion",
            "May show lobar, bronchopneumonia, or interstitial pattern"
        ],
        "typical_location": "Lower lobes commonly affected; can be lobar (single lobe), bronchopneumonia (patchy bilateral), or interstitial pattern. May be unilateral or bilateral.",
        "severity": "Moderate - assess with CURB-65 or PSI score for disposition",
        "severity_level": 2,
        "next_steps": "CBC, CMP, blood cultures if febrile/septic. Sputum culture if productive cough. Empiric antibiotics per local guidelines (typically macrolide or fluoroquinolone for CAP). Monitor oxygen saturation. Consider CT if complicated or treatment failure.",
        "differential": ["Bacterial pneumonia", "Viral pneumonia", "Aspiration pneumonia", "Atypical pneumonia"],
        "source": "IDSA/ATS Community-Acquired Pneumonia Guidelines 2019",
        "common_symptoms": ["High fever", "Chills", "Productive cough (yellow/green sputum)", "Pleuritic chest pain", "Fatigue"],
        "standard_treatment": "Antibiotics (for bacterial causes), rest, fluids, and antipyretics. Severe cases may require hospitalization and oxygen therapy."
    }
}


def get_condition_info(diagnosis_label: str) -> Dict[str, Any]:
    """
    Retrieves grounded medical context for a given diagnosis label.
    
    Args:
        diagnosis_label: Raw label from classifier (e.g., "03_PNEUMONIA", "PNEUMONIA", "06_PNEUMONIA")
    
    Returns:
        Dictionary containing verified medical information for the condition,
        or a safe fallback for unknown conditions.
    """
    if not diagnosis_label:
        return _get_fallback_info("Unknown")
    
    # Normalize: uppercase, strip whitespace, remove numeric prefixes
    clean_label = diagnosis_label.upper().strip()
    clean_label = re.sub(r'^\d+_', '', clean_label)  # Remove "01_", "02_", etc.
    clean_label = clean_label.replace(' ', '_')       # Handle spaces
    clean_label = clean_label.replace('-', '_')       # Handle hyphens
    
    # Exact match
    if clean_label in CONDITION_DETAILS:
        return CONDITION_DETAILS[clean_label]
    
    # Partial match (e.g., "LUNG" in "NORMAL_LUNG", "CANCER" in "LUNG_CANCER")
    for key in CONDITION_DETAILS:
        if clean_label in key or key in clean_label:
            return CONDITION_DETAILS[key]
    
    # Keyword-based matching
    keyword_map = {
        "NORMAL": "NORMAL_LUNG",
        "HEALTHY": "NORMAL_LUNG",
        "CLEAR": "NORMAL_LUNG",
        "FRACTURE": "FRACTURED",
        "BROKEN": "FRACTURED",
        "CANCER": "LUNG_CANCER",
        "TUMOR": "LUNG_CANCER",
        "MASS": "LUNG_CANCER",
        "NODULE": "LUNG_CANCER",
        "INFECTION": "PNEUMONIA",
        "CONSOLIDATION": "PNEUMONIA"
    }
    
    for keyword, condition_key in keyword_map.items():
        if keyword in clean_label:
            return CONDITION_DETAILS[condition_key]
    
    # Safe fallback for unknown conditions
    return _get_fallback_info(diagnosis_label)


def _get_fallback_info(diagnosis_label: str) -> Dict[str, Any]:
    """Returns a safe fallback response for unknown conditions."""
    return {
        "description": f"Radiological finding '{diagnosis_label}' detected. This condition requires specialist interpretation.",
        "radiological_features": [
            "Specific features require radiologist interpretation",
            "AI classification confidence should be noted",
            "Clinical correlation is essential"
        ],
        "typical_location": "Varies by presentation",
        "severity": "Clinical correlation required",
        "severity_level": 1,
        "next_steps": "Recommend specialist radiologist review for definitive interpretation. Correlate with clinical presentation and patient history.",
        "differential": [],
        "source": "VoxRay General Protocol (condition not in primary knowledge base)"
    }


def format_context_for_prompt(condition_info: Dict[str, Any], diagnosis: str, confidence: float) -> str:
    """
    Formats condition information into a structured prompt section for the LLM.
    
    Args:
        condition_info: Dictionary from get_condition_info()
        diagnosis: The diagnosis label
        confidence: Confidence percentage (0-100)
    
    Returns:
        Formatted string for injection into system prompt
    """
    # Format features as bullet list
    features_formatted = '\n'.join(f"    - {f}" for f in condition_info.get('radiological_features', []))
    
    # Format differential if present
    differential = condition_info.get('differential', [])
    differential_text = ', '.join(differential) if differential else 'N/A'
    
    # Severity indicator with emoji
    severity_level = condition_info.get('severity_level', 1)
    severity_emoji = {
        0: '🟢 NORMAL',
        1: '🟡 REVIEW NEEDED',
        2: '🟠 MODERATE',
        3: '🔴 URGENT'
    }.get(severity_level, '⚪ UNKNOWN')
    
    return f"""
=== SCAN ANALYSIS RESULTS ===
DETECTED CONDITION: {diagnosis}
AI CONFIDENCE: {confidence:.1f}%
SEVERITY: {severity_emoji} - {condition_info.get('severity', 'Unknown')}

CONDITION DESCRIPTION:
{condition_info.get('description', 'N/A')}

TYPICAL RADIOLOGICAL FEATURES:
{features_formatted}

COMMON ANATOMICAL LOCATION:
{condition_info.get('typical_location', 'N/A')}

DIFFERENTIAL CONSIDERATIONS:
{differential_text}

RECOMMENDED NEXT STEPS:
{condition_info.get('next_steps', 'N/A')}

TYPICAL SYMPTOMS (General Knowledge):
{chr(10).join(f"    - {s}" for s in condition_info.get('common_symptoms', []))}

STANDARD TREATMENT OPTIONS (General Knowledge):
{condition_info.get('standard_treatment', 'N/A')}

REFERENCE: {condition_info.get('source', 'Standard clinical guidelines')}
KNOWLEDGE BASE VERSION: {KNOWLEDGE_BASE_VERSION} (Updated: {LAST_UPDATED})
=== END SCAN RESULTS ===

CRITICAL INSTRUCTIONS FOR GENERATING RESPONSES:
1. USE THE VERIFIED INFORMATION ABOVE to answer questions accurately.
2. SAY "typically presents with" NOT "I can see" (you cannot see specific locations).
3. When asked about findings/indicators - Reference TYPICAL RADIOLOGICAL FEATURES.
4. When asked about location - Reference COMMON ANATOMICAL LOCATION.
5. When asked about next steps - Reference RECOMMENDED NEXT STEPS.
6. ALWAYS recommend professional consultation for treatment decisions.
7. DO NOT invent specific findings not listed above.
"""


def get_knowledge_base_info() -> Dict[str, Any]:
    """Returns metadata about the knowledge base for version checking."""
    return {
        "version": KNOWLEDGE_BASE_VERSION,
        "last_updated": LAST_UPDATED,
        "conditions_count": len(CONDITION_DETAILS),
        "conditions": list(CONDITION_DETAILS.keys())
    }
