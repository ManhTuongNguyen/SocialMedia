from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .process import process
from .models import Profile, Post, LikePost, FollowerCount, Comment, CustomName
from django.views import View
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


# Create your views here.
@login_required(login_url='core:sign_in')
def index(request):
    title = 'Trang chủ'
    page_number = request.GET.get('page')
    content_obj = process.get_context_index(request.user.username, page_number)
    feed = content_obj['page_obj']
    if not feed:
        #  User chưa follow người nào hoặc những người đang follow chưa có bài viết nào
        popup = {
            'title_msg': "Mẹo!",
            'message': "Hãy theo dõi người khác để có thể cập nhật thông tin mới nhất từ họ nhé!",
            'type': 'INFO',
            'time': 3000,
            'redirect': ''
        }
    else:
        popup = {}
    cont = {
        'title': title,
        'popup': popup,
        'user_profile': content_obj['user_profile'],
        'posts': feed,
        'username': request.user.username,
        'suggestions_user_profile_list': (content_obj['suggestions_user_profile_list'])[:4]
    }
    return render(request, 'index.html', cont)


def sign_up(request):
    title = 'Đăng ký'
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        try:
            process.is_valid_account(username, email, password, password2)
        except Exception as ex:
            popup = {
                'title_msg': "Lưu ý.",
                'message': ex,
                'type': 'INFO',
                'time': 3000,
                'redirect': ''
            }
            cont = {
                'title': title,
                'popup': popup
            }
            return render(request, 'signup.html', cont)
        # Tạo tài khoản và lưu lên database
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        # Tạo model profile cho tài khoản vừa tạo và lưu lên db
        user_model = User.objects.get(username=username)
        new_profile = Profile.objects.create(id_user=user_model.id, user=user_model)
        new_profile.save()
        # Xác thực và đăng nhập cho tài khoản vừa tạo
        user_login = auth.authenticate(username=username, password=password)
        auth.login(request, user_login)
        popup = {
            'title_msg': "Thành công",
            'message': "Bạn đã đăng ký;tài khoản thành công!",
            'type': 'OK',
            'time': 1600,
            'redirect': reverse('core:setting-general')
        }
        cont = {
            'title': title,
            'popup': popup
        }
        return render(request, 'signup.html', cont)
    else:
        cont = {
            'title': title
        }
        return render(request, 'signup.html', cont)


def sign_in(request):
    title = 'Đăng nhập'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = auth.authenticate(request, username=User.objects.get(email=username).username,
                                     password=password)
        except:
            user = auth.authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('core:index')
        else:
            return process.return_render_sign_in_fail(request, username, password)
    else:
        cont = {
            'title': title
        }
        return render(request, 'signin.html', cont)


@login_required(login_url='core:sign_in')
def log_out(request):
    auth.logout(request)
    return redirect('core:sign_in')


