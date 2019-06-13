import random
from MyBlog.models import Admin, Category, Post, Comment
from MyBlog.extensions import db
from faker import Faker
from sqlalchemy.exc import IntegrityError

fake = Faker()


def fake_admin():
    admin = Admin(
        username='xixi1216',
        blog_title="授我以驴'blog",
        blog_sub_title='yo~yo~yo!',
        name='一头特立独行的猪',
        about="Welcome to my personal website,um,i , He Jian,likes uses python to coding"
    )
    admin.set_password('helloflask')
    db.session.add(admin)
    db.session.commit()


def fake_category(count=5):
    # 定义默认分类
    category = Category(name='Default')
    db.session.add(category)

    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        # 若随机生成分类名重复则回滚，取消添加到category的临时会话
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_post(count=25):
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(post)
    db.session.commit()


def fake_comment(count=150):
    for i in range(count):
        comment = Comment(
            author=fake.name(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            post=Post.query.get(random.randint(1, Post.query.count())),
            reviewed=True
        )
        db.session.add(comment)
    db.session.commit()

    salt = int(0.1*count)
    for i in range(salt):
        comment = Comment(
            author='一头特立独行的猪',
            from_admin=True,
            reviewed=True,
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()

    for i in range(salt):
        comment = Comment(
            author=fake.name(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            replied=Comment.query.get(random.randint(1, Comment.query.count())),
            post=Post.query.get(random.randint(1, Post.query.count())),
            reviewed=False
        )
        db.session.add(comment)
    db.session.commit()
    for i in range(salt):
        comment = Comment(
            author=fake.name(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            replied=Comment.query.get(random.randint(1, Comment.query.count())),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()
