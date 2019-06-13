from flask import redirect, request, url_for, current_app

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin


# 判断安全链接，防止形成开放重定向漏洞
def is_safe_url(target):
    # request.host_url获取程序内主机URL
    ref_url = urlparse(request.host_url)
    # urljoin()函数将目标URL转换为绝对URL
    test_url = urlparse(urljoin(request.host_url, target))
    # 最后对目标URL的URL模式和主机地址进行验证，确保只返回属于程序内部的URL
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='blog.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


# 给允许上传的文件加上“.”
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['MYBLOG_ALLOWED_IMAGE_EXTENSIONS']