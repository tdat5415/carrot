import json
from function.crypto import decrypt, KEY

# post 형식 체크
def get_post(request): # return: err_flag, post, err
    data = {}
    try:
        post = json.loads(request.body.decode('utf-8'))
        return False, post, None
    except:
        data['state'] = False
        data['detail'] = 'post 형식 에러'
        return True, None, data

# 키워드 유무 체크
def keyword_check(check_list, post): # return: err_flag, err
    data = {}
    for check in check_list:
        if not check in post:
            data['state'] = False
            data['detail'] = '키 누락 : {}'.format(check)
            return True, data
    return False, None

# 토큰 인증
def token_auth(token): # return: err_flag, user_id, err
    data = {}
    data['state'] = False
    data['detail'] = 'user_token이 NULL이거나 변조됨'
    try: dec_token = decrypt(token) # "mysecret{'user_id':text,}"
    except: return True, None, data
    
    # if not KEY in dec_token:
    #     return True, None, data

    dic = json.loads(dec_token)#[len(KEY):])
    user_id = dic['user_id']
    return False, user_id, None