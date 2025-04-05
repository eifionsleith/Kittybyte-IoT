
import React, { useState } from 'react';
import '../../styles/common.css';
import { provisionDevice } from '../../api';
import { useNavigate } from 'react-router-dom';

export default function BluetoothConnect() {
  const [deviceId, setDeviceId] = useState('');
  const navigate = useNavigate();

  const handleConnect = async () => {
    if (!deviceId) return;
    try {
      await provisionDevice(deviceId);
      alert('Device connected and provisioned!');
      navigate('/calibration');
    } catch (err) {
      alert('Failed to connect to device');
    }
  };

  return (
    <div className="page-container">
      <h2>Bluetooth Pairing</h2>
      <input
        type="text"
        placeholder="Enter Device ID"
        value={deviceId}
        onChange={e => setDeviceId(e.target.value)}
      />
      <button onClick={handleConnect}>Connect</button>
    </div>
  );
}
