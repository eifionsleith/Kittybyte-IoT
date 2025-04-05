
import React from 'react';
import '../../styles/common.css';
import { useNavigate } from 'react-router-dom';

export default function Calibration() {
  const navigate = useNavigate();

  const handleFinish = () => {
    alert('Calibration complete!');
    navigate('/home');
  };

  return (
    <div className="page-container">
      <h2>Calibration</h2>
      <p>Please make sure the feeder is filled with food and positioned correctly.</p>
      <button onClick={handleFinish}>Finish</button>
    </div>
  );
}
