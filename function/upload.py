from django.utils import timezone
from function.crypto import get_random_str

def handle_uploaded_file(f):
    name, tail = str(f).split('.')
    now = str(timezone.now()).split()[0]
    r_str = get_random_str()
    file_name = '{}_{}_{}.{}'.format(name, now, r_str, tail)

    with open('static/{}'.format(file_name), 'wb+') as dst:
        for chunk in f.chunks():
            dst.write(chunk)

    return file_name
