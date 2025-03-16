from twilio.rest import Client
from app.core.config import settings
from typing import Optional, Dict, Any
import tempfile
import os

class WhatsAppClient:
    def __init__(self):
        self.client = Client(
            settings.WHATSAPP_ACCOUNT_SID,
            settings.WHATSAPP_AUTH_TOKEN
        )
        self.whatsapp_number = settings.WHATSAPP_PHONE_NUMBER

    async def send_message(
        self,
        to: str,
        text: str,
        audio: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp message with optional audio.
        """
        try:
            # Send text message
            message = self.client.messages.create(
                body=text,
                from_=f"whatsapp:{self.whatsapp_number}",
                to=f"whatsapp:{to}"
            )

            # If audio is provided, send it as a voice message
            if audio:
                # Save audio to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                    temp_file.write(audio)
                    temp_file_path = temp_file.name

                # Send voice message
                voice_message = self.client.messages.create(
                    media_url=[temp_file_path],
                    from_=f"whatsapp:{self.whatsapp_number}",
                    to=f"whatsapp:{to}"
                )

                # Clean up temporary file
                os.unlink(temp_file_path)

                return {
                    'text_message_sid': message.sid,
                    'voice_message_sid': voice_message.sid,
                    'status': 'sent'
                }

            return {
                'text_message_sid': message.sid,
                'status': 'sent'
            }

        except Exception as e:
            return {
                'error': str(e),
                'status': 'failed'
            }

    async def handle_incoming_message(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming WhatsApp message.
        """
        try:
            # Extract message details
            message_sid = request_data.get('MessageSid')
            from_number = request_data.get('From', '').replace('whatsapp:', '')
            message_body = request_data.get('Body', '')
            num_media = int(request_data.get('NumMedia', 0))
            media_content_type = request_data.get('MediaContentType0', '')
            media_url = request_data.get('MediaUrl0', '')

            # Prepare response data
            response_data = {
                'message_sid': message_sid,
                'from_number': from_number,
                'text': message_body,
                'has_media': num_media > 0,
                'media_type': media_content_type if num_media > 0 else None,
                'media_url': media_url if num_media > 0 else None
            }

            return response_data

        except Exception as e:
            return {
                'error': str(e),
                'status': 'failed'
            }

    async def start_voice_call(self, to: str) -> Dict[str, Any]:
        """
        Initiate a voice call using Twilio.
        """
        try:
            call = self.client.calls.create(
                url='http://your-webhook-url/voice',  # Replace with your webhook URL
                to=f"whatsapp:{to}",
                from_=f"whatsapp:{self.whatsapp_number}"
            )

            return {
                'call_sid': call.sid,
                'status': call.status
            }

        except Exception as e:
            return {
                'error': str(e),
                'status': 'failed'
            }

    def validate_webhook(self, request_data: Dict[str, Any]) -> bool:
        """
        Validate incoming webhook request from Twilio.
        """
        # Add your webhook validation logic here
        # For example, validate the request signature
        return True 