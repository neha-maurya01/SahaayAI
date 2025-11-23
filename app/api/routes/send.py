"""
Direct SMS/WhatsApp sending endpoints for testing and manual messaging
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.twilio_service import twilio_service
from app.utils.logger import logger

router = APIRouter(prefix="/api/v1/send", tags=["messaging-send"])


class SendMessageRequest(BaseModel):
    """Request model for sending messages"""
    phone_number: str
    message: str
    media_url: Optional[str] = None
    channel: str = "sms"  # "sms" or "whatsapp"


@router.post("/sms")
async def send_sms_message(request: SendMessageRequest):
    """
    Send SMS message directly (for testing/manual messages)
    
    Args:
        request: SMS message details
        
    Returns:
        Send status
    """
    if not twilio_service.enabled:
        raise HTTPException(
            status_code=503,
            detail="Twilio service is not enabled. Please configure Twilio credentials."
        )
    
    try:
        result = twilio_service.send_sms(
            to_number=request.phone_number,
            message=request.message,
            media_url=request.media_url
        )
        
        if result and result.get("success"):
            return {
                "success": True,
                "message": "SMS sent successfully",
                "details": result
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to send SMS"))
            
    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whatsapp")
async def send_whatsapp_message(request: SendMessageRequest):
    """
    Send WhatsApp message directly (for testing/manual messages)
    
    Args:
        request: WhatsApp message details
        
    Returns:
        Send status
    """
    if not twilio_service.enabled:
        raise HTTPException(
            status_code=503,
            detail="Twilio service is not enabled. Please configure Twilio credentials."
        )
    
    try:
        result = twilio_service.send_whatsapp(
            to_number=request.phone_number,
            message=request.message,
            media_url=request.media_url
        )
        
        if result and result.get("success"):
            return {
                "success": True,
                "message": "WhatsApp message sent successfully",
                "details": result
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to send WhatsApp"))
            
    except Exception as e:
        logger.error(f"Error sending WhatsApp: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{message_sid}")
async def get_message_status(message_sid: str):
    """
    Get delivery status of a sent message
    
    Args:
        message_sid: Twilio message SID
        
    Returns:
        Message status details
    """
    if not twilio_service.enabled:
        raise HTTPException(
            status_code=503,
            detail="Twilio service is not enabled"
        )
    
    status = twilio_service.get_message_status(message_sid)
    
    if status:
        return status
    else:
        raise HTTPException(status_code=404, detail="Message not found")


@router.post("/validate-phone")
async def validate_phone_number(phone_number: str):
    """
    Validate a phone number using Twilio Lookup API
    
    Args:
        phone_number: Phone number to validate
        
    Returns:
        Validation result
    """
    if not twilio_service.enabled:
        raise HTTPException(
            status_code=503,
            detail="Twilio service is not enabled"
        )
    
    result = twilio_service.validate_phone_number(phone_number)
    
    if result:
        return result
    else:
        raise HTTPException(status_code=400, detail="Invalid phone number")
