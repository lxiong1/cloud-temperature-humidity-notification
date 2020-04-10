from datetime import datetime
from google.cloud import storage
import pandas
import plotly.graph_objects as go

TEMPERATURE = 'temperature'
HUMIDITY = 'humidity'
TODAY = datetime.today().strftime('%Y-%m-%d')
BUCKET_NAME = 'climate-data-files'
CLIMATE_DATA_FILE_NAME = 'climate_data_aggregate.csv'
CLIMATE_DATA_GRAPH_FILE_NAME = 'climate_data_aggregate_graph.html'


def send_climate_data_graph_to_storage(event, context):
    html_path = f'/tmp/{CLIMATE_DATA_GRAPH_FILE_NAME}'
    climate_dataframe = pandas.read_csv(f'gs://{BUCKET_NAME}/{CLIMATE_DATA_FILE_NAME}')

    figure = create_figure(climate_dataframe)
    figure.write_html(html_path)
    upload_html_file_to_storage(html_path)


def create_figure(dataframe):
    dates = []
    temperature_data = []
    humidity_data = []

    for index, row in dataframe.iterrows():
        dates.append(row['date'])
        temperature_data.append(row[f'{TEMPERATURE}Average'])
        humidity_data.append(row[f'{HUMIDITY}Average'])

    trace_temperature = go.Scatter(
        name=TEMPERATURE.capitalize(),
        x=dates,
        y=temperature_data
    )
    trace_humidity = go.Scatter(
        name=HUMIDITY.capitalize(),
        x=dates,
        y=humidity_data
    )
    layout = go.Layout(
        title=f'{TEMPERATURE.capitalize()} & {HUMIDITY.capitalize()} Over Time from {dates[0]} to {dates[-1]}',
        xaxis=dict(title='Date'),
        yaxis=dict(title=f'{TEMPERATURE.capitalize()} (Fahrenheit) & {HUMIDITY.capitalize()} (Percentage)')
    )

    return go.Figure(data=[trace_temperature, trace_humidity], layout=layout)


def upload_html_file_to_storage(html_path):
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(CLIMATE_DATA_GRAPH_FILE_NAME)

    blob.upload_from_filename(html_path)
