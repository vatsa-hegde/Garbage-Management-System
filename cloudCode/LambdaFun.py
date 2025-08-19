import boto3
import json

# Initialize AWS services
s3_client = boto3.client('s3')
ses_client = boto3.client('ses')

SENDER_EMAIL = <email>
RECIPIENT_EMAIL = <email>

def lambda_handler(event, context): 

    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    if bucket_name == "garbagemanagementsystem" and object_key == "bin_fill_data.json":
        # Send email notification
        try:
            email_subject = "BIN ALERT"
            email_body = "Trash needs to be collected."
            
            ses_client.send_email(
                Source=SENDER_EMAIL,
                Destination={'ToAddresses': [RECIPIENT_EMAIL]},
                Message={
                    'Subject': {'Data': email_subject},
                    'Body': {'Text': {'Data': email_body}}
                }
            )
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email via SES: {e}")
            raise e
    else:
        print("Event does not match criteria. No action taken.")

    return {"statusCode": 200, "body": json.dumps("Function executed successfully.")}
