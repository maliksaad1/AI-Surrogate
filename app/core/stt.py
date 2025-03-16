from google.cloud import speech
import io
from typing import Optional

async def speech_to_text(audio_data: bytes) -> Optional[str]:
    """
    Convert speech to text using Google Cloud Speech-to-Text API.
    Supports multiple languages.
    """
    # Create speech client
    client = speech.SpeechClient()

    # Create audio object
    audio = speech.RecognitionAudio(content=audio_data)

    # Configure recognition
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        enable_automatic_punctuation=True,
        language_codes=['en-US', 'ur-PK', 'pa-IN'],  # Support multiple languages
        model='default',
        use_enhanced=True,  # Use enhanced model for better accuracy
    )

    # Detect speech in audio
    try:
        response = client.recognize(
            config=config,
            audio=audio
        )

        # Process results
        if not response.results:
            return None

        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript + " "

        return transcript.strip()

    except Exception as e:
        print(f"Speech recognition error: {str(e)}")
        return None

def get_language_code(detected_language: str) -> str:
    """
    Convert detected language to Google Cloud Speech-to-Text language code.
    """
    language_codes = {
        'english': 'en-US',
        'urdu': 'ur-PK',
        'punjabi': 'pa-IN'
    }
    return language_codes.get(detected_language.lower(), 'en-US') 