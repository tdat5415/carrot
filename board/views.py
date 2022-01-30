from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from function.crypto import encrypt, decrypt, hash, get_random_str, KEY
from function.location import get_address, get_coordinates
from function.check import get_post, keyword_check, token_auth
from function.upload import handle_uploaded_file
from home.models import *
import json
from functools import reduce

# multipart/form-data 요단어 기억
# application/x-www-form-urlencoded

DB_NAME = 'carrot_db'

@csrf_exempt
def index(request):
    data = {}

    print('###')
    # print(dir(request))
    # print(request.header)
    # print(request.body)
    print(request.headers)
    print(request.POST)
    print(request.POST['title'])
    # print(request.FILES)
    file = request.FILES.getlist('files')[0]
    handle_uploaded_file(file, get_random_str())
    print(type(request.FILES))
    print(type(request.FILES['files']))
    print(type(request.FILES.getlist('files')[0]))
    # print(request.body.decode('utf-8'))
    # print(type(request.body.decode('utf-8')))
    # print(json.loads(request.body.decode('utf-8')))
    # ff = FileFieldFormView()
    print('####')
    # aa = ff.post(request)
    # print(aa)
    # post 형식 체크
    # err_flag, post, err = get_post(request)
    # if err_flag: return JsonResponse(err)

    data['state'] = True
    data['detail'] = None
    # name = get_random_str() + '.jpg'
    # err_flag, err = upload_file(request, name)
    # if err_flag: return JsonResponse(err)

    return JsonResponse(data)

@csrf_exempt
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
    if not user.user_address:
        data['state'] = False
        data['detail'] = 'db에 주소 저장이 안되있음'
        return JsonResponse(data)

    users = Users.objects.using(DB_NAME).filter(user_address=user.user_address)
    # users = Users.objects.using(DB_NAME).filter(Q(user_address=user.user_address) & ~Q(user_id=user_id))
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
    
@csrf_exempt
def create(request): # 메모 : 가격, 전번, 지역은 판매랑 광고게시판?
    data = {}
    
    # post 형식 체크
    err_flag, post, err = get_post(request)
    if err_flag: return JsonResponse(err)

    # 키워드 유무 체크
    check_list = ['user_token', 'board_title', 'board_type', 'board_body']
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)

    # 토큰 인증
    user_token = post['user_token']
    err_flag, user_id, err = token_auth(user_token)
    if err_flag: return JsonResponse(err)

    user = Users.objects.using(DB_NAME).get(user_id=user_id)
    # request.FILES
    values = [post[key] for key in check_list[1:]]
    dic = dict(zip(check_list[1:],values))
    dic['board_delete_flag'] = 'N'
    dic['board_like_num'] = 0
    dic['board_view_num'] = 0
    board = user.boards_set.create(**dic)

    data['state'] = True
    data['detail'] = '게시판 생성완료'
    data['board_idx'] = board.board_idx
    return JsonResponse(data)

def detail(request, board_idx):
    pass

    


    
        


