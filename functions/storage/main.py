import csv
from datetime import datetime, timedelta
from dateutil import parser
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import pubsub_v1
from google.cloud import storage

PROJECT_ID = 'alert-parsec-273000'
TEMPERATURE = 'temperature'
HUMIDITY = 'humidity'
TIMESTAMP = 'timestamp'
TODAY = datetime.today().strftime('%Y-%m-%d')
BUCKET_NAME = 'climate-data-files'
CLIMATE_DATA_FILE_NAME = 'climate_data_aggregate.csv'


def send_climate_data_file_to_storage(event, context):
    append_climate_averages_to_file()
    upload_climate_data_file(CLIMATE_DATA_FILE_NAME)
    publish_updated_climate_file()


def publish_updated_climate_file():
    topic_name = 'graph'
    publisher_client = pubsub_v1.PublisherClient()
    publisher_client.publish(
        publisher_client.topic_path(PROJECT_ID, topic_name),
        'Updated climate date file'
    )

    print(f'Climate data file has been updated for the day, publishing message to topic "{topic_name}"')


def append_climate_averages_to_file():
    temperature_data = get_climate_data_today(TEMPERATURE)
    humidity_data = get_climate_data_today(HUMIDITY)
    temperature_average = calculate_average(temperature_data)
    humidity_average = calculate_average(humidity_data)

    if check_climate_data_file_exists() is False:
        with open(CLIMATE_DATA_FILE_NAME, 'w') as climate_data_file:
            upload_climate_data_file(climate_data_file)

    climate_data_file_path = download_latest_climate_data_file()

    with open(climate_data_file_path, mode='a') as climate_data_file:
        writer = csv.writer(climate_data_file, delimiter=',')
        writer.writerow([TODAY, temperature_average, humidity_average])


def calculate_average(numbers):
    return sum(numbers)/len(numbers)


def get_climate_data_today(climate_type):
    tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    start = parser.parse(f'{TODAY}T11:00:00.000Z')
    end = parser.parse(f'{tomorrow}T02:00:00.000Z')

    if check_firestore_initialized() is False:
        set_firestore_credentials()

    firestore_client = firestore.client()
    climate_collection = firestore_client.collection(climate_type)
    climate_today_documents = climate_collection \
        .order_by(TIMESTAMP, direction=firestore.Query.DESCENDING) \
        .start_at({TIMESTAMP: start}) \
        .end_at({TIMESTAMP: end}) \
        .stream()

    return [document.to_dict()[climate_type] for document in climate_today_documents]


def download_latest_climate_data_file():
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(CLIMATE_DATA_FILE_NAME)

    return blob.download_to_filename(CLIMATE_DATA_FILE_NAME)


def upload_climate_data_file(file_to_upload):
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(file_to_upload)

    blob.upload_from_filename(file_to_upload)


def check_climate_data_file_exists():
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(BUCKET_NAME)

    if CLIMATE_DATA_FILE_NAME not in blobs:
        return False

    return True


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
