
import React, { useEffect, useState } from 'react';
import '../../styles/common.css';
import Navbar from '../Shared/Navbar';
import { useNavigate } from 'react-router-dom';

export default function ScheduleOverview() {
  const [cats, setCats] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem('cats')) || [
      { id: 1, name: 'Milo' },
      { id: 2, name: 'Luna' }
    ];
    setCats(stored);
  }, []);

  const handleClick = (cat) => {
    localStorage.setItem('selectedCat', JSON.stringify(cat));
    navigate('/schedule/details');
  };

  return (
    <div className="page-container">
      <h2>Feeding Profiles</h2>
      {cats.map(cat => (
        <div
          key={cat.id}
          style={{
            padding: '10px',
            marginBottom: '10px',
            background: '#f0f0f0',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
          onClick={() => handleClick(cat)}
        >
          <strong>{cat.name}</strong>
        </div>
      ))}
      <button onClick={() => navigate('/new-cat')} style={{ marginTop: '20px' }}>
        + Add New Cat
      </button>
      <Navbar />
    </div>
  );
}
