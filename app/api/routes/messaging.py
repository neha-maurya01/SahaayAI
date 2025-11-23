from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional
from datetime import datetime

from app.database import get_db, User, Conversation, Message, ActionPlan
from app.database import Channel, MessageRole
from app.services.ai_service import ai_service
from app.services.translation_service import translation_service
from app.services.action_planner import action_planner
from app.services.multimodal_service import multimodal_service
from app.services.twilio_service import twilio_service
from app.utils.encryption import encryption_service
from app.utils.validation import MessageRequest, sanitize_input, validate_message_content
from app.utils.logger import logger

router = APIRouter(prefix="/api/v1/message", tags=["messaging"])

@router.post("/sms")
async def handle_sms(request: MessageRequest, db: Session = Depends(get_db)):
    """
    Handle incoming SMS messages
    
    Args:
        request: SMS message request
        db: Database session
        
    Returns:
        Response message to send back via SMS
    """
    try:
        # Sanitize input
        user_message = sanitize_input(request.message)
        phone_number = request.phone_number
        
        # Detect language if not provided
        if not request.language:
            detected_language = translation_service.detect_language(user_message)
        else:
            detected_language = request.language
        
        # Get or create user
        user = await get_or_create_user(
            db=db,
            phone_number=phone_number,
            language=detected_language,
            channel="sms"
        )
        
        # Create or get active conversation
        conversation = await get_or_create_conversation(
            db=db,
            user_id=user.id,
            channel=Channel.SMS
        )
        
        # Save user message
        await save_message(
            db=db,
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=user_message,
            language=detected_language
        )
        
        # Extract intent
        intent_data = await ai_service.extract_intent(user_message, detected_language)
        
        # Generate AI response
        user_context = {
            "location": f"{user.location_district}, {user.location_state}" if user.location_district else None,
            "literacy_level": user.literacy_level.value,
            "language": detected_language,
            "intent": intent_data
        }
        
        ai_response = await ai_service.generate_response(
            user_message=user_message,
            context=user_context,
            language=detected_language,
            literacy_level=user.literacy_level.value
        )
        
        response_text = ai_response.get("response_text", "")
        
        # If intent suggests need for action plan, generate it
        if intent_data.get("domain") != "general" and intent_data.get("confidence", 0) > 0.7:
            action_plan_data = await action_planner.create_action_plan(
                user_query=user_message,
                domain=intent_data["domain"],
                user_context=user_context,
                language=detected_language
            )
            
            # Save action plan
            await save_action_plan(db, conversation.id, action_plan_data)
            
            # Format for SMS
            response_text = action_planner.format_action_plan_for_sms(action_plan_data)
        
        # Save assistant response
        await save_message(
            db=db,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=response_text,
            language=detected_language
        )
        
        # Update user last active
        user.last_active = datetime.utcnow()
        db.commit()
        
        # Send SMS via Twilio if enabled
        if twilio_service.enabled:
            send_result = twilio_service.send_sms(
                to_number=phone_number,
                message=response_text
            )
            logger.info(f"Twilio SMS send result: {send_result}")
        
        logger.info(f"Processed SMS message for user {user.id}")
        
        return {
            "success": True,
            "response": response_text,
            "language": detected_language,
            "conversation_id": conversation.id
        }
        
    except Exception as e:
        logger.error(f"Error handling SMS: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing message")

@router.post("/whatsapp")
async def handle_whatsapp(request: MessageRequest, db: Session = Depends(get_db)):
    """
    Handle incoming WhatsApp messages
    Similar to SMS but can support richer content
    """
    try:
        # Similar logic to SMS but with WhatsApp channel
        request.channel = "whatsapp"
        return await handle_sms(request, db)
        
    except Exception as e:
        logger.error(f"Error handling WhatsApp: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing message")

