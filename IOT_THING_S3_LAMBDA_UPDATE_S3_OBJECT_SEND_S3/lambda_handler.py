import json
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read().decode('utf-8')
        data = json.loads(file_content)
        data["status"] = "Modified field added"

        s3.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=json.dumps(data),
            ContentType="application/json"
        )

        # print(f"Processed file: {object_key}, Updated Data: {data}")

    return {
        'statusCode': 200,
        'body': json.dumps('IoT Data Processed Successfully!')
    }
