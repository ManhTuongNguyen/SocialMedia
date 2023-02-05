import uuid
from django.contrib.auth.models import User
import re
from django.core.paginator import Paginator
from core.process import email_service
from core.models import Profile, Post, LikePost, FollowerCount, CustomName, GetPasswordLog
from itertools import chain
import timeit
from django.urls import reverse
from django.shortcuts import render
import random
import os
from datetime import datetime, timezone


def is_valid_account(username: str, email: str, pass1: str, pass2: str) -> bool:
    is_valid_username(username)
    if not is_valid_email(email):
        raise Exception("Địa chỉ email không hợp lệ!")
    is_valid_password(pass1, pass2)
    return True


def is_valid_username(username):
    if not username.strip():
        raise Exception("Không được bỏ trống tên tài khoản!")
    if username.__len__() < 4:
        raise Exception("Độ dài tên tài khoản không hợp lệ!")
    if User.objects.filter(username=username).exists():
        raise Exception("Tên tài khoản đã được sử dụng!")
    return True


def is_valid_password(pass1, pass2):
    if not pass1.strip():
        raise Exception("Không được bỏ trống mật khẩu!")
    if pass1.__len__() < 4:
        raise Exception("Độ dài mật khẩu không hợp lệ!")
    if pass1 != pass2:
        raise Exception("Mật khẩu nhập lại không khớp!")
    return True


def is_match_password_account(username, old_pass) -> bool:
    u = User.objects.get(username=username)
    if u.check_password(old_pass):
        return True
    raise Exception("Mật khẩu cũ không đúng!")


def update_password(username, new_pass):
    u = User.objects.get(username=username)
    u.set_password(new_pass)
    u.save()


def change_password(username: str, old_pass: str, new_pass: str, re_pass: str) -> bool:
    is_match_password_account(username, old_pass)
    if not new_pass.strip():
        raise Exception("Không được bỏ trống mật khẩu mới!")
    if new_pass.__len__() < 4:
        raise Exception("Độ dài mật khẩu mới không hợp lệ!")
    if new_pass != re_pass:
        raise Exception("Mật khẩu mới nhập lại không khớp!")
    update_password(username, new_pass)
    return True


def is_valid_email(email: str) -> bool:
    if not email.strip():
        raise Exception("Không được bỏ trống địa chỉ email!")
    if User.objects.filter(email=email).exists():
        raise Exception("Địa chỉ email đã được sử dụng!")
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(regex, email):
        if email.endswith(('.com', '.co.uk', '.fr', '.ru', '.vn')):
            # https://email-verify.my-addr.com/list-of-most-popular-email-domains.php#:~:text=Top%20100%20%20%201%20%20%20gmail.com,%20%201.27%25%20%2095%20more%20rows%20
            return True
        raise Exception("Địa chỉ email không được chấp nhận tại hệ thống!")
    raise Exception("Địa chỉ email không hợp lệ!")


def generate_password() -> str:
    return str(uuid.uuid4())[24:37]


def retrieve_password(username, email) -> str:
    if not username.strip():
        raise Exception("Không được bỏ trống tên tài khoản!")
    if username.__len__() < 4:
        raise Exception("Độ dài tên tài khoản không hợp lệ!")
    try:
        user = User.objects.get(username=username)
    except:
        raise Exception("Tài khoản không tồn tại trên hệ thống! Vui lòng kiểm tra và thử lại!")
    if user.email != email:
        raise Exception("Địa chỉ email không khớp!;Vui lòng kiểm tra và thử lại!")

    last_get_pasword = GetPasswordLog.objects.filter(user=username).order_by('-created')[:1]
    if last_get_pasword.__len__() == 1:
        # User này đã yêu cầu lấy lại mật khẩu trước đó
        time_send_before = last_get_pasword[0].created
        now = datetime.now(timezone.utc)
        time_interval_second = (now - time_send_before).total_seconds()
        min_time_get_password = 300
        if time_interval_second < min_time_get_password:
            time_remaining = min_time_get_password - time_interval_second
            raise Exception(f"Tính năng sẽ khả dụng sau;{int(time_remaining)} giây! Vui lòng kiểm tra;hòm thư spam!")

    # Tạo một chuỗi ngẫu nhiên làm mật khẩu
    random_pass = generate_password()
    try:
        custom_name = CustomName.objects.get(user=username)
    except:
        custom_name = None
    # Gửi thông tin tài khoản đến địa chỉ email của user
    # Gửi thành công thông tin mới tiến hành đổi mật khẩu của user trên db
    if not email_service.send_password_to_email(username, custom_name, random_pass, email):
        raise Exception("Một lỗi không xác định đã xảy ra! Hãy quay lại và sử dụng chức năng này sau!")
    # Đổi mật khẩu cho user bằng một mật khẩu ngẫu nhiên vừa tạo
    user.set_password(random_pass)
    user.save()
    get_password_log = GetPasswordLog.objects.create(user=username)
    get_password_log.save()
    return random_pass


