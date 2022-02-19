from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, DecimalField
from wtforms.validators import Length, DataRequired, NumberRange


class PaymentForm(FlaskForm):
    """Form for redirection to pay
    Contains:
        amount - amount of money to pay
        currency - currency for payment
        description - description of payment
        """
    amount = DecimalField(label='Enter amount: ', validators=[DataRequired(), NumberRange(min=1, max=9999999999)])
    currency = SelectField(label='Choose currency: ', choices=[
        ('978', 'EUR'),
        ('840', 'USD'),
        ('643', 'RUB')])
    description = TextAreaField(label='Enter description: ', default='Test invoice')
    submit = SubmitField(label='Submit')
