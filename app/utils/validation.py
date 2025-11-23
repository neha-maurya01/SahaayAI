import re
from typing import Optional
from pydantic import BaseModel, validator

class MessageRequest(BaseModel):
    phone_number: str
    message: str
    channel: str = "sms"
    language: Optional[str] = None
    
    @validator('phone_number')
    def validate_phone(cls, v):
        # Basic phone number validation
        phone_pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
        if not phone_pattern.match(v.replace(" ", "").replace("-", "")):
            raise ValueError('Invalid phone number format')
        return v.replace(" ", "").replace("-", "")
    
    @validator('channel')
    def validate_channel(cls, v):
        valid_channels = ['sms', 'whatsapp', 'voice', 'web']
        if v not in valid_channels:
            raise ValueError(f'Channel must be one of {valid_channels}')
        return v

class ActionPlanRequest(BaseModel):
    user_query: str
    domain: str
    user_context: dict = {}
    
    @validator('domain')
    def validate_domain(cls, v):
        valid_domains = ['health', 'agriculture', 'finance', 'education', 'government_schemes', 'climate']
        if v not in valid_domains:
            raise ValueError(f'Domain must be one of {valid_domains}')
        return v

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>{}[\]\\]', '', text)
    
    # Limit length
    max_length = 5000
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()

def validate_language_code(lang_code: str, supported_languages: list) -> bool:
    """Validate if language code is supported"""
    return lang_code in supported_languages

