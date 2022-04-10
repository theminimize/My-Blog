from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length
from flask_ckeditor import CKEditorField
from MyBlog.models import Category


# 登录表单
class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 32)])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')


# 评论表单
class CommentForm(FlaskForm):
    name = StringField('昵称', validators=[DataRequired()])
    comment = TextAreaField('评论内容', validators=[DataRequired(), Length(1, 256)])
    submit = SubmitField('发布评论')


# 设置表单
class SettingForm(FlaskForm):
    blog_title = StringField('博客名称', validators=[DataRequired()])
    name = StringField('昵称', validators=[DataRequired(), Length(1, 20)])
    about = TextAreaField('关于', validators=[DataRequired()])
    submit = SubmitField('更新')


# 新增文章
class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired()])
    category = SelectField('分类', coerce=int, default=1)
    body = CKEditorField('正文', validators=[DataRequired()])
    submit = SubmitField('提交')

    # 文章表单中分类下拉列表的选项必须是包含两个元素元组的列表,元组分别包含选项值和选项标签,
    # 使用分类id作为选项值,分类名称作为选项标签,通过迭代Category.query.order_by(Category.name).all()返回分类记录实现
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.order_by(Category.name).all()]


# 新增分类
class CategoryForm(FlaskForm):
    name = StringField('分类名', validators=[DataRequired()])
    submit = SubmitField('提交')

    # 表单自定义行内验证器，用于验证分类名重复
    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError('分类名已存在')