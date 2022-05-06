from flask_wtf import FlaskForm
from wtforms import SearchField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    to_find = SearchField('Write here')
    submit = SubmitField('Search')
