import os
import uuid
import json
from datetime import datetime
from decimal import Decimal
# 1) silence TF logs before anything else
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
# 2) redirect matplotlib cache
os.environ["MPLCONFIGDIR"] = "/tmp/.matplotlib"
os.environ["NUMBA_CACHE_DIR"] = "/tmp/numba_cache"
os.environ["NUMBA_DISABLE_JIT"] = "1"

import boto3
import time
from collections import Counter
from boto3.dynamodb.conditions import Attr
import librosa

# AWS 配置
s3    = boto3.client("s3",    region_name="us-east-1")
ddb   = boto3.resource("dynamodb", region_name="us-east-1")
sns   = boto3.client("sns",   region_name="us-east-1")
TABLE = "bird-recognition-files"  # 更新为你的 DynamoDB 表名
SNS_TOPIC = "arn:aws:sns:us-east-1:229834810247:bird-recognition-notification"  # 更新为你的 SNS Topic ARN

# 模型文件路径
MODEL_PATH = "BirdNET-Analyzer/BirdNET-Analyzer/BirdNET-Analyzer-model-V2.4/V2.4/BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite"
LABELS_PATH = "BirdNET-Analyzer/BirdNET-Analyzer/BirdNET-Analyzer-model-V2.4/V2.4/BirdNET_GLOBAL_6K_V2.4_Labels.txt"
BUCKET_NAME = "bird-recognition-files"

def download_model_files():
    """从 S3 下载模型文件到 Lambda 临时目录"""
    local_model_path = "/tmp/model.tflite"
    local_labels_path = "/tmp/labels.txt"
    
    s3.download_file(BUCKET_NAME, MODEL_PATH, local_model_path)
    s3.download_file(BUCKET_NAME, LABELS_PATH, local_labels_path)
    
    return local_model_path, local_labels_path

def audio_prediction(audio_path, min_conf=0.25):
    print(f"[DEBUG] Enter audio_prediction: {audio_path}")
    import os
    from pydub import AudioSegment
    import librosa
    from birdnetlib.analyzer import Analyzer
    from birdnetlib import Recording
    try:
        print(f"[DEBUG] file exists: {os.path.exists(audio_path)}")
        if os.path.exists(audio_path):
            print(f"[DEBUG] file size: {os.path.getsize(audio_path)} bytes")
        audio = AudioSegment.from_file(audio_path)
        print(f"[DEBUG] Audio duration: {audio.duration_seconds}s, channels: {audio.channels}, frame_rate: {audio.frame_rate}")
        # 转码为 16bit PCM 单声道 44100Hz
        pcm_path = audio_path + '_pcm.wav'
        audio = audio.set_channels(1).set_frame_rate(44100).set_sample_width(2)
        audio.export(pcm_path, format='wav')
        print(f"[DEBUG] Exported PCM wav: {pcm_path}, size: {os.path.getsize(pcm_path)} bytes")
        # librosa 兼容性测试
        try:
            y, sr = librosa.load(pcm_path, sr=None, mono=True)
            print(f"[DEBUG] librosa loaded audio: shape={y.shape}, sr={sr}")
        except Exception as e:
            print(f"[ERROR] librosa.load error: {e}")
            import traceback; traceback.print_exc()
            raise
        # BirdNET 只用转码后的 PCM wav
        try:
            model_path, labels_path = download_model_files()
            analyzer = Analyzer(
                classifier_model_path=model_path,
                classifier_labels_path=labels_path
            )
            recording = Recording(analyzer, pcm_path, min_conf=min_conf)
            recording.analyze()
            detections = []
            for d in recording.detections:
                detection = {
                    "M": {
                        "name": {"S": d["common_name"]},
                        "confidence": {"N": str(d["confidence"])}
                    }
                }
                detections.append(detection)
            print(f"[DEBUG] Return detections: {detections}")
            return detections
        except Exception as e:
            print(f"[ERROR] BirdNET/Recording error: {e}")
            import traceback; traceback.print_exc()
            raise
    except Exception as e:
        print(f"[ERROR] audio_prediction error: {e}")
        import traceback; traceback.print_exc()
        raise

def write_to_dynamodb(file_key, detections, timestamp):
    """写入识别结果到 DynamoDB"""
    try:
        table = ddb.Table(TABLE)
        # 生成结果文件路径
        result_file = f"results/{os.path.basename(file_key).split('.')[0]}_detected.wav"
        thumbnail_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/thumbnails/{os.path.basename(file_key).split('.')[0]}_detected.jpg"
        
        # 格式化检测结果 - 确保正确的 DynamoDB 格式
        formatted_detections = []
        for d in detections:
            formatted_detections.append({
                "name": d["M"]["name"]["S"],
                "confidence": float(d["M"]["confidence"]["N"])
            })
        
        item = {
            "fileKey": file_key,
            "detections": formatted_detections,
            "id": str(uuid.uuid4()),
            "originalFile": f"/tmp/{os.path.basename(file_key)}",
            "resultFile": f"s3://{BUCKET_NAME}/{result_file}",
            "thumbnailUrl": thumbnail_url,
            "timestamp": timestamp,
            "type": "audio",
            "userId": "anonymous"
        }
        
        # 转换浮点数为 Decimal
        item = float_to_decimal(item)
        
        print(f"[DEBUG] Writing to DynamoDB: {item}")
        try:
            response = table.put_item(Item=item)
            print(f"[DEBUG] DynamoDB response: {response}")
            print("[DEBUG] Successfully wrote to DynamoDB")
            return item
        except Exception as e:
            print(f"[ERROR] DynamoDB put_item error: {e}")
            print(f"[ERROR] Table name: {TABLE}")
            print(f"[ERROR] Item: {item}")
            raise
    except Exception as e:
        print(f"[ERROR] Failed to write to DynamoDB: {e}")
        raise

