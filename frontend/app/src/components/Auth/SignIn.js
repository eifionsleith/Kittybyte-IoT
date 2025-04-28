
import React, { useState } from 'react';
import '../../styles/common.css';
import { login } from '../../api';
import { useNavigate } from 'react-router-dom';

export default function SignIn() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const user = await login(username, password);
      localStorage.setItem('user', JSON.stringify({ name: username }));
      navigate('/Calibration');
    } catch (err) {
      setError("Invalid username or password");
    }
  };

  return (
    <div className="page-container">
      <h2>Sign In</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
        <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
        <button type="submit">Sign In</button>
      </form>
      <p style={{ marginTop: '1rem' }}>
        <a href="#">Forgot Password?</a> | <a href="#" onClick={() => alert('Signup coming soon!')}>Sign Up</a>
      </p>
    </div>
  );
}
