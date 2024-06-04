import os
from flask import Flask, render_template, redirect, url_for, request, session
from azure.cosmos import CosmosClient
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from flask_wtf.csrf import CSRFProtect
import hashlib
import uuid
import json

app = Flask(__name__)

url = 'https://monitor-db.documents.azure.com:443/'
key = os.environ.get('COSMOS_DB_KEY')
client = CosmosClient(url, credential=key)
database_name = 'Monitor'
container_name = 'Users'
app.secret_key = '123AD##'
csrf = CSRFProtect(app)

#TODO: Do usunięcia
def format_user_data(user_data):
    name = user_data.get('name', '')
    surname = user_data.get('surname', '')
    return f'Witaj {name} {surname}'

def get_user_by_email(email):
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    query = (f"SELECT c.id, c.name,c.surname, c.email, c.passwordHash, c.phone "
             f"FROM c WHERE c.email = '{email}'")
    result = list(container.query_items(query=query, enable_cross_partition_query=True))
    if len(result) == 0:
        return None

    return result[0]

def add_new_user(user):
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    container.upsert_item(user)


@app.route('/')
def index():
    user = session['user']

    return render_template("index.html", user=user)


@app.route('/login')
def login():
    return render_template("login.html", form=LoginForm())

@app.route('/login', methods=['POST'])
def login_post():
    form = LoginForm()
    if request.method == 'POST':
        hash_object = hashlib.sha1(form.password.data.encode())
        password_hash = hash_object.hexdigest()
        user_data = get_user_by_email(form.email.data)
        if user_data and password_hash == user_data['passwordHash']:
            session['user'] = user_data
            return redirect(url_for('index'))
        else:
            return render_template('login.html', form)
    return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template("index.html")

@app.route('/register')
def register():
    #TODO: stylowanie błędów w formularzu
    return render_template("register.html", form=RegistrationForm())

@app.route('/register', methods=['POST'])
def register_post():
    form = RegistrationForm()
    hash_object = hashlib.sha1(form.password.data.encode())
    hex_digest = hash_object.hexdigest()

    valid = form.validate_on_submit()
    #TODO: unikalność maila
    if valid:
        user = User(
            id=str(uuid.uuid4()),
            name=form.name.data,
            lastname=form.lastname.data,
            email=form.email.data,
            phone=form.phone.data,
            city=form.city.data,
            passwordHash=hex_digest
        )

        add_new_user(user.to_dict())
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run()

class RegistrationForm(FlaskForm):
    name = StringField('Imię', validators=[DataRequired(), Length(min=2, max=50)])
    lastname = StringField('Nazwisko', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Telefon', validators=[DataRequired(), Length(min=9, max=15)])
    city = StringField('Miasto', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Hasło', validators=[
        DataRequired(),
        Length(min=6, message='Hasło musi mieć przynajmniej 6 znaków.')
    ])
    password2 = PasswordField('Powtórz hasło', validators=[
        DataRequired(),
        EqualTo('password', message='Hasła muszą być identyczne.')
    ])

    def validate_phone(form, field):
        if not field.data.isdigit():
            raise ValidationError('Numer telefonu może zawierać tylko cyfry.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[
        DataRequired(),
        Length(min=6, message='Hasło musi mieć przynajmniej 6 znaków.')
    ])

class User:
    def __init__(self, id, name, lastname, email, phone, city, passwordHash):
        self.id = id
        self.name = name
        self.lastname = lastname
        self.email = email
        self.phone = phone
        self.city = city
        self.passwordHash = passwordHash

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'lastname': self.lastname,
            'email': self.email,
            'phone': self.phone,
            'city': self.city,
            'passwordHash': self.passwordHash,
            'partition': self.lastname[0]
        }

    def to_json(self):
        return json.dumps(self.to_dict())