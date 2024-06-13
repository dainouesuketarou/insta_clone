from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

def upload_avatar_path(instance, filename):
    # .jpegや.pngなどが代入される
    ext = filename.split('.')[-1]
    # avatars(folderになる？？)/str(instance.usrProfile.id)+str(instance.nickName)+str(".")+str(ext)が返される
    # userのプロフィール画像のパスを返している
    return '/'.join(['avatars', str(instance.usrProfile.id)+str(instance.nickName)+str(".")+str(ext)])

def upload_post_path(instance, filename):
    ext = filename.split('.')[-1]
    return '/'.join(['posts', str(instance.userPost.id)+str(instance.title)+str(".")+str(ext)])


class UserManager(BaseUserManager):
    
    # 一般ユーザーを作成するメソッド
    # emailとパスワードでユーザーのオブジェクトを作成する
    # パスワードの引数のデフォルトを空とする
    def create_user(self, email, password=None):
        # emailがない場合絵エラーを投げる
        if not email:
            raise ValueError('email is must')

        # ユーザーオブジェクトを作成するところ
        # 与えられたemailアドレスを正規化している。(全て小文字に変換)
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        # 新しく作成されたユーザーオブジェクトをデータベースに保存
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(max_length=50, unique=True)
    # ログイン機能を付与
    is_active = models.BooleanField(default=True)
    # AdminのDashboardのログイン権限は与えない
    is_staff = models.BooleanField(default=False)

    # こちらのクラスからUserManagerクラスのメソッドを使用できるようにするため
    objects = UserManager()

    # emailフィールドをユーザーの識別子として使用することができる
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

class Profile(models.Model):
    nickname = models.CharField(max_length=20)
    userProfile = models.OneToOneField(
        # カスタムUserモデルとuserProfileを一対一で紐付け
        # 'profile'はUserモデルからProfileモデルにアクセスする際に使用される逆参照の名前の指定
        settings.AUTH_USER_MODEL, related_name='profile'
        # userProfile削除時にProfileインスタンスも削除されるようになる
        , on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(blank=True, null=True, upload_to=upload_avatar_path)

    def __str__(self):
        return self.nickname

class Post(models.Model):
    title = models.CharField(max_length=100)
    userPost = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='userPost',
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(blank=True, null=True, upload_to=upload_post_path)
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.title

class Comment(models.Model):
    text = models.TextField(max_length=100)
    userComment = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='userComment',
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.text