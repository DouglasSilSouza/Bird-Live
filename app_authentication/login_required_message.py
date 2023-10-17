try:
    from functools import wraps, WRAPPER_ASSIGNMENTS
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.

from django.contrib import messages

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required

default_message = "Por favor, faça o login, a fim de ver a página solicitada."
extra = 'class="bi flex-shrink-0 me-2" role="img" aria-label="Warning:" _mstaria-label="105781" _mstHash="244"><use xlink:href="#exclamation-triangle-fill"></use>'

def user_passes_test(test_func, message=default_message):
    """
    Decorator for views that checks that the user passes the given test,
    setting a message in case of no success. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    def decorator(view_func):
        @wraps(view_func,assigned=WRAPPER_ASSIGNMENTS)
        def _wrapped_view(request, *args, **kwargs):
            if not test_func(request.user):
                messages.warning(request, message, extra_tags=extra)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def login_required_message(function=None, message=default_message):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated, #fixed by removing ()
        message=message,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def login_required_message_and_redirect(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None, message=default_message):

    if function:
        return login_required_message(
            login_required(function, redirect_field_name, login_url),
            message
        )

    return lambda deferred_function: login_required_message_and_redirect(deferred_function, redirect_field_name, login_url, message)