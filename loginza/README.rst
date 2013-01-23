==============
Django Loginza
==============

Django-приложение, обеспечивающее работу с сервисом авторизации Loginza (loginza.ru)

Установка
=========

В настоящее время приложение доступно только в виде исходного кода без установки в систему.
Последняя актуальная версия доступна в `репозитории GitHub`__.

Для того, чтобы добавить приложение в свой Django-проект, поместите модуль в корень проекта,
причем название пакета (директории) должно быть *loginza*, а не *django-loginza*. Для корректной
работы приложения необходимо, чтобы так же был установлено приложения ``django.contrib.auth``,
``django.contrib.sessions`` и ``django.contrib.sites``.

После этого, необходимо добавить приложение в ``INSTALLED_APPS`` и добавить бэкэнд авторизации -
``loginza.authentication.LoginzaBackend`` в ``AUTHENTICATION_BACKENDS``. В общем случае, бэкэнды
авторизации после добавления нового, будут выглядеть так::

 AUTHENTICATION_BACKENDS = (
     'django.contrib.auth.backends.ModelBackend',
     'loginza.authentication.LoginzaBackend',
 )

В этом случае, можно будет использовать как стандартную форму авторизации по логину и паролю
(например, для доступа в админскую панель), так и loginza-авторизацию.

После добавления приложения, необходимо установить необходимый таблицы в БД (выполнить
``python manage.py suncdb`` в корне проекта).

Далее, нужно зарегистрировать ссылки приложения в проекте. В общем случае,
необходимо добавить следующий элемент в ``urlpatterns`` проекта в ``urls.py``::

 (r'^loginza/', include('loginza.urls')),

Использование
=============

Приложение можно условно разделить на 3 составляющих:

- шаблонные теги, для отображения виджета авторизации на странице
- сигналы, позволяющие другим приложениям взаимодействовать с данным
- внутрення логика приложения

Этот документ рассматривает только первые две составляющие.

Шаблонные теги
==============

Для того, чтобы отобразить виджет авторизации в шаблоне, сначала необходимо загрузить тэги::

 {% load loginza_widget %}

После этого, становятся доступны следущие теги:

- ``loginza_iframe`` - встраиваемый виджета авторизации Loginza (спаренная форма авторизации)
- ``loginza_button`` - кнопка виджета Loginza
- ``loginza_icons`` - набор иконок провайдеров

Примеры отображения виджетов можно посмотреть на странице
`Примеры интеграции Loginza в форму авторизации сайта`__.

Для всех тэгов, кроме ``loginza_iframe`` необходим обязательный параметр caption.
Для ``loginza_button`` он используется для атрибутов ``alt`` и ``title`` изображения кнопки,
для ``loginza_icons`` - текст, перед набором иконок (например, *Войти используя:*).

Так же, для всех виджетов доступны следующие именованные параметры:

- ``lang`` - язык виджета
- ``providers_set`` - доспуные кнопки и порядок провайдеров
- ``provider`` - провайдер авторизации по умолчанию

Например::

  {% loginza_iframe providers_set="google,facebook,twitter" lang="en" %}

Более подробно об этих параметрах можно прочитать в `Руководстве по Loginza.API`__.

В общем случае шаблон, отвечающий за авторизацию, будет выглядеть следующим образом::

 {% load loginza_widget %}
 {% if user.is_authenticated %}
   Добро пожаловать, {{ user }}
 {% else %}
   {% loginza_button "Войти через loginza" %}
 {% endif %}

Сигналы
=======

Приложение предоставляет 3 сигнала:

- ``created`` - создана новая связка между идентификатором Loginza и пользователем Django
- ``error`` - во время авторизации произошла ошибка
- ``authenticated`` - пользователь спешно авторизован (authenticated) и готов быть залогинен

Более подробно о сигналах и их параметрах можно прочитать в их документации к сигналам в ``signals.py``
приложения.

