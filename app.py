import os
from flask import Flask, render_template, redirect, url_for, request, session, make_response
from azure.cosmos import CosmosClient, user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from flask_wtf.csrf import CSRFProtect
import hashlib
import uuid
import json
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.text import MIMEText
import jinja2
import requests
from datetime import datetime, timezone, timedelta

sender = "monitorpowietrza@gmail.com"

app = Flask(__name__)

scheduler = BackgroundScheduler()

url = 'https://monitor-db.documents.azure.com:443/'
key = os.environ.get('COSMOS_DB_KEY')
openApiKey = os.environ.get('OPEN_API_KEY')
password = os.environ.get('GMAIL_KEY')
client = CosmosClient(url, credential=key)
database_name = 'Monitor'
container_name = 'Users'
app.secret_key = '123AD##'
csrf = CSRFProtect(app)
aqi_descriptions = { "3" : "fair", "4": "poor", "5": "very poor"}
aqi_advice = { "3" : "limit outdoor activities", "4": "avoid outdoor activities", "5": "stay home"}

def generate_air_quality_email(recipient, location, air_quality_index):
    description = aqi_descriptions[str(air_quality_index)]
    advice = aqi_advice[str(air_quality_index)]
    template_html = """
    <html>
    <head></head>
    <body>
        <h2 style="color: red;">Air Quality Alert!</h2>
        <p>Dear {{ recipient }},</p>
        <p>We are writing to inform you that the air quality in {{ location }} is currently {{ description }}.</p>
        <p>The Air Quality Index (AQI) is {{ air_quality_index }}.</p>
        <p>Please take necessary precautions: {{ advice }}</p>
        <p>Stay safe!</p>
        <br>
        <p>Best regards,</p>
        <p>Your Air Quality Monitoring Team</p>
    </body>
    </html>
    """
    # Create a Jinja2 Template object
    template = jinja2.Template(template_html)
    return template.render(recipient=recipient, location=location, air_quality_index=air_quality_index, description=description,advice=advice)

def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())


def is_between_4_to_20_utc():
    current_time_utc = datetime.now(timezone.utc)
    current_hour = current_time_utc.hour

    return 4 <= current_hour < 21

def was_notified_recently(person):
    last_notification_str = person.get('lastNotification', None)

    if last_notification_str:
        last_notification_time = datetime.fromisoformat(last_notification_str)
        current_time_utc = datetime.now(timezone.utc)
        time_difference = current_time_utc - last_notification_time

        return time_difference < timedelta(minutes=30)
    else:
        return False

#@app.route('/notify')
def job():
    print("Scheduled job executed")
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    query = (f"SELECT * "
             f"FROM c WHERE c.notification = true")
    result = list(container.query_items(query=query, enable_cross_partition_query=True))
    if len(result) == 0:
        print('No notification needed')
        return
    #scheduler.remove_job('notification_job')
    for person in result:
        if not is_between_4_to_20_utc():
            print('Skipping sending notifications at night')
            continue
        if was_notified_recently(person):
            print('This person has been notified within last 4 hours')
            continue

        city = person['city']
        locationUrl = 'http://api.openweathermap.org/geo/1.0/direct?q='+city+'&limit=5&appid='+ openApiKey
        response = requests.get(locationUrl)
        json_data = response.json()
        lon = json_data[0]['lon']
        lat = json_data[0]['lat']
        # print(lon, lat)
        airUrl = 'http://api.openweathermap.org/data/2.5/air_pollution?lat=' + str(lat) + '&lon=' + str(lon) + '&appid='+openApiKey
        response = requests.get(airUrl)
        json_data = response.json()
        aqi = json_data['list'][0]['main']['aqi']
        if aqi < 3:
            continue

        email_body = generate_air_quality_email(person['name'], person['city'], aqi)
        send_email('Air quality alert',email_body,sender,[person['email']],password)

        person['lastNotification'] = datetime.now(timezone.utc).isoformat()
        container.upsert_item(person)
        print('Done')

def hearbeat_job():
    print('Heart beat')

scheduler.add_job(job, 'interval', seconds = 600, id='notification_job')
scheduler.add_job(hearbeat_job, 'interval', seconds = 5, id='hearbeat_job')
appHasRunBefore: bool = False

@app.before_request
def start_scheduler():
    print('Got request')
    global appHasRunBefore
    if not appHasRunBefore:
        print('Starting scheduler...')
        scheduler.start()
        appHasRunBefore = True

def get_user_by_email(email):
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    query = (f"SELECT c.id, c.name,c.lastname, c.email, c.passwordHash, c.phone, c.city, c.notification "
             f"FROM c WHERE c.email = '{email}'")
    result = list(container.query_items(query=query, enable_cross_partition_query=True))
    if len(result) == 0:
        return None

    return result[0]

def add_new_user(user):
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    container.upsert_item(user)


# @app.route('/mail')
# def mail():
#     print('Sending...')
#     send_email(body, subject, sender, recipients, password)
#     print('Sent')
#     return "Ok"

@app.route('/toggle')
def toggle():
    id = session['user']['id'];
    print(session['user'])
    key = session['user']['lastname'][0];
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    document = container.read_item(item=id, partition_key=key)
    document['notification'] = not document['notification']
    container.replace_item(item=id, body=document)
    return make_response('OK', 200)


@app.route('/')
def index():
    if('user' in session):
        return render_template("index.html", user=session['user'], openApiKey=openApiKey)

    return render_template("default.html", openApiKey=openApiKey)

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
    return render_template('default.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(location="/");

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
            passwordHash=hex_digest,
            notification=False
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
    def __init__(self, id, name, lastname, email, phone, city, passwordHash, notification, lastNotification=None):
        self.id = id
        self.name = name
        self.lastname = lastname
        self.email = email
        self.phone = phone
        self.city = city
        self.passwordHash = passwordHash
        self.notification = notification
        self.lastNotification = lastNotification

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'lastname': self.lastname,
            'email': self.email,
            'phone': self.phone,
            'city': self.city,
            'passwordHash': self.passwordHash,
            'partition': self.lastname[0],
            'notification': self.notification,
            'lastNotification': self.lastNotification
        }

    def to_json(self):
        return json.dumps(self.to_dict())