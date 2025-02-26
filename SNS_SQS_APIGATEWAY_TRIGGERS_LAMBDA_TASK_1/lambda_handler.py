import json
import datetime

def get_event_source(event):
    """Determine the event source and extract relevant details."""
    sources = {
        "API Gateway": lambda e: "httpMethod" in e,
        "SQS": lambda e: e.get("Records", [{}])[0].get("eventSource") == "aws:sqs",
        "SNS": lambda e: "Records" in e and "Sns" in e["Records"][0],
    }

    for source, check in sources.items():
        if check(event):
            return source

    return "Unknown"

def extract_event_details(event, event_source):
    """Extract relevant details based on the event source."""
    extractors = {
        "API Gateway": lambda e: {
            "httpMethod": e["httpMethod"],
            "path": e.get("path", "N/A"),
            "queryStringParameters": e.get("queryStringParameters", {}),
            "headers": e.get("headers", {}),
            "body": e.get("body", "N/A"),
        },
        "SQS": lambda e: {
            "messageId": e["Records"][0]["messageId"],
            "body": e["Records"][0]["body"],
        },
        "SNS": lambda e: {
            "messageId": e["Records"][0]["Sns"]["MessageId"],
            "subject": e["Records"][0]["Sns"].get("Subject", "N/A"),
            "message": e["Records"][0]["Sns"]["Message"],
        },
    }

    return extractors.get(event_source, lambda e: {"message": "Unknown event format"})(event)


def lambda_handler(event, context):
    event_source = get_event_source(event)
    source_details = extract_event_details(event, event_source)

    log_details = {
        "event_source": event_source,
        "source_details": source_details,
    }

    print(json.dumps(log_details, indent=2))  # Logging the information

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Lambda executed successfully", "event_source": event_source}),
    }