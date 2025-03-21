from kafka import KafkaProducer
import json
import requests
# Inisialisasi KafkaProducer
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',  
    # karna kafka cluster hanya menerima byte maka untuk mengubah data menjadi byte maka digunakan code dibawah
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
r = requests.get('https://api.github.com/events')
json_data = r.json()
# Kirim pesan ke topic
producer.send('new-topic', value=json_data)
# Wajib flush supaya dikirim
producer.flush()
print("Pesan berhasil dikirim!")

# Tutup koneksi (opsional)
producer.close()
