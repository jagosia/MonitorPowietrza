from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class RegistrationForm(FlaskForm):
    name = StringField('Imię', validators=[DataRequired(message="To pole jest wymagane"), Length(min=2, max=50, message="Wymagana długość od 2 do 50 znaków")])
    lastname = StringField('Nazwisko', validators=[DataRequired(message="To pole jest wymagane"), Length(min=2, max=50, message="Wymagana długość od 2 do 50 znaków")])
    email = StringField('Email', validators=[DataRequired(message="To pole jest wymagane"), Email()])
    phone = StringField('Telefon', validators=[DataRequired(message="To pole jest wymagane"), Length(min=9, max=15, message="Wymagana długość od 2 do 15 znaków")])
    city = StringField('Miasto', validators=[DataRequired(message="To pole jest wymagane"), Length(min=2, max=50, message="Wymagana długość od 2 do 50 znaków")])

    password = PasswordField('Hasło', validators=[
        DataRequired(message="To pole jest wymagane"),
        Length(min=6, message='Hasło musi mieć przynajmniej 6 znaków.')
    ])
    password2 = PasswordField('Powtórz hasło', validators=[
        DataRequired(message="To pole jest wymagane"),
        EqualTo('password', message='Hasła muszą być identyczne.')
    ])

    @staticmethod
    def validate_phone(field):
        if not field.data.isdigit():
            raise ValidationError('Numer telefonu może zawierać tylko cyfry.')