from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from core.process import email_service
from .models import EmailLog
from datetime import datetime, timezone


# Create your views here.

class SendEmail(APIView):
    def post(self, request):
        try:
            # Thông tin được gửi từ feedback social
            name = request.data['name']
            sender = request.data['sender']
            content = request.data['feedback']
        except:
            name = None
            try:
                # Dữ liệu không được gửi từ Social Media
                title = request.data['title']
                content = request.data['content']
                mail_receive = request.data['receive']
            except:
                message = {
                    'type': "ERROR",
                    'message': "Thông tin gửi lên không hợp lệ! "
                               "Expected:[title], [content], [receive]"

                }
                return Response(data=message, status=200)
        if name is not None:
            # Xử lý dữ liệu gửi từ feedback social
            receive = "username251001@gmail.com"
            # validate data
            email = email_service.EmailHelper()
            try:
                email_service.is_valid_info(content, sender, name)
            except Exception as ex:
                message = {
                    'type': 'ERROR',
                    'message': str(ex)
                }
                return Response(data=message, status=200)
            last_email_sender = EmailLog.objects.filter(email_address=sender).order_by('-created')[:1]
            if last_email_sender.__len__() == 1:
                # User này đã gửi feedback trước đó
                time_send_before = last_email_sender[0].created
                now = datetime.now(timezone.utc)
                time_interval_second = (now - time_send_before).total_seconds()
                min_time_send_other_feedback = 120
                if time_interval_second < min_time_send_other_feedback:
                    time_remaining = min_time_send_other_feedback - time_interval_second
                    message = {
                        'type': "INFO",
                        'message': f"Tính năng sẽ khả dụng sau {int(time_remaining)} giây!"
                    }
                    return Response(data=message, status=200)
            title = "Góp ý cho mạng xã hội Media Social!"
            if email.send_email(title, content, receive):
                message = {
                    'type': "OK",
                    'message': "Đã gửi thông tin thành công!<br/>Cảm ơn bạn đã đóng góp ý kiến!"
                }
                email_feedback = EmailLog.objects.create(email_address=sender)
                email_feedback.save()
                email_service.thank_for_feedback(name, sender)
                return Response(data=message, status=200)
            else:
                # Gửi email thất bại
                message = {
                    'type': "ERROR",
                    'message': "Gửi thông tin không thành công!<br/>Rất xin lỗi vì sự bất tiện này!"
                }
                return Response(data=message, status=200)

        # Xử lý dữ liệu được post lên không phải được gửi từ feedback social!
        email = email_service.EmailHelper()
        try:
            email_service.is_valid_post_send_email(title, content, mail_receive)
        except Exception as ex:
            message = {
                'type': "ERROR",
                'message': str(ex)
            }
            return Response(data=message, status=200)
        if email.send_email(title, content, mail_receive):
            message = {
                'type': "OK",
                'message': "Đã gửi email thành công"
            }
            return Response(data=message, status=200)
        else:
            # Gửi email thất bại
            message = {
                'type': "ERROR",
                'message': "Gửi email không thành công! Rất xin lỗi vì sự bất tiện này!"
            }
            return Response(data=message, status=200)


def index_email(request):
    if request.method == 'GET':
        cont = {
            'title': "Đóng góp ý kiến"
        }
        return render(request, 'app_email/feedback.html', cont)
