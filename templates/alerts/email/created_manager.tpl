{% extends 'email/base_email.tpl' %}
{% block content %}
<p>Вы авторизованы на портале {{ settings.APP_HOST }} как менеджер компании "{{company.name}}".</p>
<p>login: {{ login }}</p>
<p>password: {{ password }}</p>
<p><a href="https://{{action['url']}}">Для аутентификации пройдите по ссылке</a></p>
{% endblock %}