@login_required(login_url='core:sign_in')
def setting_general(request):
    title = 'Thiết lập thông tin cá nhân'
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        location = request.POST['location']
        bio = request.POST['bio']
        image = request.FILES.get('image')
        cover_img = request.FILES.get('cover_image')
        if not (process.is_valid_image(image)) or not (process.is_valid_image(cover_img)):
            # Nếu 1 trong 2 file không phải hình ảnh
            content_obj = process.get_context_index(request.user.username, None)
            popup = {
                'title_msg': "Lỗi",
                'message': "Chỉ được phép upload hình ảnh!",
                'type': 'ERROR',
                'time': 3000,
                'redirect': reverse('core:index')
            }
            cont = {
                'title': title,
                'popup': popup,
                'user_profile': content_obj['user_profile'],
                'posts': content_obj['page_obj'],
                'username': request.user.username,
                'suggestions_user_profile_list': (content_obj['suggestions_user_profile_list'])[:4]
            }
            return render(request, 'index.html', cont)
        if image is None:
            image = user_profile.profileimg
        else:
            try:
                if not user_profile.profileimg.name.split('/')[1:][0] == Profile._meta.get_field('profileimg').get_default():
                    # Ảnh cũ không phải là ảnh mặc định
                    # => Xóa ảnh cũ và cập nhật ảnh mới
                    process.remove_old_image(user_profile.profileimg.url)
            except:
                pass
        if cover_img is None:
            cover_img = user_profile.cover_img
        else:
            if not user_profile.cover_img.name.split('/')[1:][0] == Profile._meta.get_field('cover_img').get_default():
                # Ảnh cũ không phải là ảnh mặc định
                # => Xóa ảnh cũ và cập nhật ảnh mới
                process.remove_old_image(user_profile.cover_img.url)

        user_profile.profileimg = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.cover_img = cover_img
        user_profile.save()

        # Lưu tên người dùng
        custom_name_str = request.POST['custom_name']
        is_updated_custom_name = False
        if process.is_valid_custom_name(custom_name_str) and not str(custom_name_str).__contains__('\\'):
            try:
                username = request.user.username
                old_custom_name = CustomName.objects.get(user=username)
                old_custom_name.fullname = custom_name_str
                old_custom_name.save()
            except:
                # Người dùng chưa có tên
                # => Tạo mới đối tượng lưu tên người dùng
                new_custom_name = CustomName.objects.create(user=username, fullname=custom_name_str)
                new_custom_name.save()
            is_updated_custom_name = True
        message = "Bạn đã cập nhật thông;tin cá nhân thành công!;"
        set_custom_name_fail = custom_name_str != '' and not is_updated_custom_name
        if set_custom_name_fail:
            message += 'Tên hiển thị không hợp lệ!'

        try:
            old_name = CustomName.objects.get(user=request.user.username).fullname
        except:
            old_name = ''
        popup = {
            'title_msg': "Thành công",
            'message': message,
            'type': 'OK' if not set_custom_name_fail else 'INFO',
            'time': 2000 if not set_custom_name_fail else 4000,
            'redirect': ''
        }
        cont = {
            'title': title,
            'user_profile': user_profile,
            'popup': popup,
            'custom_name': custom_name_str if not set_custom_name_fail else old_name
        }
        return render(request, 'setting.html', cont)
    else:
        try:
            custom_name = CustomName.objects.get(user=request.user.username).fullname
        except:
            custom_name = ''
        cont = {
            'title': title,
            'user_profile': user_profile,
            'custom_name': custom_name
        }
        return render(request, 'setting.html', cont)


@login_required(login_url='core:sign_in')
def setting_secure(request):
    title = 'Thay đổi mật khẩu'
    if request.method == 'POST':
        username = request.user.username
        old_pass = request.POST['old_password']
        new_pass = request.POST['new_password']
        re_pass = request.POST['re_password']
        try:
            process.change_password(username, old_pass, new_pass, re_pass)
        except Exception as ex:
            popup = {
                'title_msg': "Lỗi!",
                'message': ex,
                'type': 'ERROR',
                'time': 3000,
                'redirect': ''
            }
            cont = {
                'title': title,
                'popup': popup
            }
            return render(request, 'account_secure.html', cont)
        popup = {
            'title_msg': "Thành công!",
            'message': "Bạn đã cập nhật mật khẩu thành công!",
            'type': 'OK',
            'time': 2000,
            'redirect': ''
        }
        cont = {
            'title': title,
            'popup': popup
        }
        # login user sau khi cập nhật mật khẩu
        user_login = auth.authenticate(username=username, password=new_pass)
        auth.login(request, user_login)
        return render(request, 'account_secure.html', cont)
    cont = {
        'title': title
    }
    return render(request, 'account_secure.html', cont)


def forget_password(request):
    title = 'Quên mật khẩu'
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        try:
            new_pass = process.retrieve_password(username, email)
        except Exception as ex:
            popup = {
                'title_msg': "Lỗi!",
                'message': str(ex),
                'type': 'ERROR',
                'time': 3000,
                'redirect': ''
            }
            cont = {
                'title': title,
                'popup': popup
            }
            return render(request, 'retrieve_password.html', cont)

        # login user sau khi cập nhật mật khẩu
        user_login = auth.authenticate(username=username, password=new_pass)
        auth.login(request, user_login)

        popup = {
            'title_msg': "Thành công!",
            'message': "Thông tin đã được gửi tới địa chỉ email của bạn!",
            'type': 'OK',
            'time': 2500,
            'redirect': reverse('core:setting-secure')
        }
        cont = {
            'title': title,
            'popup': popup
        }
        return render(request, 'retrieve_password.html', cont)
    cont = {
        'title': title
    }
    return render(request, 'retrieve_password.html', cont)


