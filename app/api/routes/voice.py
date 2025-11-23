from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from twilio.twiml.voice_response import VoiceResponse, Gather
from typing import Optional

from app.database import get_db
from app.services.ai_service import ai_service
from app.services.multimodal_service import multimodal_service
from app.api.routes.messaging import get_or_create_user, get_or_create_conversation, save_message
from app.database import Channel, MessageRole
from app.utils.logger import logger

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])

@router.post("/incoming")
async def handle_incoming_call(
    From: str,
    CallSid: str,
    db: Session = Depends(get_db)
):
    """
    Handle incoming IVR calls
    
    Args:
        From: Caller's phone number
        CallSid: Twilio call SID
        db: Database session
    """
    try:
        response = VoiceResponse()
        
        # Welcome message
        gather = Gather(
            input='speech',
            action='/api/v1/voice/gather',
            language='en-US',
            speechTimeout='auto',
            method='POST'
        )
        
        gather.say(
            "Welcome to SahaayAI. How can I help you today? "
            "You can ask about healthcare, government schemes, agriculture, or financial help.",
            voice='alice',
            language='en-US'
        )
        
        response.append(gather)
        
        # Fallback
        response.say("We didn't receive any input. Goodbye!", voice='alice')
        
        logger.info(f"Handled incoming call from {From}")
        
        return str(response)
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {str(e)}")
        response = VoiceResponse()
        response.say("Sorry, we're experiencing technical difficulties. Please try again later.", voice='alice')
        return str(response)

@router.post("/gather")
async def handle_voice_input(
    SpeechResult: Optional[str] = None,
    From: str = None,
    CallSid: str = None,
    db: Session = Depends(get_db)
):
    """
    Process voice input from user
    
    Args:
        SpeechResult: Transcribed speech from user
        From: Caller's phone number
        CallSid: Twilio call SID
        db: Database session
    """
    try:
        response = VoiceResponse()
        
        if not SpeechResult:
            response.say("Sorry, I didn't catch that. Please try again.", voice='alice')
            return str(response)
        
        # Get or create user
        user = await get_or_create_user(
            db=db,
            phone_number=From,
            language="en",  # Default to English for voice
            channel="voice"
        )
        
        # Create conversation
        conversation = await get_or_create_conversation(
            db=db,
            user_id=user.id,
            channel=Channel.VOICE
        )
        
        # Save user message
        await save_message(
            db=db,
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=SpeechResult,
            language="en"
        )
        
        # Extract intent and generate response
        intent_data = await ai_service.extract_intent(SpeechResult, "en")
        
        user_context = {
            "location": f"{user.location_district}, {user.location_state}" if user.location_district else None,
            "literacy_level": user.literacy_level.value,
            "language": "en",
            "intent": intent_data
        }
        
        ai_response = await ai_service.generate_response(
            user_message=SpeechResult,
            context=user_context,
            language="en",
            literacy_level=user.literacy_level.value
        )
        
        response_text = ai_response.get("response_text", "")
        
        # Simplify for voice
        simplified_text = await ai_service.simplify_text(
            response_text,
            literacy_level=user.literacy_level.value,
            language="en"
        )
        
        # Save assistant response
        await save_message(
            db=db,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=simplified_text,
            language="en"
        )
        
        # Speak the response
        response.say(simplified_text, voice='alice', language='en-US')
        
        # Ask if they need more help
        gather = Gather(
            input='speech',
            action='/api/v1/voice/gather',
            language='en-US',
            speechTimeout='auto',
            method='POST'
        )
        gather.say("Is there anything else I can help you with?", voice='alice')
        response.append(gather)
        
        response.say("Thank you for calling SahaayAI. Goodbye!", voice='alice')
        
        logger.info(f"Processed voice input for user {user.id}")
        
        return str(response)
        
    except Exception as e:
        logger.error(f"Error processing voice input: {str(e)}")
        response = VoiceResponse()
        response.say("Sorry, we encountered an error. Please try again later.", voice='alice')
        return str(response)
