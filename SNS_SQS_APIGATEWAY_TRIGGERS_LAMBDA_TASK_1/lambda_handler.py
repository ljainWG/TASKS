import json
import datetime
from abc import ABC, abstractmethod

# ==============================
# Abstract Base Class for Event Handlers
# ==============================
class EventHandler(ABC):
    @abstractmethod
    def extract_details(self, event) -> dict:
        """Extract relevant details from the event."""
        pass

# ==============================
# API Gateway Event Handler
# ==============================
class APIGatewayHandler(EventHandler):
    def extract_details(self, event) -> dict:
        return {
            "httpMethod": event["httpMethod"],
            "path": event.get("path", "N/A"),
            "queryStringParameters": event.get("queryStringParameters", {}),
            "headers": event.get("headers", {}),
            "body": event.get("body", "N/A"),
        }

# ==============================
# SQS Event Handler
# ==============================
class SQSEventHandler(EventHandler):
    def extract_details(self, event) -> dict:
        return {
            "messageId": event["Records"][0]["messageId"],
            "body": event["Records"][0]["body"],
        }

# ==============================
# SNS Event Handler
# ==============================
class SNSEventHandler(EventHandler):
    def extract_details(self, event) -> dict:
        return {
            "messageId": event["Records"][0]["Sns"]["MessageId"],
            "subject": event["Records"][0]["Sns"].get("Subject", "N/A"),
            "message": event["Records"][0]["Sns"]["Message"],
        }

# ==============================
# Unknown Event Handler (Default)
# ==============================
class UnknownEventHandler(EventHandler):
    def extract_details(self, event) -> dict:
        return {"message": "Unknown event format"}

# ==============================
# Function to Detect Event Type
# ==============================
def get_event_handler(event) -> EventHandler:
    """Determines the type of event and returns the appropriate handler instance."""
    if "httpMethod" in event:
        return APIGatewayHandler()
    elif event.get("Records", [{}])[0].get("eventSource") == "aws:sqs":
        return SQSEventHandler()
    elif "Records" in event and "Sns" in event["Records"][0]:
        return SNSEventHandler()
    else:
        return UnknownEventHandler()  # Default handler for unknown event types

# ==============================
# Event Processor
# ==============================
class EventProcessor:
    def process_event(self, event):
        """Processes the event using the appropriate handler."""
        invocation_time = datetime.datetime.utcnow().isoformat()
        handler = get_event_handler(event)  # Get the handler based on event type

        event_source = handler.__class__.__name__.replace("Handler", "")  # Extract clean event name
        source_details = handler.extract_details(event)

        log_details = {
            "invocation_time": invocation_time,
            "event_source": event_source,
            "source_details": source_details,
        }

        print(json.dumps(log_details, indent=2))  # Logging the information

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Lambda executed successfully", "event_source": event_source}),
        }

# ==============================
# Main Lambda Handler
# ==============================
def lambda_handler(event, context):
    processor = EventProcessor()
    return processor.process_event(event)
