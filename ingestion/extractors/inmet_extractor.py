import requests
import pandas as pd
import boto3
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

BASE_URL = "https://apitempo.inmet.gov.br"

def get_stations():
    url = f"{BASE_URL}/estacoes/T"
    print("Buscando estações automáticas do INMET...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    stations = response.json()
    print(f"{len(stations)} estações encontradas.")
    return stations

def parse_stations(stations):
    records = []
    for s in stations:
        records.append({
            "station_id": s.get("CD_ESTACAO"),
            "station_name": s.get("DC_NOME"),
            "state": s.get("SG_ESTADO"),
            "latitude": s.get("VL_LATITUDE"),
            "longitude": s.get("VL_LONGITUDE"),
            "altitude": s.get("VL_ALTITUDE"),
            "station_type": "automatica",
        })
    return pd.DataFrame(records)

def get_daily_data(station_id, date_str):
    url = f"{BASE_URL}/estacao/dados/{station_id}/{date_str}/{date_str}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

def get_sample_measurements(stations_df, max_stations=10):
    date_str = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    all_records = []

    sp_stations = stations_df[stations_df["state"] == "SP"].head(max_stations)
    print(f"Buscando medições de {len(sp_stations)} estações de SP para {date_str}...")

    for _, station in sp_stations.iterrows():
        sid = station["station_id"]
        data = get_daily_data(sid, date_str)
        for row in data:
            row["station_id"] = sid
            row["station_name"] = station["station_name"]
            row["state"] = station["state"]
            row["latitude"] = station["latitude"]
            row["longitude"] = station["longitude"]
            all_records.append(row)

    print(f"{len(all_records)} registros coletados.")
    return pd.DataFrame(all_records) if all_records else pd.DataFrame()

def upload_to_s3(df, bucket, prefix, date_str):
    s3 = boto3.client("s3", region_name=AWS_REGION)
    filename = f"inmet_{prefix}_{date_str}.parquet"
    local_path = f"inmet_temp_{prefix}.parquet"
    s3_key = f"raw/inmet/{prefix}/{date_str}/{filename}"

    df.to_parquet(local_path, index=False)
    s3.upload_file(local_path, bucket, s3_key)
    os.remove(local_path)

    print(f"Enviado para s3://{bucket}/{s3_key}")
    return s3_key

def run():
    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    stations = get_stations()
    stations_df = parse_stations(stations)
    print(stations_df.head())
    print(f"Shape estações: {stations_df.shape}")
    upload_to_s3(stations_df, S3_BUCKET, "stations", date_str)

    measurements_df = get_sample_measurements(stations_df)
    if not measurements_df.empty:
        print(measurements_df.head())
        print(f"Shape medições: {measurements_df.shape}")
        upload_to_s3(measurements_df, S3_BUCKET, "measurements", date_str)
    else:
        print("Nenhuma medição retornada.")

    print("\nIngestão INMET concluída!")

if __name__ == "__main__":
    run()