# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_HOST_USER = "robot@nft2go.io"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = 'KotovITBST42!'
SERVER_EMAIL = EMAIL_HOST_USER

EMAIL_USE_SSL = True
EMAIL_USE_TLS = False

ADMINS = (('Владелец', 'mail@host.ru'), )
EMAIL_MANAGER = "manager@host.ru"

# SMS API
SMS_SEND_URL = "https://webintellect42@gmail.com:rMeKvbVPMVnfbxaNt0om931wdyod@gate.smsaero.ru/v2/sms/send?number={0}&text={1}&sign=SMS Aero"

# DADATA
DADATA_API_KEY = "357a3dc3ba7123805ce798d5fd5f634d0837185a"
DADATA_SECRET = "3d5cacc9b15c6f62db0141cbad54527a7c5735c1"

# GOOGLE CAPCHA
RECAPTCHA_SECRET_KEY = "6LfmZTEfAAAAAExwsNAgSqRnUzdmhNd684NfeTJY"
