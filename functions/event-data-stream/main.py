import base64
from dateutil import parser
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import pubsub_v1
import textwrap

PROJECT_ID = 'alert-parsec-273000'
TEMPERATURE = 'temperature'
HUMIDITY = 'humidity'


def send_data_to_firestore(event, context):
    event_name = event['attributes']['event']
    event_data = int(base64.b64decode(event['data']).decode('utf-8'))
    threshold_reached = check_threshold_reached(event_name, event_data)

    if check_firestore_initialized() is False:
        set_firestore_credentials()

    climate_document = {
        'degreesFahrenheit' if event_name == TEMPERATURE else 'relativeHumidity': event_data,
        'thresholdReached': threshold_reached,
        'timestamp': parser.parse(event['attributes']['published_at'])
    }

    firestore_client = firestore.client()
    climate_collection = firestore_client.collection(event_name)
    climate_collection.add(climate_document)

    print(
        textwrap.dedent(
            f'''
            The following document has been added to the firestore:
            {climate_document}
            '''
        )
    )

    if threshold_reached is True:
        publish_threshold_event(
            craft_topic_message(
                event_name,
                event_data
            ),
            event_name
        )


def check_threshold_reached(event_name, event_data):
    if event_name == TEMPERATURE and (event_data > 75 or event_data < 65):
        return True
    elif event_name == HUMIDITY and (event_data > 60 or event_data < 30):
        return True
    else:
        return False


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


def publish_threshold_event(topic_message, event_name):
    topic_name = 'threshold'
    publisher_client = pubsub_v1.PublisherClient()
    publisher_client.publish(
        publisher_client.topic_path(PROJECT_ID, topic_name),
        topic_message
    )

    print(f'{event_name.capitalize()} threshold has been reached, publishing message to topic "{topic_name}"')


def craft_topic_message(event_name, event_data):
    if event_name == TEMPERATURE:
        return textwrap.dedent(
            f'''
            The current {event_name} is at {event_data} degrees fahrenheit.
            Please adjust the {event_name} to anywhere between 65 to 75 degrees fahrenheit.
            '''
        ).encode("utf-8")
    elif event_name == HUMIDITY:
        return textwrap.dedent(
            f'''
            The current {event_name} is at {event_data} percent relative humidity.
            Please adjust the {event_name} to anywhere between 30 to 60 percent relative humidity.
            '''
        ).encode("utf-8")
