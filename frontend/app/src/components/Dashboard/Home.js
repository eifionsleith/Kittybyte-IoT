
import React, { useEffect, useState } from 'react';
import '../../styles/common.css';
import { getFoodStatus } from '../../api';
import Navbar from '../Shared/Navbar';
import { useNavigate } from 'react-router-dom';

export default function Home() {
  const [status, setStatus] = useState(null);
  const [user, setUser] = useState({ name: 'User' });
  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = JSON.parse(localStorage.getItem('user')) || { name: 'Ziad' };
    setUser(storedUser);
    fetchStatus();
    const interval = setInterval(fetchStatus, 60000); 
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
          <div style={{ 
            textAlign: 'center', 
            margin: '20px 0',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center' }}>
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

          <button onClick={() => navigate('/ImageFeed')} style={{ marginTop: '20px' }}>
        View Live Image
      </button>
        </>
      ) : (
        <p>Loading...</p>
      )}
      <Navbar />
    </div>
  );
}
