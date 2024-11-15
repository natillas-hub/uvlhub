from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.validators import Optional, NumberRange


class ExploreForm(FlaskForm):
    min_features = IntegerField('Minimum number of features', 
                              validators=[Optional(), NumberRange(min=0)])
    max_features = IntegerField('Maximum number of features', 
                              validators=[Optional(), NumberRange(min=0)])
    min_products = IntegerField('Minimum number of products', 
                              validators=[Optional(), NumberRange(min=0)])
    max_products = IntegerField('Maximum number of products', 
                              validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Submit')
