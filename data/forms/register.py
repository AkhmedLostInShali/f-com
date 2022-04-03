from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, IntegerField, SubmitField, EmailField, FileField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    nickname = StringField('Nickname', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ExtensionForm(FlaskForm):
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    portrayal = StringField('Portrayal', validators=[DataRequired()])
    speciality = StringField('Speciality', validators=[DataRequired()])
    avatar = FileField('Avatar', validators=[DataRequired()])
    city_from = StringField('City from', validators=[DataRequired()])
    submit = SubmitField('Submit')