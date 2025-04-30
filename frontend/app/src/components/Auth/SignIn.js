import React, { useState } from 'react';
import '../../styles/common.css';
import { login } from '../../api';
import { useNavigate, Link } from 'react-router-dom';

export default function SignIn() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!username || !password) {
      setError('Username and password are required');
      return;
    }
    
    try {
      const data = await login(username, password);
      // Store token in localStorage
      localStorage.setItem('user', JSON.stringify({ 
        username, 
        token: data.access_token 
      }));
      navigate('/Calibration');
    } catch (err) {
      setError('Invalid username or password');
    }
  };

  return (
    <div className="page-container">
      <h2>Sign In</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          placeholder="Username" 
          value={username} 
          onChange={e => setUsername(e.target.value)} 
          required
        />
        <input 
          type="password" 
          placeholder="Password" 
          value={password} 
          onChange={e => setPassword(e.target.value)} 
          required
        />
        <button type="submit">Sign In</button>
      </form>
      <p style={{ marginTop: '1rem' }}>
        <Link to="/forgot-password">Forgot Password?</Link> | <Link to="/signup">Sign Up</Link>
      </p>
    </div>
  );
}