@login_required(login_url='core:sign_in')
def upload(request):
    if request.method == 'POST':
        username = request.user.username
        page_number = request.GET.get('page')
        content_obj = process.get_context_index(username, page_number)
        image = request.FILES.get('image_upload')
        if not process.is_valid_image(image):
            popup = {
                'title_msg': "Lỗi!",
                'message': "Hệ thống không chấp nhận;tập tin không phải hình ảnh!",
                'type': 'ERROR',
                'time': 2700,
                'redirect': reverse('core:index')
            }
            cont = {
                'title': "Trang chủ",
                'popup': popup,
                'user_profile': content_obj['user_profile'],
                'posts': content_obj['page_obj'],
                'username': request.user.username,
                'suggestions_user_profile_list': (content_obj['suggestions_user_profile_list'])[:4]
            }
            return render(request, 'index.html', cont)
        caption = request.POST['caption']

        try:
            process.is_valid_caption(caption)
        except Exception as ex:
            popup = {
                'title_msg': "Lỗi!",
                'message': str(ex),
                'type': 'INFO',
                'time': 3000,
                'redirect': reverse('core:index')
            }
            cont = {
                'title': "Trang chủ",
                'popup': popup,
                'user_profile': content_obj['user_profile'],
                'posts': content_obj['page_obj'],
                'username': request.user.username,
                'suggestions_user_profile_list': (content_obj['suggestions_user_profile_list'])[:4]
            }
            return render(request, 'index.html', cont)
        new_post = Post.objects.create(user=username, image=image, caption=caption)
        new_post.save()
        return redirect('core:post_details', new_post.id)
    else:
        return redirect('core:index')


@login_required(login_url='core:sign_in')
def like_post(request):
    username = request.user.username
    post_id = request.POST['post_id']
    try:
        post = Post.objects.get(id=post_id)
    except:
        post_id = None
    if post_id is None:
        cont = {
            "ERROR": "Bài viết không tồn tại trên hệ thống!"
        }
        return JsonResponse(data=cont, status=200)
    like_filter = LikePost.objects.filter(username=username, post=post).first()
    if not like_filter:
        # User chưa thích bài viết này
        new_like = LikePost.objects.create(post=post, username=username)
        new_like.save()
        # Tăng số lượng lượt like của post lên 1
        post.no_of_likes += 1
        post.save()
        cont = {
            "like_count": post.no_of_likes
        }
        return JsonResponse(data=cont, status=200)
    # User đã like bài viết
    # => Hủy like bài viết này
    like_filter.delete()
    post.no_of_likes -= 1
    post.save()
    cont = {
        "like_count": post.no_of_likes
    }
    return JsonResponse(data=cont, status=200)


@login_required(login_url='core:sign_in')
def profile(request, pk):
    try:
        User.objects.get(username=pk)
    except:
        return process.return_render_index(request)
    cont = process.get_context_profile(request.user.username, pk)
    return render(request, 'profile.html', cont)


@login_required(login_url='core:sign_in')
def follow(request):
    if request.method != 'POST':
        return process.return_render_index(request)
    follower = request.POST['follower']
    user = request.POST['user']
    if FollowerCount.objects.filter(follower=follower, user=user).first():
        # User đang theo dõi tài khoản này
        # => Hủy theo dõi
        delete_follower = FollowerCount.objects.get(follower=follower, user=user)
        delete_follower.delete()
        return redirect('core:profile', user)
    # User chưa theo dõi tài khoản này
    # => Tạo theo dõi
    new_follower = FollowerCount.objects.create(follower=follower, user=user)
    new_follower.save()
    return redirect('core:profile', user)


@login_required(login_url='core:sign_in')
def search(request):
    if request.method == 'POST':
        search_name = request.POST['search_username']
        cont = process.get_context_search(search_name, request.user.username)
        return render(request, 'search.html', cont)
    content_obj = process.get_context_index(request.user.username, None)
    popup = {
        'title_msg': "Lỗi!",
        'message': "Hành động không được phép!",
        'type': 'ERROR',
        'time': 2000,
        'redirect': reverse('core:index')
    }
    cont = {
        'title': "Trang chủ",
        'user_profile': content_obj['user_profile'],
        'posts': content_obj['page_obj'],
        'username': request.user.username,
        'popup': popup
    }
    return render(request, 'index.html', cont)


