from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class NewRegistrationForm(FlaskForm):
    types = ['BS', 'BU', 'F']
    models = ['P82', 'P102', 'PP002', 'P302']
    causes = ['Porysowanie', 'Wada materiału']
    departments = ['Piła', 'Laser 3D', 'Galanteria', 'Spawalnia']
    type = SelectField('Rodzaj', choices=types, validators=[DataRequired()])
    model = SelectField('Model', choices=models, validators=[DataRequired()])
    cause = SelectField('Przyczyna', choices=causes, validators=[DataRequired()])
    detection_department = SelectField('Dział wykrycia', choices=departments, validators=[DataRequired()])
    # Numer zlecenia
    # Dział wykrycia
    # Opis