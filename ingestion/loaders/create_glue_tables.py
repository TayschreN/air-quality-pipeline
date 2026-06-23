import boto3
import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = "us-east-2"
S3_BUCKET = os.getenv("S3_BUCKET")
DATABASE = "air_quality_raw"

def create_glue_database(glue_client):
    try:
        glue_client.create_database(
            DatabaseInput={"Name": DATABASE, "Description": "Raw air quality data"}
        )
        print(f"Database '{DATABASE}' criado.")
    except glue_client.exceptions.AlreadyExistsException:
        print(f"Database '{DATABASE}' já existe.")

def create_openaq_table(glue_client):
    try:
        glue_client.create_table(
            DatabaseName=DATABASE,
            TableInput={
                "Name": "openaq_stations",
                "StorageDescriptor": {
                    "Columns": [
                        {"Name": "location_id", "Type": "bigint"},
                        {"Name": "location_name", "Type": "string"},
                        {"Name": "city", "Type": "string"},
                        {"Name": "country", "Type": "string"},
                        {"Name": "parameter", "Type": "string"},
                        {"Name": "unit", "Type": "string"},
                        {"Name": "latitude", "Type": "double"},
                        {"Name": "longitude", "Type": "double"},
                        {"Name": "is_active", "Type": "boolean"},
                        {"Name": "last_updated", "Type": "string"},
                    ],
                    "Location": f"s3://{S3_BUCKET}/raw/openaq/",
                    "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
                    "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
                    "SerdeInfo": {
                        "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
                    },
                },
                "TableType": "EXTERNAL_TABLE",
                "Parameters": {"classification": "parquet", "has_encrypted_data": "false"},
            },
        )
        print("Tabela 'openaq_stations' criada.")
    except glue_client.exceptions.AlreadyExistsException:
        print("Tabela 'openaq_stations' já existe.")

def create_inmet_table(glue_client):
    try:
        glue_client.create_table(
            DatabaseName=DATABASE,
            TableInput={
                "Name": "inmet_stations",
                "StorageDescriptor": {
                    "Columns": [
                        {"Name": "station_id", "Type": "string"},
                        {"Name": "station_name", "Type": "string"},
                        {"Name": "state", "Type": "string"},
                        {"Name": "latitude", "Type": "string"},
                        {"Name": "longitude", "Type": "string"},
                        {"Name": "altitude", "Type": "string"},
                        {"Name": "station_type", "Type": "string"},
                    ],
                    "Location": f"s3://{S3_BUCKET}/raw/inmet/stations/",
                    "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
                    "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
                    "SerdeInfo": {
                        "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
                    },
                },
                "TableType": "EXTERNAL_TABLE",
                "Parameters": {"classification": "parquet", "has_encrypted_data": "false"},
            },
        )
        print("Tabela 'inmet_stations' criada.")
    except glue_client.exceptions.AlreadyExistsException:
        print("Tabela 'inmet_stations' já existe.")

def run():
    glue = boto3.client("glue", region_name=AWS_REGION)
    create_glue_database(glue)
    create_openaq_table(glue)
    create_inmet_table(glue)
    print("\nGlue Catalog configurado!")

if __name__ == "__main__":
    run()