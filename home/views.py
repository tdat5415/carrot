from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from function.crypto import encrypt, decrypt, hash, get_random_str, KEY
from function.location import get_address, get_coordinates
from function.check import get_post, keyword_check, token_auth
from .models import *
import json

DB_NAME = 'carrot_db'

@csrf_exempt
def index(request):
    data = {}
    data['state'] = True
    data['detail'] = None
    return JsonResponse(data)

@csrf_exempt
def login(request):
    data = {}

    # post 형식 체크
    err_flag, post, err = get_post(request)
    if err_flag: return JsonResponse(err)

    # 키워드 유무 체크
    check_list = ['user_id', 'user_pw', ]
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)

    user_id = post['user_id']
    user_pw = hash(post['user_pw'])
    user = Users.objects.using(DB_NAME).filter(Q(user_id=user_id) & Q(user_pw=user_pw))

    if not user:
        data['state'] = False
        data['detail'] = '로그인정보 불일치'
        return JsonResponse(data)

    user[0].user_last_login_datetime = timezone.now()
    user[0].save()
    
    temp = json.dumps({'user_id':user[0].user_id}) # KEY + 
    user_token = encrypt(temp)
    data['state'] = True
    data['detail'] = 'login 성공'
    data['user_token'] = user_token
    data['user_idx'] = user[0].user_idx
    data['user_nickname'] = user[0].user_nickname
    data['user_profile'] = user[0].user_profile
    data['user_address'] = user[0].user_address
    return JsonResponse(data)
        

@csrf_exempt
def auto_login(request):
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

    user = Users.objects.using(DB_NAME).filter(Q(user_id=user_id))
    data['state'] = True
    data['detail'] = 'auto_login 성공'
    data['user_idx'] = user[0].user_idx
    data['user_id'] = user[0].user_id
    data['user_nickname'] = user[0].user_nickname
    data['user_profile'] = user[0].user_profile
    data['user_address'] = user[0].user_address
    return JsonResponse(data)
        


@csrf_exempt
def join_check(request):
    data = {}

    # post 형식 체크
    err_flag, post, err = get_post(request)
    if err_flag: return JsonResponse(err)

    for check in ['user_id', 'user_phone', 'user_nickname']:
        if check == post['field']:
            dic = {check:post['value']}
            user = Users.objects.using(DB_NAME).filter(**dic)
            # 존재하면 False, exist ~~
            data['state'] = not bool(user)
            data['detail'] = '{} {}'.format('exist' if bool(user) else 'unique', check)
            return JsonResponse(data)
    else:
        data['state'] = False
        data['detail'] = 'user_id, user_phone, user_nickname 중 하나를 안보냄'
        return JsonResponse(data)

@csrf_exempt
def join(request):
    data = {}

    # post 형식 체크
    err_flag, post, err = get_post(request)
    if err_flag: return JsonResponse(err)

    # 키워드 유무 체크
    check_list = ['user_id', 'user_pw', 'user_nickname', 'user_phone', 'user_birth', ] # 2021-01-01
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)
    
    values = [post[key] for key in check_list]
    dic = dict(zip(check_list, values))
    new_user = Users(**dic)
    new_user.user_pw = hash(new_user.user_pw)
    new_user.user_delete_flag = 'N'
    new_user.save(using=DB_NAME)

    data['state'] = True
    data['detail'] = '회원가입 성공'
    return JsonResponse(data)

@csrf_exempt
def location(request):
    data = {}

    # post 형식 체크
    err_flag, post, err = get_post(request)
    if err_flag: return JsonResponse(err)

    # 키워드 유무 체크
    # check_list = ['user_latitude', 'user_longitude']
    check_list = ['user_latitude', 'user_longitude', 'user_token']
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)

    # 토큰 인증
    user_token = post['user_token']
    err_flag, user_id, err = token_auth(user_token)
    if err_flag: return JsonResponse(err)

    user = Users.objects.using(DB_NAME).get(user_id=user_id)
    # print(post)
    err_flag, user_address, err = get_address((post['user_latitude'], post['user_longitude']))
    if err_flag: return JsonResponse(err)

    user.user_address = user_address.split(',')[0]
    user.save()

    data['state'] = True
    data['detail'] = '좌표 -> 주소 성공'
    data['user_address'] = user_address
    return JsonResponse(data)

@csrf_exempt
def token(request):
    data = {}
    post = request.POST
    print(request.headers)
    print(request.POST)

    # # 키워드 유무 체크
    check_list = ['user_token', ]
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)

    # # 토큰 인증
    user_token = post['user_token']
    err_flag, user_id, err = token_auth(user_token)
    if err_flag: return JsonResponse(err)

    data['user_id'] = user_id
    print('보냄')
    
    return JsonResponse(data)