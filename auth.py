from flask import jsonify
from functools import wraps
from flask import request
from models import SolarPanel

def validate_token(access_token):
    '''Verifies that an access-token is valid and
    meant for this app.

    Returns None on fail, and an e-mail on success'''
    '''h = Http()
    resp, cont = h.request("https://www.googleapis.com/oauth2/v2/userinfo",
                           headers={'Host': 'www.googleapis.com',
                                    'Authorization': access_token})

    if not resp['status'] == '200':
        return None

    try:
        data = json.loads(cont)
    except TypeError:
        # Running this in Python3
        # httplib2 returns byte objects
        data = json.loads(cont.decode())

    return data['email']'''
    x = SolarPanel.query.filter(email=access_token)
    return x.id if x else 'Not found you mf idiot'
    

def authorized(fn):
    @wraps(fn)
    def check_auth(*args, **kwargs):
        if 'Authorization' not in request.headers:
            # Unauthorized
            print("No token in header")
            return 'Unauthorized', 404

        print("Checking token...")
        userid = validate_token(request.headers['Authorization'])
        if userid is None:
            print("Check returned FAIL!")
            # Unauthorized
            return 'Unauthorized', 404

        return fn(userid=userid, *args, **kwargs)
    return check_auth
