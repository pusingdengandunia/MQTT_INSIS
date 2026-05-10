import React from 'react';

const StatusLog = ({ logs }) => {
  return (
    <div>
      <div className="logs-header">
        Live Activity Log
      </div>
      
      <div className="table-container">
        <table className="logs-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Topic</th>
              <th>Payload</th>
              <th>QoS</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan="4" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
                  Menunggu pesan masuk...
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.id}>
                  <td>{log.time}</td>
                  <td>
                    <span className="topic-badge">{log.topic}</span>
                  </td>
                  <td className="payload-cell" title={log.payload}>
                    {log.payload}
                  </td>
                  <td>{log.qos}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StatusLog;
