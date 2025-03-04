import boto3
import json


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': json.dumps({'error': str(err)}) if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def payloadCreator(event, operation):
    if operation == "POST":
        return {
            'time': {'S': event.get("time")},
            'quality': {'S': event.get("quality")},
            'hostname': {'S': event.get("hostname")},
            'cpu utilization': {'S': event.get("cpu utilization")}
        }
    elif operation == "GET WITH SK":
        return {
            'hostname': {'S': event.get("hostname")},
            'quality': {'S': event.get("quality")}
        }


def lambda_handler(event, context):
    dynamodb = boto3.client('dynamodb')
    table = 'ljain-iot'

    operations = {
        'GET WITH SK': lambda dynamodb, table, x: dynamodb.get_item(TableName=table, Key=payload),
        'POST': lambda dynamodb, table, x: dynamodb.put_item(TableName=table, Item=payload),
        'BATCH POST': lambda dynamodb, requestItems: dynamodb.batch_write_item(RequestItems=requestItems)
        # 'DELETE WITH SK': lambda dynamodb:dynamodb.delete_item(Key = key)
    }

    print("Received event: " + json.dumps(event))

    operation = event.get("operation")
    if operation not in operations:
        message = f"Unsupported operation {operation}"
        print(message)
        return respond(message)

    try:
        if (operation.startswith("BATCH")):
            transformed_data = {}
            data = event['data']
            for table_name, records in data.items():
                transformed_data[table_name] = []

                for record in records:
                    item = {}
                    for key, value in record.items():
                        item[key] = {"S": str(value)}  # Convert everything to string format (DynamoDB expects types)

                    transformed_data[table_name].append({
                        "PutRequest": {
                            "Item": item
                        }
                    })
            payload = transformed_data
            result = operations[operation](dynamodb, payload)

        else:
            payload = payloadCreator(event, operation)
            result = operations[operation](dynamodb, table, payload)

        print(result)
        return respond(None, result)
    except Exception as e:
        print(e)
        return respond(str(e))