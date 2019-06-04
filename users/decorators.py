from csgame.views import stop
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from functools import wraps


def player_required(func):
    '''
    Decorator for views that checks that the logged in user is a player,
    redirects to the log-in page if necessary.
    '''
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        assignment = request.GET.get('assignment')
        is_mturker = assignment not in (None, 'ASSIGNMENT_ID_NOT_AVAILABLE')

        if is_mturker:
            request.session['assignment'] = assignment

        if request.user.is_staff or "assignment" in request.session:
            return func(request, *args, **kwargs)
        else:
            return stop(request)
    return wrapper



def requester_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    '''
    Decorator for views that checks that the logged in user is a player,
    redirects to the log-in page if necessary.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_staff or (u.is_active and u.is_requester),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
