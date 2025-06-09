import json
import os
import boto3
import tempfile
import uuid
import datetime
import decimal
from birds_detection import video_prediction

# S3 bucket and key for the model file
MODEL_BUCKET = "bird-recognition-files"
MODEL_KEY = "BirdImg-Analyzer/model.pt"
TABLE_NAME = "bird-recognition-files"

# Local path (inside /tmp) to download the model
MODEL_LOCAL_PATH = os.path.join(tempfile.gettempdir(), "model.pt")

dynamodb = boto3.resource('dynamodb')

def float_to_decimal(obj):
    if isinstance(obj, list):
        return [float_to_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        return decimal.Decimal(str(obj))
    else:
        return obj

# Ensure the model is downloaded (or use cached version if available)
def ensure_model():
    if not os.path.exists(MODEL_LOCAL_PATH):
        s3 = boto3.client("s3")
        s3.download_file(MODEL_BUCKET, MODEL_KEY, MODEL_LOCAL_PATH)
    return MODEL_LOCAL_PATH

# Lambda handler for video recognition
def lambda_handler(event, context):
    print("Event received:", json.dumps(event))
    # 兼容 API Gateway 2.0 event
    if "body" in event and isinstance(event["body"], str):
        payload = json.loads(event["body"])
    else:
        payload = event

    video_url = payload.get("video_url", None)
    video_path = payload.get("video_path", None)
    if video_path:
        video_url = video_path
        original_filename = os.path.basename(video_path)
    elif video_url:
        original_filename = os.path.basename(video_url)
    elif "Records" in event and event["Records"][0]["eventSource"] == "aws:s3":
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]
        video_url = f"s3://{bucket}/{key}"
        original_filename = os.path.basename(key)
    else:
        raise ValueError("Event must contain an S3 event or a payload with 'video_url' or 'video_path'.")

    # Download model (if not already cached)
    model_path = ensure_model()

    # If video_url is an S3 URL, download it locally
    if video_url.startswith("s3://"):
        s3 = boto3.client("s3")
        bucket, key = video_url.replace("s3://", "").split("/", 1)
        local_video_path = os.path.join(tempfile.gettempdir(), os.path.basename(key))
        s3.download_file(bucket, key, local_video_path)
        video_url = local_video_path

    # Generate result video filename
    name, ext = os.path.splitext(original_filename)
    result_filename = f"{name}_detected{ext}"
    save_dir = "/tmp"

    # Process video and save result
    detections = video_prediction(video_url, result_filename=result_filename, save_dir=save_dir, model=model_path)

    # Upload result video to S3 results directory
    s3 = boto3.client("s3")
    result_s3_key = f"results/{result_filename}"
    s3.upload_file(
        os.path.join(save_dir, result_filename),
        MODEL_BUCKET,
        result_s3_key,
        ExtraArgs={"ContentType": "video/mp4"}
    )
    result_url = f"s3://{MODEL_BUCKET}/{result_s3_key}"

    # 生成 presigned URL
    presigned_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': MODEL_BUCKET, 'Key': result_s3_key},
        ExpiresIn=3600
    )

    # 生成识别时间
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    user_id = payload.get("user_id", "anonymous")
    # 写入 DynamoDB
    item = {
        "fileKey": result_s3_key,
        "id": str(uuid.uuid4()),
        "userId": user_id,
        "type": "video",
        "originalFile": video_url,
        "resultFile": result_url,
        "detections": detections,
        "timestamp": timestamp
    }
    item = float_to_decimal(item)
    table = dynamodb.Table(TABLE_NAME)
    table.put_item(Item=item)

    # --- SNS 通知 ---
    def notify_new_detection(detections, file_info):
        sns = boto3.client('sns')
        notified_tags = set()
        for det in detections:
            tag = det.get("name")
            if not tag or tag in notified_tags:
                continue
            topic_name = f"bird-tag-{tag.replace(' ', '_')}"
            topic_arn = sns.create_topic(Name=topic_name)['TopicArn']
            message = (
                f"New bird recognition result!\n\n"
                f"Species: {tag}\n"
                f"File: {file_info.get('filename')}\n"
                f"Type: {file_info.get('type')}\n"
                f"Detected at: {file_info.get('timestamp')}\n"
                f"All detected species: {', '.join(set(d['name'] for d in detections if d.get('name')))}\n"
                f"File link: {file_info.get('url')}\n"
            )
            sns.publish(
                TopicArn=topic_arn,
                Message=message,
                Subject=f"New {tag} recognition result"
            )
            notified_tags.add(tag)

    file_info = {
        "filename": result_filename,
        "type": "video",
        "timestamp": timestamp,
        "url": result_url
    }
    notify_new_detection(detections, file_info)

    # 返回前端结构
    return {
        "statusCode": 200,
        "body": json.dumps({
            "annotatedVideo": result_url,
            "annotatedVideoUrl": presigned_url,
            "detections": detections,
            "timestamp": timestamp
        })
    } 