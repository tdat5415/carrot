from django.utils import timezone
from function.crypto import get_random_str
import os

def handle_uploaded_file(f):
    name, tail = str(f).split('.')
    now = str(timezone.now()).split()[0]
    r_str = get_random_str()
    file_name = '{}_{}_{}.{}'.format(name, now, r_str, tail)

    with open('static/{}'.format(file_name), 'wb+') as dst:
        for chunk in f.chunks():
            dst.write(chunk)

    return file_name

def handle_files(request, board):
    # 기존 이미지 삭제
    for path in board.boardimages_set.values_list("image_path_name", flat=True):
        if os.path.isfile("." + path):
            os.remove("." + path)
    board.boardimages_set.all().delete()
    # 새로운 이미지 저장
    files = request.FILES.getlist('files')
    thumb_flag = True
    for f in files:
        file_name = handle_uploaded_file(f)
        dic = {}
        dic['image_path_name'] = '/static/{}'.format(file_name)
        dic['image_thumbnail'] = thumb_flag
        thumb_flag = False
        board.boardimages_set.create(**dic)
