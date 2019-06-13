from flask_moment import datetime
from MyBlog.extensions import db
from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash


# 管理员类(存储用户名,密码hash值,博客相关设置)
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))  # 用户名(用于登录)
    password_hash = db.Column(db.String(128))
    # 博客设置
    blog_title = db.Column(db.String(60))   # 博客标题
    blog_sub_title = db.Column(db.String(100))  # 子标题
    name = db.Column(db.String(30))  # 用户昵称(评论中显示)
    about = db.Column(db.Text)

    # 生成密码函数
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 验证密码函数
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


# 分类
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)    # 分类名不允许重复,unique=True
    # back_populates为SQLAlchemy的关系函数参数,用于定义反向引用,建立双向关系,在关系的另一侧也必须显式定义关系属性
    posts = db.relationship('Post', back_populates='category')

    def delete(self):
        default_category = Category.query.get(1)  # 获取默认分类
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()


# 文章
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # 时间戳
    body = db.Column(db.Text)
    can_comments = db.Column(db.Boolean, default=True)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))    # 将category_id设置为外键
    category = db.relationship('Category', back_populates='posts')

    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')  # cascade设置级联操作


# 评论
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    body = db.Column(db.Text)
    from_admin = db.Column(db.Boolean, default=False)
    reviewed = db.Column(db.Boolean, default=False)

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='comments')
    # 建立邻接列表关系(在同一个模型内的一对多关系)
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    # replied表示被回复评论的标量关系属性, remote_side=[id]将id字段定义为关系远程侧
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])
    replies = db.relationship('Comment', back_populates='replied', cascade='all')