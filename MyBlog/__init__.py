import os
import click
from flask import Flask, request
import logging

from MyBlog.blueprint.admin import admin_my
from MyBlog.blueprint.blog import blog_my
from MyBlog.blueprint.login import login_my
from MyBlog.extensions import db, ckeditor, moment, bootstrap, login, csrf, migrate
from MyBlog.settings import config
from MyBlog.models import Admin, Category, Post, Comment
from MyBlog.fakes import fake_admin, fake_post, fake_category, fake_comment
from flask_login import current_user
from logging.handlers import RotatingFileHandler

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


# 定义工厂函数
def create_app(config_name=None):
    if config_name == None:
        config_name = os.getenv('FLASK_CONFIG', 'development')  # 设置配置名

    app = Flask('MyBlog')
    app.config.from_object(config[config_name])  # 从settings.py中的配置字典获取配置

    # 注册工厂函数
    register_template_context(app)
    register_commands(app)
    register_shell_context(app)
    register_errors(app)
    register_extensions(app)
    register_blueprint(app)
    register_logging(app)

    return app


# 日志管理
def register_logging(app):
    class RequestFormatter(logging.Formatter):

        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/MyBlog.log'),
                                       maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    if not app.debug:
        app.logger.addHandler(file_handler)


# 组织蓝本
def register_blueprint(app):
    app.register_blueprint(blog_my)
    app.register_blueprint(login_my, url_prefix='/auth')
    app.register_blueprint(admin_my, url_prefix='/admin')


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        posts = Post.query.order_by(Post.timestamp).all()

        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(
            admin=admin,
            categories=categories,
            posts=posts,
            unread_comments=unread_comments
        )


# 调用init_app()方法，传入程序实例，完成拓展初始化
def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    ckeditor.init_app(app)
    login.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app)

    return app


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)


def register_commands(app):
    @app.cli.command()  # 添加命令行接口
    @click.option('--drop', is_flag=True, help='重新创建数据库表')  # 使用click提供的option装饰器添加自定义数量支持
    def initdb(drop):  # 初始化数据库,传入drop参数
        """初始化数据库"""
        if drop:
            click.confirm('该操作将删除原有数据库，确定删除?', abort=True)
            db.drop_all()
            click.echo('删除数据库')
        db.create_all()
        click.echo('已重置数据库')

    @app.cli.command()
    @click.option('--username', prompt=True, help='登录用户名')
    @click.option('--password', prompt=True, hide_input=True,  # hide_input隐藏输入内容
                  confirmation_prompt=True, help='登录密码')  # confirmation_prompt设置二次确认输入
    def init(username, password):  # 博客初始化,传入用户名和密码
        """创建BLUELOG，个性化博客"""

        click.echo('配置数据库中...')
        db.create_all()

        admin = Admin.query.first()  # 从数据库中查找管理员记录
        if admin is not None:  # 如果数据库中已经有管理员记录就更新用户名和密码
            click.echo('管理员已存在，更新中...')
            admin.username = username
            admin.set_password(password)  # 调用Admin模型类中的set_password()方法，生成password
        else:  # 没有管理员记录则创建新的管理员记录
            click.echo('新建管理员账户...')
            admin = Admin(
                username=username,
                blog_title='Theminimize',
                name='授我以驴',
                about='Anything about you.'
            )
            admin.set_password(password)
            db.session.add(admin)  # 将新创建对象添加到数据库会话

        category = Category.query.first()
        if category is None:  # 如果没有分类则创建默认分类
            click.echo('创建默认分类...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()  # 调用session.commit()，将改动提交到数据库
        click.echo('完成.')


    @app.cli.command()
    @click.option('--category', default=5, help='分类数量,默认值为5个')
    @click.option('--post', default=25, help='文章数量,默认值为25篇')
    @click.option('--comment', default=150, help='评论数量,默认值为150个')
    def forge(category, post, comment):
        db.drop_all()
        db.create_all()

        click.echo('生成管理员...')
        fake_admin()

        click.echo('生成 %d 个分类...' % category)
        fake_category(category)

        click.echo('生成 %d 篇文章...' % post)
        fake_post(post)

        click.echo('生成 %d 个评论...' % comment)
        fake_comment(comment)

        click.echo('数据生成完毕！')

def register_errors(app):
    pass