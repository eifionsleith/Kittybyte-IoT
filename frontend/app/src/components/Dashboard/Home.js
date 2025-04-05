
import React, { useEffect, useState } from 'react';
import '../../styles/common.css';
import { getFoodStatus } from '../../api';
import Navbar from '../Shared/Navbar';

export default function Home() {
  const [status, setStatus] = useState(null);
  const [user, setUser] = useState({ name: 'User' });

  useEffect(() => {
    const storedUser = JSON.parse(localStorage.getItem('user')) || { name: 'Ziad' };
    setUser(storedUser);
    fetchStatus();
    const interval = setInterval(fetchStatus, 60000); // Refresh every 60s
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    const data = await getFoodStatus();
    setStatus(data);
  };

  return (
    <div className="page-container">
      <h2>Hello {user.name}!</h2>
      {status ? (
        <>
          <div style={{ textAlign: 'center', margin: '20px 0' }}>
            <div style={{
              width: 120,
              height: 120,
              borderRadius: '50%',
              border: '10px solid #007BFF',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.2rem',
              fontWeight: 'bold'
            }}>
              {status.level}%
            </div>
            <p>Food remaining</p>
          </div>
          <p><strong>{status.feedsRemaining}</strong> Feeds to go!</p>
          <p>Last fed at {new Date(status.lastFeed).toLocaleTimeString()}</p>
        </>
      ) : (
        <p>Loading...</p>
      )}
      <Navbar />
    </div>
  );
}
