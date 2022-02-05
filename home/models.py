# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Boards(models.Model):
    board_idx = models.BigAutoField(primary_key=True)
    board_title = models.TextField()
    board_body = models.TextField()
    board_type = models.CharField(max_length=1)
    board_writer_idx = models.ForeignKey('Users', models.DO_NOTHING, db_column='board_writer_idx', blank=True, null=True)
    board_write_datetime = models.DateTimeField()
    board_delete_flag = models.CharField(max_length=1)
    board_delete_datetime = models.DateTimeField(blank=True, null=True)
    board_like_num = models.PositiveIntegerField()
    board_view_num = models.PositiveIntegerField()
    board_price = models.PositiveIntegerField(blank=True, null=True)
    board_category_idx = models.ForeignKey('BoardCategory', models.DO_NOTHING, db_column='board_category_idx', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'BOARDS'


class BoardCategory(models.Model):
    category_idx = models.BigAutoField(primary_key=True)
    category_name = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'BOARD_CATEGORY'


class BoardImages(models.Model):
    image_idx = models.BigAutoField(primary_key=True)
    image_path_name = models.CharField(unique=True, max_length=1500, db_collation='euckr_korean_ci')
    image_upload_datetime = models.DateTimeField()
    image_delete_flag = models.CharField(max_length=1)
    image_delete_datetime = models.DateTimeField(blank=True, null=True)
    image_board_idx = models.ForeignKey(Boards, models.DO_NOTHING, db_column='image_board_idx', blank=True, null=True)
    image_thumbnail = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'BOARD_IMAGES'


class BoardLikes(models.Model):
    like_idx = models.BigAutoField(primary_key=True)
    like_user_idx = models.ForeignKey('Users', models.DO_NOTHING, db_column='like_user_idx')
    like_board_idx = models.ForeignKey(Boards, models.DO_NOTHING, db_column='like_board_idx')
    like_datetime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'BOARD_LIKES'
        unique_together = (('like_user_idx', 'like_board_idx'),)


class Chat(models.Model):
    chat_idx = models.BigAutoField(primary_key=True)
    chat_write_datetime = models.DateTimeField()
    chat_body = models.TextField()
    chat_user_a_idx = models.ForeignKey('Users', models.DO_NOTHING, db_column='chat_user_a_idx', blank=True, null=True, related_name='chat_a_set')
    chat_user_b_idx = models.ForeignKey('Users', models.DO_NOTHING, db_column='chat_user_b_idx', blank=True, null=True, related_name='chat_b_set')
    chat_delete_flag = models.CharField(max_length=1)
    chat_delete_datetime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'CHAT'


class Comment(models.Model):
    comment_idx = models.BigAutoField(primary_key=True)
    comment_writer_idx = models.ForeignKey('Users', models.DO_NOTHING, db_column='comment_writer_idx', blank=True, null=True)
    comment_board_idx = models.ForeignKey(Boards, models.DO_NOTHING, db_column='comment_board_idx')
    comment_write_datetime = models.DateTimeField()
    comment_body = models.TextField()
    comment_like_num = models.PositiveIntegerField()
    comment_reply_idx = models.ForeignKey('self', models.DO_NOTHING, db_column='comment_reply_idx', blank=True, null=True)
    comment_delete_flag = models.CharField(max_length=1)
    comment_delete_datetime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'COMMENT'


class Notices(models.Model):
    notice_idx = models.BigAutoField(primary_key=True)
    notice_title = models.TextField()
    notice_body = models.TextField()
    notice_send_datetime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'NOTICES'


class Users(models.Model):
    user_idx = models.BigAutoField(primary_key=True)
    user_id = models.CharField(unique=True, max_length=50)
    user_pw = models.CharField(max_length=500)
    user_nickname = models.CharField(unique=True, max_length=500)
    user_phone = models.CharField(unique=True, max_length=11)
    user_birth = models.DateField()
    user_join_datetime = models.DateTimeField()
    user_last_login_datetime = models.DateTimeField(blank=True, null=True)
    user_delete_flag = models.CharField(max_length=1)
    user_delete_datetime = models.DateTimeField(blank=True, null=True)
    user_profile = models.TextField(blank=True, null=True)
    user_address = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'USERS'
