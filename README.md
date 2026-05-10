# MQTT INSIS Project

This project demonstrates advanced MQTTv5 features using Python (`paho-mqtt`) and includes a real-time React-based monitoring dashboard. It was developed to simulate and visualize sensor data, system events, and remote procedure calls using the MQTT protocol.

## Features Demonstrated (MQTTv5)

The project implements the following key features of the MQTTv5 specification:
1. **QoS (Quality of Service) 1 & 2**: Ensuring message delivery for critical data like alarms.
2. **Topic Wildcards (`+` and `#`)**: Flexible subscription patterns for data logging.
3. **Topic Alias**: Optimizing bandwidth by replacing long topic strings with integer aliases.
4. **User Properties**: Attaching custom metadata (e.g., `severity`, `region`) to publish messages.
5. **Retain**: Storing the last known good value (like temperature) on the broker for new subscribers.
6. **Message Expiry Interval**: Setting a time-to-live for messages so outdated data is discarded.
7. **Last Will and Testament (LWT)**: Notifying the system when a client (like the alarm system) disconnects unexpectedly.
8. **Request-Response (RPC)**: Implementing two-way communication over MQTT using `ResponseTopic` and `CorrelationData`.
9. **Shared Subscriptions (`$share/group/topic`)**: Load balancing incoming messages across multiple worker instances.
10. **Flow Control**: Managing concurrent message limits using the `ReceiveMaximum` property to prevent overwhelming the subscriber.

## Project Structure

- `pub.py`: Contains multiple MQTT Publisher scripts simulating different scenarios:
  - **Sensor Suhu**: Publishes temperature data (Retain, Expiry, QoS 1).
  - **Sistem Alarm**: Publishes critical alarms and manages LWT (User Properties, QoS 2, LWT).
  - **RPC Client**: Sends requests and expects responses (Topic Alias, Request-Response).
- `subs.py`: Contains MQTT Subscriber scripts handling incoming data:
  - **Data Logger**: Listens to multiple topics using Wildcards and Shared Subscriptions.
  - **RPC Server & Manager**: Handles incoming RPC requests, sends responses, and implements Flow Control.
- `mqtt-dashboard/`: A Vite + React web application that visualizes the MQTT data, including gauge charts for temperature and logs for system events.

## Prerequisites

- **Python 3.7+**
- **Node.js** (v16+ recommended) and **npm**
- An MQTTv5 compatible broker. The code is currently configured to use the public EMQX broker (`broker.emqx.io`).

## Installation & Setup

### 1. Python Environment

Install the required Python library:
```bash
pip install paho-mqtt
```

### 2. Dashboard

Navigate to the dashboard directory and install the necessary Node modules:
```bash
cd mqtt-dashboard
npm install
```

## Running the Application

To see the full system in action, you should run the components in multiple terminal windows.

### 1. Start the Dashboard
In the first terminal, navigate to the `mqtt-dashboard` directory and start the Vite development server:
```bash
cd mqtt-dashboard
npm run dev
```
Open your browser to the URL provided in the terminal (usually `http://localhost:5173`) to view the real-time dashboard.

### 2. Start the Subscribers
In a second terminal, run `subs.py` to start listening for incoming data and handling RPC requests:
```bash
python subs.py
```

### 3. Start the Publishers
In a third terminal, run `pub.py` to start sending simulated sensor data, alarms, and RPC requests:
```bash
python pub.py
```
*Note: `pub.py` is designed to run its simulation and then exit. You can re-run it to send another batch of data to the dashboard and subscribers.*

## Topics Reference

The system uses the following topic structure (namespaced under `afrizan/insis/`):
- `afrizan/insis/sensor/suhu/ruang1`: Real-time temperature sensor data.
- `afrizan/insis/alarm/kebakaran`: Critical alarm notifications.
- `afrizan/insis/status/lwt`: Offline status notifications (Last Will).
- `afrizan/insis/rpc/request`: Topic for incoming RPC requests.
- `afrizan/insis/rpc/response/client123`: Topic for RPC server responses.
