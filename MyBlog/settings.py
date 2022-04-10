import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))   # 找到当前根目录

'''
>>> os.path.abspath('~/Flask_hj/MyBlog/MyBlog/settings.py')
'/home/zijian-computer/Flask_hj/MyBlog/MyBlog/~/Flask_hj/MyBlog/MyBlog/settings.py'
>>> os.path.abspath(os.path.dirname('~/Flask_hj/MyBlog/MyBlog/settings.py'))
'/home/zijian-computer/Flask_hj/MyBlog/MyBlog/~/Flask_hj/MyBlog/MyBlog'
>>> os.path.abspath(os.path.dirname(os.path.dirname('~/Flask_hj/MyBlog/MyBlog/settings.py')))
'/home/zijian-computer/Flask_hj/MyBlog/MyBlog/~/Flask_hj/MyBlog'
'''
prefix = 'sqlite:///'


# 基本配置类
class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')   # 获取环境密钥

    SQLALCHEMY_TRACK_MODIFICATIONS = False   # 关闭警告信息
    SQLALCHEMY_RECORD_QUERIES = True    # 启用查询记录

    CKEDITOR_ENABLE_CSRF = True  # 开启CSRF保护
    CKEDITOR_FILE_UPLOADER = 'admin.upload_image'   # cke富文本编辑器的图片上传

    MYBLOG_POST_PER_PAGE = 7   # 每页文章数
    MYBLOG_MANAGE_POST_PER_PAGE = 15    # 后台管理界面每页文章数
    MYBLOG_COMMENT_PER_PAGE = 5    # 每页评论数
    MYBLOG_MANAGE_COMMENT_PER_PAGE = 15

    MYBLOG_UPLOAD_PATH = os.path.join(basedir, 'uploads')   # 上传路径
    MYBLOG_ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'png', 'gif', 'jpeg']    # 允许的图片格式


# 开发配置类
class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'Myblog.db')   # 设置数据库URI


# 测试配置类
class TestConfig(BaseConfig):
    TESTING = True
    CKEDITOR_ENABLE_CSRF = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # 采用内存型数据库


# 生产配置类
class ProductionConfig(BaseConfig):
    # 生产环境下更换其他类型DBMS时，数据库URI会包含敏感信息，因此优先从环境变量DATABASE_URL获取
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'Myblog_pd.db'))


# 定义配置映射字典
config = {
    'development': DevelopmentConfig,
    'test': TestConfig,
    'production': ProductionConfig
}
