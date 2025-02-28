import json
import datetime


def get_event_source(event):
    if "httpMethod" in event:
        return "API Gateway Proxy"
    elif event.get("Records", [{}])[0].get("eventSource") == "aws:sqs":
        return "SQS"
    elif event.get("Records", [{}])[0].get("EventSource") == "aws:sns":
        return "SNS"

    return "Unknown"    # else case

def get_event_details(event, event_source):
    event_handlers = {
        "API Gateway Proxy": get_api_gateway_details,
        "SNS": get_sns_details,
        "SQS": get_sqs_details,
        "Unknown": get_unknown_details
    }

    handler = event_handlers.get(event_source)

    if handler:
        return handler(event)
    else:
        raise Exception("Something unexpected happened")


def get_api_gateway_details(event):
    return {
            "httpMethod": event["httpMethod"],
            "path": event.get("path", "N/A"),
            "queryStringParameters": event.get("queryStringParameters", {}),
            "headers": event.get("headers", {}),
            "body": event.get("body", "N/A")
        }


def get_sns_details(event):
    return {
            "messageId": event["Records"][0]["Sns"]["MessageId"],
            "subject": event["Records"][0]["Sns"].get("Subject", "N/A"),
            "message": event["Records"][0]["Sns"]["Message"]
        }

def get_sqs_details(event):
    return {
        "messageId": event["Records"][0]["messageId"],
        "body": event["Records"][0]["body"]
    }

def get_unknown_details(event):
    return {"message": f"{event}"}


def lambda_handler(event, context):
    invocation_time = datetime.datetime.utcnow().isoformat()
    event_source = get_event_source(event)
    source_details = get_event_details(event, event_source)
    log_details = {
        "invocation_time": invocation_time,
        "event_source": event_source,
        "source_details": source_details
    }

    # print(log_details)
    # print(json.dumps(log_details, indent=2))

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Lambda executed successfully", "event_source": event_source}),
    }