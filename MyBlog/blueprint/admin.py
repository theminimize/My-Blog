import os
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, send_from_directory
from flask_login import login_required, current_user

from MyBlog.forms import SettingForm, PostForm, CategoryForm
from MyBlog.extensions import db
from MyBlog.models import Post, Category, Comment
from MyBlog.utils import redirect_back, allowed_file
from flask_ckeditor import upload_success, upload_fail


admin_my = Blueprint('admin', __name__)


@admin_my.route('/setting', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingForm()

    # if和下面代码的顺序不能变
    if form.validate_on_submit():
        current_user.blog_title = form.blog_title.data
        current_user.name = form.name.data
        current_user.about = form.about.data
        db.session.commit()
        flash('博客设置已更新！', 'success')
        return redirect(url_for('blog.index'))

    form.blog_title.data = current_user.blog_title
    form.name.data = current_user.name
    form.about.data = current_user.about

    return render_template('admin/settings.html', form=form)


@admin_my.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category = Category.query.get(form.category.data)
        post = Post(title=title, body=body, category=category)
        db.session.add(post)
        db.session.commit()
        flash('新文章创建成功！', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)


@admin_my.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()

    if form.validate_on_submit():
        name = form.name.data
        category = Category(
            name=name
        )
        db.session.add(category)
        db.session.commit()
        flash("新建分类成功！", 'success')
        return redirect(url_for('.manage_category'))
    return render_template('admin/new_category.html', form=form)


@admin_my.route('/post/manage')
@login_required
def manage_post():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MYBLOG_MANAGE_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items

    return render_template('admin/manage_post.html', pagination=pagination, posts=posts, page=page )


@admin_my.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)

    if form.validate_on_submit():
        post.title = form.title.data
        post.category = Category.query.get(form.category.data)
        post.body = form.body.data
        db.session.commit()
        flash('文章已更新！', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))

    form.title.data = post.title
    form.category.data = post.category_id
    form.body.data = post.body

    return render_template('admin/edit_post.html', form=form)


@admin_my.route('post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('文章已删除.', 'success')
    return redirect_back()


@admin_my.route('/category/manage')
@login_required
def manage_category():
    return render_template('admin/manage_category.html')


@admin_my.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    form = CategoryForm()
    category = Category.query.get_or_404(category_id)
    # 默认分类不能更改
    if category_id == 1:
        flash('你不能修改默认分类', 'warning')
        return redirect(url_for('blog.index'))
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('分类更新成功！', 'success')
        return redirect(url_for('.manage_category'))

    form.name.data = category.name
    return render_template('admin/edit_category.html', form=form)


@admin_my.route('category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('不能删除默认分类！', 'warning')
        return redirect(url_for('blog.index'))
    # 特殊的删除分类方法，在Category类中定义
    category.delete()
    flash('删除分类成功！', 'success')
    return redirect(url_for('.manage_category'))


@admin_my.route('/comment/manages')
@login_required
def manage_comments():
    filter_rule = request.args.get('filter', 'all')  # 从查询字符串获取过滤规则
    page = request.args.get('page', 1, type=int)

    if filter_rule == 'unread':
        filtered_comments = Comment.query.filter_by(reviewed=False)
    elif filter_rule == 'admin':
        filtered_comments = Comment.query.filter_by(from_admin=True)
    else:
        filtered_comments = Comment.query

    # 筛选后的实例化对象进行排序
    pagination = filtered_comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['MYBLOG_MANAGE_COMMENT_PER_PAGE'])
    comments = pagination.items

    return render_template('admin/manage_comments.html',  pagination=pagination, comments=comments)


@admin_my.route('/set-comment/<int:post_id>', methods=['POST'])
@login_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_comments:
        post.can_comments = False
        flash('评论已关闭！', 'info')
    else:
        post.can_comments = True
        flash('评论已开启！', 'info')
    db.session.commit()
    return redirect(url_for('blog.show_post', post_id=post.id))


@admin_my.route('/comment/<int:comment_id>/approve', methods=['POST'])
@login_required
def approve_comments(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()
    flash('评论已读', 'success')
    return redirect_back()


@admin_my.route('/comment/<int:comment_id>/delete')
@login_required
def delete_comments(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除.', 'success')
    return redirect_back()


# 获取图片路径
@admin_my.route('/uploads/<path:filename>')
def get_image(filename):
    return send_from_directory(current_app.config['MYBLOG_UPLOAD_PATH'], filename)


# 上传图片
@admin_my.route('/upload', methods=['POST'])
def upload_image():
    # 创建uploads文件夹用于上传图片
    folder = os.path.exists(current_app.config['MYBLOG_UPLOAD_PATH'])
    if not folder:
            os.makedirs(current_app.config['MYBLOG_UPLOAD_PATH'])
    # 获取上传对象
    f = request.files.get('upload')
    # 若不符合规定文件名
    if not allowed_file(f.filename):
        return upload_fail('Image only!')
    f.save(os.path.join(current_app.config['MYBLOG_UPLOAD_PATH'], f.filename))
    # 设置图片url规则
    url = url_for('.get_image', filename=f.filename)
    return upload_success(url, f.filename)