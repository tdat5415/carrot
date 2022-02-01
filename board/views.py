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
import os

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
    print(request.FILES)
    print(request.FILES['files'])
    # print(request.FILES.getlist('files'))
    # file = request.FILES.getlist('files')[0]
    # file_name = handle_uploaded_file(file)
    # print(file_name)
    # print(type(request.FILES))
    # print(type(request.FILES['files']))
    # print(type(request.FILES.getlist('files')[0]))
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

    data['state'] = True
    data['detail'] = '주변사용자 게시글({}) 가져오기 성공'.format(post['board_type'])
    data['idxs'] = [b.board_idx for b in users_boards]
    data['titles'] = [b.board_title for b in users_boards]
    data['bodies'] = [b.board_body for b in users_boards]
    data['write_datetimes'] = [b.board_write_datetime for b in users_boards]
    data['like_nums'] = [b.board_like_num for b in users_boards]
    data['writers'] = [b.board_writer_idx.user_id for b in users_boards]
    data['thumbnails'] = [b.boardimages_set.filter(image_thumbnail=True) for b in users_boards]
    data['thumbnails'] = [img[0].image_path_name if img else None for img in data['thumbnails']]
    if post['board_type'] == 'S':
        data['prices'] = [b.board_price for b in users_boards]
    return JsonResponse(data)

@csrf_exempt
def detail(request, board_idx):
    data = {}

    # post 형식 체크
    err_flag, post, err = get_post(request)
    if err_flag: return JsonResponse(err)

    # 키워드 유무 체크
    check_list = ['user_token', ]
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)
    
    # 토큰 인증
    user_token = post['user_token']
    err_flag, user_id, err = token_auth(user_token)
    if err_flag: return JsonResponse(err)

    board = Boards.objects.using(DB_NAME).filter(board_idx=board_idx)
    if not board:
        data['state'] = False
        data['detail'] = "해당 게시글이 사라짐"
        return JsonResponse(data)
        
    b = board[0]
    
    data['state'] = True
    data['detail'] = "해당 게시글 가져오기 성공"
    data['user_id'] = user_id
    data['board_title'] = b.board_title
    data['board_body'] = b.board_body
    data['board_type'] = b.board_type
    data['board_write_datetime'] = b.board_write_datetime
    data['board_price'] = b.board_price
    data['image_paths'] = list(b.boardimages_set.values_list('image_path_name', flat=True))

    data['writer_id'] = None
    if b.board_writer_idx:
        data['writer_id'] = b.board_writer_idx.user_id
        data['writer_nickname'] = b.board_writer_idx.user_nickname
        data['writer_phone'] = b.board_writer_idx.user_phone
        data['writer_address'] = b.board_writer_idx.user_address
        
    return JsonResponse(data)

@csrf_exempt
def edit(request, board_idx):
    data = {}
    keys = []

    # post 형식 체크
    # err_flag, post, err = get_post(request)
    # if err_flag: return JsonResponse(err)
    post = request.POST

    # 키워드 유무 체크
    check_list = ['user_token', 'board_title', 'board_type', 'board_body']
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)
    keys += check_list[1:]

    # type이 S일때 키워드 유무 체크
    if post['board_type'] == 'S':
        check_list = ['board_price', ]
        err_flag, err = keyword_check(check_list, post)
        if err_flag: return JsonResponse(err)
        keys += check_list
        if not request.FILES:
            data['state'] = False
            data['detail'] = "type이 S일 경우 이미지파일 필수"
            return JsonResponse(data)

    # 토큰 인증
    user_token = post['user_token']
    err_flag, user_id, err = token_auth(user_token)
    if err_flag: return JsonResponse(err)

    board = Boards.objects.using(DB_NAME).filter(board_idx=board_idx)
    if not board:
        data['state'] = False
        data['detail'] = "해당 게시글이 사라짐"
        return JsonResponse(data)

    b = board[0]
    if b.board_writer_idx.user_id != user_id:
        data['state'] = False
        data['detail'] = "작성자만 수정가능"
        return JsonResponse(data)

    # 기존 이미지 삭제
    for path in b.boardimages_set.values_list("image_path_name", flat=True):
        if os.path.isfile("." + path):
            os.remove("." + path)
    b.boardimages_set.all().delete()
    for key in keys:
        setattr(b, key, post[key])
    b.save()

    if request.FILES:
        # 키워드 유무 체크
        check_list = ['files', ]
        err_flag, err = keyword_check(check_list, request.FILES)
        if err_flag: return JsonResponse(err)

        files = request.FILES.getlist('files')
        thumb_flag = True
        for f in files:
            file_name = handle_uploaded_file(f)
            dic = {}
            dic['image_path_name'] = '/static/{}'.format(file_name)
            dic['image_delete_flag'] = 'N'
            dic['image_thumbnail'] = thumb_flag
            thumb_flag = False
            b.boardimages_set.create(**dic)
        
    data['state'] = True
    data['detail'] = '게시판 생성완료'
    data['board_idx'] = b.board_idx
    return JsonResponse(data)






