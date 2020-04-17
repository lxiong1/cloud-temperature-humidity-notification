from datetime import datetime
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
CDT_TIMEZONE = timezone("America/Chicago")
NOW_CDT = datetime.now(CDT_TIMEZONE)


def send_sms_message_with_device_status(event, context):
    if check_device_on() is True:
        print("Device is on and sending climate readings")
        return ""

    if check_valid_time_range() is False:
        print("SMS message will not be sent after 9 PM or before 6 AM")
        return ""

    try:
        email_address = "gcp.sms.robot@gmail.com"
        password = get_sms_password()
        sms_gateway = "9207504346@tmomail.net"

        sms_message = MIMEMultipart()
        sms_message["From"] = email_address
        sms_message["To"] = sms_gateway
        sms_message["Subject"] = "Device Status: Inactive"
        sms_message.attach(
            MIMEText(
                "Your Particle Argon is currently not sending temperature and humidity readings",
                "plain",
            )
        )

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_address, password)
        server.sendmail(email_address, sms_gateway, sms_message.as_string())

        print(f"Successfully sent SMS message to {sms_gateway} with device status")
    except Exception as exception:
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


def check_device_on():
    if check_firestore_initialized() is False:
        set_firestore_credentials()

    firestore_client = firestore.client()
    temperature_collection = firestore_client.collection("temperature")
    contact_attempt_latest_successful_document = (
        temperature_collection.order_by(
            "timestamp", direction=firestore.Query.DESCENDING
        )
        .limit(1)
        .stream()
    )

    timestamp_values = [
        document.to_dict()["timestamp"]
        for document in contact_attempt_latest_successful_document
    ]

    if not timestamp_values:
        return True

    timestamp_record = timestamp_values[0]
    timestamp_difference = NOW_CDT - timestamp_record
    timestamp_difference_hours = timestamp_difference.total_seconds() / 3600

    if timestamp_difference_hours < 1:
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
