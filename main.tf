provider "aws" {
  region                   = "us-east-1"
}

provider "archive" {}

# Pobieramy istniejącą rolę IAM
data "aws_iam_role" "main_role" {
  name = "LabRole"
}

# DynamoDB Table
resource "aws_dynamodb_table" "sensor_status" {
  name         = "SensorStatusNewTerraform"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "sensor_id"

  attribute {
    name = "sensor_id"
    type = "S"
  }
}

# SQS Queue
resource "aws_sqs_queue" "temperature_readings" {
  name = "TemperatureReadingsQueue"
}

# SNS Topic
resource "aws_sns_topic" "temperature_alerts" {
  name = "TemperatureAlerts"
}

# Pakowanie kodu Lambda (zakładam, że masz plik lambda_function.py z tym kodem w folderze ./lambda)
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_function.py"
  output_path = "${path.module}/lambda_function.zip"
}

# Lambda Function
resource "aws_lambda_function" "temperature_sensor" {
  function_name = "TemperatureSensorLambda"
  role          = data.aws_iam_role.main_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  filename      = data.archive_file.lambda_zip.output_path

  environment {
    variables = {
      SQS_QUEUE_URL  = aws_sqs_queue.temperature_readings.id
      SNS_TOPIC_ARN  = aws_sns_topic.temperature_alerts.arn
      DYNAMODB_TABLE = aws_dynamodb_table.sensor_status.name
    }
  }
}

# Uprawnienia do wywoływania Lambdy i dostępu do SQS, SNS, DynamoDB do roli LabRole dodamy później.
