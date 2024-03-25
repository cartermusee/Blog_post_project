"""module for all forms"""
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField,PasswordField, SubmitField,BooleanField,TextAreaField
from flask_wtf.file import FileAllowed,FileField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from flaskblog.modules import User



class Registration(FlaskForm):
    """class for the regitration form"""
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=30)])

    email = StringField("Email",validators=[DataRequired(),Email()])

    password = PasswordField("Password",validators=[DataRequired()])

    Confirmpassword = PasswordField("Confrim Password",validators=[DataRequired(),EqualTo('password')])

    submit = SubmitField("Sign up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("That username is taken")
    
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("That email is taken")

class Login(FlaskForm):
    """class for login form"""
    email = StringField("Email",validators=[DataRequired(),Email()])

    password = PasswordField("Password",validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")



class AccountUpdateForm(FlaskForm):
    """class for updating the account"""
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=30)])

    email = StringField("Email",validators=[DataRequired(),Email()])
    picture = FileField('update profile picture',validators=[FileAllowed(['png','jpg'])])
    submit = SubmitField("Update Account")

    def validate_username(self, username):
        """method to validate a useranme"""
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("That username is taken")
    
    def validate_email(self, email):
         """method to validate email when loging in"""
         if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError("That email is taken")


class PostForm(FlaskForm):
    """class for ceating a post"""
    title = StringField('Title',validators=[DataRequired()])
    content = TextAreaField('Content',validators=[DataRequired()])
    submit = SubmitField('Post')

class RequestResetForm(FlaskForm):
    """class for reset token form"""
    email = StringField("Email",validators=[DataRequired(),Email()])
    submit = SubmitField('Password Reset')
    def validate_email(self, email):
        """email validation to get the request"""
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')
class ResetPassword(FlaskForm):
    """password reset form"""
    password = PasswordField("Password",validators=[DataRequired()])
    Confirmpassword = PasswordField("Confrim Password",validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Reset Password')

class SearchForm(FlaskForm):
    searched = StringField("searched", validators=[DataRequired()])
    submit = SubmitField("Search")