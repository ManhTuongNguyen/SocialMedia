import smtplib
from email.mime.text import MIMEText
import re


class EmailHelper:
    username = ''
    password = ''

    def send_email(self, subject: str, content: str, to_address: str) -> bool:
        crypto = CeasarHelper()
        username = crypto.decrypt(self.username, 6)
        password = crypto.decrypt(self.password, 3)

        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['from'] = username
        msg['To'] = to_address

        # Send message using smtp server
        try:
            server = smtplib.SMTP('smtp-mail.outlook.com', 587)
            server.starttls()
            server.ehlo()
            server.login(username, password)
            server.sendmail(username, to_address, msg.as_string())
            server.quit()
            return True
        except Exception as ex:
            print(ex)
            return False


class CeasarHelper:
    bangTra = ['C', 'D', '-', '=', '_', '(', ')', 'E', 'o', 'p', 'z', 'A', '2', 'Z', ';',
               'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', '@',
               'Q', 'R', 'S', 'q', 'v', 'w', 'x', 'y', 'T', '6', '7', '9', '.', '3', '*',
               'r', 's', 't', 'u', 'F', 'G', 'H', 'L', 'M', 'N', 'O', 'P', 'V', 'W', '/',
               '4', 'X', 'Y', '0', '1', '5', '!', '+', 'I', 'B', ',', 'U', ' ', 'J', 'K', ]

    def encrypt(self, raw_str: str, key: int = None) -> str:
        """ Encrypt string using Ceasar Algorithm
        Args:
            raw_str: String need encrypt
            key: key using to encrypt string
        Return:
            String encrypted using Ceasar algorithm
        Raise:
            Raise Exception if key is not number
        """
        if key is None:
            key = 5
        if type(key) != int:
            raise Exception('Key must be a number!')
        encrypted = ''
        for i in raw_str:
            old_index = -1
            try:
                old_index = self.bangTra.index(i)
            except:
                old_index = -1
            if old_index == -1:
                encrypted += i
                continue
            new_index = old_index + key
            while new_index < 0:
                new_index += len(self.bangTra)
            while new_index > len(self.bangTra) - 1:
                new_index -= len(self.bangTra)
            encrypted += self.bangTra[new_index]
        return encrypted

    def decrypt(self, raw_str: str, key: int = None) -> str:
        """
        Decrypt string using Ceasar Algorithm
        Args:
            raw_str: String need decrypt
            key: key using to decrypt string
        Return:
            string decrypt using ceasar algorithm
        Raise:
            Raise Exception if key is not number
        """
        if key is None:
            key = 5
        if type(key) != int:
            raise Exception('Key must be a number!')
        decrypted = ''
        for i in raw_str:
            old_index = -1
            try:
                old_index = self.bangTra.index(i)
            except:
                old_index = -1
            if old_index == -1:
                decrypted += i
                continue
            new_index = old_index - key
            while new_index < 0:
                new_index += len(self.bangTra)
            while new_index > len(self.bangTra) - 1:
                new_index -= len(self.bangTra)
            decrypted += self.bangTra[new_index]
        return decrypted


def get_message_content_retrieve_password(name: str, custom_name: str, password: str) -> str:
    if custom_name is None:
        custom_name = name
    return f"""
    Xin chào {custom_name}!
    Ai đó vừa yêu cầu lấy lại mật khẩu cho tài khoản {name} từ Social Media.
    Tôi hi vọng đó là bạn!
    Mật khẩu của bạn là: {password}
    Hãy bảo mật thông tin này cẩn thận!
    Thay đổi mật khẩu ngay khi bạn đăng nhập lại Social Media!
    Nếu có góp ý, thắc mắc hãy liên hệ với tôi qua địa chỉ: Mtuongpk@gmail.com
    Tôi rất mong muốn được lắng nghe những ý kiến đóng góp của bạn!
    Trân trọng!
    """


def get_message_subject_retrieve_password():
    return "Thông tin tài khoản của bạn tại Social Media!"


def send_password_to_email(username: str, custom_name: str, password: str, to_address: str) -> bool:
    subject = get_message_subject_retrieve_password()
    content = get_message_content_retrieve_password(username, custom_name, password)
    email_service = EmailHelper()
    return email_service.send_email(subject, content, to_address)


def is_valid_email(email: str) -> bool:
    if not email.strip():
        raise Exception("Không được bỏ trống địa chỉ email!")
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(regex, email):
        if email.endswith(".com") or email.endswith(".co.uk") or email.endswith(".fr")\
                or email.endswith(".ru") or email.endswith(".vn"):
            # https://email-verify.my-addr.com/list-of-most-popular-email-domains.php#:~:text=Top%20100%20%20%201%20%20%20gmail.com,%20%201.27%25%20%2095%20more%20rows%20
            return True
        raise Exception("Địa chỉ email không được chấp nhận tại hệ thống!")
    raise Exception("Địa chỉ email không hợp lệ!")


def is_valid_feedback(content):
    if len(str(content).strip()) < 20:
        raise Exception("Nội dung góp ý không được quá ngắn!")


def is_valid_name(name):
    if len((str(name).strip())) < 5:
        raise Exception("Tên không hợp lệ!")


def is_valid_info(content, sender, name):
    is_valid_email(sender)
    is_valid_feedback(content)
    is_valid_name(name)
    return True


def get_message_subject_feedback():
    return "Lời cảm ơn từ Social Media!"


def get_message_content_feedback(name):
    return f"""
    Xin chào {name}!
    Rất vui khi nhận được ý kiến đóng góp của bạn.
    Chúng tôi đã ghi nhận và chuyển đến bộ phận phát triển.
    Hy vọng bạn sẽ đồng hành cùng chúng tôi thật lâu,
    đóng góp cho chúng tôi những ý tưởng mới, hoặc báo cáo những lỗi đang tồn đọng.
    Trân trọng!
    """


def thank_for_feedback(name, sender):
    subject = get_message_subject_feedback()
    content = get_message_content_feedback(name)
    email_service = EmailHelper()
    return email_service.send_email(subject, content, sender)


def is_valid_content(content):
    if len((str(content).strip())) < 15:
        raise Exception("Nội dung email không được quá ngắn!")
    return True


def is_valid_title(title):
    if len((str(title).strip())) < 10:
        raise Exception("Nội dung tiêu đề không được quá ngắn!")
    return True


def is_valid_post_send_email(title, content, mail_receive):
    is_valid_title(title)
    is_valid_content(content)
    is_valid_email(mail_receive)
    return True