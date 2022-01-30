from function.crypto import get_random_str

def handle_uploaded_file(f, name, tail='.jpg'):
    with open('static/{}{}'.format(name, tail), 'wb+') as dst:
        for chunk in f.chunks():
            dst.write(chunk)