def is_valid_image(image) -> bool:
    if image is None:
        # User không upload ảnh.
        return True
    is_valid = image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))
    return is_valid


def get_context_index(username: str, page_num) -> dict:
    user_obj = User.objects.get(username=username)
    user_profile = Profile.objects.get(user=user_obj)

    user_following_list = []

    list_post_id = []

    # Danh sách người đang được user theo dõi
    user_following = FollowerCount.objects.filter(follower=username)
    for x in user_following:
        user_following_list.append(x.user)

    # Danh sách bài viết của người đang được user theo dõi
    for username in user_following_list:
        feed_lists = Post.objects.filter(user=username)
        for post in feed_lists:
            list_post_id.append(post.id)

    list_feed = Post.objects.filter(id__in=list_post_id).order_by('-created')
    # Phân trang
    quantity_post_for_one_page = 8
    paginator = Paginator(list_feed, quantity_post_for_one_page)
    page_obj = paginator.get_page(page_num)

    # Tìm danh sách người chưa follow ngoại trừ bản thân
    all_user = User.objects.all()
    user_following_all = []
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    temp_suggestion_list = [x for x in list(all_user) if x not in list(user_following_all)]
    temp_suggestion_list.remove(user_obj)
    random.shuffle(temp_suggestion_list)
    user_id_suggest = []
    user_profile_suggest = []
    for user in temp_suggestion_list:
        user_id_suggest.append(user.id)
    for _id in user_id_suggest:
        temp_profile_user = Profile.objects.filter(id_user=_id)
        user_profile_suggest.append(temp_profile_user)

    suggestions_user_profile_list = list(chain(*user_profile_suggest))

    return {
        'user_profile': user_profile,
        'page_obj': page_obj,
        'suggestions_user_profile_list': suggestions_user_profile_list
    }


def return_render_index(request):
    username = request.user.username
    content_obj = get_context_index(username=username, page_num=None)
    popup = {
        'title_msg': "Lỗi!",
        'message': "Tài khoản không tồn;tại trên hệ thống!",
        'type': 'ERROR',
        'time': 2000,
        'redirect': reverse('core:index')
    }
    cont = {
        'title': "Trang chủ",
        'popup': popup,
        'user_profile': content_obj['user_profile'],
        'posts': content_obj['page_obj'],
        'username': username,
        'suggestions_user_profile_list': (content_obj['suggestions_user_profile_list'])[:4]
    }
    return render(request, 'index.html', cont)


def return_render_sign_in_fail(request, username: str, password: str):
    if not username and not password:
        message = "Không được bỏ trống tên;tài khoản và mật khẩu!"
    elif not username or not password:
        if not username:
            message = "Không được bỏ;trống tên tài khoản"
        else:
            message = "Không được bỏ trống mật khẩu!"
    else:
        message = "Thông tin tài khoản; không chính xác!"

    popup = {
        'title_msg': "Lỗi",
        'message': message,
        'type': 'ERROR',
        'time': 3000,
        'redirect': ''
    }
    cont = {
        'title': 'Đăng nhập',
        'popup': popup
    }
    return render(request, 'signin.html', cont)


