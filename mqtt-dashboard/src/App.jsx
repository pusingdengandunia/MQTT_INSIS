import React, { useEffect, useState } from 'react';
import mqtt from 'mqtt';
import TemperatureWidget from './components/TemperatureWidget';
import AlarmWidget from './components/AlarmWidget';
import StatusLog from './components/StatusLog';
import './index.css';

const BROKER_URL = 'wss://broker.emqx.io:8084/mqtt';

function App() {
  const [client, setClient] = useState(null);
  const [connectStatus, setConnectStatus] = useState('Connecting');
  const [temperature, setTemperature] = useState('--');
  const [alarmStatus, setAlarmStatus] = useState('SAFE');
  const [alarmMessage, setAlarmMessage] = useState('');
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const clientId = `mqttjs_` + Math.random().toString(16).substr(2, 8);
    const mqttClient = mqtt.connect(BROKER_URL, {
      clientId,
      clean: true,
      connectTimeout: 4000,
      reconnectPeriod: 1000,
    });

    setClient(mqttClient);

    mqttClient.on('connect', () => {
      setConnectStatus('Connected');
      // Subscribe to topics
      mqttClient.subscribe('afrizan/insis/sensor/suhu/ruang1', { qos: 1 });
      mqttClient.subscribe('afrizan/insis/alarm/kebakaran', { qos: 2 });
      mqttClient.subscribe('afrizan/insis/status/lwt', { qos: 1 });
      mqttClient.subscribe('afrizan/insis/rpc/#', { qos: 1 });
    });

    mqttClient.on('error', (err) => {
      console.error('Connection error: ', err);
      mqttClient.end();
      setConnectStatus('Error');
    });

    mqttClient.on('reconnect', () => {
      setConnectStatus('Reconnecting');
    });

    mqttClient.on('message', (topic, message, packet) => {
      const payload = message.toString();

      const newLog = {
        id: Date.now() + Math.random(),
        time: new Date().toLocaleTimeString(),
        topic,
        payload,
        qos: packet.qos
      };

      setLogs((prev) => [newLog, ...prev].slice(0, 50)); // Keep last 50 logs

      if (topic === 'afrizan/insis/sensor/suhu/ruang1') {
        setTemperature(payload);
      } else if (topic === 'afrizan/insis/alarm/kebakaran') {
        setAlarmStatus('CRITICAL');
        setAlarmMessage(payload);
        // Reset alarm after 10 seconds if no new messages
        setTimeout(() => setAlarmStatus('SAFE'), 10000);
      } else if (topic === 'afrizan/insis/status/lwt') {
        setAlarmStatus('OFFLINE');
        setAlarmMessage(payload);
        setTimeout(() => setAlarmStatus('SAFE'), 10000);
      }
    });

    return () => {
      if (mqttClient) {
        mqttClient.end();
      }
    };
  }, []);

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>MQTT Monitor</h1>
          <div className="status-badge">
            <span className={`status-indicator ${connectStatus.toLowerCase()}`}></span>
            {connectStatus}
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="widgets-grid">
          <TemperatureWidget value={temperature} />
          <AlarmWidget status={alarmStatus} message={alarmMessage} />
        </div>
        <div className="logs-section">
          <StatusLog logs={logs} />
        </div>
      </main>
    </div>
  );
}

export default App;
