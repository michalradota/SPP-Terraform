import json
import math
import boto3
import logging
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns_client = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

sqs = boto3.client('sqs')
SQS_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/300195457806/TemperatureReadingsQueue"


table = dynamodb.Table('SensorStatus')
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:300195457806:TemperatureAlerts"

def send_sns_alert(message, subject="Temperature Alert"):
    try:
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=subject
        )
        logger.info(f"SNS Message Sent: {response}")
    except sns_client.exceptions.InvalidParameterException as e:
        logger.error(f"InvalidParameterException: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to send SNS alert: {str(e)}")

def mark_sensor_as_broken(sensor_id):
    try:
        table.put_item(
            Item={
                'sensor_id': sensor_id,
                'broken': True
            }
        )
        logger.info(f"Sensor {sensor_id} marked as broken in DynamoDB")
    except Exception as e:
        logger.error(f"Failed to update sensor status in DynamoDB: {str(e)}")

def send_to_sqs(sensor_id, location_id, temperature):
    try:
        message = {
            "sensor_id": sensor_id,
            "location_id": location_id,
            "temperature": round(temperature, 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        response = sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(message)
        )
        logger.info(f"Message sent to SQS: {response}")
    except Exception as e:
        logger.error(f"Failed to send message to SQS: {str(e)}")


def lambda_handler(event, context):
    # Parametry równania Steinharta-Harta
    a = 1.40 * 10**-3
    b = 2.37 * 10**-4
    c = 9.90 * 10**-8

    # Odczyt danych z eventu
    sensor_id = event.get('sensor_id')
    location = event.get('location_id')
    resistance = event.get('value')

    try:
        resistance = float(resistance)
    except (ValueError, TypeError):
        mark_sensor_as_broken(sensor_id)
        return {"error": "INVALID RESISTANCE VALUE"}

    if resistance < 1 or resistance > 20000:
        mark_sensor_as_broken(sensor_id)
        return {"error": "VALUE OUT OF RANGE"}

    try:
        temperature = (1 / (a + b * math.log(resistance) + c * (math.log(resistance)**3))) - 273.15
    except ValueError:
        mark_sensor_as_broken(sensor_id)
        return {"error": "CALCULATION ERROR"}

    logger.info(f"Sensor ID: {sensor_id}, Resistance: {resistance}, Temperature: {temperature}")
    send_to_sqs(sensor_id, location, temperature)

    if temperature < -273.15:
        mark_sensor_as_broken(sensor_id)
        return {"error": "TEMPERATURE TOO LOW"}
    elif 20 <= temperature <= 100:
        send_sns_alert(f"Sensor {sensor_id}: Temperatura w normie. {temperature:.2f}C")
        return {"status": "OK"}
    elif 100 < temperature <= 250:
        send_sns_alert(f"Sensor {sensor_id}: Temperatura wysoka! {temperature:.2f}C")
        return {"status": "TEMPERATURE TOO HIGH"}
    else:
        critical_message = f"Sensor {sensor_id}: Temperatura krytyczna! {temperature:.2f}C"
        send_sns_alert(critical_message, subject="CRITICAL TEMPERATURE ALERT")
        mark_sensor_as_broken(sensor_id)
        return {"error": "TEMPERATURE CRITICAL"}