Пример ``views.py`` вспомогательного приложения ``users``, использующего сигналы приложения ``loginza``::

 # -*- coding:utf-8 -*-
 from django import http
 from django.contrib import messages, auth
 from django.shortcuts import redirect, render_to_response
 from django.core.urlresolvers import reverse
 from django.template.context import RequestContext

 from users import forms
 from loginza import signals, models
 from loginza.templatetags.loginza_widget import _return_path

 def loginza_error_handler(sender, error, **kwargs):
     messages.error(sender, error.message)

 signals.error.connect(loginza_error_handler)

 def loginza_auth_handler(sender, user, identity, **kwargs):
     try:
         # it's enough to have single identity verified to treat user as verified
         models.UserMap.objects.get(user=user, verified=True)
         auth.login(sender, user)
     except models.UserMap.DoesNotExist:
         sender.session['users_complete_reg_id'] = identity.id
         return redirect(reverse('users.views.complete_registration'))

 signals.authenticated.connect(loginza_auth_handler)

 def complete_registration(request):
     if request.user.is_authenticated():
         return http.HttpResponseForbidden(u'Вы попали сюда по ошибке')
      try:
         identity_id = request.session.get('users_complete_reg_id', None)
         user_map = models.UserMap.objects.get(identity__id=identity_id)
     except models.UserMap.DoesNotExist:
         return http.HttpResponseForbidden(u'Вы попали сюда по ошибке')
     if request.method == 'POST':
         form = forms.CompleteReg(user_map.user.id, request.POST)
         if form.is_valid():
             user_map.user.username = form.cleaned_data['username']
             user_map.user.email = form.cleaned_data['email']
             user_map.user.save()

             user_map.verified = True
             user_map.save()

             user = auth.authenticate(user_map=user_map)
             auth.login(request, user)

             messages.info(request, u'Добро пожаловать!')
             del request.session['users_complete_reg_id']
             return redirect(_return_path(request))
     else:
         form = forms.CompleteReg(user_map.user.id, initial={
             'username': user_map.user.username, 'email': user_map.user.email,
             })

     return render_to_response('users/complete_reg.html',
                               {'form': form},
                               context_instance=RequestContext(request),
                               )

Для того, чтобы пример выше работал корректно, необходимо так же в ``settings.py`` проекта добавить
следующие настройки (подробнее читайте в разделе *Настройки*)::

 # can't use reverse url resolver here (raises ImportError),
 # so we should carefully control paths
 LOGINZA_AMNESIA_PATHS = ('/users/complete_registration/',)

Настройки
=========

В приложении доступны следующие настройки:

- ``LOGINZA_DEFAULT_LANGUAGE`` - язык по умолчанию, если параметр ``lang`` не задан для виджета явно.
  Выбирается на основе ``LANGUAGE_CODE`` проекта.
- ``LOGINZA_DEFAULT_PROVIDERS_SET`` - набор провайдеров, используемых по умолчанию,
  если параметр ``providers_set`` не задан. Формат - имена провайдеров через запятую,
  например 'facebook,twitter,google'. ``None`` - все доступные провайдеры.
- ``LOGINZA_DEFAULT_PROVIDER`` - провайдер, используемый по умолчанию,
  если параметр ``provider`` не задан для виджета явно. ``None`` - не задан.
- ``LOGINZA_ICONS_PROVIDERS`` - иконки провайдеров, отображаемые виджетом loginza_icons,
  по умолчанию все доступные. Используется, только если параметр `providers_set`` не задан для виджета явно и
  настройка ``LOGINZA_DEFAULT_PROVIDERS_SET`` не задана. Формат - имена провайдеров через запятую,
  например 'facebook,twitter,google'.
- ``LOGINZA_PROVIDER_TITLES`` - заголовки провайдеров, используемые для изображений виджета
  ``loginza_icons``. Формат - словарь с ключами именами провайдерв, и значениями - заголовками, например
  {'google': u'Корпорация добра', 'twitter': u'Щебетальня', 'vkontakte': u'Вконтактик'}
- ``LOGINZA_DEFAULT_EMAIL`` - адрес электронной почты, используемый для новых пользователей, в случае,
  если Loginza не предоставила, таковой. По умолчанию - 'user@loginza'
- ``LOGINZA_AMNESIA_PATHS`` - список или кортеж путей, которые не будут запоминаться для взврата.
  Например, как показано в примере выше, страница завершения регистрации не запоминается, для того,
  чтобы после успешной авторизации пользователь был возвращен на страницу, с которой авторзация началась,
  а не на пустую страницу завершения регистрации.

:Автор: Владимир Гарвардт
:Благодарности: Ивану Сагалаеву, Юрию Юревичу

__ https://github.com/vgarvardt/django-loginza
__ http://loginza.ru/signin-integration
__ http://loginza.ru/api-overview
