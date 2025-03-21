import os
import json
import pandas as pd
from kafka import KafkaConsumer
from sqlalchemy import create_engine,text
import pymysql  # Pastikan pymysql sudah terinstal
from dotenv import load_dotenv
from sqlalchemy import text



# Inisialisasi KafkaConsumer
consumer = KafkaConsumer(
    'new-topic',
    bootstrap_servers='kafka:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-python-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))  # Deserialisasi JSON
)

print("Menunggu pesan...")
load_dotenv()
db_user = os.getenv("db_user")
db_password = os.getenv("db_password")
db_host = os.getenv("db_host")
db_name = os.getenv("db_name")
table_name = os.getenv("table_name")

# Buat koneksi ke database
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}:3306/{db_name}")

# Buat tabel jika belum ada (dieksekusi sekali sebelum loop Kafka)
create_table_query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    id VARCHAR(255) PRIMARY KEY,
    type VARCHAR(255),
    public BOOLEAN,
    created_at DATE,
    repo_name VARCHAR(255),
    url TEXT
);
"""

with engine.connect() as connection:
    connection.execute(text(create_table_query))

# Loop untuk membaca pesan dari Kafka
for message in consumer:
    data = message.value  # Kafka mengirim dictionary atau list of dictionaries
    
    # Pastikan data berbentuk list sebelum dimasukkan ke DataFrame
    if isinstance(data, dict):
        data = [data]  # Ubah ke list of dict agar DataFrame bisa dibuat
    
    data = pd.DataFrame(data)

    # Pastikan kolom "created_at" ada sebelum diubah formatnya
    if "created_at" in data.columns:
        data["created_at"] = pd.to_datetime(data["created_at"], errors="coerce").dt.date
    
    # Pastikan kolom "repo" ada sebelum diolah
    if "repo" in data.columns:
        data.dropna(subset=["repo"], inplace=True)
        df_repo = data["repo"].apply(pd.Series)
        
        if "id" in df_repo.columns:
            df_repo.drop(columns=["id"], inplace=True)
        
        df_repo.rename(columns={"name": "repo_name"}, inplace=True)
        data = pd.concat([data.drop(columns=["repo"]), df_repo], axis=1)

    # Hapus kolom yang tidak diperlukan (jika ada)
    data.drop(columns=["org", "actor", "payload"], inplace=True, errors="ignore")

    # Filter hanya kolom yang diperlukan
    required_columns = ["id", "type", "public", "created_at", "repo_name", "url"]
    data = data[[col for col in required_columns if col in data.columns]]

    # Pastikan "id" berbentuk string agar sesuai dengan VARCHAR(255) di MySQL
    if "id" in data.columns:
        data["id"] = data["id"].astype(str)

    # Simpan data ke database
    data.to_sql(table_name, con=engine, if_exists="append", index=False)

    print(f"Data berhasil dimasukkan ke tabel `{table_name}` di database `{db_name}`.")
