{% extends 'email/base_email.tpl' %}
{% block content %}
<p>У вас новая задача!</p>
<p><a href="https://{{action['url']}}">Для аутентификации пройдите по ссылке</a></p>
{% endblock %}
