import os
import smtplib
import jinja2

from email.mime.text import MIMEText

aqi_descriptions = {"3": "fair", "4": "poor", "5": "very poor"}
aqi_advice = {"3": "limit outdoor activities", "4": "avoid outdoor activities", "5": "stay home"}
password = os.environ.get('GMAIL_KEY')
sender = "monitorpowietrza@gmail.com"


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
    return template.render(recipient=recipient, location=location, air_quality_index=air_quality_index,
                           description=description, advice=advice)


def send_email(subject, body, recipients):
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())