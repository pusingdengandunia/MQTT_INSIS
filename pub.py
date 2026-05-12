# publishers.py
import time
import paho.mqtt.client as mqtt
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

BROKER = "broker.emqx.io"

# PUBLISHER 1: Sensor Suhu (Retain, Expiry, QoS 1)
pub1 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="sensor_suhu", protocol=mqtt.MQTTv5)
pub1.connect(BROKER)

props_pub1 = Properties(PacketTypes.PUBLISH)
# Fitur 6: Expiry (Pesan akan dihapus broker jika tidak dikirim ke sub dalam 60 detik)
props_pub1.MessageExpiryInterval = 60

# Fitur 1 & 5: QoS 1 dan Retain (Menyimpan pesan terakhir di broker)
# Simulasi sensor suhu yang berubah-ubah agar gauge di dashboard bergerak
import random
base_temp = 24.0
for i in range(6):
    temp = base_temp + random.uniform(-2.5, 5.0)
    pub1.publish("afrizan/insis/sensor/suhu/ruang1", f"{temp:.1f} Celcius", qos=1, retain=True, properties=props_pub1)
    print(f"[Pub 1] Mengirim data suhu: {temp:.1f} Celcius")
    

# PUBLISHER 2: Sistem Alarm (LWT, User Properties, QoS 2)
pub2 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="alarm_system", protocol=mqtt.MQTTv5)

# Fitur 7: Last Will Testament (LWT)
lwt_props = Properties(PacketTypes.WILLMESSAGE)
lwt_props.MessageExpiryInterval = 5
pub2.will_set("afrizan/insis/status/lwt", payload="ALARM SYSTEM OFFLINE", qos=1, retain=True, properties=lwt_props)

pub2.connect(BROKER)

props_pub2 = Properties(PacketTypes.PUBLISH)
# Fitur 4: User Properties 
props_pub2.UserProperty = [("severity", "CRITICAL"), ("region", "Gedung A")]

#simulasi error pub2 untuk menjalankan fitur 7
pub2._sock.close()

# Fitur 1: QoS 2 (Exactly once delivery)
pub2.publish("afrizan/insis/alarm/kebakaran", "Asap terdeteksi!", qos=2, properties=props_pub2)
print("[Pub 2] Mengirim data alarm (User Properties & LWT diset)")


# PUBLISHER 3: RPC Client (Topic Alias, Request-Response)
def on_rpc_response(client, userdata, msg):
    print(f"[Pub 3 - RPC Response] Balasan dari server: {msg.payload.decode()}")
    if hasattr(msg, 'properties') and msg.properties is not None:
        print(f"   -> Correlation Data: {msg.properties.CorrelationData}")

pub3 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="rpc_client", protocol=mqtt.MQTTv5)
pub3.on_message = on_rpc_response
pub3.connect(BROKER)

# Subscribe ke topic balasan terlebih dahulu
pub3.subscribe("afrizan/insis/rpc/response/client123", qos=1)
pub3.loop_start()

props_pub3 = Properties(PacketTypes.PUBLISH)
# Fitur 3: Topic Alias
props_pub3.TopicAlias = 1 

# Fitur 8: Request-Response
props_pub3.ResponseTopic = "afrizan/insis/rpc/response/client123"
props_pub3.CorrelationData = b"REQ-001"

# Publish pertama: menyertakan string topic DAN alias
pub3.publish("afrizan/insis/rpc/request", "Minta data status server", qos=1, properties=props_pub3)
print("[Pub 3] Mengirim Request pertama (Set Topic Alias = 1)")
time.sleep(2)

# Publish kedua: Topic string kosong, broker/klien tahu alias 1 = "rpc/request"
pub3.publish("", "Minta data status server lagi", qos=1, properties=props_pub3)
print("[Pub 3] Mengirim Request kedua (Hanya menggunakan Topic Alias)")

time.sleep(3) # Tunggu balasan RPC
pub1.disconnect()
pub2.disconnect()
pub3.loop_stop()
pub3.disconnect()