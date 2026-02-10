import requests

from flask import redirect, render_template, session
from functools import wraps



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user_id is NOT in session (user is logged out)
        if "user_id" not in session:
            return redirect("/login")

        # If they are logged in, run the original function (f)
        return f(*args, **kwargs)

    return decorated_function

def get_12_hour_time(hour_24):
    if hour_24 < 12:
        return f"{str(hour_24)}:00 AM"
    elif hour_24 == 12:
        return f"{str(hour_24)}:00 AM"
    elif hour_24 > 12:
        return f"{str(hour_24-12)}:00 PM"
