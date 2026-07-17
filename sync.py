import json
import requests
from kafka import KafkaConsumer


KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
KAFKA_TOPIC = 'auditbeat'
ES_URL = 'http://localhost:9200/auditbeat-6.5.4/_doc'
ES_AUTH = ('admin', 'admin')

print("[*] Запуск скрипта переливки логов из Kafka в Elasticsearch...")

try:
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest', 
        enable_auto_commit=True,
        group_id='siem-sink-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8', errors='ignore'))
    )
    print("[+] Успешно подключились к Kafka. Ожидаем события...")
except Exception as e:
    print(f"[-] Ошибка подключения к Kafka: {e}")
    exit(1)

for message in consumer:
    log_data = message.value
    try:
        response = requests.post(
            ES_URL,
            json=log_data,
            auth=ES_AUTH,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code in [200, 201]:
            print(f"[+] Лог отправлен! Offset: {message.offset}")
        else:
            print(f"[-] Ошибка ES ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"[-] Ошибка отправки запроса: {e}")