@csrf_exempt
def delete(request, board_idx):
    data = {}

    # post 형식 체크
    err_flag, post, err = get_post(request)
    if err_flag: return JsonResponse(err)

    # 키워드 유무 체크
    check_list = ['user_token', ]
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)
    
    # 토큰 인증
    user_token = post['user_token']
    err_flag, user_id, err = token_auth(user_token)
    if err_flag: return JsonResponse(err)

    board = Boards.objects.using(DB_NAME).filter(board_idx=board_idx)
    if not board:
        data['state'] = False
        data['detail'] = "해당 게시글이 사라짐"
        return JsonResponse(data)

    b = board[0]
    if b.board_writer_idx.user_id != user_id:
        data['state'] = False
        data['detail'] = "작성자만 삭제가능"
        return JsonResponse(data)
    
    b.delete()
    data['state'] = True
    data['detail'] = "게시글 삭제 완료"
    return JsonResponse(data)

@csrf_exempt
def create(request): # 메모 : 가격, 전번, 지역은 판매랑 광고게시판?
    data = {}
    keys = []
    # post 형식 체크
    # err_flag, post, err = get_post(request)
    # if err_flag: return JsonResponse(err)
    post = request.POST

    # 키워드 유무 체크
    check_list = ['user_token', 'board_title', 'board_type', 'board_body']
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)
    keys += check_list[1:]

    # type이 S일때 키워드 유무 체크
    if post['board_type'] == 'S':
        check_list = ['board_price', ]
        err_flag, err = keyword_check(check_list, post)
        if err_flag: return JsonResponse(err)
        keys += check_list
        if not request.FILES:
            data['state'] = False
            data['detail'] = "type이 S일 경우 이미지파일 필수"
            return JsonResponse(data)

    # 토큰 인증
    user_token = post['user_token']
    err_flag, user_id, err = token_auth(user_token)
    if err_flag: return JsonResponse(err)

    user = Users.objects.using(DB_NAME).get(user_id=user_id)
    # request.FILES
    values = [post[key] for key in keys]
    dic = dict(zip(keys,values))
    dic['board_delete_flag'] = 'N'
    dic['board_like_num'] = 0
    dic['board_view_num'] = 0
    if post['board_type'] == 'S':
        dic['board_price'] = post['board_price']

    board = user.boards_set.create(**dic)

    if request.FILES:
        # 키워드 유무 체크
        check_list = ['files', ]
        err_flag, err = keyword_check(check_list, request.FILES)
        if err_flag: return JsonResponse(err)

        files = request.FILES.getlist('files')
        thumb_flag = True
        for f in files:
            file_name = handle_uploaded_file(f)
            dic = {}
            dic['image_path_name'] = '/static/{}'.format(file_name)
            dic['image_delete_flag'] = 'N'
            dic['image_thumbnail'] = thumb_flag
            thumb_flag = False
            board.boardimages_set.create(**dic)
        
    data['state'] = True
    data['detail'] = '게시판 생성완료'
    data['board_idx'] = board.board_idx
    return JsonResponse(data)


    


    
        


