from collections import defaultdict
from csgame.views import over
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib.sessions.models import Session
from django.shortcuts import redirect
from functools import wraps
from .models import HIT
import uuid


NUMROUNDS = settings.NUMROUNDS


def player_required(func):
    '''
    Decorator for views that checks that the logged in user is a mturk worker, or staff
    redirects to the log-in page if necessary.
    '''
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        newCookie = request.GET.get('assignmentId')

        if newCookie == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            assignmentId = newCookie = None
        else:
            assignmentId = newCookie or request.COOKIES.get('assignmentid')

        if (request.user.is_staff or request.user.is_superuser) and not assignmentId:
            assignmentId = newCookie = request.user.username + "__" + uuid.uuid4().hex
        #if not assignmentId: # TODO: This line is ONLY for the June test of our code. Do not put on MTurk
        #    assignmentId = newCookie = "testing__" + uuid.uuid4().hex

        if assignmentId:
            hitObj = HIT.objects.only('data').get_or_create(assignment_id=assignmentId, defaults={'data': {}})[0]
            request.hit = hitObj.data

            roundnums = request.hit.setdefault('roundnums', {})

            numInPhase = roundnums.get(func.__name__, 0) # this line is pretty unsafe, but it will do

            if request.method == 'POST':
                output = func(request, *args, **kwargs)
                if newCookie: output.set_cookie('assignmentid', newCookie)
                roundnums[func.__name__] = numInPhase + 1
                hitObj.save()
                return output
            else:
                if numInPhase >= NUMROUNDS:
                    hitObj['hitId'] = request.GET['hitId']
                    hitObj.save()
                    return over(request, func.__name__)
                else:
                    output = func(request, *args, **kwargs)
                    if newCookie: output.set_cookie('assignmentid', newCookie)
                    return output
        else:
            return func(request, *args, **{'previewMode': True, **kwargs})
    return wrapper


# decorator that will not be used now
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
