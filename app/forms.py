from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField
from wtforms.validators import DataRequired, NumberRange, Optional, Length
from datetime import date  # Import the date class

class HomePageForm(FlaskForm):
    name = StringField('Food Name', validators=[DataRequired(), Length(min=1, max=128)])
    quantity = IntegerField('Quantity', default=1, validators=[DataRequired(), NumberRange(min=1)])
    date = DateField('Date', default=date.today, validators=[DataRequired()])
    expiryDate = DateField('Expiry Date', validators=[Optional()])