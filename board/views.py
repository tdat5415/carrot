from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from function.crypto import encrypt, decrypt, hash, get_random_str, KEY
from function.location import get_address, get_coordinates
from function.check import get_post, keyword_check, token_auth
from function.forms import upload_file
from home.models import *
import json
from functools import reduce

DB_NAME = 'carrot_db'

def index(request):
    data = {}
    data['state'] = True
    data['detail'] = None
    name = get_random_str() + '.jpg'
    err_flag, err = upload_file(request, name)
    if err_flag: return JsonResponse(err)

    return JsonResponse(data)

def board(request):
    data = {}
    
    # post 형식 체크
    err_flag, post, err = get_post(request)
    if err_flag: return JsonResponse(err)

    # 키워드 유무 체크
    check_list = ['user_token', 'board_type']
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)

    # 토큰 인증
    user_token = post['user_token']
    err_flag, user_id, err = token_auth(user_token)
    if err_flag: return JsonResponse(err)

    user = Users.objects.using(DB_NAME).get(user_id=user_id)

    # 주소 None 확인
    if not user.address:
        data['state'] = False
        data['detail'] = 'db에 주소 저장이 안되있음'
        return JsonResponse(data)

    users = Users.objects.using(DB_NAME).filter(user_address=user.address)
    if not users:
        data['state'] = False
        data['detail'] = '주변 사용자들이 없습니다.'
        return JsonResponse(data)

    users_boards = [user.boards_set.filter(board_type=post['board_type']) for user in users]
    users_boards = reduce(lambda x,y:x|y, users_boards)
    if not users_boards:
        data['state'] = False
        data['detail'] = '주변 사용자들의 게시글이 없습니다.'
        return JsonResponse(data)

    titles = [b.board_title for b in users_boards]
    bodies = [b.board_body for b in users_boards]
    write_times = [b.board_write_datetime for b in users_boards]
    like_nums = [b.board_like_num for b in users_boards]
    writers = [b.board_writer_idx.user_id for b in users_boards]
    # thumbnails = [b.board_images_set.image_path_name for b in users_boards]


    data['state'] = True
    data['detail'] = '주변사용자 게시글({}) 가져오기 성공'.format(post['board_type'])
    data['titles'] = titles
    data['bodies'] = bodies
    data['write_times'] = write_times
    data['like_nums'] = like_nums
    data['writers'] = writers
    return JsonResponse(data)
    


    

    


    
        


