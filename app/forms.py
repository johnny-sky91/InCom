from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Regexp

from app.models import User


class LoginForm(FlaskForm):
    username = StringField(_l('User'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember me'))
    submit = SubmitField(_l('Login'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('User'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Use different name'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('Use different email'))


class NewAreaForm(FlaskForm):
    new_area = StringField(_l('Enter a name for the new area'),
                           validators=[DataRequired(message=_l('Area name cannot be empty'))])
    submit = SubmitField(_l('Add new area'))


class NewComplaintForm(FlaskForm):
    order_number = StringField(_l('Order number'), validators=[Regexp(r'\b\d{5}\b',
                                                                      message=_l(
                                                                          'Wrong order number (only 5 digits)'))])
    product_type = SelectField(_l('Product type'), validators=[DataRequired()])
    model = SelectField(_l('Model'), validators=[DataRequired()])
    cause = SelectField(_l('Cause'), validators=[DataRequired()])
    detection_area = SelectField(_l('Detection area'), validators=[DataRequired()])
    description = TextAreaField(_l('Description'), validators=[DataRequired(message=_l('Description cannot be empty')),
                                                               Length(min=1, max=140)])
    submit = SubmitField(_l('Add complaint'))
