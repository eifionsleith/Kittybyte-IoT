import React from 'react';
import '../../styles/common.css';
import Navbar from '../Shared/Navbar';

export default function ImageFeed() {
  return (
    <div className="page-container">
      <h2>Live Image</h2>
      <h3>Your Cat Awaits!</h3>
      
      <div style={{ textAlign: 'center' }}>
        <img
          src="..."
          alt="Live Feed"
          style={{ maxWidth: '100%', height: 'auto', borderRadius: '10px' }}
        />
      </div>

      <Navbar />
    </div>
  );
}