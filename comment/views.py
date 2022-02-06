from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from function.check import keyword_check, token_auth
from home.models import *

DB_NAME = 'carrot_db'

@csrf_exempt
def create(request):
    data = {}
    post = request.POST

    # 키워드 유무 체크
    check_list = ['user_token', 'comment_body', "board_idx"]
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)

    # 토큰 인증
    user_token = post['user_token']
    err_flag, user_id, err = token_auth(user_token)
    if err_flag: return JsonResponse(err)

    # 댓글생성
    user = get_object_or_404(Users.objects.using(DB_NAME), user_id=user_id)
    board = get_object_or_404(Boards.objects.using(DB_NAME), board_idx=post["board_idx"])
    comment = Comment(comment_writer_idx=user, comment_board_idx=board, comment_body=post["comment_body"])
    comment.save(using=DB_NAME)
    comment.refresh_from_db()

    data["state"] = True
    data["detail"] = "댓글 생성 성공"
    # 해당댓글정보
    data["coment_idx"] = comment.comment_idx
    data["coment_writer_idx"] = comment.coment_writer_idx.user_idx
    data["coment_writer_id"] = comment.coment_writer_idx.user_id
    data["coment_write_datetime"] = comment.coment_write_datetime
    data["coment_body"] = comment.comment_body
    data["coment_like_num"] = comment.comment_like_num
    return JsonResponse(data)

@csrf_exempt
def edit(request, comment_idx):
    data = {}
    post = request.POST

    # 키워드 유무 체크
    check_list = ['user_token', 'comment_body']
    err_flag, err = keyword_check(check_list, post)
    if err_flag: return JsonResponse(err)

    # 토큰 인증
    user_token = post['user_token']
    err_flag, user_id, err = token_auth(user_token)
    if err_flag: return JsonResponse(err)

    comment = get_object_or_404(Comment.objects.using(DB_NAME), comment_idx=comment_idx)

    if comment.comment_writer_idx.user_id != user_id:
        data['state'] = False
        data['detail'] = "작성자만 수정가능"
        return JsonResponse(data)

    comment.comment_body = post["comment_body"]
    comment.save()
    comment.refresh_from_db()

    data["state"] = True
    data["detail"] = "댓글 수정 성공"
    # 해당댓글정보
    data["coment_idx"] = comment.comment_idx
    data["coment_writer_idx"] = comment.coment_writer_idx.user_idx
    data["coment_writer_id"] = comment.coment_writer_idx.user_id
    data["coment_write_datetime"] = comment.coment_write_datetime
    data["coment_body"] = comment.comment_body
    data["coment_like_num"] = comment.comment_like_num
    return JsonResponse(data)

@csrf_exempt
def delete(request, comment_idx):
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

    comment = get_object_or_404(Comment.objects.using(DB_NAME), comment_idx=comment_idx)

    if comment.comment_writer_idx.user_id != user_id:
        data['state'] = False
        data['detail'] = "작성자만 삭제가능"
        return JsonResponse(data)

    comment.delete()
    data['state'] = True
    data['detail'] = "댓글 삭제 완료"
    return JsonResponse(data)
