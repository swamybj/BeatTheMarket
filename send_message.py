import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")


def send_twilio_message(to_phone_number: str, message: str) -> None:
    """
    Send SMS message using Twilio
    
    Args:
        to_phone_number (str): Recipient phone number with country code
        message (str): Message content to send
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Sending the SMS message
        message = client.messages.create(
            body=message, 
            from_=TWILIO_PHONE_NUMBER, 
            to=to_phone_number
        )

        print(f"Message sent with SID: {message.sid}")
        
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        # Don't raise the error to prevent breaking the alert system