import requests
import pandas as pd
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")

def get_brazil_locations(limit=100):
    url = "https://api.openaq.org/v3/locations"
    params = {
        "countries_id": 45,
        "limit": limit,
    }
    headers = {
        "Accept": "application/json",
        "X-API-Key": OPENAQ_API_KEY
    }
    
    print("Buscando estações brasileiras...")
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    results = data.get("results", [])
    print(f"{len(results)} estações encontradas.")
    return results

def parse_locations(results):
    records = []
    for item in results:
        for sensor in item.get("sensors", []):
            records.append({
                "location_id": item.get("id"),
                "location_name": item.get("name"),
                "city": item.get("locality"),
                "country": "BR",
                "parameter": sensor.get("parameter", {}).get("name"),
                "unit": sensor.get("parameter", {}).get("units"),
                "latitude": item.get("coordinates", {}).get("latitude"),
                "longitude": item.get("coordinates", {}).get("longitude"),
                "is_active": item.get("isActive"),
                "last_updated": item.get("datetimeLast", {}).get("utc") if item.get("datetimeLast") else None,
            })
    return pd.DataFrame(records)

def upload_to_s3(df, bucket, date_str):
    s3 = boto3.client("s3", region_name=AWS_REGION)
    
    filename = f"openaq_brazil_{date_str}.parquet"
    local_path = f"openaq_temp_{date_str}.parquet"
    s3_key = f"raw/openaq/{date_str}/{filename}"
    
    df.to_parquet(local_path, index=False)
    s3.upload_file(local_path, bucket, s3_key)
    os.remove(local_path)
    
    print(f"Arquivo enviado para s3://{bucket}/{s3_key}")
    return s3_key

def run():
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    locations = get_brazil_locations(limit=100)
    
    if not locations:
        print("Nenhuma estação encontrada.")
        return
    
    df = parse_locations(locations)
    print(df.head())
    print(f"\nShape: {df.shape}")
    print(f"Parâmetros encontrados: {df['parameter'].unique()}")
    
    s3_key = upload_to_s3(df, S3_BUCKET, date_str)
    print(f"\nIngestão concluída: {s3_key}")

if __name__ == "__main__":
    run()