class PostDetails(View):
    def get(self, request, pk):
        # pk = ae6faab4-81ec-4965-b723-642a6a87396b
        try:
            post = Post.objects.get(id=pk)
        except:
            page_number = request.GET.get('page')
            content_obj = process.get_context_index(request.user.username, page_number)
            popup = {
                'title_msg': "Lỗi!",
                'message': "Bài viết không tồn tại!",
                'type': 'ERROR',
                'time': 2000,
                'redirect': reverse('core:index')
            }
            cont = {
                'title': "Trang chủ",
                'popup': popup,
                'user_profile': content_obj['user_profile'],
                'posts': content_obj['page_obj'],
                'username': request.user.username,
                'suggestions_user_profile_list': (content_obj['suggestions_user_profile_list'])[:4]
            }
            return render(request, 'index.html', cont)
        comments = post.comment.all()
        editable = True if post.user == request.user.username else False
        user_profile = Profile.objects.get(user=request.user)
        cont = {
            'title': f"Chi tiết bài viết của {post.user}",
            'post': post,
            'edit': editable,
            'comments': comments,
            'user_profile': user_profile,
            'username': request.user.username
        }
        return render(request, 'post_details.html', cont)


@login_required(login_url='core:sign_in')
def post_comment(request):
    if request.method == 'POST':
        try:
            user_comment = request.POST['user_comment']
            post_id = request.POST['post_id']
            comment = request.POST['comment']
            post = Post.objects.get(id=post_id)
        except:
            return redirect('core:index')
        if len(str(comment).strip()) < 4:
            # Nội dung cmt không hợp lệ
            content_obj = process.get_context_index(request.user.username, None)
            popup = {
                'title_msg': "Lỗi!",
                'message': "Bình luận có độ dài không phù hợp!",
                'type': 'ERROR',
                'time': 3000,
                'redirect': reverse('core:index')
            }
            cont = {
                'title': "Trang chủ",
                'popup': popup,
                'user_profile': content_obj['user_profile'],
                'posts': content_obj['page_obj']
            }
            return render(request, 'index.html', cont)
        comment = Comment.objects.create(post=post, user=user_comment, comment_content=comment)
        comment.save()
        return redirect('core:post_details', post_id)
    else:
        content_obj = process.get_context_index(request.user.username, None)
        popup = {
            'title_msg': "Lỗi!",
            'message': "Hành động không được phép!",
            'type': 'ERROR',
            'time': 2000,
            'redirect': reverse('core:index')
        }
        cont = {
            'title': "Trang chủ",
            'popup': popup,
            'user_profile': content_obj['user_profile'],
            'posts': content_obj['page_obj']
        }
        return render(request, 'index.html', cont)


class DeletePost(TemplateView):

    @method_decorator(login_required)
    def post(self, request):
        post_id = request.POST['post_id']
        username = request.user.username
        user_profile = request.POST['user_profile']
        message_error = "Bài viết không tồn tại!"
        try:
            post = Post.objects.get(id=post_id)
            if post.user != username:
                message_error = "Bạn không được phép;xóa bài viết này!"
                raise Exception()
        except:
            page_number = request.GET.get('page')
            content_obj = process.get_context_index(request.user.username, page_number)
            popup = {
                'title_msg': "Lỗi!",
                'message': message_error,
                'type': 'ERROR',
                'time': 2000,
                'redirect': f'post-details/{post_id}'
            }
            cont = {
                'title': "Trang chủ",
                'popup': popup,
                'user_profile': content_obj['user_profile'],
                'posts': content_obj['page_obj'],
                'username': request.user.username,
                'suggestions_user_profile_list': (content_obj['suggestions_user_profile_list'])[:4]
            }
            return render(request, 'index.html', cont)
        post.delete()
        content_obj = process.get_context_index(request.user.username, None)
        popup = {
            'title_msg': "Thành công!",
            'message': "Bạn đã xóa bài viết thành công!",
            'type': 'OK',
            'time': 2000,
            'redirect': reverse('core:profile', kwargs={'pk': user_profile})
        }
        cont = {
            'title': "Trang chủ",
            'popup': popup,
            'user_profile': content_obj['user_profile'],
            'posts': content_obj['page_obj'],
            'username': request.user.username,
            'suggestions_user_profile_list': (content_obj['suggestions_user_profile_list'])[:4]
        }
        return render(request, 'index.html', cont)


