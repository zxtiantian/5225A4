import json
import boto3
import decimal

TABLE_NAME = "bird-recognition-files"
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)
s3 = boto3.client("s3")

def decimal_to_float(obj):
    if isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj

def parse_detections(detections):
    result = []
    for d in detections:
        # Compatible with DynamoDB native format
        if isinstance(d, dict) and "M" in d:
            m = d["M"]
            name = m.get("name", {}).get("S")
            confidence = float(m.get("confidence", {}).get("N", 0))
            trackId = m.get("trackId", {}).get("N") if "trackId" in m else None
            entry = {"name": name, "confidence": confidence}
            if trackId is not None:
                try:
                    entry["trackId"] = int(trackId)
                except Exception:
                    pass
            result.append(entry)
        # Compatible with Python dict format
        elif isinstance(d, dict) and "name" in d and "confidence" in d:
            entry = {
                "name": d["name"],
                "confidence": float(d["confidence"])
            }
            if "trackId" in d:
                try:
                    entry["trackId"] = int(d["trackId"])
                except Exception:
                    pass
            result.append(entry)
    return result

def search_by_tags(event):
    print('search_by_tags event:', event)
    method = event.get("httpMethod") or (event.get("requestContext", {}).get("http", {}).get("method"))
    if method == "POST":
        body = json.loads(event["body"])
        tags = body.get("tags", {})
    else:
        params = event.get("queryStringParameters") or {}
        tags = {}
        for k, v in params.items():
            if k.startswith("tag") and "count" in k:
                tag = params.get(k.replace("count", ""))
                tags[tag] = int(v)
    print('tags:', tags)
    if not tags:
        return {"results": []}
    resp = table.scan()
    results = []
    for item in resp.get("Items", []):
        raw_detections = item.get("detections", [])
        detections = parse_detections(raw_detections)
        tag_count = {}
        for d in detections:
            if d["name"]:
                tag_name = d["name"].strip().lower()
                tag_count[tag_name] = tag_count.get(tag_name, 0) + 1
        if all(tag.lower() in tag_count and tag_count[tag.lower()] >= count for tag, count in tags.items()):
            item_type = item.get("type")
            url = None
            if item_type == "image":
                url = item.get("thumbnailUrl") or item.get("resultFile")
            elif item_type == "video":
                url = item.get("resultFile")
            if url:
                results.append({
                    "url": url,
                    "detections": detections,
                    "type": item_type or "image"
                })
    print('search_by_tags results:', results)
    return {"results": results}

def search_by_species(event):
    print('search_by_species event:', event)
    try:
        method = event.get("httpMethod") or (event.get("requestContext", {}).get("http", {}).get("method"))
        print('method:', method)
        if method == "POST":
            body = json.loads(event["body"])
            print('body:', body)
            species = body.get("species", [])
            if isinstance(species, str):
                species = [species]
        else:
            params = event.get("queryStringParameters") or {}
            print('params:', params)
            species = params.get("species", "")
            if species:
                species = species.split(",")
            else:
                species = []
        # Remove spaces and lowercase
        species = [s.strip().lower() for s in species if s.strip()]
        print('species to match:', species)
        if not species:
            return {"results": []}
        resp = table.scan()
        results = []
        for item in resp.get("Items", []):
            print('item:', item)
            raw_detections = item.get("detections", [])
            detections = parse_detections(raw_detections)
            print('detections:', detections)
            detected_species = set((d["name"] or "").strip().lower() for d in detections if d["name"])
            print('detected_species:', detected_species)
            if any(tag in detected_species for tag in species):
                url = item.get("thumbnailUrl") or item.get("resultFile")
                item_type = item.get("type") or "image"
                if url:
                    results.append({
                        "url": url,
                        "detections": detections,
                        "type": item_type
                    })
        print('search_by_species results:', results)
        return {"results": results}
    except Exception as e:
        print('Exception in search_by_species:', str(e))
        return {"error": str(e)}

def full_image_by_thumbnail(event):
    params = event.get('queryStringParameters') or {}
    thumb_url = params.get('thumbnail')
    if not thumb_url:
        return {"error": "No thumbnail param"}
    # Unified processing
    thumb_url_norm = thumb_url.strip().lower()
    resp = table.scan()
    for item in resp.get("Items", []):
        item_thumb = (item.get("thumbnailUrl") or "").strip().lower()
        if item_thumb == thumb_url_norm:
            return {"fullImageUrl": item.get("resultFile")}
    return {"error": "Not found"}

def bulk_tag(event):
    print('bulk_tag event:', event)
    body = json.loads(event["body"])
    urls = body["url"]
    operation = body["operation"]  # 1=add, 0=remove
    tags = {}
    for t in body["tags"]:
        name, count = t.split(",")
        tags[name] = int(count)
    for url in urls:
        resp = table.scan()
        for item in resp.get("Items", []):
            if item.get("thumbnailUrl") == url or item.get("resultFile") == url:
                raw_detections = item.get("detections", [])
                detections = parse_detections(raw_detections)
                if operation == 1:
                    for name, count in tags.items():
                        for _ in range(count):
                            detections.append({"name": name, "confidence": 1.0})
                else:
                    detections = [d for d in detections if d["name"] not in tags]
                # Reverse conversion to DynamoDB native format
                item["detections"] = [
                    {"M": {
                        "name": {"S": d["name"]},
                        "confidence": {"N": str(d.get("confidence", 1.0))}
                    }} for d in detections
                ]
                table.put_item(Item=item)
    return {"status": "ok"}


