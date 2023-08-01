from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from datetime import timedelta
from django.utils import timezone
from utils.kavenegar import send_sms


class UserManager(BaseUserManager):
    def create_user(self, username, firstname, lastname, password=None):
        if not username:
            raise ValueError('username must have an username')
        user = self.model(username=username, firstname=firstname, lastname=lastname)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, firstname, lastname, password):
        user = self.create_user(username, firstname, lastname, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    MALE = 1
    FEMALE = 2
    GENDER_TYPE_FIELDS = ((MALE, 'male'), (FEMALE, 'female'))

    username = models.CharField(max_length=256, unique=True, null=False, blank=False, verbose_name='username')
    phone_number = models.CharField(max_length=20, unique=True, null=False, blank=False, verbose_name='phone_number')
    email = models.CharField(max_length=256, unique=True, null=False, blank=False, verbose_name='email')
    firstname = models.CharField(max_length=48, null=False, verbose_name='firstname')
    lastname = models.CharField(max_length=48, null=False, verbose_name='lastname')
    gender = models.PositiveSmallIntegerField(null=True, blank=True, choices=GENDER_TYPE_FIELDS, verbose_name='gender')
    birthday = models.DateField(null=True, blank=True, verbose_name='birthday')
    is_active = models.BooleanField(default=True, verbose_name='is_active')
    is_staff = models.BooleanField(default=False, verbose_name='is_staff')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')
    modified_time = models.DateTimeField(auto_now=True, verbose_name='modified_time')

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    @classmethod
    def check_user_exist(cls, user):
        try:
            return cls.objects.get(username=user)
        except User.DoesNotExist:
            return None


class Verify(models.Model):
    phone_number = models.CharField(max_length=20, unique=True, verbose_name='phone_number')
    code = models.CharField(max_length=4, verbose_name='code')
    count_wrong = models.IntegerField(default=0)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="created_time")
    modified_time = models.DateTimeField(auto_now=True, verbose_name="modified_time")

    @classmethod
    def create_verify(cls, request, code):
        try:
            verify = cls.objects.get(phone_number=request.data['phone_number'])
            if timezone.now() < verify.modified_time + timedelta(minutes=2):
                return verify, 'sent', 'sent'
            verify.code = code
            verify.save()
            response_sms = send_sms(request.data['phone_number'], 'verifyLogin', code, '', '')
            return verify, response_sms, 'created'
        except Verify.DoesNotExist:
            verify_create = cls.objects.create(phone=request.data['phone_number'], code=code)
            response_sms = send_sms(request.data['phone_number'], 'verifyLogin', code, '', '')
            return verify_create, response_sms, 'created'

    @classmethod
    def check_verify(cls, request):
        try:
            verify = cls.objects.get(phone=request.data['phone_number'])
            if verify.code == request.data['code']:
                if timezone.now() < verify.modified_time + timedelta(minutes=2):
                    verify.delete()
                    return 'verify'
                else:
                    return 'notValid'
            else:
                verify.count_wrong = verify.count_wrong + 1
                verify.save()
                return 'notFound'
        except Verify.DoesNotExist:
            return 'notFound'
