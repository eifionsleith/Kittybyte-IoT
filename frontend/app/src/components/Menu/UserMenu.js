
import React from 'react';
import '../../styles/common.css';
import Navbar from '../Shared/Navbar';

export default function UserMenu() {
  const user = JSON.parse(localStorage.getItem('user')) || { name: 'Ziad' };

  return (
    <div className="page-container">
      <h2>Welcome, {user.name}</h2>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        <li><a href="/schedule">Manage Feeding Schedule</a></li>
        <li><a href="/new-cat">Add Another Cat</a></li>
        <li><a href="#" onClick={() => alert('Support coming soon!')}>Help & Support</a></li>
        <li><a href="#" onClick={() => { localStorage.clear(); window.location.href = '/' }}>Sign Out</a></li>
      </ul>
      <Navbar />
    </div>
  );
}
