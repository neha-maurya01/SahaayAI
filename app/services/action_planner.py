from typing import Dict, List
from datetime import datetime
from app.services.ai_service import ai_service
from app.utils.logger import logger

class ActionPlanner:
    """
    Service for generating actionable plans based on user queries
    """
    
    async def create_action_plan(
        self,
        user_query: str,
        domain: str,
        user_context: Dict,
        language: str = "en"
    ) -> Dict:
        """
        Create a comprehensive action plan for the user
        
        Args:
            user_query: User's question or request
            domain: Service domain (health, agriculture, etc.)
            user_context: User profile and context information
            language: User's preferred language
            
        Returns:
            Structured action plan with steps, documents, and resources
        """
        try:
            # Get action plan from AI service
            action_plan = await ai_service.generate_action_plan(
                user_query=user_query,
                domain=domain,
                user_context=user_context,
                language=language
            )
            
            # Enhance action plan with additional metadata
            enhanced_plan = {
                **action_plan,
                "created_at": datetime.utcnow().isoformat(),
                "domain": domain,
                "language": language,
                "user_context": {
                    "location": user_context.get("location"),
                    "literacy_level": user_context.get("literacy_level")
                }
            }
            
            logger.info(f"Created action plan for domain: {domain}")
            return enhanced_plan
            
        except Exception as e:
            logger.error(f"Error creating action plan: {str(e)}")
            return self._get_fallback_plan(domain)
    
    def _get_fallback_plan(self, domain: str) -> Dict:
        """Return a generic fallback plan when AI generation fails"""
        return {
            "summary": "We're here to help you. Please provide more details so we can assist you better.",
            "immediate_actions": [
                "Share your specific situation or question",
                "Mention your location if relevant",
                "Tell us if this is urgent"
            ],
            "steps": [
                {
                    "step_number": 1,
                    "action": "Provide more details",
                    "details": "Help us understand your situation better by sharing specific information"
                }
            ],
            "documents_required": [],
            "eligibility": {
                "criteria": [],
                "status": "check_needed"
            },
            "risk_alerts": [],
            "resources": [],
            "estimated_time": "Unknown",
            "domain": domain,
            "created_at": datetime.utcnow().isoformat()
        }
    
    def format_action_plan_for_sms(self, action_plan: Dict) -> str:
        """
        Format action plan for SMS (160 character limit consideration)
        
        Args:
            action_plan: Full action plan dictionary
            
        Returns:
            SMS-friendly formatted text
        """
        summary = action_plan.get("summary", "")
        immediate_actions = action_plan.get("immediate_actions", [])
        
        # Create concise SMS message
        sms_text = f"{summary}\n\n"
        sms_text += "Quick Steps:\n"
        
        for i, action in enumerate(immediate_actions[:3], 1):  # Limit to 3 actions
            sms_text += f"{i}. {action}\n"
        
        # Add document info if available
        docs = action_plan.get("documents_required", [])
        if docs:
            sms_text += f"\nDocuments needed: {', '.join(docs[:2])}"
        
        # Truncate if too long
        if len(sms_text) > 300:
            sms_text = sms_text[:297] + "..."
        
        return sms_text
    
    def format_action_plan_for_whatsapp(self, action_plan: Dict) -> str:
        """
        Format action plan for WhatsApp with rich formatting
        
        Args:
            action_plan: Full action plan dictionary
            
        Returns:
            WhatsApp-friendly formatted text with emojis and formatting
        """
        summary = action_plan.get("summary", "")
        steps = action_plan.get("steps", [])
        
        # WhatsApp supports bold (*text*) and italic (_text_)
        whatsapp_text = f"*📋 Your Action Plan*\n\n{summary}\n\n"
        
        # Add immediate actions if available
        immediate_actions = action_plan.get("immediate_actions", [])
        if immediate_actions:
            whatsapp_text += "*⚡ Immediate Actions:*\n"
            for i, action in enumerate(immediate_actions, 1):
                whatsapp_text += f"• {action}\n"
            whatsapp_text += "\n"
        
        # Add detailed steps
        if steps:
            whatsapp_text += "*📝 Step-by-Step Guide:*\n\n"
            for step in steps[:5]:  # Limit to 5 steps for WhatsApp
                whatsapp_text += f"*{step['step_number']}.* {step['action']}\n"
                if step.get('details'):
                    whatsapp_text += f"   _{step['details']}_\n"
                whatsapp_text += "\n"
        
        # Add documents
        docs = action_plan.get("documents_required", [])
        if docs:
            whatsapp_text += "*📄 Required Documents:*\n"
            for doc in docs:
                whatsapp_text += f"• {doc}\n"
            whatsapp_text += "\n"
        
        # Add resources/contacts
        resources = action_plan.get("resources", [])
        if resources:
            whatsapp_text += "*📞 Help & Resources:*\n"
            for resource in resources[:3]:  # Limit to 3 resources
                whatsapp_text += f"• *{resource.get('name', 'Resource')}*"
                if resource.get('contact'):
                    whatsapp_text += f": {resource['contact']}"
                whatsapp_text += "\n"
            whatsapp_text += "\n"
        
        # Add risk alerts if any
        risk_alerts = action_plan.get("risk_alerts", [])
        if risk_alerts:
            whatsapp_text += "*⚠️ Important Alerts:*\n"
            for alert in risk_alerts[:2]:
                whatsapp_text += f"• {alert}\n"
            whatsapp_text += "\n"
        
        # Add estimated time
        estimated_time = action_plan.get("estimated_time")
        if estimated_time:
            whatsapp_text += f"*⏱️ Estimated Time:* {estimated_time}\n"
        
        return whatsapp_text
    
    def format_action_plan_for_voice(self, action_plan: Dict) -> str:
        """
        Format action plan for voice/audio output
        
        Args:
            action_plan: Full action plan dictionary
            
        Returns:
            Voice-friendly formatted text
        """
        summary = action_plan.get("summary", "")
        steps = action_plan.get("steps", [])
        
        voice_text = f"{summary}\n\n"
        voice_text += "Here are the steps you need to follow:\n\n"
        
        for step in steps:
            voice_text += f"Step {step['step_number']}: {step['action']}. "
            if step.get('details'):
                voice_text += f"{step['details']}. "
            voice_text += "\n"
        
        # Add documents
        docs = action_plan.get("documents_required", [])
        if docs:
            voice_text += f"\nYou will need the following documents: {', '.join(docs)}.\n"
        
        # Add resources
        resources = action_plan.get("resources", [])
        if resources:
            voice_text += "\nFor help, you can contact:\n"
            for resource in resources[:2]:  # Limit to 2 resources for voice
                voice_text += f"{resource['name']}: {resource.get('contact', '')}. "
        
        return voice_text
    
    async def get_eligibility_check(
        self,
        scheme_name: str,
        user_context: Dict,
        language: str = "en"
    ) -> Dict:
        """
        Check user eligibility for a specific scheme or service
        
        Args:
            scheme_name: Name of the government scheme or service
            user_context: User information for eligibility check
            language: User's preferred language
            
        Returns:
            Eligibility information
        """
        prompt = f"""
        Check eligibility for: {scheme_name}
        User information: {user_context}
        
        Provide eligibility information in simple language.
        Include:
        1. Eligibility criteria
        2. Whether the user is likely eligible (yes/no/maybe)
        3. What additional information is needed
        4. How to apply
        
        Respond in JSON format.
        """
        
        try:
            # Use AI service to check eligibility
            result = await ai_service.generate_response(
                user_message=prompt,
                context=user_context,
                language=language,
                literacy_level=user_context.get("literacy_level", "medium")
            )
            
            return {
                "scheme": scheme_name,
                "eligibility_info": result.get("response_text"),
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking eligibility: {str(e)}")
            return {
                "scheme": scheme_name,
                "eligibility_info": "Unable to check eligibility at this time. Please try again or contact the relevant office.",
                "checked_at": datetime.utcnow().isoformat()
            }

# Initialize singleton
action_planner = ActionPlanner()
