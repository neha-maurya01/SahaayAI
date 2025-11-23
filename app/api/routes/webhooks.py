"""
Twilio Webhooks for SMS and WhatsApp
Handles incoming messages from Twilio
"""
from fastapi import APIRouter, Form, Request, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
from twilio.twiml.messaging_response import MessagingResponse

from app.database import get_db
from app.services.twilio_service import twilio_service
from app.api.routes.messaging import (
    get_or_create_user,
    get_or_create_conversation,
    save_message,
    save_action_plan
)
from app.database import Channel, MessageRole
from app.services.ai_service import ai_service
from app.services.translation_service import translation_service
from app.services.action_planner import action_planner
from app.utils.logger import logger
from app.utils.validation import sanitize_input

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/sms/incoming")
async def receive_sms(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...),
    NumMedia: Optional[int] = Form(0),
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for incoming SMS messages from Twilio
    
    Twilio sends POST requests to this endpoint when SMS is received
    """
    try:
        logger.info(f"Received SMS from {From}: {Body}")
        
        # Sanitize input
        user_message = sanitize_input(Body)
        phone_number = From.replace('whatsapp:', '')  # Remove whatsapp: prefix if present
        
        # Detect language
        detected_language = translation_service.detect_language(user_message)
        
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
        
        # Create TwiML response
        twiml_response = MessagingResponse()
        twiml_response.message(response_text)
        
        logger.info(f"Sent SMS response to {From}")
        
        return Response(content=str(twiml_response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling incoming SMS: {str(e)}")
        # Send error message back to user
        twiml_response = MessagingResponse()
        twiml_response.message("Sorry, I encountered an error. Please try again.")
        return Response(content=str(twiml_response), media_type="application/xml")


@router.post("/whatsapp/incoming")
async def receive_whatsapp(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...),
    NumMedia: Optional[int] = Form(0),
    MediaUrl0: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for incoming WhatsApp messages from Twilio
    
    Twilio sends POST requests to this endpoint when WhatsApp message is received
    """
    try:
        logger.info(f"Received WhatsApp from {From}: {Body}")
        
        # Sanitize input
        user_message = sanitize_input(Body) if Body else ""
        phone_number = From.replace('whatsapp:', '')  # Remove whatsapp: prefix
        
        # Handle media messages
        has_media = NumMedia and NumMedia > 0
        if has_media and MediaUrl0:
            user_message = f"[User sent media: {MediaUrl0}] " + user_message
            logger.info(f"WhatsApp message includes media: {MediaUrl0}")
        
        if not user_message.strip():
            user_message = "Hello"
        
        # Detect language
        detected_language = translation_service.detect_language(user_message)
        
        # Get or create user
        user = await get_or_create_user(
            db=db,
            phone_number=phone_number,
            language=detected_language,
            channel="whatsapp"
        )
        
        # Create or get active conversation
        conversation = await get_or_create_conversation(
            db=db,
            user_id=user.id,
            channel=Channel.WHATSAPP
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
            "intent": intent_data,
            "has_media": has_media
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
            
            # Format for WhatsApp (can be richer than SMS)
            response_text = action_planner.format_action_plan_for_whatsapp(action_plan_data)
        
        # Save assistant response
        await save_message(
            db=db,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=response_text,
            language=detected_language
        )
        
        # Create TwiML response
        twiml_response = MessagingResponse()
        
        # WhatsApp supports formatted text
        message = twiml_response.message()
        message.body(response_text)
        
        # Could add media to response if needed
        # message.media('https://example.com/image.jpg')
        
        logger.info(f"Sent WhatsApp response to {From}")
        
        return Response(content=str(twiml_response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling incoming WhatsApp: {str(e)}")
        # Send error message back to user
        twiml_response = MessagingResponse()
        twiml_response.message("क्षमा करें, एक त्रुटि हुई। कृपया पुनः प्रयास करें।\nSorry, an error occurred. Please try again.")
        return Response(content=str(twiml_response), media_type="application/xml")


@router.post("/sms/status")
async def sms_status_callback(
    request: Request,
    MessageSid: str = Form(...),
    MessageStatus: str = Form(...),
    To: str = Form(...),
    ErrorCode: Optional[str] = Form(None)
):
    """
    Webhook for SMS delivery status updates
    Twilio calls this when message status changes (sent, delivered, failed, etc.)
    """
    logger.info(f"SMS Status Update - SID: {MessageSid}, Status: {MessageStatus}, To: {To}")
    
    if ErrorCode:
        logger.error(f"SMS Error - Code: {ErrorCode}, SID: {MessageSid}")
    
    # Could update database with delivery status here
    return {"status": "received"}


@router.post("/whatsapp/status")
async def whatsapp_status_callback(
    request: Request,
    MessageSid: str = Form(...),
    MessageStatus: str = Form(...),
    To: str = Form(...),
    ErrorCode: Optional[str] = Form(None)
):
    """
    Webhook for WhatsApp delivery status updates
    """
    logger.info(f"WhatsApp Status Update - SID: {MessageSid}, Status: {MessageStatus}, To: {To}")
    
    if ErrorCode:
        logger.error(f"WhatsApp Error - Code: {ErrorCode}, SID: {MessageSid}")
    
    # Could update database with delivery status here
    return {"status": "received"}


@router.get("/health")
async def webhook_health():
    """Health check for webhook endpoints"""
    return {
        "status": "healthy",
        "twilio_enabled": twilio_service.enabled,
        "endpoints": {
            "sms_incoming": "/webhooks/sms/incoming",
            "whatsapp_incoming": "/webhooks/whatsapp/incoming",
            "sms_status": "/webhooks/sms/status",
            "whatsapp_status": "/webhooks/whatsapp/status"
        }
    }
