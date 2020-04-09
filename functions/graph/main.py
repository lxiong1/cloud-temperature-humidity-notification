# import base64
import csv
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
# import pandas
# import plotly

PROJECT_ID = 'alert-parsec-273000'
TEMPERATURE = 'temperature'
HUMIDITY = 'humidity'


def send_climate_data_file_to_storage(event, context):
    # event_data = int(base64.b64decode(event['data']).decode('utf-8'))
    today = datetime.today().strftime('%Y-%m-%d')

    if check_firestore_initialized() is False:
        set_firestore_credentials()

    firestore_client = firestore.client()
    temperature_collection = firestore_client.collection(TEMPERATURE)
    temperature_collection.where('timestamp', 'array-contains', today).stream()

    humidity_collection = firestore_client.collection(HUMIDITY)
    humidity_collection.where('timestamp', 'array-contains', today).stream()

    with open(f'{today}_climate_data_daily_aggregate.csv', mode='a') as climate_data_file:
        writer = csv.writer(climate_data_file, delimiter=',')
        writer.writerow([today, '', ''])


def download_climate_data_file():
    print()


def check_firestore_initialized():
    if firebase_admin._DEFAULT_APP_NAME in firebase_admin._apps:
        return True
    else:
        return False


def set_firestore_credentials():
    credential = credentials.ApplicationDefault()
    firebase_admin.initialize_app(
        credential,
        {
            'projectId': PROJECT_ID,
        }
    )
