'''
This middleware checks whether the incoming ip is allowed or not
'''
from django.conf import settings


def get_private_ips():
    '''
    Returns
        List of all private IPs of the form 192.168.X.Y
    TODO:
        Extend this to a more extensive list of private IPs
    '''

    private_ips = [f'192.168.{i}.{j}' for i in range(256) for j in range(256)]
    return private_ips


def get_client_ip(request):
    '''
    Returns
        returns client's ip

    Args
        request object as given by django

    TODO
        This function isn't secure at the moment. Either use the package django-ipware or create your own.
    '''
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
        print('FORWARDED:', ip)
    else:
        ip = request.META.get('REMOTE_ADDR')
        print('REMOTE:', ip)
    return ip


def allow_known_ip(get_response):
    ALLOWED_IPS = ['localhost', '127.0.0.1', ]
    ALLOWED_IPS.append(get_private_ips())

    def middleware(request):
        if get_client_ip(request) not in ALLOWED_IPS:
            return None

        response = get_response(request)
        return response

    return middleware
