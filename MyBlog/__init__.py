import os
import click
from flask import Flask

from MyBlog.blueprint.admin import admin_my
from MyBlog.blueprint.blog import blog_my
from MyBlog.blueprint.login import login_my
from MyBlog.extensions import db, ckeditor, moment, bootstrap, login, csrf
from MyBlog.settings import config
from MyBlog.models import Admin, Category, Post, Comment
from MyBlog.fakes import fake_admin, fake_post, fake_category, fake_comment
from flask_login import current_user


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
    pass


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

    return app


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)


def register_commands(app):
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