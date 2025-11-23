from typing import Dict, Optional
from langdetect import detect, LangDetectException
from app.config import settings
from app.utils.logger import logger

# Language code mapping (ISO 639-1 to full name)
LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
    "as": "Assamese"
}

class TranslationService:
    def __init__(self):
        self.supported_languages = settings.supported_languages_list
        logger.info(f"Translation service initialized with languages: {self.supported_languages}")
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text
        
        Args:
            text: Input text to detect language
            
        Returns:
            Language code (e.g., 'en', 'hi')
        """
        try:
            detected = detect(text)
            
            # Map detected language to supported language
            if detected in self.supported_languages:
                logger.info(f"Detected language: {detected}")
                return detected
            else:
                logger.warning(f"Detected unsupported language: {detected}, defaulting to English")
                return settings.DEFAULT_LANGUAGE
                
        except LangDetectException as e:
            logger.error(f"Language detection failed: {str(e)}")
            return settings.DEFAULT_LANGUAGE
    
    def get_language_name(self, code: str) -> str:
        """Get full language name from code"""
        return LANGUAGE_MAP.get(code, "English")
    
    def translate_text(self, text: str, target_language: str, source_language: Optional[str] = None) -> str:
        """
        Translate text to target language
        Note: For POC, we're using Gemini for translation which is more reliable
        For production, consider using Google Translate API or similar service
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (optional)
            
        Returns:
            Translated text
        """
        # For POC, we'll use the AI service for translation
        # In production, use a dedicated translation API
        
        if not text:
            return ""
        
        # If target language is same as detected/source language, no translation needed
        if source_language and source_language == target_language:
            return text
        
        # For now, return original text and let AI service handle translation in context
        # This is a placeholder for actual translation implementation
        logger.info(f"Translation requested from {source_language} to {target_language}")
        return text
    
    def get_multilingual_response(self, response_text: str, languages: list) -> Dict[str, str]:
        """
        Get response in multiple languages
        
        Args:
            response_text: Original response text
            languages: List of language codes
            
        Returns:
            Dictionary mapping language codes to translated text
        """
        result = {}
        for lang in languages:
            if lang in self.supported_languages:
                # In production, translate to each language
                result[lang] = response_text  # Placeholder
        
        return result
    
    def is_supported_language(self, language_code: str) -> bool:
        """Check if language is supported"""
        return language_code in self.supported_languages

# Initialize singleton
translation_service = TranslationService()
