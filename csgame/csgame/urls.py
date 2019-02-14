"""csgame URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, path, include
from django.contrib import admin
from users.views import player, requester

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('', include('users.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', users.SignUpView.as_View(), name='SignUp'),
    path('accounts/signup/player/', player.PlayerSignUpView.as_view(), name='player_signup'),
    path('accounts/signup/requester/', requester.RequesterSignUpView.as_view(), name='requester_signup'),
]
