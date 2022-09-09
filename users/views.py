import re
import logging
from random import randint
from urllib import response
from django.shortcuts import render, redirect
from django.views import View
from django.http.response import HttpResponseBadRequest, HttpResponse, JsonResponse
from django_redis import get_redis_connection
from django.db import DatabaseError
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from libs.captcha.captcha import captcha
from libs.yuntongxun.sms import CCP
from utils.response_code import RETCODE
from users.models import User

logger = logging.getLogger('django')


class RegisterView(View):

    def get(self, request):

        return render(request, 'register.html')

    def post(self, request):

        # 1.接收数据
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        smscode = request.POST.get('sms_code')
        # 2.验证数据
        # 参数是否齐全
        if not all([mobile, password, password2, smscode]):
            return HttpResponseBadRequest('缺少必要的参数')
        # 手机号的格式是否正确
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('手机号不符合规则')
        # 密码是否符合格式
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseBadRequest('请输入8-20位密码，密码是数字、大小写字母')
        # 密码和确认信息要一致
        if password != password2:
            return HttpResponseBadRequest('两次密码不一致')
        # 短信验证码是否和redis中的一致
        redis_conn = get_redis_connection('default')
        redis_sms_code = redis_conn.get(f'sms:{mobile}')
        if redis_sms_code is None:
            return HttpResponseBadRequest('短信验证码已过期')
        if smscode != redis_sms_code.decode():
            return HttpResponseBadRequest('短信验证码不一致')
        # 3.保存注册信息
        try:
            user = User.objects.create_user(username=mobile,
                                            mobile=mobile,
                                            password=password)
        except DatabaseError as e:
            logger.error(e)
            return HttpResponseBadRequest('注册失败')

        # 保存登录状态
        login(request, user)
        # 4.返回响应跳转到制定页面
        # redirect 进行重定向
        # reverse 可以通过namespace:name来获取视图对应的路由
        response = redirect(reverse('home:index'))
        # 设置cookie信息，以方便首页中用户信息的判断和展示
        response.set_cookie('is_login', True)
        response.set_cookie('username', user.username, max_age=7*24*3600)

        return response


class ImageCodeView(View):
    def get(self, request):
        # 1.接受前段传递的uuid
        uuid = request.GET.get('uuid')
        # 2.判断uuid是否获取到
        if uuid is None:
            return HttpResponseBadRequest('没有传递uuid')
        # 3.通过调用captcha来生成图片验证码（图片二进制和图片内容）
        text, image = captcha.generate_captcha()
        # 4.将图片内容保存到redis中,uuid作为key，图片内容作为value，同时设置一个时效
        redis_conn = get_redis_connection('default')
        # key=img:uuid, seconds=300, value=text
        redis_conn.setex(f'img:{uuid}', 300, text)
        # 5.返回图片二进制
        return HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):

    def get(self, request):

        # 1.接收参数（查询字符串）
        mobile = request.GET.get('mobile')
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        # 2.参数的验证
        # 2.1 验证参数是否齐全
        if not all([mobile, image_code, uuid]):
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必要的参数'})
        # 2.2 图片验证码的验证
        # 连接redis，获取redis中的图片验证码
        redis_conn = get_redis_connection('default')
        redis_image_code = redis_conn.get(f'img:{uuid}')
        # 判断图片验证码是否存在
        if redis_image_code is None:
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图片验证码已过期'})
        # 如果图片验证码没有过期，获取之后，删除验证码
        try:
            redis_conn.delete(f'img:{uuid}')
        except Exception as e:
            logger.error(e)
        # 对比图片验证码，注意大小写，redis的数据是byte类型
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图片验证码错误'})
        # 3.生成短信验证码
        sms_code = f'{randint(0, 999999):06d}'
        # 为了后期比对方便，可以将短信验证码，记录到日志中
        logger.info(sms_code)
        # 4.保存短信验证码到redis中
        redis_conn.setex(f'sms:{mobile}', 300, sms_code)
        # 5.发送短信
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # 6.返回响应
        return JsonResponse({'code': RETCODE.OK, 'msg': '短信发送成功'})


class LoginView(View):
    """登录界面视图"""
    def get(self, request):

        return render(request, 'login.html')

    def post(self, request):

        # 1.接收参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        # 2.参数的验证
        # 验证手机号是否符合规则
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('手机号不符合规则')
        # 验证密码是否符合规则
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseBadRequest('密码不符合规则')
        
        # 3.用户认证登录
        # 采用系统自带的认证方式进行验证
        # 如果我们的用户名和密码正确，会返回usder
        # 如果我们的用户名或密码不正确，会返回None
        # 默认的认证方法是针对username字段进行用户名的判断
        # 当前我们使用的是mobile，需要修改认证字段，需要到User模型中修改
        user = authenticate(mobile=mobile, password=password)
        if user is None:
            return HttpResponseBadRequest('用户名或密码错误')

        # 4.状态的保持
        login(request, user)
        response = redirect(reverse('home:index'))

        # 5.根据用户选择的是否记住登录状态来进行判断
        # 6.为了首页显示我们需要设置一些cookie信息
        if remember != 'on':
            # 0，浏览器关闭之后过期
            request.session.set_expiry(0)
            response.set_cookie('is_login', True)
            response.set_cookie('username', user.username, max_age=14*24*3600)
        else:
            # None，默认记住两周
            request.session.set_expiry(None)
            response.set_cookie('is_login', True, max_age=14*24*3600)
            response.set_cookie('username', user.username, max_age=14*24*3600)

        # 7.返回响应
        return response


class LogoutView(View):

    def get(self, request):
        # 1.session数据清除
        logout(request)
        # 2.删除部分cookie数据
        response = redirect(reverse('home:index'))
        response.delete_cookie('is_login')
        # 3.跳转到首页
        return response
        