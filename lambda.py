import os
# 1) silence TF logs before anything else
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
# 2) redirect matplotlib cache
os.environ["MPLCONFIGDIR"] = "/tmp/.matplotlib"

import boto3
import time
from collections import Counter
from boto3.dynamodb.conditions import Attr

s3    = boto3.client("s3",    region_name="us-east-1")
ddb   = boto3.resource("dynamodb", region_name="us-east-1")
TABLE = "BirdDetectionResults"


def audio_prediction(audio_path, min_conf=0.25):
    from pydub import AudioSegment
    from birdnetlib.analyzer import Analyzer
    from birdnetlib import Recording

    analyzer = Analyzer(
        classifier_model_path="model/BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite",
        classifier_labels_path="model/BirdNET_GLOBAL_6K_V2.4_Labels.txt"
    )
    recording = Recording(analyzer, audio_path, min_conf=min_conf)
    recording.analyze()
    return [d["common_name"] for d in recording.detections]


def lambda_handler(event, context):
    for rec in event["Records"]:
        bucket = rec["s3"]["bucket"]["name"]
        key    = rec["s3"]["object"]["key"]
        local  = f"/tmp/{os.path.basename(key)}"
        s3.download_file(bucket, key, local)

        labels = []
        if key.startswith("audio/"):
            labels = audio_prediction(local)

        file_url = f"https://{bucket}.s3.us-east-1.amazonaws.com/{key}"
        counter = Counter(labels)
        ddb.Table(TABLE).put_item(
            Item={
                "file_id": file_url,
                "tags": counter
            }
        )
        print(f"Processed {key}: {counter}")

    table = ddb.Table(TABLE)
    table.update_item(
    Key={"file_id": file_url},
    UpdateExpression="SET tags = :t, last_updated = :u",
    ExpressionAttributeValues={
        ":t": dict(counter),
        ":u": int(time.time())
    },
    ConditionExpression=Attr("file_id").exists()
    )

    return {"statusCode": 200, "body": "OK"}


# ─────────────────────────────────────────────────────────────
# Local test harness:
if __name__ == "__main__":
    result = audio_prediction("crickets_-_kiwi_and_ruru_birds_SV2.wav", min_conf=0.1)
    print("Local test result:", Counter(result))


# alias for Lambda’s runtime
handler = lambda_handler