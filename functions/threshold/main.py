import base64
from dateutil import parser
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import secretmanager
from pytz import timezone
import smtplib
import textwrap

PROJECT_ID = "alert-parsec-273000"
TEMPERATURE = "temperature"
HUMIDITY = "humidity"
CDT_TIMEZONE = timezone("America/Chicago")
NOW_CDT = datetime.now(CDT_TIMEZONE)
DATE_TODAY = NOW_CDT.strftime("%Y-%m-%d")


def send_sms_message(event, context):
    if check_valid_time_range() is False:
        print("SMS message will not be sent after 9 PM or before 6 AM")
        return ""

    event_data = base64.b64decode(event["data"]).decode("utf-8")
    climate_type = TEMPERATURE if TEMPERATURE in event_data else HUMIDITY

    if check_sms_message_within_valid_gap(climate_type) is False:
        print(
            f"SMS message for {climate_type} has already been sent within the past hour"
        )
        return ""

    try:
        email_address = "gcp.sms.robot@gmail.com"
        password = get_sms_password()
        sms_gateway = "9207504346@tmomail.net"

        sms_message = MIMEMultipart()
        sms_message["From"] = email_address
        sms_message["To"] = sms_gateway
        sms_message["Subject"] = f"{climate_type.capitalize()} Threshold Reached"
        sms_message.attach(MIMEText(f"{event_data}", "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_address, password)
        server.sendmail(email_address, sms_gateway, sms_message.as_string())

        send_contact_attempt_history_to_firestore(climate_type, True, context.timestamp)
        print(f"Successfully sent SMS message to {sms_gateway}")
    except Exception as exception:
        send_contact_attempt_history_to_firestore(
            climate_type, False, context.timestamp
        )
        print(
            textwrap.dedent(
                f"""
                Failed to send SMS message to {sms_gateway}
                Error: {exception}
                """
            )
        )
    finally:
        server.quit()


def send_contact_attempt_history_to_firestore(climate_type, status, context_timestamp):
    if check_firestore_initialized() is False:
        set_firestore_credentials()

    contact_attempt_history_document = {
        "climateType": climate_type,
        "contactAttemptSuccessful": status,
        "timestamp": parser.parse(context_timestamp),
    }

    firestore_client = firestore.client()
    contact_attempt_history_collection = firestore_client.collection(
        "contact_attempt_history"
    )
    contact_attempt_history_collection.add(contact_attempt_history_document)

    print(
        textwrap.dedent(
            f"""
            The following document has been added to the firestore:
            {contact_attempt_history_document}
            """
        )
    )


def check_valid_time_range():
    start = datetime(NOW_CDT.year, NOW_CDT.month, NOW_CDT.day, 6, 0, 0).replace(
        tzinfo=CDT_TIMEZONE
    )
    end = datetime(NOW_CDT.year, NOW_CDT.month, NOW_CDT.day, 21, 0, 0).replace(
        tzinfo=CDT_TIMEZONE
    )

    if NOW_CDT >= start or NOW_CDT <= end:
        return True

    return False


def check_sms_message_within_valid_gap(climate_type):
    if check_firestore_initialized() is False:
        set_firestore_credentials()

    firestore_client = firestore.client()
    contact_attempt_history_collection = firestore_client.collection(
        "contact_attempt_history"
    )
    contact_attempt_latest_successful_document = (
        contact_attempt_history_collection.where("climateType", "==", climate_type)
        .where("contactAttemptSuccessful", "==", True)
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(1)
        .stream()
    )

    timestamp_values = [
        document.to_dict()["timestamp"]
        for document in contact_attempt_latest_successful_document
    ]

    if not timestamp_values:
        return True

    timestamp_record_cdt = timestamp_values[0] - timedelta(hours=5)
    timestamp_difference = NOW_CDT - timestamp_record_cdt
    timestamp_difference_hours = timestamp_difference.total_seconds() / 3600

    if timestamp_difference_hours > 1:
        return True

    return False


def check_firestore_initialized():
    if firebase_admin._DEFAULT_APP_NAME in firebase_admin._apps:
        return True
    else:
        return False


def set_firestore_credentials():
    credential = credentials.ApplicationDefault()
    firebase_admin.initialize_app(credential, {"projectId": PROJECT_ID})


def get_sms_password():
    secret_manager_client = secretmanager.SecretManagerServiceClient()

    return secret_manager_client.access_secret_version(
        "projects/203517643656/secrets/sms/versions/1"
    ).payload.data.decode("utf-8")
