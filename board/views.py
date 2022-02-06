from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from function.check import keyword_check, token_auth
from function.upload import handle_files
from home.models import *

DB_NAME = 'carrot_db'
NUM_PER_PAGE = 5

@csrf_exempt
def index(request):
    data = {}
    print('###')
    # print(request.headers)
    print(request.POST)
    # print(request.FILES)
    print('####')
    # board = Boards(board_title="asd", board_body="🥺")
    # board.save(using=DB_NAME)
    # board.refresh_from_db()

    data['state'] = True
    # data['detail'] = board.board_title
    return JsonResponse(data)

@csrf_exempt
def board(request):
    data = {}
    post = request.POST

    # 키워드 유무 체크
    check_list = ['user_token', 'board_type', 'board_category_idx']
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)

    # 토큰 인증
    user_token = post['user_token']
    err_flag, user_id, err = token_auth(user_token)
    if err_flag: return JsonResponse(err)

    user = Users.objects.using(DB_NAME).get(user_id=user_id)

    if int(post["board_category_idx"]) or user.user_address==None: # 0이 아니면 카테고리 전체지역
        user_idxs = Users.objects.using(DB_NAME).all().values_list("pk", flat=True)
    else: # 0이면 홈버튼
        user_idxs = Users.objects.using(DB_NAME).filter(user_address=user.user_address).values_list("pk", flat=True)
 
    if "page" in post and post["page"] != None:
        data["page"] = int(post["page"]) + 1
    else: data["page"] = 0
    p1, p2 = data["page"]*NUM_PER_PAGE, (data["page"]+1)*NUM_PER_PAGE
        
    # 게시판들 가져오기
    condition = Q(board_type=post['board_type']) & Q(board_writer_idx__in=list(user_idxs))
    cate = BoardCategory.objects.using(DB_NAME).filter(category_idx=int(post["board_category_idx"]))
    if cate: condition &= Q(board_category_idx=cate[0])
    boards = Boards.objects.using(DB_NAME).filter(condition).order_by("-board_write_datetime")[p1:p2]

    if not boards:
        data['state'] = False
        data['detail'] = '주변 사용자들의 게시글이 없습니다.'
        return JsonResponse(data)

    dic = {}
    dic['idx'] = [b.board_idx for b in boards]
    dic['title'] = [b.board_title for b in boards]
    dic['write_datetime'] = [b.board_write_datetime for b in boards]
    dic['like_num'] = [b.board_like_num for b in boards]
    dic['writer'] = [b.board_writer_idx.user_id for b in boards]
    dic['thumbnail'] = [b.boardimages_set.filter(image_thumbnail=True) for b in boards]
    dic['thumbnail'] = [img[0].image_path_name if img else None for img in dic['thumbnail']]
    dic['price'] = [b.board_price for b in boards]

    data['state'] = True
    data['detail'] = '주변사용자 게시글({}) 가져오기 성공'.format(post['board_type'])
    data["boards"] = [dict(zip(dic.keys(), row)) for row in zip(*dic.values())]
    return JsonResponse(data)

@csrf_exempt
def detail(request, board_idx):
    data = {}
    post = request.POST

    # 키워드 유무 체크
    check_list = ['user_token', ]
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)

    # 토큰 인증
    user_token = post['user_token']
    err_flag, user_id, err = token_auth(user_token)
    if err_flag: return JsonResponse(err)

    board = get_object_or_404(Boards.objects.using(DB_NAME), board_idx=board_idx)

    data['state'] = True
    data['detail'] = "해당 게시글 가져오기 성공"
    data['user_id'] = user_id

    # 게시글 정보
    keys = ["board_title", "board_body", "board_type", "board_write_datetime", "board_price", ]
    for key in keys:
        data[key] = getattr(board, key)
    data['board_category'] = board.board_category_idx.category_name if board.board_category_idx else None
    data['image_paths'] = list(board.boardimages_set.values_list('image_path_name', flat=True))
    
    # 유저가 추천을 눌렀는지
    user = get_object_or_404(Users.objects.using(DB_NAME), user_id=user_id)
    like = board.boardlikes_set.filter(like_user_idx=user)
    data["like"] = bool(like)
    data["num_likes"] = len(board.boardlikes_set.all())

    # 작성자 정보
    data['writer_id'] = None
    if board.board_writer_idx:
        keys = ["idx", "id", "nickname", "phone", "address", "profile"]
        for key in keys:
            data["writer_" + key] = getattr(board.board_writer_idx, "user_" + key)
    return JsonResponse(data)

