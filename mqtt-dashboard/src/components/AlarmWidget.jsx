import React from 'react';

const AlarmWidget = ({ status, message }) => {
  const isCritical = status === 'CRITICAL';
  const isOffline = status === 'OFFLINE';
  
  let widgetClass = 'widget-card';
  if (isCritical) widgetClass += ' alarm-critical';
  if (isOffline) widgetClass += ' alarm-offline';

  return (
    <div className={widgetClass}>
      <div className="widget-header">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
        </svg>
        Sistem Alarm
      </div>
      
      <div className={`alarm-status-badge ${status.toLowerCase()}`}>
        {status}
      </div>

      <div className="alarm-message">
        {status === 'SAFE' ? 'Semua sistem berjalan normal.' : message}
      </div>
    </div>
  );
};

export default AlarmWidget;
