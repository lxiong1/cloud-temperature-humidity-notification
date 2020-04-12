![master](https://github.com/lxiong1/cloud-temperature-humidity-system/workflows/master/badge.svg) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![made-with-c](https://img.shields.io/badge/Made%20with-C-1f425f.svg)](https://en.cppreference.com/w/) [![made-with-latex](https://img.shields.io/badge/Made%20with-LaTeX-1f425f.svg)](https://www.latex-project.org/)

# Cloud Temperature & Humidity Notification

The purpose of this project is to be able to notify a user via SMS when their ambient room temperature and relative humidity are in the range for discomfort and potential health risks. It is an Internet of Things (IoT) project, built with an event-driven serverless architecture and accomplished using a mixture of specified hardware and cloud technologies mentioned below.

## Hardware
- Particle Argon
- Adafruit Si7021
- Breadboard
- Jumper Wires
- Lithium Ion Polymer Battery 1000 mAh

The following is the breadboard schematic:

![Breadboard Schematic](./latex/images/breadboard-schematic.png)

## Technology Stack
- Python
- C
- Github Actions
- Docker
- NGINX
- Plotly
- Particle Cloud
- Google Cloud Platform
    - Compute Engine
    - Firestore
    - Functions
    - IAM
    - PubSub
    - Secret Manager
    - Storage

## SMS Notification
### Rules
- Minimum 1 hour gap between each message per climate type
- Trigger only between 6AM - 9PM
### Trigger Criteria
- Ambient room temperature above 75 degrees Fahrenheit or below 65 degrees Fahrenheit
- Relative humidity above 60% or below 30%

## Interactive Graph
The results of temperature and humidty readings are calculated for daily averages, and then used at data points in this interactive graph: [![Interactive Graph !](https://img.shields.io/badge/Interactive%20Graph-1abc9c.svg)](http://35.238.110.48:8080)

The graph is hosted on a Google Cloud Compute Engine instance, which has a scheduled cron job that retrieves the latest data aggregated on daily basis from Google Cloud Storage and plots it in the graph. The described process is only the end result of a bigger process, which is wholly explained in this `LaTex` report: [![Report !](https://img.shields.io/badge/Report-1abc9c.svg)](latex/cloud-temperature-humidity-system.pdf)
