import json
import os
import boto3
import tempfile
import uuid
import datetime
import decimal
from birds_detection import image_prediction

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

# Lambda handler for image recognition
def lambda_handler(event, context):
    print("Event received:", json.dumps(event))
    # 兼容 API Gateway 2.0 event
    if "body" in event and isinstance(event["body"], str):
        payload = json.loads(event["body"])
    else:
        payload = event

    image_url = payload.get("image_url", None)
    image_path = payload.get("image_path", None)
    if image_path:
        image_url = image_path
        original_filename = os.path.basename(image_path)
    elif image_url:
        original_filename = os.path.basename(image_url)
    elif "Records" in event and event["Records"][0]["eventSource"] == "aws:s3":
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]
        image_url = f"s3://{bucket}/{key}"
        original_filename = os.path.basename(key)
    else:
        raise ValueError("Event must contain an S3 event or a payload with 'image_url' or 'image_path'.")
    # Download model (if not already cached) and call image_prediction
    model_path = ensure_model()
    # (Optional) if image_url is an S3 URL, download it locally (e.g. to /tmp) and pass the local path
    if image_url.startswith("s3://"):
         s3 = boto3.client("s3")
         bucket, key = image_url.replace("s3://", "").split("/", 1)
         local_image_path = os.path.join(tempfile.gettempdir(), os.path.basename(key))
         s3.download_file(bucket, key, local_image_path)
         image_url = local_image_path
    # 生成结果图片名
    name, ext = os.path.splitext(original_filename)
    result_filename = f"{name}_detected{ext}"
    save_dir = "/tmp"
    # 获取识别结果
    detections = image_prediction(image_url, result_filename=result_filename, save_dir=save_dir, model=model_path)
    # 上传结果图片到 S3 results 目录
    s3 = boto3.client("s3")
    result_s3_key = f"results/{result_filename}"
    s3.upload_file(os.path.join(save_dir, result_filename), MODEL_BUCKET, result_s3_key)
    result_url = f"s3://{MODEL_BUCKET}/{result_s3_key}"
    # 生成识别时间
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    # 获取用户ID（如 event 里有 Cognito 信息）
    user_id = event.get("user_id", "anonymous")
    # 写入 DynamoDB
    item = {
        "fileKey": result_s3_key,
        "id": str(uuid.uuid4()),
        "userId": user_id,
        "type": "image",
        "originalFile": image_url,
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
        "type": "image",
        "timestamp": timestamp,
        "url": result_url
    }
    notify_new_detection(detections, file_info)

    # 返回前端结构
    return {
        "statusCode": 200,
        "body": json.dumps({
            "annotatedImage": result_url,
            "detections": detections,
            "timestamp": timestamp
        })
    } 