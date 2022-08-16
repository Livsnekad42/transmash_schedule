{% extends 'email/base_email.tpl' %}
{% block content %}
<p>Для вашего аккаунта были изменены роли.</p>
<p><a href="https://{{action['url']}}">Для аутентификации пройдите по ссылке</a></p>
{% endblock %}
