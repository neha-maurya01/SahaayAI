import pytest
from app.services.ai_service import ai_service
from app.services.translation_service import translation_service
from app.services.action_planner import action_planner

@pytest.mark.asyncio
async def test_language_detection():
    """Test language detection"""
    # English text
    lang = translation_service.detect_language("Hello, how are you?")
    assert lang == "en"
    
    # Hindi text (if detection works)
    # lang = translation_service.detect_language("नमस्ते, आप कैसे हैं?")
    # assert lang == "hi"

@pytest.mark.asyncio
async def test_intent_extraction():
    """Test intent extraction from user message"""
    message = "I need information about health insurance schemes"
    intent = await ai_service.extract_intent(message, "en")
    
    assert "intent" in intent
    assert "domain" in intent
    assert "confidence" in intent

@pytest.mark.asyncio
async def test_action_plan_generation():
    """Test action plan generation"""
    user_query = "How do I apply for PM-KISAN scheme?"
    user_context = {
        "location": "Karnataka",
        "literacy_level": "medium"
    }
    
    action_plan = await action_planner.create_action_plan(
        user_query=user_query,
        domain="agriculture",
        user_context=user_context,
        language="en"
    )
    
    assert "summary" in action_plan
    assert "steps" in action_plan
    assert "documents_required" in action_plan

@pytest.mark.asyncio
async def test_text_simplification():
    """Test text simplification for different literacy levels"""
    complex_text = "The beneficiary must submit requisite documentation to the designated authority."
    
    simplified = await ai_service.simplify_text(
        text=complex_text,
        literacy_level="low",
        language="en"
    )
    
    assert len(simplified) > 0
    assert simplified != complex_text  # Should be different

@pytest.mark.asyncio
async def test_ai_response_generation():
    """Test AI response generation"""
    context = {
        "location": "Mumbai, Maharashtra",
        "literacy_level": "medium",
        "language": "en"
    }
    
    response = await ai_service.generate_response(
        user_message="I have a fever, what should I do?",
        context=context,
        language="en",
        literacy_level="medium"
    )
    
    assert "response_text" in response
    assert response["success"] is True
    assert len(response["response_text"]) > 0

def test_action_plan_formatting_sms():
    """Test formatting action plan for SMS"""
    sample_plan = {
        "summary": "Here's how to apply for the scheme",
        "immediate_actions": ["Visit CSC", "Bring Aadhaar", "Fill form"],
        "documents_required": ["Aadhaar", "Bank details"]
    }
    
    sms_text = action_planner.format_action_plan_for_sms(sample_plan)
    
    assert len(sms_text) > 0
    assert "Quick Steps" in sms_text or "Steps" in sms_text

def test_action_plan_formatting_voice():
    """Test formatting action plan for voice"""
    sample_plan = {
        "summary": "Here's how to apply",
        "steps": [
            {"step_number": 1, "action": "Visit office", "details": "Bring documents"}
        ],
        "documents_required": ["Aadhaar"],
        "resources": [{"name": "Helpline", "contact": "1234"}]
    }
    
    voice_text = action_planner.format_action_plan_for_voice(sample_plan)
    
    assert len(voice_text) > 0
    assert "Step 1" in voice_text

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
