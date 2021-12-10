from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Regexp
from app.models import User, Types, Models, Causes


class LoginForm(FlaskForm):
    username = StringField('User', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('User', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Use different name')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Use different email')


class NewAreaForm(FlaskForm):
    new_area = StringField('Enter a name for the new area',
                           validators=[DataRequired(message='Area name cannot be empty')])
    submit = SubmitField('Add new area')


class NewComplaintForm(FlaskForm):
    types_query = Types.query.with_entities(Types.product_type)
    types = [item for t in types_query for item in t]

    models_query = Models.query.with_entities(Models.product_model)
    models = [item for t in models_query for item in t]

    causes_query = Causes.query.with_entities(Causes.cause_type)
    causes = [item for t in causes_query for item in t]

    order_number = StringField('Order number', validators=[Regexp(r'\b\d{5}\b',
                                                                  message='Wrong order number (only 5 digits)')])
    product_type = SelectField('Product type', choices=types, validators=[DataRequired()])
    model = SelectField('Model', choices=models, validators=[DataRequired()])
    cause = SelectField('Cause', choices=causes, validators=[DataRequired()])
    detection_area = SelectField('Detection area', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(message='Description cannot be empty'),
                                                           Length(min=1, max=140)])
    submit = SubmitField('Add complaint')