def get_context_profile(username: str, pk: str) -> dict:
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk).order_by('-created')
    user_post_length = len(user_posts)

    # Kiểm tra xem user hiện tại đã theo dõi user đang xem profile hay chưa
    if FollowerCount.objects.filter(user=pk, follower=username).first():
        button_text = "Hủy theo dõi"
    else:
        button_text = "Theo dõi"
    user_follower = len(FollowerCount.objects.filter(user=pk))
    user_following = len(FollowerCount.objects.filter(follower=pk))

    title = f'Trang cá nhân - {user_profile.user.username}'
    return {
        'title': title,
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_follower,
        'user_following': user_following,
        'username': username
    }


def get_context_search(search, username):
    start = timeit.default_timer()
    user_object = User.objects.get(username=username)
    user_profile = Profile.objects.get(user=user_object)
    user_object_search_username = User.objects.filter(username__icontains=search)
    user_object_search_email = User.objects.filter(email__icontains=search)

    # Tìm kiếm bằng tên
    username_search_custom_name = []
    all_custom_name = CustomName.objects.all()
    username_search = remove_sign_for_vn(search).lower()
    for custom_name in all_custom_name:
        username_object = remove_sign_for_vn(custom_name.fullname).lower()
        if username_object.__contains__(username_search):
            username_search_custom_name.append(custom_name.user)
    user_object_search_custom_name = []
    for _username in username_search_custom_name:
        temp_user = User.objects.get(username=_username)
        user_object_search_custom_name.append(temp_user)

    user_id = []
    username_profile_list = []
    [user_id.append(user.id) for user in user_object_search_username if user not in user_id]
    [user_id.append(user.id) for user in user_object_search_email if user not in user_id]
    [user_id.append(user.id) for user in user_object_search_custom_name if user not in user_id]

    for _id in set(user_id):
        profile_lists = Profile.objects.filter(id_user=_id)
        username_profile_list.append(profile_lists)
    username_profile_list = list(chain(*username_profile_list))
    time_process = timeit.default_timer() - start

    return {
        'title': f'Tìm kiếm - {search}',
        'user_profile': user_profile,
        'username_profile_list': username_profile_list,
        'username': username,
        'search_name': search,
        'result_count': len(username_profile_list),
        'time': round(time_process, 4)
    }


def remove_old_image(image_path):
    if str(image_path).startswith('/'):
        image_path = image_path[1:]
    if os.path.exists(image_path):
        os.remove(image_path)


def is_valid_custom_name(custom_name):
    if str(custom_name).strip().__len__() < 5:
        return False
    special_characters = """`~!@#$%^&*()_-+={}[]:;'|*,./\<>?"""
    if any(c in special_characters for c in custom_name):
        return False
    return True


def remove_sign_for_vn(raw_str: str) -> str:
    vietnamese_signs = ["aAeEoOuUiIdDyY",
                        "áàạảãâấầậẩẫăắằặẳẵ",
                        "ÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴ",
                        "éèẹẻẽêếềệểễ",
                        "ÉÈẸẺẼÊẾỀỆỂỄ",
                        "óòọỏõôốồộổỗơớờợởỡ",
                        "ÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠ",
                        "úùụủũưứừựửữ",
                        "ÚÙỤỦŨƯỨỪỰỬỮ",
                        "íìịỉĩ",
                        "ÍÌỊỈĨ",
                        "đ",
                        "Đ",
                        "ýỳỵỷỹ",
                        "ÝỲỴỶỸ"]
    for i in range(1, len(vietnamese_signs)):
        for j in range(0, len(vietnamese_signs[i])):
            raw_str = raw_str.replace(
                vietnamese_signs[i][j], vietnamese_signs[0][i - 1])
    return raw_str


def is_valid_caption(caption):
    if len(str(caption).strip()) < 5:
        raise Exception("Bài viết có độ dài không phù hợp!")
