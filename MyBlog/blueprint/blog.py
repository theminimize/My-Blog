from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from MyBlog.models import Post, Category, Comment
from MyBlog.forms import CommentForm
from MyBlog.extensions import db

blog_my = Blueprint('blog', __name__)


@blog_my.route('/')
def index():
    page = request.args.get('page', 1, type=int)    # 从查询字符串获取当前页数
    per_page = current_app.config['MYBLOG_POST_PER_PAGE']   #每页文章数
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/index.html', pagination=pagination, posts=posts)


@blog_my.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MYBLOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).order_by(Comment.timestamp.desc()).paginate(page, per_page=per_page)
    comments = pagination.items

    form = CommentForm()

    if form.validate_on_submit():
        author = form.name.data
        body = form.comment.data

        # 必须加入post=post参数，否则无法显示出对应评论，因为comment不知道自己属于哪一篇文章
        comment = Comment(
            author=author,
            body=body,
            post=post
        )
        replied_id = request.args.get('reply')
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment

        db.session.add(comment)
        db.session.commit()
        flash('评论成功！', 'success')
        return redirect(url_for('.show_post', post_id=post_id))
    return render_template('blog/post.html', post=post, pagination=pagination, comments=comments, form=form)


@blog_my.route('/reply/comment/<int:comment_id>', methods=['GET', 'POST'])
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if not comment.post.can_comments:
        flash('暂时不能回复，文章评论已关闭')
        return redirect(url_for('.show_post', post_id=comment.post.id))
    return redirect(url_for
                    ('.show_post', post_id=comment.post.id, reply=comment_id, author=comment.author) + '#comment-form')


@blog_my.route('/category/<int:category_id>', methods=['GET', 'POST'])
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MYBLOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)