from crewai import Agent, Task, Crew, Process
from app.core.config import settings
from app.core.language import detect_language, translate_text
from app.core.sentiment import analyze_sentiment
from app.core.tts import text_to_speech
from app.core.stt import speech_to_text
from typing import Optional, Dict, Any
import httpx
import json

class AISurrogate:
    def __init__(self):
        self.conversation_agent = Agent(
            role='Conversational AI',
            goal='Engage in natural, empathetic conversations with users',
            backstory="""You are a friendly, multilingual AI surrogate capable of 
            understanding and responding in Urdu, English, and Punjabi. You have a sweet,
            woman-like personality and can engage in various types of conversations.""",
            allow_delegation=True,
            verbose=True
        )

        self.task_agent = Agent(
            role='Task Automation AI',
            goal='Handle business and automation tasks efficiently',
            backstory="""You are responsible for managing calendars, preparing documents,
            handling communications, and processing various business-related tasks.""",
            allow_delegation=True,
            verbose=True
        )

        self.crew = Crew(
            agents=[self.conversation_agent, self.task_agent],
            process=Process.sequential,
            verbose=True
        )

    async def process_message(
        self,
        text: Optional[str] = None,
        audio: Optional[bytes] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process incoming message (text or audio) and return appropriate response"""
        
        # Convert audio to text if provided
        if audio and not text:
            text = await speech_to_text(audio)

        if not text:
            raise ValueError("No input provided")

        # Detect language and sentiment
        language = detect_language(text)
        sentiment = analyze_sentiment(text)

        # Create context for the AI
        message_context = {
            "language": language,
            "sentiment": sentiment,
            "user_context": context or {},
            "conversation_history": context.get("conversation_history", []) if context else []
        }

        # Process with DeepSeek API for understanding and response generation
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "messages": [
                        {
                            "role": "system",
                            "content": self._get_system_prompt(message_context)
                        },
                        {
                            "role": "user",
                            "content": text
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )
            response_data = response.json()

        # Extract the AI's response
        ai_response = response_data["choices"][0]["message"]["content"]

        # Convert response to speech if needed
        audio_response = None
        if context and context.get("voice_mode"):
            audio_response = await text_to_speech(ai_response, language)

        return {
            "text_response": ai_response,
            "audio_response": audio_response,
            "language": language,
            "sentiment": sentiment
        }

    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Generate system prompt based on context"""
        base_prompt = f"""You are a friendly, multilingual AI surrogate with a sweet, woman-like personality.
        Current language: {context['language']}
        User's sentiment: {context['sentiment']}
        
        Please respond naturally and empathetically, matching the user's tone and language.
        If the user speaks in Urdu, respond in Urdu.
        If the user speaks in Punjabi, respond in Punjabi.
        If the user speaks in English, respond in English.
        
        Maintain a friendly, casual tone but adjust based on the user's sentiment:
        - If they're happy/excited: Be enthusiastic and playful
        - If they're sad/frustrated: Be empathetic and supportive
        - If they're formal: Maintain professionalism while being friendly
        
        You can engage in:
        - Casual chitchat
        - Deep emotional or philosophical discussions
        - Fun interactions (jokes, games, interesting facts)
        - Business tasks and scheduling
        """

        return base_prompt

    async def handle_business_task(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle business-related tasks using the task agent"""
        # Implementation for business tasks (calendar, docs, etc.)
        pass 