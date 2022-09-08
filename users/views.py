from django.shortcuts import render
from django.views import View
from django.http.response import HttpResponseBadRequest, HttpResponse
from django_redis import get_redis_connection
from libs.captcha.captcha import captcha

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

