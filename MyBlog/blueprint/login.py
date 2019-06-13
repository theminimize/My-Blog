from flask import Blueprint, render_template, flash, redirect, url_for
from MyBlog.forms import LoginForm
from flask_login import logout_user, login_required, login_user
from MyBlog.utils import redirect_back
from MyBlog.models import Admin
from flask_login import current_user


login_my = Blueprint('login', __name__)


@login_my.route('/login', methods=['GET', 'POST'])
def login():
    # 如果已登录，重定向回到主页
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()  # 返回查询的第一条记录
        if admin:
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)  # 登入用户
                flash('欢迎回来！', 'info')
                return redirect_back()
            flash("用户名或密码错误", 'warning')
        else:
            flash("没有管理员账户")
    return render_template('login/login.html', form=form)


@login_my.route('/logout')
@login_required
def logout():
    logout_user()
    flash('注销成功！', 'info')
    return redirect_back()
    # return redirect(url_for('blog.index'))