def validate_message_content(text: str) -> dict:
    """
    Validate message content for appropriateness and relevance
    Returns dict with is_valid and message
    """
    if not text:
        return {
            "is_valid": False,
            "message": "Please enter a message."
        }
    
    lower_text = text.lower()
    
    # 1. Check message length
    if len(text) < 3:
        return {
            "is_valid": False,
            "message": "Hi there! 👋\n\nYour message seems a bit short. Could you please describe your question in a little more detail? I'm here to help!"
        }
    
    # 2. Block inappropriate content
    inappropriate_patterns = [
        r'\b(porn|xxx|sex|nude|naked)\b',
        r'\b(hack|crack|pirate|warez)\b',
        r'\b(cocaine|heroin|marijuana|drug)\b',
        r'\b(weapon|gun|bomb|explosive)\b',
        r'\b(kill|murder|suicide)\b',
        r'\b(scam|fraud scheme|money laundering)\b',
        r'\b(casino|gambling|betting|lottery)\b'
    ]
    
    for pattern in inappropriate_patterns:
        if re.search(pattern, lower_text, re.IGNORECASE):
            return {
                "is_valid": False,
                "message": (
                    "I appreciate you reaching out! 😊\n\n"
                    "However, I'm specifically designed to help with essential services like:\n\n"
                    "🏥 Healthcare and medical support\n"
                    "🌾 Agriculture and farming assistance\n"
                    "💰 Banking and financial services\n"
                    "🏛️ Government schemes and welfare\n"
                    "📚 Education and scholarships\n"
                    "📋 Legal documentation help\n\n"
                    "How can I assist you with any of these topics today?"
                )
            }
    
    # 3. Check for spam patterns
    if re.search(r'(.)\1{10,}', text):  # Repeated characters
        return {
            "is_valid": False,
            "message": "Hmm... 🤔\n\nI couldn't understand your message. Could you please write a clear question? I'm here to help with government services and essential information!"
        }
    
    # 4. Detect off-topic entertainment/shopping queries
    off_topic_patterns = [
        # Entertainment
        r'\b(movie|film|cinema|song|music|singer|actor|actress|celebrity|bollywood|hollywood)\b',
        r'\b(game|video game|gaming|xbox|playstation|pubg|fortnite|minecraft)\b',
        r'\b(netflix|amazon prime|hotstar|youtube|tiktok|instagram|facebook|twitter|snapchat|whatsapp)\b',
        r'\b(tv show|series|episode|season|anime|cartoon)\b',
        # Sports
        r'\b(cricket|football|soccer|hockey|tennis|basketball|badminton|ipl|world cup)\b',
        r'\b(match|player|team|tournament|score|champion|league)\b',
        # Food & Dining
        r'\b(recipe|cook|cooking|restaurant|cafe|pizza|burger|biryani|chai|coffee)\b',
        r'\b(food delivery|swiggy|zomato|uber eats|dominos|mcdonalds|kfc)\b',
        # Shopping & E-commerce
        r'\b(shopping|shop|buy|amazon|flipkart|myntra|ajio|meesho)\b',
        r'\b(fashion|clothes|dress|shoes|jewelry|makeup|cosmetic)\b',
        r'\b(mobile phone|smartphone|iphone|samsung|laptop|headphone|gadget)\b',
        # Travel & Tourism
        r'\b(vacation|holiday|tour|travel|hotel|resort|flight|ticket|booking)\b',
        r'\b(tourist|destination|beach|mountain|trip)\b',
        # Technology (general consumer tech)
        r'\b(android app|ios app|download app|mobile game|whatsapp status)\b',
        # Relationships & Personal
        r'\b(boyfriend|girlfriend|relationship|dating|love|marriage proposal|crush)\b',
        # Astrology
        r'\b(horoscope|astrology|zodiac|luck|fortune|kundli|vastu)\b',
    ]
    
    for pattern in off_topic_patterns:
        if re.search(pattern, lower_text, re.IGNORECASE):
            return {
                "is_valid": False,
                "message": (
                    "Thanks for your question! 😊\n\n"
                    "I noticed this might be about entertainment, shopping, or general topics. "
                    "While I'd love to chat about everything, I'm specially trained to help with:\n\n"
                    "🏥 Healthcare - Finding doctors, getting insurance, medical schemes\n"
                    "🌾 Agriculture - Crop advice, farming loans, subsidies\n"
                    "💰 Finance - Opening bank accounts, getting loans, financial planning\n"
                    "🏛️ Government Schemes - PM-JAY, PM-KISAN, scholarships, and more\n"
                    "📚 Education - School admission, scholarships, training programs\n"
                    "🌦️ Climate & Disasters - Weather alerts, emergency support\n\n"
                    "What can I help you with from these areas?"
                )
            }
    
    # 5. Check if message is relevant (has domain-specific keywords)
    domain_specific_keywords = [
        # Health
        'health', 'hospital', 'doctor', 'medical', 'medicine', 'disease', 'illness', 'treatment',
        'insurance', 'ayushman', 'clinic', 'surgery', 'patient', 'healthcare', 'covid',
        # Agriculture
        'farm', 'crop', 'seed', 'fertilizer', 'agriculture', 'kisan', 'irrigation', 'harvest',
        'soil', 'pesticide', 'tractor', 'land', 'cultivation', 'organic', 'farmer',
        # Finance
        'bank', 'loan', 'money', 'finance', 'saving', 'account', 'credit', 'debit',
        'payment', 'insurance', 'investment', 'pension', 'subsidy', 'mudra', 'financial',
        # Government schemes
        'scheme', 'yojana', 'government', 'welfare', 'benefit', 'eligibility',
        'registration', 'certificate', 'document', 'aadhar', 'ration', 'pension',
        'subsidy', 'pradhan mantri', 'ayushman', 'ujjwala', 'awas',
        # Education
        'education', 'school', 'college', 'scholarship', 'student', 'study', 'exam',
        'degree', 'course', 'training', 'skill', 'learning', 'admission', 'fees',
        # Legal/Documentation
        'legal', 'law', 'court', 'certificate', 'license', 'permit',
        'passport', 'voter', 'pan', 'rights', 'complaint', 'ration card',
        # Climate
        'weather', 'rain', 'flood', 'drought', 'disaster', 'climate', 'cyclone',
        'emergency', 'relief', 'alert'
    ]
    
    has_domain_content = any(keyword in lower_text for keyword in domain_specific_keywords)
    
    # If no domain-specific keywords found
    if not has_domain_content:
        return {
            "is_valid": False,
            "message": (
                "Hello! 👋 I'm SahaayAI, your friendly assistant for essential services.\n\n"
                "I'm here to make your life easier by helping with:\n\n"
                "🏥 Healthcare - \"How do I get Ayushman Bharat card?\"\n"
                "🌾 Agriculture - \"What loans are available for farmers?\"\n"
                "💰 Finance - \"How can I open a Jan Dhan account?\"\n"
                "🏛️ Government Schemes - \"Am I eligible for PM-KISAN?\"\n"
                "📚 Education - \"What scholarships are available for students?\"\n"
                "🌦️ Climate Support - \"How to get flood relief assistance?\"\n\n"
                "Try asking me something like the examples above, and I'll do my best to help! 😊"
            )
        }
    
    # Message passed all checks
    return {
        "is_valid": True,
        "message": ""
    }