def float_to_decimal(obj):
    """将浮点数转换为 Decimal 类型"""
    if isinstance(obj, list):
        return [float_to_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj

def send_sns_notification(file_key, detections, timestamp):
    """发送 SNS 通知"""
    try:
        # 生成结果文件路径
        result_file = f"results/{os.path.basename(file_key).split('.')[0]}_detected.wav"
        thumbnail_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/thumbnails/{os.path.basename(file_key).split('.')[0]}_detected.jpg"
        
        # 格式化检测结果 - 转换为普通 Python 字典
        formatted_detections = []
        for d in detections:
            formatted_detections.append({
                "name": d["M"]["name"]["S"],
                "confidence": float(d["M"]["confidence"]["N"])
            })
            
        message = {
            "fileKey": file_key,
            "detections": formatted_detections,
            "id": str(uuid.uuid4()),
            "originalFile": f"/tmp/{os.path.basename(file_key)}",
            "resultFile": f"s3://{BUCKET_NAME}/{result_file}",
            "thumbnailUrl": thumbnail_url,
            "timestamp": timestamp,
            "type": "audio",
            "userId": "anonymous"
        }
        print(f"[DEBUG] Sending SNS notification: {message}")
        try:
            # 检查 SNS Topic 是否存在
            sns.get_topic_attributes(TopicArn=SNS_TOPIC)
            response = sns.publish(
                TopicArn=SNS_TOPIC,
                Message=json.dumps(message, default=str),  # 使用 default=str 处理 Decimal
                MessageAttributes={
                    "type": {
                        "DataType": "String",
                        "StringValue": "audio"
                    }
                }
            )
            print(f"[DEBUG] SNS notification sent: {response}")
            return response
        except sns.exceptions.NotFoundException:
            print(f"[WARN] SNS Topic {SNS_TOPIC} does not exist. Skipping notification.")
            return None
        except Exception as e:
            print(f"[ERROR] SNS publish error: {e}")
            raise
    except Exception as e:
        print(f"[ERROR] Failed to send SNS notification: {e}")
        raise

def lambda_handler(event, context):
    try:
        print("[DEBUG] Lambda event:", event)
        # 解析 body
        body = event.get("body", "")
        if event.get("isBase64Encoded"):
            import base64
            body = base64.b64decode(body).decode()
        data = json.loads(body)
        s3_key = data.get("audio_url") or data.get("image_url") or data.get("video_url") or data.get("s3Key")
        if s3_key.startswith("s3://"):
            s3_key = s3_key.replace("s3://bird-recognition-files/", "")
            s3_key = s3_key.replace("s3://", "")
        local = f"/tmp/{os.path.basename(s3_key)}"
        print(f"[DEBUG] Try to download S3 file: {s3_key} to {local}")
        try:
            s3.download_file(BUCKET_NAME, s3_key, local)
            print(f"[DEBUG] Downloaded {s3_key} to {local}")
        except Exception as e:
            print(f"[ERROR] S3 download error: {e}")
            import traceback; traceback.print_exc()
            return {
                "statusCode": 404,
                "body": json.dumps({"error": f"S3 file not found: {str(e)}"})
            }
        try:
            print(f"[DEBUG] Call audio_prediction for {local}")
            detections = audio_prediction(local)
            print(f"[DEBUG] Lambda detections: {detections}")
            
            # 格式化检测结果 - 转换为普通 Python 字典用于 API 响应
            formatted_detections = [
                {
                    "name": d["M"]["name"]["S"],
                    "confidence": float(d["M"]["confidence"]["N"])
                } for d in detections
            ]
            
            timestamp = datetime.utcnow().isoformat() + "Z"
            
            # 写入 DynamoDB - 使用原始的 DynamoDB 格式
            try:
                db_item = write_to_dynamodb(s3_key, detections, timestamp)
                print("[DEBUG] Successfully wrote to DynamoDB")
            except Exception as e:
                print(f"[ERROR] DynamoDB write error: {e}")
                # 继续执行，不中断流程
            
            # 发送 SNS 通知 - 使用普通 Python 字典
            try:
                sns_response = send_sns_notification(s3_key, detections, timestamp)
                print("[DEBUG] Successfully sent SNS notification")
            except Exception as e:
                print(f"[ERROR] SNS notification error: {e}")
                # 继续执行，不中断流程
            
            result = {
                "detections": formatted_detections,
                "file": s3_key,
                "timestamp": timestamp
            }
            print(f"[DEBUG] Lambda return: {result}")
            return {
                "statusCode": 200,
                "body": json.dumps(result, default=str)  # 使用 default=str 处理 Decimal
            }
        except Exception as e:
            print(f"[ERROR] Lambda handler error: {e}")
            import traceback; traceback.print_exc()
            return {
                "statusCode": 500,
                "body": json.dumps({"error": f"Lambda handler error: {str(e)}"})
            }
    except Exception as e:
        print(f"[ERROR] Lambda outer error: {e}")
        import traceback; traceback.print_exc()
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Lambda outer error: {str(e)}"})
        }

# alias for Lambda's runtime
handler = lambda_handler

# ─────────────────────────────────────────────────────────────
# Local test harness:
if __name__ == "__main__":
    result = audio_prediction("crickets_-_kiwi_and_ruru_birds_SV2.wav", min_conf=0.1)
    print("Local test result:", Counter(result))