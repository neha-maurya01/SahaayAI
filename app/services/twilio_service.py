"""
Twilio Service for SMS and WhatsApp messaging
Handles sending and receiving messages via Twilio
"""
from typing import Optional, Dict, List
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.config import settings
from app.utils.logger import logger


class TwilioService:
    """Service for Twilio SMS and WhatsApp integration"""
    
    def __init__(self):
        self.enabled = settings.twilio_enabled
        if self.enabled:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.phone_number = settings.TWILIO_PHONE_NUMBER
            logger.info("Twilio service initialized successfully")
        else:
            self.client = None
            self.phone_number = None
            logger.warning("Twilio service not initialized - credentials not provided")
    
    def send_sms(
        self,
        to_number: str,
        message: str,
        media_url: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Send SMS message via Twilio
        
        Args:
            to_number: Recipient phone number (E.164 format)
            message: Message text to send
            media_url: Optional media URL for MMS
            
        Returns:
            Message details or None if failed
        """
        if not self.enabled:
            logger.warning("Twilio not enabled - cannot send SMS")
            return None
        
        try:
            # Ensure phone number is in E.164 format
            if not to_number.startswith('+'):
                to_number = f'+{to_number}'
            
            # Split long messages (SMS limit is 1600 chars for concatenated messages)
            messages_sent = []
            if len(message) > 1600:
                chunks = self._chunk_message(message, 1600)
                for i, chunk in enumerate(chunks):
                    msg_text = f"({i+1}/{len(chunks)}) {chunk}"
                    msg = self._send_single_sms(to_number, msg_text, media_url if i == 0 else None)
                    if msg:
                        messages_sent.append(msg)
            else:
                msg = self._send_single_sms(to_number, message, media_url)
                if msg:
                    messages_sent.append(msg)
            
            logger.info(f"Successfully sent {len(messages_sent)} SMS message(s) to {to_number}")
            return {
                "success": True,
                "messages_sent": len(messages_sent),
                "message_sids": [m["sid"] for m in messages_sent]
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS: {e.msg}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _send_single_sms(
        self,
        to_number: str,
        message: str,
        media_url: Optional[str] = None
    ) -> Optional[Dict]:
        """Send a single SMS message"""
        kwargs = {
            "body": message,
            "from_": self.phone_number,
            "to": to_number
        }
        
        if media_url:
            kwargs["media_url"] = [media_url]
        
        message_obj = self.client.messages.create(**kwargs)
        
        return {
            "sid": message_obj.sid,
            "status": message_obj.status,
            "to": message_obj.to,
            "from": message_obj.from_
        }
    
    def send_whatsapp(
        self,
        to_number: str,
        message: str,
        media_url: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Send WhatsApp message via Twilio
        
        Args:
            to_number: Recipient phone number (E.164 format)
            message: Message text to send
            media_url: Optional media URL
            
        Returns:
            Message details or None if failed
        """
        if not self.enabled:
            logger.warning("Twilio not enabled - cannot send WhatsApp")
            return None
        
        try:
            # WhatsApp numbers must be prefixed with 'whatsapp:'
            if not to_number.startswith('whatsapp:'):
                if not to_number.startswith('+'):
                    to_number = f'+{to_number}'
                to_number = f'whatsapp:{to_number}'
            
            # WhatsApp sender must also have 'whatsapp:' prefix
            from_number = f'whatsapp:{self.phone_number}'
            
            kwargs = {
                "body": message,
                "from_": from_number,
                "to": to_number
            }
            
            if media_url:
                kwargs["media_url"] = [media_url]
            
            message_obj = self.client.messages.create(**kwargs)
            
            logger.info(f"Successfully sent WhatsApp message to {to_number}")
            return {
                "success": True,
                "sid": message_obj.sid,
                "status": message_obj.status,
                "to": message_obj.to
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending WhatsApp: {e.msg}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error sending WhatsApp: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_message_status(self, message_sid: str) -> Optional[Dict]:
        """
        Get status of a sent message
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            Message status details
        """
        if not self.enabled:
            return None
        
        try:
            message = self.client.messages(message_sid).fetch()
            return {
                "sid": message.sid,
                "status": message.status,
                "error_code": message.error_code,
                "error_message": message.error_message,
                "date_sent": message.date_sent,
                "date_updated": message.date_updated
            }
        except Exception as e:
            logger.error(f"Error fetching message status: {str(e)}")
            return None
    
    def _chunk_message(self, message: str, chunk_size: int) -> List[str]:
        """
        Split long message into chunks
        
        Args:
            message: Message to split
            chunk_size: Maximum size per chunk
            
        Returns:
            List of message chunks
        """
        # Try to split at sentence boundaries
        sentences = message.replace('. ', '.|').replace('! ', '!|').replace('? ', '?|').split('|')
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def validate_phone_number(self, phone_number: str) -> Optional[Dict]:
        """
        Validate phone number using Twilio Lookup API
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            Validation details or None
        """
        if not self.enabled:
            return None
        
        try:
            phone_info = self.client.lookups.v1.phone_numbers(phone_number).fetch()
            return {
                "valid": True,
                "phone_number": phone_info.phone_number,
                "national_format": phone_info.national_format,
                "country_code": phone_info.country_code
            }
        except Exception as e:
            logger.error(f"Error validating phone number: {str(e)}")
            return {"valid": False, "error": str(e)}


# Global instance
twilio_service = TwilioService()
