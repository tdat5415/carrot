from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from home.crypto import encrypt, decrypt, hash, KEY
from .models import *
import json

DB_NAME = 'carrot_db'

def login_check(token):
    dic = {}
    data = decrypt(token) # "mysecret{'user_id':text,}"
    if KEY in data:
        dic = json.loads(data[len(KEY):])
        user_id = dic['user_id']
        return True, user_id
    else:
        return False, None

def index(request):
    data = {}
    data['state'] = 'OK'
    return HttpResponse(json.dumps(data))

@csrf_exempt
def login(request):
    data = {}
    post = json.loads(request.body.decode('utf-8')) # dic
    
    check_list = ['user_id', 'user_pw', ]
    for check in check_list:
        if not check in post:
            data['state'] = 'incorrect access'
            return HttpResponse(json.dumps(data))

    user_id = post['user_id']
    user_pw = hash(post['user_pw'])

    user = Users.objects.using(DB_NAME).filter(Q(user_id=user_id) & Q(user_pw=user_pw))

    if user:
        user[0].user_last_login_datetime = timezone.now()
        user[0].save()
        
        temp = KEY + json.dumps({'user_id':user[0].user_id})
        enc_str = encrypt(temp)
        data['state'] = 'success login'
        data['user_token'] = enc_str
        data['user_idx'] = user[0].user_idx
        data['user_nickname'] = user[0].user_nickname
        data['user_profile'] = user[0].user_profile
        data['user_latitude'] = user[0].user_latitude
        data['user_longitude'] = user[0].user_longitude

        return HttpResponse(json.dumps(data))
    else:
        data['state'] = 'No User'
        return HttpResponse(json.dumps(data))

@csrf_exempt
def join_check(request):
    data = {}
    post = json.loads(request.body.decode('utf-8'))
    value = post['value']
    field = post['field']

    for check in ['user_id', 'user_phone', 'user_nickname']:
        if check == field:
            dic = {check:value}
            user = Users.objects.using(DB_NAME).filter(**dic)
            if user: 
                data['state'] = 'exist {}'.format(check)
                return HttpResponse(json.dumps(data))
            else:
                data['state'] = 'unique {}'.format(check)
                return HttpResponse(json.dumps(data))
    else:
        data['state'] = 'incorrect access'
        return HttpResponse(json.dumps(data))

@csrf_exempt
def join(request):
    data = {}
    post = json.loads(request.body.decode('utf-8'))

    check_list = ['user_id', 'user_pw', 'user_nickname', 'user_phone', 'user_birth', ] # 2021-01-01
    for check in check_list:
        if not check in post:
            data['state'] = 'incorrect access'
            return HttpResponse(json.dumps(data))
    
    values = [post[key] for key in check_list]
    dic = dict(zip(check_list, values))
    new_user = Users(**dic)
    new_user.user_pw = hash(new_user.user_pw)
    new_user.user_delete_flag = 'N'
    new_user.save(using=DB_NAME)

    data['state'] = 'success join'
    return HttpResponse(json.dumps(data))
    
def location(request):
    data = {}
    post = json.loads(request.body.decode('utf-8'))

    token = post['token']
    state, user_id = login_check(token)
    if state:
        user = Users.objects.using(DB_NAME).filter(Q(user_id=user_id))
        data['user_latitude'] = user[0].user_latitude
        data['user_longitude'] = user[0].user_longitude
        return HttpResponse(json.dumps(data))





    
