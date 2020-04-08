import base64
from dateutil import parser
from datetime import datetime,timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import secretmanager
import smtplib
import textwrap

PROJECT_ID = 'alert-parsec-273000'
TEMPERATURE = 'temperature'
HUMIDITY = 'humidity'

def send_sms_message(event, context):
    event_data = base64.b64decode(event['data']).decode('utf-8')
    climate_type = TEMPERATURE if TEMPERATURE in event_data else HUMIDITY

    if check_sms_message_gap_valid(climate_type) == False:
        return ''

    try:
        email_address = 'gcp.sms.robot@gmail.com'
        password = get_sms_password()
        sms_gateway = '9207504346@tmomail.net'

        sms_message = MIMEMultipart()
        sms_message['From'] = email_address
        sms_message['To'] = sms_gateway
        sms_message['Subject'] = f'{climate_type.capitalize()} Threshold Reached'
        sms_message.attach(MIMEText(f'{event_data}', 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_address, password)
        server.sendmail(email_address, sms_gateway, sms_message.as_string())

        send_contact_attempt_history_to_firestore(climate_type, True, context.timestamp)
        print(f'Successfully sent SMS message to {sms_gateway}')
    except Exception as exception:
        send_contact_attempt_history_to_firestore(climate_type, False, context.timestamp)
        print(
            textwrap.dedent(
                f'''
                Failed to send SMS message to {sms_gateway}
                Error: {exception}
                '''
            )
        )
    finally:
        server.quit()

def check_sms_message_gap_valid(climate_type):
    if check_application_initialized() == False:
        set_credentials()

    firestore_client = firestore.client()
    contact_attempt_history_collection = firestore_client.collection('contact_attempt_history')
    contact_attempt_latest_successful_record = contact_attempt_history_collection \
        .where('climateType', '==', climate_type) \
        .where('contact_attempt_successful', '==', True) \
        .order_by('timestamp', direction=firestore.Query.DESCENDING) \
        .limit(1) \
        .stream()

    timestamp_record = [document.to_dict()['timestamp'] for document in contact_attempt_latest_successful_record][0]
    timestamp_now = datetime.now(timezone.utc)
    timestamp_difference = timestamp_now - timestamp_record
    timestamp_difference_hours = timestamp_difference.total_seconds() / 3600

    if timestamp_difference_hours < 1:
        return False

    return True

def send_contact_attempt_history_to_firestore(climate_type, status, context_timestamp):
    if check_application_initialized() == False:
        set_credentials()

    contact_attempt_history_document = {
        'climateType': climate_type,
        'contact_attempt_successful': status,
        'timestamp': parser.parse(context_timestamp)
    }

    firestore_client = firestore.client()
    contact_attempt_history_collection = firestore_client.collection('contact_attempt_history')
    contact_attempt_history_collection.add(contact_attempt_history_document)

    print(
        textwrap.dedent(
            f'''
            The following document has been added to the firestore:
            {contact_attempt_history_document}
            '''
        )
    )

def check_application_initialized():
    if firebase_admin._DEFAULT_APP_NAME in firebase_admin._apps:
        return True
    else:
        return False

def set_credentials():
    credential = credentials.ApplicationDefault()
    firebase_admin.initialize_app(
        credential,
        {
            'projectId': PROJECT_ID,
        }
    )

def get_sms_password():
    secret_manager_client = secretmanager.SecretManagerServiceClient()
    sms_password = secret_manager_client \
        .access_secret_version('projects/203517643656/secrets/sms/versions/1') \
        .payload \
        .data \
        .decode("utf-8")

    return sms_password

