import datetime
from functools import singledispatch
import json

class APIGatewayProxy:
    def __init__(self, event):
        self.event = event

    # def gather_event_details(self):
    #     return {
    #         "httpMethod": self.event["httpMethod"],
    #         "path": self.event.get("path", "N/A"),
    #         "queryStringParameters": self.event.get("queryStringParameters", {}),
    #         "headers": self.event.get("headers", {}),
    #         "body": self.event.get("body", "N/A")
    #     }

class SQS:
    def __init__(self, event):
        self.event = event

    # def gather_event_details(self):
    #     return {
    #         "messageId": self.event["Records"][0]["messageId"],
    #         "body": self.event["Records"][0]["body"]
    #     }

class SNS:
    def __init__(self, event):
        self.event = event

    # def gather_event_details(self):
    #     return {
    #         "messageId": self.event["Records"][0]["Sns"]["MessageId"],
    #         "subject": self.event["Records"][0]["Sns"].get("Subject", "N/A"),
    #         "message": self.event["Records"][0]["Sns"]["Message"]
    #     }

class UnknownService:
    def __init__(self, event):
        self.event = event

    # def gather_event_details(self):
    #     return {"message": "Unknown Service",
    #             "event" : f"{self.event}"}

class CustomSignature:
    def __init__(self, event):
        self.event = event

@singledispatch
def get_event_details(eventObject):
    return {"message": "Unknown Service",
                "event_details" : f"{eventObject.event}"}


@get_event_details.register(APIGatewayProxy)
def _(eventObject):
    # return eventObject.gather_event_details()
    return {
            "httpMethod": eventObject.event["httpMethod"],
            "path": eventObject.event.get("path", "N/A"),
            "queryStringParameters": eventObject.event.get("queryStringParameters", {}),
            "headers": eventObject.event.get("headers", {}),
            "body": eventObject.event.get("body", "N/A")
        }

@get_event_details.register(SQS)
def _(eventObject):
    # return eventObject.gather_event_details()
    return {
        "messageId": eventObject.event["Records"][0]["messageId"],
        "body": eventObject.event["Records"][0]["body"]
    }

@get_event_details.register(SNS)
def _(eventObject):
    # return eventObject.gather_event_details()
    return {
        "messageId": eventObject.event["Records"][0]["Sns"]["MessageId"],
        "subject": eventObject.event["Records"][0]["Sns"].get("Subject", "N/A"),
        "message": eventObject.event["Records"][0]["Sns"]["Message"]
    }

def extract_message_json(event):
    try:
        message_str = event.get("message", "")
        if message_str.startswith("LAMBDA EVENT: "):
            message_str = message_str[len("LAMBDA EVENT: "):]
        return json.loads(message_str)
    except json.JSONDecodeError:
        return None

def eventMapper(event):

    parsed_message = extract_message_json(event)

    if "httpMethod" in event:
        return APIGatewayProxy(event)
    elif event.get("Records", [{}])[0].get("eventSource") == "aws:sqs":
        return SQS(event)
    elif event.get("Records", [{}])[0].get("EventSource") == "aws:sns":
        return SNS(event)
    elif parsed_message and "httpMethod" in parsed_message:
        return CustomSignature(event)
    else:
        return UnknownService(event)

def lambda_handler(event, context):
    invocation_time = datetime.datetime.utcnow().isoformat()

    eventObject = eventMapper(event)
    eventDetails = get_event_details(eventObject)

    response = {
        "invocation_time": invocation_time,
        "event_source": eventObject.__class__.__name__,
        "event_details": eventDetails
    }

    print("Hello")
    print(response)
    print("World")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Lambda executed successfully", "event_source": response.get("event_source")}),
    }