@router.post("/web")
async def handle_web_message(request: MessageRequest, db: Session = Depends(get_db)):
    """
    Handle web interface messages
    Supports richer responses and multimodal content
    """
    try:
        # Sanitize input
        user_message = sanitize_input(request.message)
        phone_number = request.phone_number
        
        # Validate content - Guardrails
        validation_result = validate_message_content(user_message)
        if not validation_result["is_valid"]:
            return {
                "success": True,
                "response": {
                    "text": validation_result["message"],
                    "language": request.language or "en"
                },
                "conversation_id": None
            }
        
        # Detect language if not provided
        if not request.language:
            detected_language = translation_service.detect_language(user_message)
        else:
            detected_language = request.language
        
        # Get or create user
        user = await get_or_create_user(
            db=db,
            phone_number=phone_number,
            language=detected_language,
            channel="web"
        )
        
        # Create or get active conversation
        conversation = await get_or_create_conversation(
            db=db,
            user_id=user.id,
            channel=Channel.WEB
        )
        
        # Save user message
        await save_message(
            db=db,
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=user_message,
            language=detected_language
        )
        
        # Extract intent
        intent_data = await ai_service.extract_intent(user_message, detected_language)
        
        # Generate AI response
        user_context = {
            "location": f"{user.location_district}, {user.location_state}" if user.location_district else None,
            "literacy_level": user.literacy_level.value,
            "language": detected_language,
            "intent": intent_data
        }
        
        ai_response = await ai_service.generate_response(
            user_message=user_message,
            context=user_context,
            language=detected_language,
            literacy_level=user.literacy_level.value
        )
        
        response_data = {
            "text": ai_response.get("response_text", ""),
            "language": detected_language,
            "intent": intent_data
        }
        
        # Generate action plan if needed
        if intent_data.get("domain") != "general" and intent_data.get("confidence", 0) > 0.7:
            action_plan_data = await action_planner.create_action_plan(
                user_query=user_message,
                domain=intent_data["domain"],
                user_context=user_context,
                language=detected_language
            )
            
            # Save action plan
            await save_action_plan(db, conversation.id, action_plan_data)
            
            # Add visual guide
            visual_guide = multimodal_service.generate_icon_guide(action_plan_data)
            
            response_data["action_plan"] = action_plan_data
            response_data["visual_guide"] = visual_guide
            
            # Generate audio (always for web interface)
            voice_text = action_planner.format_action_plan_for_voice(action_plan_data)
            audio_path = await multimodal_service.text_to_speech(
                voice_text,
                language=detected_language,
                slow=False
            )
            if audio_path:
                response_data["audio_url"] = f"/audio/{audio_path.split('/')[-1]}"
        else:
            # Generate audio for simple responses too
            audio_path = await multimodal_service.text_to_speech(
                response_data["text"],
                language=detected_language,
                slow=False
            )
            if audio_path:
                response_data["audio_url"] = f"/audio/{audio_path.split('/')[-1]}"
        
        # Save assistant response
        await save_message(
            db=db,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=response_data["text"],
            language=detected_language,
            metadata=response_data
        )
        
        # Update user last active
        user.last_active = datetime.utcnow()
        db.commit()
        
        logger.info(f"Processed web message for user {user.id}")
        
        return {
            "success": True,
            "response": response_data,
            "conversation_id": conversation.id
        }
        
    except Exception as e:
        logger.error(f"Error handling web message: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing message")

# Helper functions
async def get_or_create_user(
    db: Session,
    phone_number: str,
    language: str,
    channel: str
) -> User:
    """Get existing user or create new one"""
    phone_encrypted = encryption_service.encrypt(phone_number)
    
    user = db.query(User).filter(User.phone_number_encrypted == phone_encrypted).first()
    
    if not user:
        user = User(
            phone_number_encrypted=phone_encrypted,
            preferred_language=language,
            consent_given=1  # Assumed consent for POC
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created new user with ID: {user.id}")
    
    return user

async def get_or_create_conversation(
    db: Session,
    user_id: int,
    channel: Channel
) -> Conversation:
    """Get active conversation or create new one"""
    # Check for active conversation
    conversation = db.query(Conversation).filter(
        Conversation.user_id == user_id,
        Conversation.status == "active",
        Conversation.channel == channel
    ).first()
    
    if not conversation:
        conversation = Conversation(
            user_id=user_id,
            channel=channel,
            status="active"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        logger.info(f"Created new conversation with ID: {conversation.id}")
    
    return conversation

async def save_message(
    db: Session,
    conversation_id: int,
    role: MessageRole,
    content: str,
    language: str,
    metadata: Optional[Dict] = None
):
    """Save message to database"""
    content_encrypted = encryption_service.encrypt(content)
    
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content_encrypted=content_encrypted,
        language=language,
        metadata=metadata
    )
    db.add(message)
    db.commit()

async def save_action_plan(db: Session, conversation_id: int, action_plan_data: Dict):
    """Save action plan to database"""
    from app.database import Domain
    
    domain_str = action_plan_data.get("domain", "general")
    domain_enum = getattr(Domain, domain_str.upper(), Domain.HEALTH)
    
    action_plan = ActionPlan(
        conversation_id=conversation_id,
        domain=domain_enum,
        steps=action_plan_data.get("steps", []),
        documents_required=action_plan_data.get("documents_required", []),
        eligibility_status=action_plan_data.get("eligibility", {}).get("status"),
        risk_alerts=action_plan_data.get("risk_alerts", [])
    )
    db.add(action_plan)
    db.commit()
    logger.info(f"Saved action plan for conversation {conversation_id}")
