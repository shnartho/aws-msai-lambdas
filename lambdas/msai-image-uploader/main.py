def lambda_handler(event, context):
    """
    Simple AWS Lambda function that returns a greeting message.
    
    Args:
        event: The event data passed to the Lambda function
        context: The runtime information provided by AWS Lambda
        
    Returns:
        A dictionary containing a status code and message formatted for API Gateway
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': '{"message": "Hello from AWS Lambda!", "timestamp": "' + context.aws_request_id + '"}'
    }