@login_required(login_url='core:sign_in')
def edit_post(request):
    if request.method != 'POST' and request.method != 'GET':
        return redirect('core:index')
    if request.method == 'GET':
        try:
            post_id = request.GET['post_id']
            post = Post.objects.get(id=post_id)
        except:
            return redirect('core:index')
        if post.user != request.user.username:
            content_obj = process.get_context_index(request.user.username, None)
            popup = {
                'title_msg': "Lỗi!",
                'message': 'Bạn không đủ quyền hạn để thực hiện hành động này!',
                'type': 'INFO',
                'time': 3000,
                'redirect': reverse('core:index')
            }
            cont = {
                'title': "Trang chủ",
                'popup': popup,
                'user_profile': content_obj['user_profile'],
                'posts': content_obj['page_obj'],
                'username': request.user.username,
                'suggestions_user_profile_list': (content_obj['suggestions_user_profile_list'])[:4]
            }
            return render(request, 'index.html', cont)
        cont = {
            'title': 'Cập nhật bài viết',
            'post': post
        }
        return render(request, 'edit_post.html', cont)
    caption = request.POST['caption']
    image = request.FILES.get('image')
    if not process.is_valid_image(image):
        popup = {
            'title_msg': "Lỗi!",
            'message': "Hệ thống không chấp nhận;tập tin không phải hình ảnh!",
            'type': 'ERROR',
            'time': 2700,
            'redirect': reverse('core:index')
        }
        content_obj = process.get_context_index(request.user.username, None)
        cont = {
            'title': "Trang chủ",
            'popup': popup,
            'user_profile': content_obj['user_profile'],
            'posts': content_obj['page_obj'],
            'username': request.user.username,
            'suggestions_user_profile_list': (content_obj['suggestions_user_profile_list'])[:4]
        }
        return render(request, 'index.html', cont)
    try:
        post_id = request.GET['post_id']
        post = Post.objects.get(id=post_id)
    except:
        return redirect('core:index')

    post.caption = caption
    try:
        process.is_valid_caption(caption)
    except Exception as ex:
        content_obj = process.get_context_index(request.user.username, None)
        popup = {
            'title_msg': "Lỗi!",
            'message': str(ex),
            'type': 'INFO',
            'time': 3000,
            'redirect': reverse('core:index')
        }
        cont = {
            'title': "Trang chủ",
            'popup': popup,
            'user_profile': content_obj['user_profile'],
            'posts': content_obj['page_obj'],
            'username': request.user.username,
            'suggestions_user_profile_list': (content_obj['suggestions_user_profile_list'])[:4]
        }
        return render(request, 'index.html', cont)
    if post.user != request.user.username:
        content_obj = process.get_context_index(request.user.username, None)
        popup = {
            'title_msg': "Lỗi!",
            'message': 'Bạn không đủ quyền hạn để thực hiện hành động này!',
            'type': 'INFO',
            'time': 3000,
            'redirect': reverse('core:index')
        }
        cont = {
            'title': "Trang chủ",
            'popup': popup,
            'user_profile': content_obj['user_profile'],
            'posts': content_obj['page_obj'],
            'username': request.user.username,
            'suggestions_user_profile_list': (content_obj['suggestions_user_profile_list'])[:4]
        }
        return render(request, 'index.html', cont)
    if image is not None:
        image_path = post.image.path
        process.remove_old_image(image_path)
        post.image = image
    post.save()
    return redirect('core:post_details', post_id)


