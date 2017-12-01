import re
from flask_wtf import FlaskForm
from wtforms import TextField, SelectMultipleField, SelectField, BooleanField,\
                    IntegerField, DecimalField, FloatField, HiddenField, \
                    IntegerField, TextAreaField, PasswordField, SubmitField, validators, \
                    ValidationError

class LoginForm(FlaskForm):
    class Meta: csrf = False

    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class PasswordChangeForm(FlaskForm):
    password = PasswordField('New Password', [validators.Required()])
    password_verify = PasswordField('Password Again', [validators.Required(), validators.EqualTo('password')])
    submit = SubmitField('Change Password')

class LostPassForm(FlaskForm):
    username = TextField('Username', [validators.Required()])
    submit = SubmitField('Recover Password')

class UserRegisterBaseForm(FlaskForm):
    password = PasswordField('Password', [validators.Required()])
    firstname = TextField('First Name', [validators.Required()])
    lastname = TextField('Last Name', [validators.Required()])
    email = TextField('Email Address', [validators.Required()])
    submit = SubmitField('Register', [validators.Required()])

class OAuthUserRegisterForm(UserRegisterBaseForm):
    username = HiddenField('Username', [validators.Required()])
    password = HiddenField('Password', [validators.Required()])

class UserRegisterForm(UserRegisterBaseForm):
    def validate_password(form, field):
        password = field.data
        if len(password) < 6 or \
            not re.search(r'[A-Za-z]', password) or \
            not re.search(r'\d', password) or \
            not re.search(r'\W', password):
            raise ValidationError('Must be at least 6 characters with a letter, number, and symbol.')
