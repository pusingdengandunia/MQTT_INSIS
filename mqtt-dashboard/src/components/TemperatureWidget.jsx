import React from 'react';

const TemperatureWidget = ({ value }) => {
  const displayValue = () => {
    if (value === '--') return '--';
    let num = parseFloat(value);
    if (isNaN(num)) {
      const match = value.match(/[-+]?[0-9]*\.?[0-9]+/);
      if (match) num = parseFloat(match[0]);
    }
    return !isNaN(num) ? num.toFixed(1) : value;
  };

  const parsedVal = parseFloat(displayValue());
  const percent = !isNaN(parsedVal) ? Math.max(0, Math.min(100, (parsedVal / 50) * 100)) : 0;

  let tempStatus = 'Normal';
  let tempColorClass = 'temp-normal';
  if (!isNaN(parsedVal)) {
    if (parsedVal >= 27) {
      tempStatus = 'Panas';
      tempColorClass = 'temp-hot';
    } else if (parsedVal <= 22) {
      tempStatus = 'Dingin';
      tempColorClass = 'temp-cold';
    }
  }

  return (
    <div className="widget-card">
      <div className="widget-header">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
        </svg>
        Sensor Suhu
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
            Suhu Saat Ini:
          </div>
          <div className={`temp-value ${tempColorClass}`}>
            {displayValue()}
            {displayValue() !== '--' && !isNaN(parsedVal) && (
              <span className="temp-unit">°C</span>
            )}
          </div>
        </div>

        {displayValue() !== '--' && !isNaN(parsedVal) && (
          <div className={`temp-status-badge ${tempColorClass}`}>
            {tempStatus}
          </div>
        )}
      </div>

      <div className="temp-gauge-container">
        <div className="temp-gauge-track">
          <div
            className="temp-gauge-fill"
            style={{ width: `${percent}%` }}
          />
        </div>
        <div className="temp-gauge-labels">
          <span>Skala Bawah (0°C)</span>
          <span>Skala Atas (50°C)</span>
        </div>
      </div>
    </div>
  );
};

export default TemperatureWidget;
