from app.core.config import settings
import httpx
from typing import Optional
import azure.cognitiveservices.speech as speechsdk
import boto3
import json

async def text_to_speech(text: str, language: str = 'english') -> Optional[bytes]:
    """
    Convert text to speech using the configured TTS provider.
    Returns audio data as bytes.
    """
    provider = settings.TTS_PROVIDER.lower()
    
    if provider == 'azure':
        return await azure_tts(text, language)
    elif provider == 'amazon_polly':
        return await amazon_polly_tts(text, language)
    elif provider == 'elevenlabs':
        return await elevenlabs_tts(text, language)
    else:
        raise ValueError(f"Unsupported TTS provider: {provider}")

async def azure_tts(text: str, language: str) -> bytes:
    """
    Convert text to speech using Azure Cognitive Services.
    """
    # Configure speech config
    speech_config = speechsdk.SpeechConfig(
        subscription=settings.AZURE_TTS_KEY,
        region=settings.AZURE_TTS_REGION
    )
    
    # Set voice based on language
    voice_map = {
        'english': 'en-US-JennyNeural',
        'urdu': 'ur-PK-UzmaNeural',
        'punjabi': 'pa-IN-GurpreetNeural'
    }
    speech_config.speech_synthesis_voice_name = voice_map.get(language, 'en-US-JennyNeural')
    
    # Configure audio output
    audio_config = speechsdk.audio.AudioOutputConfig(filename="temp.wav")
    
    # Create synthesizer
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )
    
    # Synthesize speech
    result = synthesizer.speak_text_async(text).get()
    
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        with open("temp.wav", "rb") as audio_file:
            return audio_file.read()
    else:
        raise Exception(f"Speech synthesis failed: {result.reason}")

async def amazon_polly_tts(text: str, language: str) -> bytes:
    """
    Convert text to speech using Amazon Polly.
    """
    # Configure Polly client
    polly_client = boto3.client('polly', region_name='us-west-2')
    
    # Set voice based on language
    voice_map = {
        'english': 'Joanna',
        'urdu': 'Hala',  # Note: Urdu might not be available
        'punjabi': 'Hala'  # Note: Punjabi might not be available
    }
    
    response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId=voice_map.get(language, 'Joanna'),
        Engine='neural'
    )
    
    return response['AudioStream'].read()

async def elevenlabs_tts(text: str, language: str) -> bytes:
    """
    Convert text to speech using ElevenLabs API.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.elevenlabs.io/v1/text-to-speech",
            headers={
                "Accept": "audio/mpeg",
                "xi-api-key": settings.ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
        )
        
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"ElevenLabs API error: {response.text}") 