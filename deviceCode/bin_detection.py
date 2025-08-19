import RPi.GPIO as GPIO
import time
import boto3
from botocore.exceptions import NoCredentialsError

IR_SENSOR_PIN = 4
BUCKET_NAME = "garbagemanagementsystem"
FILE_NAME = "bin_fill_data.json"

AWS_ACCESS_KEY = <aws-access-key>
AWS_SECRET_KEY = <aws-secret-key>
REGION_NAME = <region-name>

GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_SENSOR_PIN, GPIO.IN)

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION_NAME
)

def upload_to_s3(bucket, file_name, data):
    try:
        s3.put_object(
            Bucket=bucket,
            Key=file_name,
            Body=data,
            ContentType="application/json"
        )
        print('IR sensor input detected bin filled for more than 3 seconds!\nSending data to S3: {"bin_fill": "yes"}')
    except NoCredentialsError:
        pass

def monitor_garbage():
    try:
        consecutive_full_time = 0
        threshold_time = 3

        while True:
            sensor_state = GPIO.input(IR_SENSOR_PIN)
            if sensor_state == GPIO.HIGH:
                consecutive_full_time += 1
                if consecutive_full_time >= threshold_time:
                    data = '{\n    "bin_fill": "yes"\n}'
                    upload_to_s3(BUCKET_NAME, FILE_NAME, data)
                    time.sleep(10)
                    consecutive_full_time = 0
            else:
                consecutive_full_time = 0
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    monitor_garbage()
