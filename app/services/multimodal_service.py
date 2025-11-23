from gtts import gTTS
from pathlib import Path
from typing import Optional
import uuid
from app.config import settings
from app.utils.logger import logger

class MultimodalService:
    """
    Service for generating audio and visual content
    """
    
    def __init__(self):
        self.storage_path = Path(settings.FILE_STORAGE_PATH)
        self.storage_path.mkdir(exist_ok=True)
        self.audio_path = self.storage_path / "audio"
        self.audio_path.mkdir(exist_ok=True)
        logger.info("Multimodal service initialized")
    
    async def text_to_speech(
        self,
        text: str,
        language: str = "en",
        slow: bool = False
    ) -> Optional[str]:
        """
        Convert text to speech audio file
        
        Args:
            text: Text to convert
            language: Language code
            slow: Whether to speak slowly
            
        Returns:
            Path to generated audio file
        """
        try:
            # Map our language codes to gTTS language codes
            lang_map = {
                "en": "en",
                "hi": "hi",
                "bn": "bn",
                "ta": "ta",
                "te": "te",
                "mr": "mr",
                "gu": "gu",
                "kn": "kn",
                "ml": "ml",
                "pa": "pa"
            }
            
            gtts_lang = lang_map.get(language, "en")
            
            # Generate unique filename
            filename = f"{uuid.uuid4()}.mp3"
            filepath = self.audio_path / filename
            
            # Generate speech
            tts = gTTS(text=text, lang=gtts_lang, slow=slow)
            tts.save(str(filepath))
            
            logger.info(f"Generated audio file: {filename}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            return None
    
    def generate_icon_guide(self, action_plan: dict) -> dict:
        """
        Generate icon-based visual guide for action plan
        For POC, returns icon mappings. In production, would generate actual images.
        
        Args:
            action_plan: Action plan dictionary
            
        Returns:
            Dictionary with icon mappings for each step
        """
        icon_map = {
            "document": "📄",
            "location": "📍",
            "phone": "📞",
            "money": "💰",
            "health": "🏥",
            "agriculture": "🌾",
            "education": "📚",
            "warning": "⚠️",
            "check": "✅",
            "time": "⏰"
        }
        
        steps_with_icons = []
        for step in action_plan.get("steps", []):
            # Simple keyword matching for icons
            action_text = step.get("action", "").lower()
            icon = "📌"  # Default icon
            
            if "document" in action_text or "paper" in action_text:
                icon = icon_map["document"]
            elif "visit" in action_text or "go to" in action_text:
                icon = icon_map["location"]
            elif "call" in action_text or "contact" in action_text:
                icon = icon_map["phone"]
            elif "pay" in action_text or "money" in action_text:
                icon = icon_map["money"]
            
            steps_with_icons.append({
                **step,
                "icon": icon
            })
        
        return {
            "steps": steps_with_icons,
            "summary_icon": self._get_domain_icon(action_plan.get("domain", "general"))
        }
    
    def _get_domain_icon(self, domain: str) -> str:
        """Get icon for domain"""
        domain_icons = {
            "health": "🏥",
            "agriculture": "🌾",
            "finance": "💰",
            "education": "📚",
            "government_schemes": "🏛️",
            "climate": "🌍"
        }
        return domain_icons.get(domain, "ℹ️")
    
    def generate_simple_infographic(self, action_plan: dict) -> str:
        """
        Generate simple text-based infographic for low-bandwidth scenarios
        
        Args:
            action_plan: Action plan dictionary
            
        Returns:
            Text-based visual representation
        """
        summary = action_plan.get("summary", "")
        steps = action_plan.get("steps", [])
        
        infographic = f"""
╔════════════════════════════════════╗
║     {action_plan.get('domain', 'Action Plan').upper()}     ║
╚════════════════════════════════════╝

{summary}

┌─ STEPS TO FOLLOW ─┐
"""
        
        for i, step in enumerate(steps, 1):
            infographic += f"\n{i}. {step.get('action', '')}"
            if step.get('details'):
                infographic += f"\n   └─ {step['details']}"
        
        docs = action_plan.get("documents_required", [])
        if docs:
            infographic += "\n\n┌─ DOCUMENTS NEEDED ─┐\n"
            for doc in docs:
                infographic += f"  • {doc}\n"
        
        return infographic
    
    async def generate_summary_card(self, conversation_summary: dict) -> dict:
        """
        Generate a summary card of the conversation
        
        Args:
            conversation_summary: Summary of conversation
            
        Returns:
            Dictionary with formatted summary
        """
        return {
            "title": "Conversation Summary",
            "timestamp": conversation_summary.get("timestamp"),
            "key_points": conversation_summary.get("key_points", []),
            "action_items": conversation_summary.get("action_items", []),
            "next_steps": conversation_summary.get("next_steps", [])
        }

# Initialize singleton
multimodal_service = MultimodalService()
