from tkinter import Image
from django.urls import path
from users.views import RegisterView, ImageCodeView, SmsCodeView

urlpatterns = [
    # 第一个参数：路由
    # 第二个参数：视图函数名
    path('register/', RegisterView.as_view(), name='register'),

    # 图片验证码的路由
    path('imagecode/', ImageCodeView.as_view(), name='imagecode'),

    # 短信验证码的路由
    path('smscode/', SmsCodeView.as_view(), name='smscode'),
]
