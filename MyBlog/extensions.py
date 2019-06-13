
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
ckeditor = CKEditor()
login = LoginManager()
csrf = CSRFProtect()


# 用户加载函数,接收用户Id作为参数，返回对应的用户对象
@login.user_loader
def load_user(user_id):
    from MyBlog.models import Admin
    user = Admin.query.get(int(user_id))
    return user