@csrf_exempt
def edit(request, board_idx):
    data = {}
    keys = []
    post = request.POST

    # 키워드 유무 체크
    check_list = ['user_token', 'board_title', 'board_type', 'board_body']
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)
    keys += check_list[1:]

    # 토큰 인증
    user_token = post['user_token']
    err_flag, user_id, err = token_auth(user_token)
    if err_flag: return JsonResponse(err)

    # type이 S일때 키워드 유무 체크
    if post['board_type'] == 'S':
        check_list = ['board_price', ]
        err_flag, err = keyword_check(check_list, post)
        if err_flag: return JsonResponse(err)
        keys += check_list

    board = get_object_or_404(Boards.objects.using(DB_NAME), board_idx=board_idx)

    if board.board_writer_idx.user_id != user_id:
        data['state'] = False
        data['detail'] = "작성자만 수정가능"
        return JsonResponse(data)

    for key in keys: setattr(board, key, post[key])
    board.save()

    if request.FILES:
        # 키워드 유무 체크
        check_list = ['files', ]
        err_flag, err = keyword_check(check_list, request.FILES)
        if err_flag: return JsonResponse(err)
        handle_files(request, board)
        
    data['state'] = True
    data['detail'] = '게시판 생성완료'
    data['board_idx'] = board.board_idx
    return JsonResponse(data)

@csrf_exempt
def delete(request, board_idx):
    data = {}
    post = request.POST

    # 키워드 유무 체크
    check_list = ['user_token', ]
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)
    
    # 토큰 인증
    user_token = post['user_token']
    err_flag, user_id, err = token_auth(user_token)
    if err_flag: return JsonResponse(err)

    board = get_object_or_404(Boards.objects.using(DB_NAME), board_idx=board_idx)

    if board.board_writer_idx.user_id != user_id:
        data['state'] = False
        data['detail'] = "작성자만 삭제가능"
        return JsonResponse(data)

    board.delete()
    data['state'] = True
    data['detail'] = "게시글 삭제 완료"
    return JsonResponse(data)

@csrf_exempt
def create(request): # 메모 : 가격, 전번, 지역은 판매랑 광고게시판?
    data = {}
    keys = []
    post = request.POST

    # 키워드 유무 체크
    check_list = ['user_token', 'board_title', 'board_type', 'board_body', "board_category_idx"]
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)
    keys += check_list[1:]

    # 토큰 인증
    user_token = post['user_token']
    err_flag, user_id, err = token_auth(user_token)
    if err_flag: return JsonResponse(err)

    # type이 S일때 키워드 유무 체크
    if post['board_type'] == 'S':
        check_list = ['board_price', ]
        err_flag, err = keyword_check(check_list, post)
        if err_flag: return JsonResponse(err)
        keys += check_list

    # 게시판 생성
    values = [post[key] for key in keys]
    dic = dict(zip(keys,values))
    if post['board_type'] == 'S':
        dic['board_price'] = post['board_price']
    cate = BoardCategory.objects.using(DB_NAME).filter(category_idx=int(post['board_category_idx']))
    dic['board_category_idx'] = cate[0] if cate else None
    user = get_object_or_404(Users.objects.using(DB_NAME), user_id=user_id)
    board = user.boards_set.create(**dic)

    if request.FILES:
        # 키워드 유무 체크
        check_list = ['files', ]
        err_flag, err = keyword_check(check_list, request.FILES)
        if err_flag: return JsonResponse(err)
        handle_files(request, board)

    data['state'] = True
    data['detail'] = '게시판 생성완료'
    data['board_idx'] = board.board_idx
    return JsonResponse(data)

@csrf_exempt
def like(request, board_idx):
    data = {}
    post = request.POST

    # 키워드 유무 체크
    check_list = ['user_token', "like_sign"]
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)

    # 토큰 인증
    user_token = post['user_token']
    err_flag, user_id, err = token_auth(user_token)
    if err_flag: return JsonResponse(err)
    
    board = get_object_or_404(Boards.objects.using(DB_NAME), board_idx=board_idx)
    user = get_object_or_404(Users.objects.using(DB_NAME), user_id=user_id)
    
    if int(post["like_sign"]): # 추천하기
        user.boardlikes_set.get_or_create(like_board_idx=board)
        board.board_like_num = len(board.boardlikes_set.all())
        board.save()
    else: # 추천취소
        user.boardlikes_set.filter(like_board_idx=board).delete()
        board.board_like_num = len(board.boardlikes_set.all())
        board.save()
    board.refresh_from_db()

    data["state"] = True
    data["detail"] = "추천{} 성공".format("하기" if int(post["like_sign"]) else "취소")
    data["num_likes"] = board.board_like_num
    return JsonResponse(data)

