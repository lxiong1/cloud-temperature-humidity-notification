from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import pubsub_v1
from google.cloud import storage
from pytz import timezone

PROJECT_ID = "alert-parsec-273000"
TEMPERATURE = "temperature"
HUMIDITY = "humidity"
TIMESTAMP = "timestamp"
NOW_CDT = datetime.now(timezone("America/Chicago"))
DATE_TODAY = NOW_CDT.strftime("%Y-%m-%d")
BUCKET_NAME = "climate-data-files"
CLIMATE_DATA_FILE_NAME = "climate_data_aggregate.csv"

storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)
blob = bucket.blob(CLIMATE_DATA_FILE_NAME)


def send_climate_data_file_to_storage(event, context):
    temperature_average = calculate_average(get_climate_data_today(TEMPERATURE))
    humidity_average = calculate_average(get_climate_data_today(HUMIDITY))

    if blob.exists() is False:
        print(
            f"Cannot aggregate data on {CLIMATE_DATA_FILE_NAME} because it does not exist in bucket {BUCKET_NAME}"
        )
        return ""

    climate_data = blob.download_as_string().decode("utf-8")

    if DATE_TODAY in climate_data:
        print(f"Date {DATE_TODAY} is already in the climate data file")
        return ""

    blob.upload_from_string(
        f"{climate_data}\n{DATE_TODAY},{temperature_average},{humidity_average}"
    )

    print(
        f"File {CLIMATE_DATA_FILE_NAME} has been uploaded and stored in bucket {BUCKET_NAME}"
    )

    publish_updated_climate_data_file_event()


def publish_updated_climate_data_file_event():
    topic_name = "graph"
    publisher_client = pubsub_v1.PublisherClient()
    publisher_client.publish(
        publisher_client.topic_path(PROJECT_ID, topic_name),
        "Updated climate data file".encode("utf-8"),
    )

    print(
        f'Climate data file has been updated for the day, publishing message to topic "{topic_name}"'
    )


def calculate_average(numbers):
    return round(sum(numbers) / len(numbers))


def get_climate_data_today(climate_type):
    start = datetime(NOW_CDT.year, NOW_CDT.month, NOW_CDT.day, 0, 0, 0)
    end = datetime(NOW_CDT.year, NOW_CDT.month, NOW_CDT.day, 23, 59, 59)

    if check_firestore_initialized() is False:
        set_firestore_credentials()

    firestore_client = firestore.client()
    climate_collection = firestore_client.collection(climate_type)
    climate_today_documents = (
        climate_collection.where(TIMESTAMP, ">=", start)
        .where(TIMESTAMP, "<=", end)
        .stream()
    )

    climate_key = (
        "degreesFahrenheit" if climate_type == TEMPERATURE else "relativeHumidity"
    )
    climate_data = [
        document.to_dict()[climate_key] for document in climate_today_documents
    ]

    return climate_data


def check_firestore_initialized():
    if firebase_admin._DEFAULT_APP_NAME in firebase_admin._apps:
        return True
    else:
        return False


def set_firestore_credentials():
    credential = credentials.ApplicationDefault()
    firebase_admin.initialize_app(credential, {"projectId": PROJECT_ID})
