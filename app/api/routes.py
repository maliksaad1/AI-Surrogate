from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from app.core.ai_agent import AISurrogate
from app.integrations.whatsapp import WhatsAppClient
from app.core.config import settings
from typing import Dict, Any
import json

router = APIRouter()
ai_surrogate = AISurrogate()
whatsapp_client = WhatsAppClient()

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle incoming WhatsApp messages and events.
    """
    try:
        # Get request data
        request_data = await request.form()
        
        # Validate webhook
        if not whatsapp_client.validate_webhook(dict(request_data)):
            raise HTTPException(status_code=403, detail="Invalid webhook request")

        # Handle the message in the background
        background_tasks.add_task(
            handle_whatsapp_message,
            dict(request_data)
        )

        return {"status": "processing"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def handle_whatsapp_message(request_data: Dict[str, Any]):
    """
    Process WhatsApp message and generate response.
    """
    try:
        # Parse incoming message
        message_data = await whatsapp_client.handle_incoming_message(request_data)
        
        if message_data.get('error'):
            print(f"Error handling message: {message_data['error']}")
            return

        # Extract message details
        from_number = message_data['from_number']
        text = message_data['text']
        has_media = message_data['has_media']
        media_type = message_data['media_type']
        media_url = message_data['media_url']

        # Handle voice message
        if has_media and media_type.startswith('audio'):
            # Download audio file
            async with httpx.AsyncClient() as client:
                response = await client.get(media_url)
                audio_data = response.content

            # Convert speech to text
            text = await speech_to_text(audio_data)
            
            if not text:
                await whatsapp_client.send_message(
                    to=from_number,
                    text="I couldn't understand the audio. Could you please type your message?"
                )
                return

        # Process message with AI surrogate
        ai_response = await ai_surrogate.process_message(
            text=text,
            context={
                'from_number': from_number,
                'voice_mode': has_media and media_type.startswith('audio')
            }
        )

        # Send response
        await whatsapp_client.send_message(
            to=from_number,
            text=ai_response['text_response'],
            audio=ai_response['audio_response'] if ai_response['audio_response'] else None
        )

    except Exception as e:
        print(f"Error processing message: {str(e)}")
        # Send error message to user
        await whatsapp_client.send_message(
            to=from_number,
            text="I'm having trouble processing your message. Please try again later."
        )

@router.post("/webhook/voice")
async def voice_webhook(request: Request):
    """
    Handle incoming voice calls.
    """
    try:
        # Get request data
        request_data = await request.form()
        
        # Generate TwiML response
        twiml_response = """
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="alice">Hello! I'm your AI surrogate. How can I help you today?</Say>
            <Record maxLength="300" action="/api/webhook/voice/recording" />
        </Response>
        """
        
        return Response(content=twiml_response, media_type="application/xml")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook/voice/recording")
async def voice_recording_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle voice recording from call.
    """
    try:
        # Get request data
        request_data = await request.form()
        
        # Process recording in background
        background_tasks.add_task(
            handle_voice_recording,
            dict(request_data)
        )
        
        return {"status": "processing"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def handle_voice_recording(request_data: Dict[str, Any]):
    """
    Process voice recording and generate response.
    """
    try:
        # Download recording
        recording_url = request_data.get('RecordingUrl')
        async with httpx.AsyncClient() as client:
            response = await client.get(recording_url)
            audio_data = response.content

        # Convert speech to text
        text = await speech_to_text(audio_data)
        
        if not text:
            return

        # Process with AI surrogate
        ai_response = await ai_surrogate.process_message(
            text=text,
            context={'voice_mode': True}
        )

        # Generate TwiML response
        twiml_response = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="alice">{ai_response['text_response']}</Say>
            <Record maxLength="300" action="/api/webhook/voice/recording" />
        </Response>
        """
        
        return Response(content=twiml_response, media_type="application/xml")

    except Exception as e:
        print(f"Error processing voice recording: {str(e)}")
        return None 