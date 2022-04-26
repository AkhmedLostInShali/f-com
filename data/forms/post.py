from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed


class PublicationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    photo = FileField('Load photo', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')