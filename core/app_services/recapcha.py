from django.conf import settings

from core.base_api import REQUEST


MIN_PERMISSION_SCOPE = 0.5


async def async_google_capcha(recaptcha_client: str) -> bool:
    recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'

    response_google = await REQUEST.arequest_post(recaptcha_url, headers={}, data={
        "secret": settings.RECAPTCHA_SECRET_KEY,
        "response": recaptcha_client,
    })

    if not response_google.is_success:
        return False

    try:
        result = response_google.json()

    except Exception:
        return False

    if result.get("score") and result["score"] >= MIN_PERMISSION_SCOPE:
        return True

    return False


def google_capcha(recaptcha_client: str) -> bool:
    recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'

    response_google = REQUEST.request_post(recaptcha_url, headers={}, data={
        "secret": settings.RECAPTCHA_SECRET_KEY,
        "response": recaptcha_client,
    })

    if not response_google.is_success:
        return False

    try:
        result = response_google.json()

    except Exception:
        return False

    if result.get("score") and result["score"] >= MIN_PERMISSION_SCOPE:
        return True

    return False
