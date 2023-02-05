from django.db import models
from django.contrib.auth import get_user_model
import uuid


User = get_user_model()


# Create your models here.
class Profile(models.Model):
    id_user = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)  # biographical
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    cover_img = models.ImageField(upload_to='profile_images', default='default_cover_img.jpg')
    location = models.CharField(max_length=125, blank=True)

    def __str__(self):
        return self.user.username


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=80)
    image = models.ImageField(upload_to='post_images', blank=True)
    caption = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        # return self.user + ' - ' + self.caption[:25]
        # return str(self.created)
        return str(self.id)


class LikePost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.username} đã thích post có id: {self.post_id}'


class FollowerCount(models.Model):
    follower = models.CharField(max_length=100)  # user theo dõi user khác
    user = models.CharField(max_length=100)  # user được theo dõi

    def __str__(self):
        return f'{self.follower} đang theo dõi {self.user}'


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment')
    user = models.CharField(max_length=80)
    comment_content = models.TextField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ('created', )


class CustomName(models.Model):
    user = models.CharField(max_length=100)
    fullname = models.CharField(max_length=100)


class GetPasswordLog(models.Model):
    user = models.CharField(max_length=80)
    created = models.DateTimeField(auto_now_add=True)