@login_required(login_url='core:sign_in')
def edit_comment(request):
    if request.method != 'POST' and request.method != 'GET':
        return redirect('core:index')
    if request.method == 'GET':
        username = request.user.username
        try:
            comment_id = request.GET['comment_id']
            comment_object = Comment.objects.get(id=comment_id)
            if username != comment_object.user:
                return redirect('core:index')
        except:
            return redirect('core:index')
        if comment_object.user != request.user.username:
            content_obj = process.get_context_index(request.user.username, None)
            popup = {
                'title_msg': "Lỗi!",
                'message': 'Bạn không đủ quyền hạn để thực hiện hành động này!',
                'type': 'INFO',
                'time': 3000,
                'redirect': reverse('core:index')
            }
            cont = {
                'title': "Trang chủ",
                'popup': popup,
                'user_profile': content_obj['user_profile'],
                'posts': content_obj['page_obj'],
                'username': request.user.username,
                'suggestions_user_profile_list': (content_obj['suggestions_user_profile_list'])[:4]
            }
            return render(request, 'index.html', cont)
        cont = {
            'title': 'Chỉnh sửa bình luận',
            'comment': comment_object
        }
        return render(request, 'edit_comment.html', cont)

    try:
        comment_content = request.POST['comment_cont']
        comment_id = request.POST['comment_id']
        comment_object = Comment.objects.get(id=comment_id)
    except:
        return redirect('core:index')
    if len(str(comment_content).strip()) < 4:
        # Bình luận không hợp lệ
        popup = {
            'title_msg': "Lỗi!",
            'message': "Bình luận có độ dài không hợp lệ!",
            'type': 'ERROR',
            'time': 3000,
            'redirect': ''
        }
        cont = {
            'title': 'Chỉnh sửa bình luận',
            'comment': comment_object,
            'popup': popup
        }
        return render(request, 'edit_comment.html', cont)

    if comment_object.user != request.user.username:
        content_obj = process.get_context_index(request.user.username, None)
        popup = {
            'title_msg': "Lỗi!",
            'message': 'Bạn không đủ quyền hạn để thực hiện hành động này!',
            'type': 'INFO',
            'time': 3000,
            'redirect': reverse('core:index')
        }
        cont = {
            'title': "Trang chủ",
            'popup': popup,
            'user_profile': content_obj['user_profile'],
            'posts': content_obj['page_obj'],
            'username': request.user.username,
            'suggestions_user_profile_list': (content_obj['suggestions_user_profile_list'])[:4]
        }
        return render(request, 'index.html', cont)
    comment_object.comment_content = comment_content
    comment_object.save()
    post = comment_object.post
    return redirect(reverse('core:post_details', kwargs={'pk': post.id}))


@login_required(login_url='core:sign_in')
def delete_comment(request):
    if request.method != 'POST':
        return redirect('core:index')
    try:
        comment_id = request.POST['comment_id']
        comment_object = Comment.objects.get(id=comment_id)
    except:
        return redirect('core:index')
    post = comment_object.post
    editable = True if post.user == request.user.username else False
    user_profile = Profile.objects.get(user=request.user)

    user_delete_comment = request.user.username
    if user_delete_comment != comment_object.user:
        # Người xóa comment không phải chủ nhân cmt
        # Cấm không được xóa comment
        comments = post.comment.all()
        popup = {
            'title_msg': "Lỗi!",
            'message': "Bạn không thể xóa bình luận của người khác!",
            'type': 'ERROR',
            'time': 3000,
            'redirect': ''
        }
        cont = {
            'title': f"Chi tiết bài viết của {post.user}",
            'post': post,
            'edit': editable,
            'comments': comments,
            'user_profile': user_profile,
            'username': request.user.username,
            'popup': popup
        }
        return render(request, 'post_details.html', cont)
    # User đang xóa comment là chủ nhân comment
    # => Cho phép user xóa comment
    comment_object.delete()
    comments = post.comment.all()
    popup = {
        'title_msg': "Thông báo",
        'message': "Bạn đã xóa bình luận;thành công!",
        'type': 'OK',
        'time': 2000,
        'redirect': reverse('core:post_details', kwargs={'pk': post.id})
    }
    cont = {
        'title': f"Chi tiết bài viết của {post.user}",
        'post': post,
        'edit': editable,
        'comments': comments,
        'user_profile': user_profile,
        'username': request.user.username,
        'popup': popup
    }
    return render(request, 'post_details.html', cont)
