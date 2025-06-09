import json
import boto3

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        email = body["email"]
        tags = body["tags"]  # list of species names
        sns = boto3.client('sns')
        for tag in tags:
            topic_name = f"bird-tag-{tag.replace(' ', '_')}"
            topic_arn = sns.create_topic(Name=topic_name)['TopicArn']
            sns.subscribe(TopicArn=topic_arn, Protocol='email', Endpoint=email)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "ok"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "error", "error": str(e)})
        }