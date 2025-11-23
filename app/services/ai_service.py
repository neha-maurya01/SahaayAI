import google.generativeai as genai
from typing import Dict, List, Optional
import json
from app.config import settings
from app.utils.logger import logger

class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        logger.info("Gemini AI Service initialized")
    
    async def generate_response(
        self,
        user_message: str,
        context: Dict,
        language: str = "en",
        literacy_level: str = "medium"
    ) -> Dict:
        """
        Generate AI response based on user message and context
        
        Args:
            user_message: The user's input message
            context: User context (location, previous conversation, etc.)
            language: Target language code
            literacy_level: User's literacy level (low/medium/high)
        
        Returns:
            Dict containing the response and metadata
        """
        try:
            # Build the system prompt
            system_prompt = self._build_system_prompt(language, literacy_level, context)
            
            # Combine system prompt with user message
            full_prompt = f"{system_prompt}\n\nUser Query: {user_message}"
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            result = {
                "response_text": response.text,
                "language": language,
                "literacy_level": literacy_level,
                "success": True
            }
            
            logger.info(f"Generated AI response for language: {language}, literacy: {literacy_level}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return {
                "response_text": "I apologize, but I'm having trouble processing your request right now. Please try again.",
                "language": language,
                "success": False,
                "error": str(e)
            }
    
    async def extract_intent(self, user_message: str, language: str = "en") -> Dict:
        """Extract user intent from message"""
        prompt = f"""
        Analyze the following user message and extract:
        1. Primary intent (what the user wants to do)
        2. Domain (health/agriculture/finance/education/government_schemes/climate)
        3. Key entities (location, dates, amounts, etc.)
        4. Urgency level (low/medium/high)
        
        User message: {user_message}
        
        Respond in JSON format:
        {{
            "intent": "string",
            "domain": "string",
            "entities": {{}},
            "urgency": "string",
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Parse JSON from response
            intent_data = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
            logger.info(f"Extracted intent: {intent_data.get('intent')}")
            return intent_data
        except Exception as e:
            logger.error(f"Error extracting intent: {str(e)}")
            return {
                "intent": "general_inquiry",
                "domain": "general",
                "entities": {},
                "urgency": "medium",
                "confidence": 0.5
            }
    
    async def generate_action_plan(
        self,
        user_query: str,
        domain: str,
        user_context: Dict,
        language: str = "en"
    ) -> Dict:
        """Generate step-by-step action plan"""
        prompt = f"""
        You are SahaayAI, an assistant helping underserved communities access essential services.
        
        Domain: {domain}
        User Context: {json.dumps(user_context)}
        User Query: {user_query}
        Language: {language}
        
        Generate a detailed action plan with:
        1. Immediate actions (what to do now)
        2. Required documents
        3. Eligibility criteria
        4. Step-by-step instructions (simple language)
        5. Risk alerts or warnings
        6. Contact information or resources
        
        Respond in JSON format:
        {{
            "summary": "Brief summary of the situation",
            "immediate_actions": ["action1", "action2"],
            "steps": [
                {{"step_number": 1, "action": "description", "details": "additional info"}}
            ],
            "documents_required": ["document1", "document2"],
            "eligibility": {{"criteria": ["criterion1"], "status": "eligible/not_eligible/check_needed"}},
            "risk_alerts": ["alert1"],
            "resources": [{{"name": "resource", "contact": "info"}}],
            "estimated_time": "time estimate"
        }}
        
        Keep language simple and appropriate for {user_context.get('literacy_level', 'medium')} literacy level.
        """
        
        try:
            response = self.model.generate_content(prompt)
            action_plan = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
            logger.info(f"Generated action plan for domain: {domain}")
            return action_plan
        except Exception as e:
            logger.error(f"Error generating action plan: {str(e)}")
            return {
                "summary": "We're here to help you. Let's break this down into simple steps.",
                "immediate_actions": ["Please provide more details about your situation"],
                "steps": [],
                "documents_required": [],
                "eligibility": {"criteria": [], "status": "check_needed"},
                "risk_alerts": [],
                "resources": [],
                "estimated_time": "Unknown"
            }
    
    async def simplify_text(
        self,
        text: str,
        literacy_level: str = "low",
        language: str = "en"
    ) -> str:
        """Simplify complex text for different literacy levels"""
        complexity_map = {
            "low": "Use very simple words, short sentences (5-8 words), explain everything like teaching a beginner. Use analogies and examples.",
            "medium": "Use common words, moderate sentence length (8-15 words), some technical terms with brief explanations.",
            "high": "Use standard language, can include technical terms with context."
        }
        
        prompt = f"""
        Simplify the following text for someone with {literacy_level} literacy level.
        
        Guidelines: {complexity_map.get(literacy_level, complexity_map['medium'])}
        Target language: {language}
        
        Original text:
        {text}
        
        Simplified version:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error simplifying text: {str(e)}")
            return text
    
    def _build_system_prompt(self, language: str, literacy_level: str, context: Dict) -> str:
        """Build system prompt based on user characteristics"""
        
        literacy_instructions = {
            "low": "Use very simple language, short sentences, avoid technical terms. Explain everything step-by-step.",
            "medium": "Use clear language, moderate complexity, explain technical terms when used.",
            "high": "Use standard language, can include technical information with proper context."
        }
        
        system_prompt = f"""
        You are SahaayAI, a compassionate AI assistant helping underserved communities access essential services like healthcare, government schemes, financial literacy, agriculture support, and education.

        User Profile:
        - Language: {language}
        - Literacy Level: {literacy_level}
        - Location: {context.get('location', 'Not specified')}
        
        Communication Guidelines:
        - {literacy_instructions.get(literacy_level, literacy_instructions['medium'])}
        - Be empathetic, patient, and respectful
        - Provide actionable, practical advice
        - Focus on immediate help and clear next steps
        - Ask clarifying questions when needed
        - Always prioritize user safety and well-being
        - Provide information about local resources when possible
        - Respect cultural context and sensitivities
        
        Response Format:
        - Start with acknowledging the user's concern
        - Provide clear, numbered steps when giving instructions
        - End with asking if they need more help
        - Keep responses concise but complete
        
        Remember: You're helping people who may be in difficult situations, have limited resources, and need clear, actionable guidance.
        """
        
        return system_prompt

# Initialize singleton
ai_service = AIService()
