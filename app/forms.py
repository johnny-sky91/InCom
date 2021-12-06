from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Regexp
from app.models import User, Types, Models, Causes


class LoginForm(FlaskForm):
    username = StringField('Użytkownik', validators=[DataRequired()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    remember_me = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj')


class RegistrationForm(FlaskForm):
    username = StringField('Użytkownik', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    password2 = PasswordField('Powtórz hasło', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Zarejestruj się')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Użyj innej nazwy')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Użyj innego adresu')


class NewRegistrationForm(FlaskForm):
    # TODO docelowo pobrane z DB
    areas = ['Piła', 'Laser 3D', 'Galanteria', 'Spawalnia']

    types_query = Types.query.with_entities(Types.product_type)
    types = [item for t in types_query for item in t]

    models_query = Models.query.with_entities(Models.product_model)
    models = [item for t in models_query for item in t]

    causes_query = Causes.query.with_entities(Causes.cause_type)
    causes = [item for t in causes_query for item in t]

    order_number = StringField('Numer zlecenia', validators=[Regexp(r'\b\d{5}\b',
                                                                    message='Błędny nr zlecenia (tylko 5 cyfr)')])
    product_type = SelectField('Rodzaj', choices=types, validators=[DataRequired()])
    model = SelectField('Model', choices=models, validators=[DataRequired()])
    cause = SelectField('Przyczyna', choices=causes, validators=[DataRequired()])
    detection_area = SelectField('Obszar wykrycia', choices=areas, validators=[DataRequired()])
    description = TextAreaField('Opis', validators=[DataRequired(message='Opis nie może być pusty'),
                                                    Length(min=1, max=140)])
    submit = SubmitField('Zapisz RW')
