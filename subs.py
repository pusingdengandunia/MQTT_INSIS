# # subscribers.py
# import time
# import random
# import paho.mqtt.client as mqtt
# from paho.mqtt.properties import Properties
# from paho.mqtt.packettypes import PacketTypes

# BROKER = "broker.emqx.io" # Ganti dengan broker Anda, misal: broker.emqx.io
# PORT = 1883

# # SUBSCRIBER 1: Data Logger (Wildcard & Shared Subs)
# def on_message_sub1(client, userdata, msg):
#     print(f"[Sub 1 - Logger] Menerima di {msg.topic}: {msg.payload.decode()} | QoS: {msg.qos}")

# client_suffix = random.randint(1000, 9999)
# sub1 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"logger_{client_suffix}", protocol=mqtt.MQTTv5)
# sub1.on_message = on_message_sub1
# sub1.connect(BROKER, PORT)

# # Fitur 2: Wildcard (# dan +)
# # Fitur 9: Shared Subscription ($share/group_name/topic)
# sub1.subscribe("$share/logger_group/afrizan/insis/sensor/#", qos=1) 
# #sub1.subscribe("afrizan/insis/sensor/#", qos=1) # Normal Subscription pesan Retained
# sub1.subscribe("afrizan/insis/alarm/+", qos=2)
# sub1.loop_start()

# # SUBSCRIBER 2: RPC Server & Manager (Flow Control & Req-Res)
# def on_message_sub2(client, userdata, msg):
#     print(f"[Sub 2 - RPC Server] Menerima di {msg.topic}: {msg.payload.decode()}")
    
#     # Membaca User Properties (Fitur 4) jika ada
#     if hasattr(msg, 'properties') and msg.properties is not None:
#         if hasattr(msg.properties, 'UserProperty'):
#             print(f"   -> User Properties: {msg.properties.UserProperty}")
        
#         # Fitur 8: Request-Response (Merespons ke ResponseTopic)
#         if hasattr(msg.properties, 'ResponseTopic') and msg.properties.ResponseTopic:
#             resp_topic = msg.properties.ResponseTopic
#             corr_data = msg.properties.CorrelationData
            
#             # Siapkan properti balasan
#             reply_props = Properties(PacketTypes.PUBLISH)
#             reply_props.CorrelationData = corr_data
            
#             reply_msg = f"Data diterima, status OK."
#             client.publish(resp_topic, reply_msg, qos=1, properties=reply_props)
#             print(f"   -> Merespons ke {resp_topic} dengan Correlation Data: {corr_data}")

# sub2 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"rpc_server_{client_suffix}", protocol=mqtt.MQTTv5)
# sub2.on_message = on_message_sub2

# # Fitur 10: Flow Control (Membatasi pesan QoS 1/2 yang belum di-acknowledge)
# connect_props = Properties(PacketTypes.CONNECT)
# connect_props.ReceiveMaximum = 5 # Hanya menerima max 5 pesan concurrent

# sub2.connect(BROKER, PORT, clean_start=True, properties=connect_props)
# sub2.subscribe("afrizan/insis/rpc/request", qos=1)
# sub2.subscribe("afrizan/insis/status/lwt", qos=1) # Subscribe ke LWT
# sub2.loop_start()

# print("Subscribers berjalan... Tekan Ctrl+C untuk berhenti.")
# try:
#     while True:
#         time.sleep(1)
# except KeyboardInterrupt:
#     sub1.loop_stop()
#     sub2.loop_stop()



# pub.py
import time
import uuid
import random
import signal
import sys

import paho.mqtt.client as mqtt
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

BROKER = "broker.emqx.io"
PORT = 1883

running = True


def stop_program(sig, frame):
    global running
    running = False
    print("\n[SYSTEM] Shutdown publisher...")


signal.signal(signal.SIGINT, stop_program)


# =========================================================
# PUBLISHER 1 - SENSOR SUHU
# QoS 1 + Retain + Message Expiry
# =========================================================

pub1 = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=f"sensor_suhu_{random.randint(1000,9999)}",
    protocol=mqtt.MQTTv5
)

pub1.connect(BROKER, PORT)

