from wtforms import SelectField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, SelectMultipleField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, InputRequired, Length, AnyOf
import datetime
from models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    remember = BooleanField('Remember me')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'That username is taken. Please choose a different one.')


class ChangePasswordForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired()])
    current_password = PasswordField('Current Password',
                                     validators=[DataRequired()])
    new_password = PasswordField('New Password',
                                 validators=[DataRequired()])
    submit = SubmitField('Change Password')
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['jpg', 'png', 'jpeg'])])


class AttendanceForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    status = SelectField('Status', choices=['Present', 'AL', 'AO', 'CCL', 'DA', 'EFO', 'FPUL', 'HL', 'MA', 'MC', 'MO',
                         'MRL', 'OC', 'OFF', 'OL', 'OML', 'PCL', 'PL', 'RL', 'RSI', 'RSO', 'SHRO', 'UL', 'WFH'], validators=[DataRequired()])
    submit = SubmitField('Submit')


class TaskForm(FlaskForm):
    task_name = StringField('Task Name', validators=[DataRequired()])
    assigned_to = SelectField('Assign To', validators=[DataRequired()])
    submit = SubmitField('Assign Task')


class UpdatePictureForm(FlaskForm):
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update Picture')


class OffBalanceForm(FlaskForm):
    usernames = SelectMultipleField('Usernames', validators=[DataRequired()])
    off_balance = IntegerField(
        'Off Balance Change', validators=[DataRequired()])
    add = SubmitField('Add Off')
    subtract = SubmitField('Subtract Off')
