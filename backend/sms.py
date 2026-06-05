import random
import africastalking
from django.conf import settings


def init_at():
    africastalking.initialize(
        username=settings.AT_USERNAME,
        api_key=settings.AT_API_KEY,
    )
    return africastalking.SMS


def send_otp(phone: str) -> dict:
    """
    Generate a 6-digit OTP, send via Africa's Talking SMS,
    and return {'success': True/False, 'code': '123456', 'message': '...'}
    """
    code = str(random.randint(100000, 999999))

    # Normalise phone: ensure it starts with +
    phone = phone.strip().replace(' ', '').replace('-', '')
    if phone.startswith('0'):
        phone = '+233' + phone[1:]
    elif not phone.startswith('+'):
        phone = '+' + phone

    try:
        sms = init_at()
        message = f"Your Avefon Trade Ltd verification code is: {code}. Valid for 10 minutes. Do not share this code."
        response = sms.send(message, [phone], sender_id=settings.AT_SENDER)
        recipients = response.get('SMSMessageData', {}).get('Recipients', [])
        if recipients and recipients[0].get('status') == 'Success':
            return {'success': True, 'code': code, 'message': f'Code sent to {phone}'}
        else:
            error = recipients[0].get('status', 'Unknown error') if recipients else 'No response'
            return {'success': False, 'code': code, 'message': error}
    except Exception as e:
        return {'success': False, 'code': code, 'message': str(e)}