props_pub1 = Properties(PacketTypes.PUBLISH)
props_pub1.MessageExpiryInterval = 60


# =========================================================
# PUBLISHER 2 - ALARM SYSTEM
# LWT + User Properties + QoS 2
# =========================================================

pub2 = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=f"alarm_system_{random.randint(1000,9999)}",
    protocol=mqtt.MQTTv5
)

# Last Will Testament
lwt_props = Properties(PacketTypes.WILLMESSAGE)
lwt_props.MessageExpiryInterval = 10

pub2.will_set(
    "afrizan/insis/status/lwt",
    payload="ALARM SYSTEM OFFLINE",
    qos=1,
    retain=True,
    properties=lwt_props
)

pub2.connect(BROKER, PORT)

props_pub2 = Properties(PacketTypes.PUBLISH)

# User Properties
props_pub2.UserProperty = [
    ("severity", "CRITICAL"),
    ("region", "Gedung A")
]


# =========================================================
# PUBLISHER 3 - RPC CLIENT
# Topic Alias + Request Response
# =========================================================

rpc_client_id = f"rpc_client_{random.randint(1000,9999)}"

pub3 = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=rpc_client_id,
    protocol=mqtt.MQTTv5
)

response_topic = f"afrizan/insis/rpc/response/{rpc_client_id}"


def on_rpc_response(client, userdata, msg):
    print(f"\n[RPC RESPONSE]")
    print(f"Topic : {msg.topic}")
    print(f"Payload : {msg.payload.decode()}")

    if hasattr(msg, 'properties') and msg.properties:
        if hasattr(msg.properties, 'CorrelationData'):
            corr_id = msg.properties.CorrelationData.decode()
            print(f"Correlation ID : {corr_id}")


pub3.on_message = on_rpc_response

pub3.connect(BROKER, PORT)

pub3.subscribe(response_topic, qos=1)
pub3.loop_start()

rpc_props = Properties(PacketTypes.PUBLISH)

# Topic Alias
rpc_props.TopicAlias = 1

# Dynamic Response Topic
rpc_props.ResponseTopic = response_topic


# =========================================================
# MAIN LOOP
# =========================================================

print("Publisher berjalan...")
print("Tekan CTRL+C untuk simulasi device offline (LWT)\n")

base_temp = 24.0
counter = 0

try:
    while running:

        # =================================================
        # SENSOR SUHU
        # =================================================
        temp = base_temp + random.uniform(-2.5, 5.0)

        pub1.publish(
            "afrizan/insis/sensor/suhu/ruang1",
            f"{temp:.1f} Celcius",
            qos=1,
            retain=True,
            properties=props_pub1
        )

        print(f"[PUB SENSOR] {temp:.1f} Celcius")

        # =================================================
        # ALARM SYSTEM
        # =================================================
        if counter % 5 == 0:

            alarm_msg = random.choice([
                "Asap terdeteksi!",
                "Suhu tinggi terdeteksi!",
                "Api terdeteksi di ruang server!"
            ])

            pub2.publish(
                "afrizan/insis/alarm/kebakaran",
                alarm_msg,
                qos=2,
                properties=props_pub2
            )

            print(f"[PUB ALARM] {alarm_msg}")

        # =================================================
        # RPC REQUEST
        # =================================================
        if counter % 7 == 0:

            request_id = str(uuid.uuid4())

            rpc_props.CorrelationData = request_id.encode()

            request_message = random.choice([
                "Minta status server",
                "Minta penggunaan CPU",
                "Minta status database"
            ])

            # Publish pertama
            pub3.publish(
                "afrizan/insis/rpc/request",
                request_message,
                qos=1,
                properties=rpc_props
            )

            print(f"[PUB RPC] Request: {request_message}")
            print(f"Correlation ID: {request_id}")

        counter += 1
        time.sleep(3)

except Exception as e:
    print(f"Error: {e}")

finally:
    print("\nDisconnecting publisher...")

    pub1.disconnect()

    # Jangan disconnect pub2 agar LWT terkirim jika app mati paksa
    if running:
        pub2.disconnect()

    pub3.loop_stop()
    pub3.disconnect()

    sys.exit(0)