# subscribers.py
import time
import random
import paho.mqtt.client as mqtt
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

BROKER = "broker.emqx.io" # Ganti dengan broker Anda, misal: broker.emqx.io
PORT = 1883

# ==========================================
# SUBSCRIBER 1: Data Logger (Wildcard & Shared Subs)
# ==========================================
def on_message_sub1(client, userdata, msg):
    print(f"[Sub 1 - Logger] Menerima di {msg.topic}: {msg.payload.decode()} | QoS: {msg.qos}")

client_suffix = random.randint(1000, 9999)
sub1 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"logger_{client_suffix}", protocol=mqtt.MQTTv5)
sub1.on_message = on_message_sub1
sub1.connect(BROKER, PORT)

# Fitur 2: Wildcard (# dan +)
# Fitur 9: Shared Subscription ($share/group_name/topic)
sub1.subscribe("$share/logger_group/afrizan/insis/sensor/#", qos=1) 
sub1.subscribe("afrizan/insis/alarm/+", qos=2)
sub1.loop_start()

# ==========================================
# SUBSCRIBER 2: RPC Server & Manager (Flow Control & Req-Res)
# ==========================================
def on_message_sub2(client, userdata, msg):
    print(f"[Sub 2 - RPC Server] Menerima di {msg.topic}: {msg.payload.decode()}")
    
    # Membaca User Properties (Fitur 4) jika ada
    if hasattr(msg, 'properties') and msg.properties is not None:
        if hasattr(msg.properties, 'UserProperty'):
            print(f"   -> User Properties: {msg.properties.UserProperty}")
        
        # Fitur 8: Request-Response (Merespons ke ResponseTopic)
        if hasattr(msg.properties, 'ResponseTopic') and msg.properties.ResponseTopic:
            resp_topic = msg.properties.ResponseTopic
            corr_data = msg.properties.CorrelationData
            
            # Siapkan properti balasan
            reply_props = Properties(PacketTypes.PUBLISH)
            reply_props.CorrelationData = corr_data
            
            reply_msg = f"Data diterima, status OK."
            client.publish(resp_topic, reply_msg, qos=1, properties=reply_props)
            print(f"   -> Merespons ke {resp_topic} dengan Correlation Data: {corr_data}")

sub2 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"rpc_server_{client_suffix}", protocol=mqtt.MQTTv5)
sub2.on_message = on_message_sub2

# Fitur 10: Flow Control (Membatasi pesan QoS 1/2 yang belum di-acknowledge)
connect_props = Properties(PacketTypes.CONNECT)
connect_props.ReceiveMaximum = 5 # Hanya menerima max 5 pesan concurrent

sub2.connect(BROKER, PORT, clean_start=True, properties=connect_props)
sub2.subscribe("afrizan/insis/rpc/request", qos=1)
sub2.subscribe("afrizan/insis/status/lwt", qos=1) # Subscribe ke LWT
sub2.loop_start()

print("Subscribers berjalan... Tekan Ctrl+C untuk berhenti.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    sub1.loop_stop()
    sub2.loop_stop()