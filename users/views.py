import logging
from random import randint
from django.shortcuts import render
from django.views import View
from django.http.response import HttpResponseBadRequest, HttpResponse, JsonResponse
from django_redis import get_redis_connection
from libs.captcha.captcha import captcha
from libs.yuntongxun.sms import CCP
from utils.response_code import RETCODE

logger = logging.getLogger('django')

class RegisterView(View):
    def get(self, request):

        return render(request, 'register.html')


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
        return JsonResponse({'code': RETCODE.OK, 'msg':'短信发送成功'})
