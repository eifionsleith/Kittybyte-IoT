
import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FaHome, FaCalendarAlt, FaCat, FaUser } from 'react-icons/fa';
import './Navbar.css';

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();

  const tabs = [
    { label: 'Home', icon: <FaHome />, path: '/home' },
    { label: 'Schedule', icon: <FaCalendarAlt />, path: '/schedule' },
    { label: 'Add Cat', icon: <FaCat />, path: '/new-cat' },
    { label: 'Menu', icon: <FaUser />, path: '/menu' },
  ];

  return (
    <div className="bottom-nav">
      {tabs.map((tab) => (
        <div
          key={tab.path}
          className={`nav-item ${location.pathname === tab.path ? 'active' : ''}`}
          onClick={() => navigate(tab.path)}
        >
          {tab.icon}
          <span>{tab.label}</span>
        </div>
      ))}
    </div>
  );
}
