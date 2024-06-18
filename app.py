import os
import hashlib
import uuid
import requests
from flask import Flask, render_template, redirect, url_for, request, session, make_response
from flask_wtf.csrf import CSRFProtect
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException, Depends
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from a2wsgi import ASGIMiddleware
from DatabaseHandler import get_user_by_email, get_user_document_by_id, replace_document, add_new_user
from LoginForm import LoginForm
from RegistrationForm import RegistrationForm
from User import User
from auth import create_access_token, verify_token
from LoginData import LoginData
from NotificationHandler import job, heartbeat_job

fast_app = FastAPI()
app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/monitor': app,
    '/api': ASGIMiddleware(fast_app),
})

scheduler = BackgroundScheduler()
open_api_key = os.environ.get('OPEN_API_KEY')
app.secret_key = '123AD##'
csrf = CSRFProtect(app)

scheduler.add_job(job, 'interval', seconds=600, id='notification_job')
scheduler.add_job(heartbeat_job, 'interval', seconds=5, id='heartbeat_job')
appHasRunBefore: bool = False

@app.before_request
def start_scheduler():
    print('Got request')
    global appHasRunBefore
    if not appHasRunBefore:
        print('Starting scheduler...')
        scheduler.start()
        appHasRunBefore = True


@fast_app.post("/login")
def login(data: LoginData):
    hash_object = hashlib.sha1(data.password.encode())
    password_hash = hash_object.hexdigest()
    user_data = get_user_by_email(data.login)
    if user_data and password_hash == user_data['passwordHash']:
        token = create_access_token({"sub": data.login})
        return {"token": token}
    else:
        raise HTTPException(status_code=400, detail="Invalid login or password")

@fast_app.get("/air/{city}")
def city(city: str, token: dict = Depends(verify_token)):
    location_url = 'https://api.openweathermap.org/geo/1.0/direct?q=' + city + '&limit=5&appid=' + open_api_key
    response = requests.get(location_url)
    json_data = response.json()
    lon = json_data[0]['lon']
    lat = json_data[0]['lat']
    air_url = 'https://api.openweathermap.org/data/2.5/air_pollution?lat=' + str(lat) + '&lon=' + str(
        lon) + '&appid=' + open_api_key
    response = requests.get(air_url)
    json_data = response.json()
    return {"air": json_data}

@app.route('/toggle')
def toggle():
    user_id = session['user']['id']
    partition_key = session['user']['lastname'][0]
    document = get_user_document_by_id(user_id, partition_key)
    document['notification'] = not document['notification']
    replace_document(user_id, document)
    return make_response('OK', 200)


@app.route('/')
def index():
    if 'user' in session:
        return render_template("index.html", user=session['user'], openApiKey=open_api_key)

    return render_template("default.html", openApiKey=open_api_key)


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
    return redirect(location="/")


@app.route('/register')
def register():
    return render_template("register.html", form=RegistrationForm())


@app.route('/register', methods=['POST'])
def register_post():
    form = RegistrationForm()
    hash_object = hashlib.sha1(form.password.data.encode())
    hex_digest = hash_object.hexdigest()

    valid = form.validate_on_submit()
    if valid:
        new_user = User(
            id=str(uuid.uuid4()),
            name=form.name.data,
            lastname=form.lastname.data,
            email=form.email.data,
            phone=form.phone.data,
            city=form.city.data,
            passwordHash=hex_digest,
            notification=False
        )

        add_new_user(new_user.to_dict())
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run()
