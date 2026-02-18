import os
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, Depends
from pydantic import BaseModel
from openai import OpenAI
from backend.api.deps import get_current_user
from backend.api.medical_context import get_condition_info, format_context_for_prompt

router = APIRouter()


class ChatMessage(BaseModel):
    """Individual chat message for history."""

    role: str  # 'user' or 'assistant'
    text: str


class ChatRequestV2(BaseModel):
    """V2 Chat request with multilingual support."""

    message: str
    context: Optional[str] = None
    history: List[ChatMessage] = []
    language: Optional[str] = "en"  # V2: Language code (en, es, fr, etc.)


@router.post("/chat")
async def chat_v2(
    request: ChatRequestV2 = Body(...), user: dict = Depends(get_current_user)
):
    """
    V2 Chat endpoint with multilingual support.
    Supports language parameter for non-English responses.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenRouter API Key not found. Please set OPENROUTER_API_KEY in .env",
        )

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    # Parse context and get medical grounding
    diagnosis_label = "Unknown"
    confidence = 0.0
    medical_context = ""

    if request.context:
        try:
            import re

            # Expected format: "Diagnosis: PNEUMONIA, Confidence: 98.7%"
            context_str = request.context.strip()

            # Extract diagnosis
            if "Diagnosis:" in context_str:
                diagnosis_part = context_str.split(",")[0]
                diagnosis_label = diagnosis_part.split(":")[-1].strip()
            elif ":" in context_str:
                diagnosis_label = context_str.split(":")[0].strip()
            else:
                diagnosis_label = context_str.split(",")[0].strip()

            # Extract confidence
            if "Confidence:" in context_str:
                conf_part = context_str.split("Confidence:")[-1]
                conf_str = conf_part.replace("%", "").replace(")", "").strip()
                confidence = float(conf_str)
            elif "%" in context_str:
                match = re.search(r"(\d+\.?\d*)%", context_str)
                if match:
                    confidence = float(match.group(1))

            # Get grounded medical context
            condition_info = get_condition_info(diagnosis_label)
            medical_context = format_context_for_prompt(
                condition_info, diagnosis_label, confidence
            )

            print(
                f"📋 Context parsed - Diagnosis: {diagnosis_label}, Confidence: {confidence}%"
            )

        except Exception as e:
            print(f"⚠️ Context parsing warning: {e}")
            medical_context = f"\nDiagnosis context provided: {request.context}\n"

    # V2: Language instruction
    language_map = {
        "en": ("English", ""),
        "es": ("Spanish", ""),
        "fr": ("French", ""),
        "de": ("German", ""),
        "zh": ("Chinese", ""),
        "hi": ("Hindi", " Use Devanagari script (हिन्दी), NOT Urdu/Arabic script."),
    }
    target_language, script_note = language_map.get(request.language, ("English", ""))
    language_instruction = (
        f"\n\nIMPORTANT: Respond in {target_language}.{script_note}"
        if request.language != "en"
        else ""
    )

    # Build system prompt with grounding
    system_prompt = f"""You are VoxRay, an AI radiology assistant designed to help healthcare professionals understand imaging findings.

YOUR ROLE:
- Explain radiological findings in clear, professional language
- Provide educational context about detected conditions  
- Recommend appropriate next steps based on clinical guidelines
- Act as a knowledgeable translator between AI analysis and clinical practice

{medical_context}

RESPONSE GUIDELINES:

1. SAFETY & BOUNDARIES (CRITICAL):
   - You MAY discuss general standard treatments and typical symptoms if listed in the provided context.
   - Do NOT provide patient-specific prescriptions or specific dosages (e.g., "Take 500mg Amoxicillin").
   - Never invent findings (e.g., "3mm nodule") if not in verified data.
   - Always prioritize the provided context over internal knowledge.

2. USE YOUR KNOWLEDGE BASE:
   - When asked about "symptoms" → Reference TYPICAL SYMPTOMS provided above
   - When asked about "treatment" → Reference STANDARD TREATMENT OPTIONS provided above
   - When asked about "next steps" → Reference RECOMMENDED NEXT STEPS

3. LANGUAGE & TONE:
   - SAY: "Pneumonia typically presents with..." (Generalizing signs)
   - DON'T SAY: "I can see..." (Implies specific localization ability)
   - Keep responses concise (2-4 sentences) for voice output.
   - Build on previous conversation.

4. LIMITATIONS:
   - You classified this image based on patterns but cannot pinpoint exact locations.
   - Specific localization requires radiologist review.
   - Always recommend professional consultation for treatment decisions.
{language_instruction}
"""

    # Build message chain with history
    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history (last 6 exchanges, with length limits)
    MAX_MESSAGE_LENGTH = 500

    for msg in request.history[-6:]:
        role = "assistant" if msg.role == "assistant" else "user"
        text = msg.text

        if len(text) > MAX_MESSAGE_LENGTH:
            text = text[:MAX_MESSAGE_LENGTH] + "..."

        if text:
            messages.append({"role": role, "content": text})

    # Add current user message
    messages.append({"role": "user", "content": request.message})

    print(
        f"💬 [V2] Processing chat - Message: '{request.message[:50]}...' in {target_language}, {len(request.history)} history items"
    )

    try:
        completion = client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=messages,
            temperature=0.4,
            max_tokens=200,
        )

        response_text = completion.choices[0].message.content.strip()
        print(f"✅ Chat response generated: '{response_text[:50]}...'")

        return {"response": response_text}

    except Exception as e:
        print(f"❌ OpenRouter error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}",
        )
