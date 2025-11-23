#!/usr/bin/env python3
"""
SahaayAI Demo Script
Demonstrates the key features of the system
"""

import asyncio
import sys
sys.path.insert(0, '/Users/ajit/Desktop/Github Projects/SahaayAI')

from app.services.ai_service import ai_service
from app.services.translation_service import translation_service
from app.services.action_planner import action_planner
from app.services.multimodal_service import multimodal_service

async def demo_intent_extraction():
    """Demo: Extract intent from user message"""
    print("\n" + "="*60)
    print("DEMO 1: Intent Extraction")
    print("="*60)
    
    queries = [
        "I have fever and cough, what should I do?",
        "How do I apply for crop insurance?",
        "Tell me about Ayushman Bharat health scheme"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        intent = await ai_service.extract_intent(query, "en")
        print(f"Intent: {intent.get('intent')}")
        print(f"Domain: {intent.get('domain')}")
        print(f"Urgency: {intent.get('urgency')}")
        print(f"Confidence: {intent.get('confidence')}")

async def demo_action_plan():
    """Demo: Generate action plan"""
    print("\n" + "="*60)
    print("DEMO 2: Action Plan Generation")
    print("="*60)
    
    query = "My crops failed due to drought. What compensation can I get?"
    user_context = {
        "location": "Karnataka",
        "literacy_level": "medium",
        "language": "en"
    }
    
    print(f"\nQuery: {query}")
    print(f"Context: {user_context}")
    print("\nGenerating action plan...")
    
    action_plan = await action_planner.create_action_plan(
        user_query=query,
        domain="agriculture",
        user_context=user_context,
        language="en"
    )
    
    print(f"\nSummary: {action_plan.get('summary')}")
    print(f"\nImmediate Actions:")
    for i, action in enumerate(action_plan.get('immediate_actions', []), 1):
        print(f"  {i}. {action}")
    
    print(f"\nDocuments Required:")
    for doc in action_plan.get('documents_required', []):
        print(f"  • {doc}")
    
    print(f"\nDetailed Steps:")
    for step in action_plan.get('steps', []):
        print(f"  Step {step.get('step_number')}: {step.get('action')}")

async def demo_multilingual():
    """Demo: Language detection and response"""
    print("\n" + "="*60)
    print("DEMO 3: Multilingual Support")
    print("="*60)
    
    messages = [
        ("Hello, I need help", "English"),
        ("नमस्ते, मुझे मदद चाहिए", "Hindi (if detected)")
    ]
    
    for message, lang_name in messages:
        print(f"\nMessage: {message} ({lang_name})")
        detected = translation_service.detect_language(message)
        print(f"Detected Language: {detected}")

async def demo_text_simplification():
    """Demo: Text simplification for different literacy levels"""
    print("\n" + "="*60)
    print("DEMO 4: Text Simplification")
    print("="*60)
    
    complex_text = """
    The Pradhan Mantri Jan Arogya Yojana provides comprehensive health insurance 
    coverage up to Rs. 5 lakhs per family per annum for secondary and tertiary 
    hospitalization to approximately 50 crore beneficiaries.
    """
    
    print(f"\nOriginal Text:\n{complex_text}")
    
    for level in ["low", "medium", "high"]:
        print(f"\n--- Simplified for '{level}' literacy level ---")
        simplified = await ai_service.simplify_text(
            text=complex_text,
            literacy_level=level,
            language="en"
        )
        print(simplified)

async def demo_ai_conversation():
    """Demo: Full AI conversation"""
    print("\n" + "="*60)
    print("DEMO 5: AI Conversation")
    print("="*60)
    
    context = {
        "location": "Mumbai, Maharashtra",
        "literacy_level": "medium",
        "language": "en"
    }
    
    queries = [
        "I need to open a bank account. What documents do I need?",
        "How can I protect myself from online fraud?"
    ]
    
    for query in queries:
        print(f"\nUser: {query}")
        response = await ai_service.generate_response(
            user_message=query,
            context=context,
            language="en",
            literacy_level="medium"
        )
        print(f"\nSahaayAI: {response.get('response_text')[:500]}...")

async def demo_visual_guide():
    """Demo: Visual guide generation"""
    print("\n" + "="*60)
    print("DEMO 6: Visual Guide with Icons")
    print("="*60)
    
    sample_plan = {
        "domain": "health",
        "summary": "Steps to apply for health insurance",
        "steps": [
            {"step_number": 1, "action": "Visit nearest Common Service Centre"},
            {"step_number": 2, "action": "Bring your Aadhaar card and documents"},
            {"step_number": 3, "action": "Fill the application form"},
            {"step_number": 4, "action": "Pay the premium amount"}
        ],
        "documents_required": ["Aadhaar", "Photo", "Address Proof"]
    }
    
    visual_guide = multimodal_service.generate_icon_guide(sample_plan)
    print(f"\nDomain Icon: {visual_guide.get('summary_icon')}")
    print("\nSteps with Icons:")
    for step in visual_guide.get('steps', []):
        print(f"  {step.get('icon')} Step {step.get('step_number')}: {step.get('action')}")

async def main():
    """Run all demos"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                    SahaayAI Demo                          ║")
    print("║     AI-Powered Assistant for Underserved Communities      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    try:
        # Check if Gemini API key is configured
        from app.config import settings
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
            print("\n⚠️  WARNING: Gemini API key not configured!")
            print("Please add your GEMINI_API_KEY to the .env file")
            print("Get your free API key from: https://makersuite.google.com/app/apikey")
            return
        
        print("\n✅ Configuration loaded successfully")
        print(f"Supported Languages: {', '.join(settings.supported_languages_list)}")
        
        # Run demos
        await demo_intent_extraction()
        await demo_action_plan()
        await demo_multilingual()
        await demo_text_simplification()
        await demo_ai_conversation()
        await demo_visual_guide()
        
        print("\n" + "="*60)
        print("✅ All demos completed successfully!")
        print("="*60)
        
        print("\n📝 Next Steps:")
        print("  1. Start the API server: uvicorn app.main:app --reload")
        print("  2. Visit API docs: http://localhost:8000/docs")
        print("  3. Test with cURL or Postman")
        print("  4. Check SETUP.md for detailed instructions")
        
    except Exception as e:
        print(f"\n❌ Error running demo: {str(e)}")
        print("\nPlease ensure:")
        print("  1. Virtual environment is activated")
        print("  2. All dependencies are installed: pip install -r requirements.txt")
        print("  3. .env file is configured with GEMINI_API_KEY")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
