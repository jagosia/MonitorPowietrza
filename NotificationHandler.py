from DatabaseHandler import get_users_to_notify, upsert_item
from MailHandler import generate_air_quality_email, send_email
import requests
import os
from datetime import datetime, timezone, timedelta

open_api_key = os.environ.get('OPEN_API_KEY')

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


def job():
    print("Scheduled job executed")
    result = get_users_to_notify()
    if len(result) == 0:
        print('No notification needed')
        return
    for person in result:
        if not is_between_4_to_20_utc():
            print('Skipping sending notifications at night')
            continue
        if was_notified_recently(person):
            print('This person has been notified within last 4 hours')
            continue

        city = person['city']
        locationUrl = 'http://api.openweathermap.org/geo/1.0/direct?q=' + city + '&limit=5&appid=' + open_api_key
        response = requests.get(locationUrl)
        json_data = response.json()
        lon = json_data[0]['lon']
        lat = json_data[0]['lat']
        airUrl = 'http://api.openweathermap.org/data/2.5/air_pollution?lat=' + str(lat) + '&lon=' + str(
            lon) + '&appid=' + open_api_key
        response = requests.get(airUrl)
        json_data = response.json()
        aqi = json_data['list'][0]['main']['aqi']
        if aqi < 3:
            continue

        email_body = generate_air_quality_email(person['name'], person['city'], aqi)
        send_email('Air quality alert', email_body, [person['email']])

        person['lastNotification'] = datetime.now(timezone.utc).isoformat()
        upsert_item(person)
        print('Done')

def heartbeat_job():
    print('Heart beat')