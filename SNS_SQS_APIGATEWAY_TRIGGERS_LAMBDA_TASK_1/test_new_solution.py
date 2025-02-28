import unittest
from unittest.mock import patch

from new_solution import eventMapper, get_event_details, extract_message_json, lambda_handler,\
    APIGatewayProxy, SQS, SNS, CustomSignature
import json
import datetime

class MyTestCase(unittest.TestCase):

    # def setUp(self):
    #     event_custom_signature = {
    #         "message": "{ "httpMethod": "POST" }"
    #     }
    #     event_api_gateway_proxy =

    def test_eventMapper_for_APIGatewayProxy(self):
        event = {
            "httpMethod" : "POST"
        }
        actualResult = eventMapper(event)
        # expectedResult = APIGatewayProxy(event)
        self.assertIsInstance(actualResult, APIGatewayProxy )

    def test_eventMapper_for_SQS(self):
        event = {
            "Records": [{"eventSource":"aws:sqs"}]
        }
        actualResult = eventMapper(event)
        # expectedResult = APIGatewayProxy(event)
        self.assertIsInstance(actualResult , SQS )

    def test_eventMapper_for_SNS(self):
        event = {
            "Records": [{"EventSource":"aws:sns"}]
        }
        actualResult = eventMapper(event)
        # expectedResult = APIGatewayProxy(event)
        self.assertIsInstance(actualResult, SNS )

    def test_eventMapper_for_CustomSignature(self):
        event = {
            "message": "{ \"httpMethod\": \"POST\" }"
        }
        actualResult = eventMapper(event)
        # expectedResult = APIGatewayProxy(event)
        self.assertIsInstance(actualResult, CustomSignature )

    # def test_eventMapper_for_UnknownService_raising_exception(self):
    #     event = {
    #
    #     }
    #     # actualResult = eventMapper(event)
    #     # expectedResult = APIGatewayProxy(event)
    #     # self.assertIsInstance(actualResult, UnknownService)
    #     with self.assertRaises(Exception):
    #         eventMapper(event)

    def test_eventMapper_for_UnknownService(self):
        event = {

        }
        actualResult = eventMapper(event)
        expectedResult = None
        self.assertEqual(expectedResult, actualResult)
        # with self.assertRaises(Exception):
        #     eventMapper(event)

    def test_extract_message_json_fun_with_valid_CustomSignature(self):
        event = {
            "message": "{ \"httpMethod\": \"POST\" }"
        }
        actualResult = extract_message_json(event)
        expectedResult = {
            "httpMethod" : "POST"
        }
        self.assertEqual(expectedResult, actualResult )

    def test_extract_message_json_fun_with_invalid_CustomSignature_raising_JSONDecodeError(self):
        event = {
            "message": "invalid signature"
        }
        actualResult = extract_message_json(event)
        expectedResult = None
        self.assertEqual(expectedResult, actualResult )
        # with self.assertRaises(json.JSONDecodeError):
        #     extract_message_json(event)

    def test_get_event_details_for_APIGatewayProxy(self):
        apigatewayproxy_object = APIGatewayProxy({
            "httpMethod" : "POST"
        })
        actualResult = get_event_details(apigatewayproxy_object)
        expectedResult = {
            "httpMethod": "POST",
            "path": "N/A",
            "queryStringParameters": {},
            "headers": {},
            "body": "N/A"
        }
        self.assertEqual(expectedResult, actualResult )



    def test_get_event_details_for_SQS(self):
        sqs_object = SQS({
            "Records": [
                {
                    "eventSource": "aws:sqs",
                        "messageId" : "1234567890",
                        "body" : "qwertyuiop"
                }
            ]
        })
        actualResult = get_event_details(sqs_object)
        expectedResult = {
        "messageId": "1234567890",
        "body": "qwertyuiop"
    }
        self.assertEqual(expectedResult, actualResult )


    def test_get_event_details_for_SNS(self):
        sns_object = SNS({
            "Records": [
                {
                    "eventSource":"aws:sns",
                    "Sns": {
                        "MessageId": "1234567890",
                        "Message" : "asdfghjkl",
                        # "Subject" : ""
                    }
                }
            ]
        })
        actualResult = get_event_details(sns_object)
        expectedResult = {
        "messageId": "1234567890",
        "subject": "N/A",
        "message": "asdfghjkl"
    }
        self.assertEqual(expectedResult, actualResult )


    def test_get_event_details_for_CustomSignature(self):
        customsignature_object = CustomSignature({
            "message": "{ \"httpMethod\": \"POST\" }"
        })
        actualResult = get_event_details(customsignature_object)
        expectedResult = {
            "message": "Custom API Gateway Service",
            "event_details": "{'message': '{ \"httpMethod\": \"POST\" }'}"
        }
        self.assertEqual(expectedResult, actualResult )


    @patch("new_solution.datetime")
    @patch("new_solution.eventMapper")
    @patch("new_solution.get_event_details")
    def test_lambda_handler_for_APIGatewayProxy(self, mock_get_event_details, mock_event_mapper, mock_datetime):
        event = {"httpMethod": "POST"}
        context = {}

        mock_datetime.datetime.utcnow.return_value = datetime.datetime(2025, 2, 28, 12, 0, 0)
        mock_event_mapper.return_value = APIGatewayProxy(event)
        mock_get_event_details.return_value = {"httpMethod": "POST"}

        actual_result = lambda_handler(event, context)
        expected_result = {
            "statusCode": 200,
            "body": json.dumps({"message": "Lambda executed successfully", "event_source": "APIGatewayProxy"}),
        }

        self.assertEqual(expected_result, actual_result)

    @patch("new_solution.datetime")
    @patch("new_solution.eventMapper")
    @patch("new_solution.get_event_details")
    def test_lambda_handler_for_SQS(self, mock_get_event_details, mock_event_mapper, mock_datetime):
        event = {
            "Records": [{"eventSource": "aws:sqs", "messageId": "1234567890", "body": "qwertyuiop"}]
        }
        context = {}

        mock_datetime.datetime.utcnow.return_value = datetime.datetime(2025, 2, 28, 12, 0, 0)
        mock_event_mapper.return_value = SQS(event)
        mock_get_event_details.return_value = {"messageId": "1234567890", "body": "qwertyuiop"}

        actual_result = lambda_handler(event, context)
        expected_result = {
            "statusCode": 200,
            "body": json.dumps({"message": "Lambda executed successfully", "event_source": "SQS"}),
        }

        self.assertEqual(expected_result, actual_result)

    @patch("new_solution.datetime")
    @patch("new_solution.eventMapper")
    @patch("new_solution.get_event_details")
    def test_lambda_handler_for_SNS(self, mock_get_event_details, mock_event_mapper, mock_datetime):
        event = {
            "Records": [{"EventSource": "aws:sns", "Sns": {"MessageId": "1234567890", "Message": "asdfghjkl"}}]
        }
        context = {}

        mock_datetime.datetime.utcnow.return_value = datetime.datetime(2025, 2, 28, 12, 0, 0)
        mock_event_mapper.return_value = SNS(event)
        mock_get_event_details.return_value = {"messageId": "1234567890", "message": "asdfghjkl"}

        actual_result = lambda_handler(event, context)
        expected_result = {
            "statusCode": 200,
            "body": json.dumps({"message": "Lambda executed successfully", "event_source": "SNS"}),
        }

        self.assertEqual(expected_result, actual_result)

    @patch("new_solution.datetime")
    @patch("new_solution.eventMapper")
    @patch("new_solution.get_event_details")
    def test_lambda_handler_for_CustomSignature(self, mock_get_event_details, mock_event_mapper, mock_datetime):
        event = {"message": '{ "httpMethod": "POST" }'}
        context = {}

        mock_datetime.datetime.utcnow.return_value = datetime.datetime(2025, 2, 28, 12, 0, 0)
        mock_event_mapper.return_value = CustomSignature(event)
        mock_get_event_details.return_value = {"httpMethod": "POST"}

        actual_result = lambda_handler(event, context)
        expected_result = {
            "statusCode": 200,
            "body": json.dumps({"message": "Lambda executed successfully", "event_source": "CustomSignature"}),
        }

        self.assertEqual(expected_result, actual_result)

    @patch("new_solution.eventMapper")
    def test_lambda_handler_for_UnknownService(self, mock_event_mapper):
        event = {}
        context = {}

        mock_event_mapper.side_effect = Exception("Invocation through Unknown Service")

        with self.assertRaises(Exception) as context_exception:
            lambda_handler(event, context)

        self.assertEqual(str(context_exception.exception), "Invocation through Unknown Service")


if __name__ == '__main__':
    unittest.main()