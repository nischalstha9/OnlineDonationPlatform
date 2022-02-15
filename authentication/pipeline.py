USER_FIELDS = ['email']
from .models import Customer
from .utils import RandomStringTokenGenerator

def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        if '@' in user.email and not user.email_verified:
            user.email_verified = True
            user.save()
        return {'is_new': False}

    fields = dict((name, kwargs.get(name, details.get(name)))
                  for name in backend.setting('USER_FIELDS', USER_FIELDS))

    fields['role'] = 2
    fields['email_verified'] = True

    response = kwargs.get('response', None)
    if response:
        email_check = response.get('email', '')
    else:
        email_check = ''
    uid = kwargs.get('uid', None)
    if '@' not in email_check and uid:
        fields['email'] = uid
        fields['email_verified'] = False
    
    if not fields:
        return

    user = Customer(**fields)
    rand = RandomStringTokenGenerator(min_length=10, max_length=15)
    password = rand.generate_token()
    user.set_password(password)
    user.save()
    return {
        'is_new': True,
        'user': user
    }