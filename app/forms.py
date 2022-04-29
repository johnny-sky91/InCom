from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Regexp

from app.models import User


class LoginForm(FlaskForm):
    username = StringField(lazy_gettext('User'), validators=[DataRequired()])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()])
    remember_me = BooleanField(lazy_gettext('Remember me'))
    submit = SubmitField(lazy_gettext('Login'))


class RegistrationForm(FlaskForm):
    username = StringField(lazy_gettext('User'), validators=[DataRequired()])
    email = StringField(lazy_gettext('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()])
    password2 = PasswordField(lazy_gettext('Repeat password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(lazy_gettext('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(lazy_gettext('Use different name'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(lazy_gettext('Use different email'))


class NewAreaForm(FlaskForm):
    new_area = StringField(lazy_gettext('Enter a name for the new area'),
                           validators=[DataRequired(message=lazy_gettext('Area name cannot be empty'))])
    submit = SubmitField(lazy_gettext('Add new area'))


class NewComplaintForm(FlaskForm):
    order_number = StringField(lazy_gettext('Order number'), validators=[Regexp(r'\b\d{5}\b', message=lazy_gettext(
        'Wrong order number (only 5 digits)'))])
    product_type = SelectField(lazy_gettext('Product type'), validators=[DataRequired()])
    model = SelectField(lazy_gettext('Model'), validators=[DataRequired()])
    cause = SelectField(lazy_gettext('Cause'), validators=[DataRequired()])
    detection_area = SelectField(lazy_gettext('Detection area'), validators=[DataRequired()])
    description = TextAreaField(lazy_gettext('Description'),
                                validators=[DataRequired(message=lazy_gettext('Description cannot be empty')),
                                            Length(min=1, max=140)])
    submit = SubmitField(lazy_gettext('Add complaint'))
