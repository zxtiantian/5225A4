# etrieve an authentication token and authenticate the Docker client to the registry. Use the AWS CLI:
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 716253337897.dkr.ecr.us-east-1.amazonaws.com

# Build the Docker image using the following command.
$TAG = (Get-Date -Format "yyyyMMdd-HHmm")

docker build --no-cache `
  --platform linux/amd64 `
  -t 716253337897.dkr.ecr.us-east-1.amazonaws.com/bird_audio_detection:$TAG `
  .

# After the build is completed, tag the image to enable pushing the image to this repository
## ## Do not run if already did
docker tag bird_audio_detection:latest 716253337897.dkr.ecr.us-east-1.amazonaws.com/bird_audio_detection:$TAG


# Run the following command to push this image to the newly created AWS repository:
docker push 716253337897.dkr.ecr.us-east-1.amazonaws.com/bird_audio_detection:$TAG

# Create Lambda Function
aws lambda create-function `
  --function-name    detect-bird-audio `
  --package-type     Image `
  --code             ImageUri=716253337897.dkr.ecr.us-east-1.amazonaws.com/bird_audio_detection:$TAG `
  --role             arn:aws:iam::716253337897:role/LabRole `
  --memory-size      2048 `
  --timeout          180 `
  --region           us-east-1 `
  --architectures    x86_64

## Expected response:
{
    "FunctionName": "detect-bird-audio",
    "FunctionArn": "arn:aws:lambda:us-east-1:716253337897:function:detect-bird-audio",
    "Role": "arn:aws:iam::716253337897:role/LabRole",
    "CodeSize": 0,
    "Description": "",
    "Timeout": 180,
    "MemorySize": 2048,
    "LastModified": "2025-06-07T12:18:15.070+0000",
    "CodeSha256": "d197c981427e093ceeca54ae6ba79275df31cbc630e8f03454ba48dea19e20b9",
    "Version": "$LATEST",
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "RevisionId": "81d1bbd5-059f-4561-bdd1-aba7788ab4df",
    "State": "Pending",
    "StateReason": "The function is being created.",
    "StateReasonCode": "Creating",
    "PackageType": "Image",
    "Architectures": [
        "x86_64"
    ],
    "EphemeralStorage": {
        "Size": 512
    },
    "SnapStart": {
        "ApplyOn": "None",
        "OptimizationStatus": "Off"
    },
    "LoggingConfig": {
        "LogFormat": "Text",
        "LogGroup": "/aws/lambda/detect-bird-audio"
    }
}

# Avoid Prefix overlapping
aws s3api get-bucket-notification-configuration `
  --bucket birdnet-audio-uploads

## Remove previous rules
aws s3api put-bucket-notification-configuration `
  --bucket birdnet-audio-uploads `
  --notification-configuration '{}'

# Update Lambda function with the newly pushed image
aws lambda update-function-code `
  --function-name detect-bird-audio `
  --image-uri 716253337897.dkr.ecr.us-east-1.amazonaws.com/bird_audio_detection:$TAG `
  --region us-east-1

## Expected Response
{
    "FunctionName": "detect-bird-audio",
    "FunctionArn": "arn:aws:lambda:us-east-1:716253337897:function:detect-bird-audio",
    "Role": "arn:aws:iam::716253337897:role/LabRole",
    "CodeSize": 0,
    "Description": "",
    "Timeout": 180,
    "MemorySize": 2048,
    "LastModified": "2025-06-07T12:40:05.000+0000",
    "CodeSha256": "d197c981427e093ceeca54ae6ba79275df31cbc630e8f03454ba48dea19e20b9",
    "Version": "$LATEST",
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "RevisionId": "a3d2c314-0277-40ac-acb3-078c97f44cf3",
    "State": "Active",
    "LastUpdateStatus": "InProgress",
    "LastUpdateStatusReason": "The function is being created.",
    "LastUpdateStatusReasonCode": "Creating",
    "PackageType": "Image",
    "Architectures": [
        "x86_64"
    ],
    "EphemeralStorage": {
        "Size": 512
    },
    "SnapStart": {
        "ApplyOn": "None",
        "OptimizationStatus": "Off"
    },
    "LoggingConfig": {
        "LogFormat": "Text",
        "LogGroup": "/aws/lambda/detect-bird-audio"
    }
}

# Create DynamoDB
aws dynamodb create-table `
  --region us-east-1 `
  --table-name BirdDetectionResults `
  --attribute-definitions AttributeName=file_id,AttributeType=S `
  --key-schema AttributeName=file_id,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST

## Expected result
{
    "TableDescription": {
        "AttributeDefinitions": [
            {
                "AttributeName": "file_id",
                "AttributeType": "S"
            }
        ],
        "TableName": "BirdDetectionResults",
        "KeySchema": [
            {
                "AttributeName": "file_id",
                "KeyType": "HASH"
            }
        ],
        "TableStatus": "CREATING",
        "CreationDateTime": "2025-06-08T01:50:30.715000+10:00",
        "ProvisionedThroughput": {
            "NumberOfDecreasesToday": 0,
            "ReadCapacityUnits": 0,
            "WriteCapacityUnits": 0
        },
        "TableSizeBytes": 0,
        "ItemCount": 0,
        "TableArn": "arn:aws:dynamodb:us-east-1:716253337897:table/BirdDetectionResults",
        "TableId": "752b13a9-7181-41bb-97cf-06a9b73e845c",
        "BillingModeSummary": {
            "BillingMode": "PAY_PER_REQUEST"
        },
        "DeletionProtectionEnabled": false
    }
}

