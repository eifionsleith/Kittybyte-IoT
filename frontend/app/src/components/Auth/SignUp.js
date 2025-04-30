import React, { useState } from 'react';
import '../../styles/common.css';
import { register } from '../../api';
import { useNavigate, Link } from 'react-router-dom';

export default function SignUp() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // Validate form
    if (!username || !email || !password || !confirmPassword) {
      setError('All fields are required');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    
    try {
      await register(username, email, password);
      
      // Show success message
      setSuccess(true);
      
      // Clear form
      setUsername('');
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      
      // Redirect to login after short delay
      setTimeout(() => {
        navigate('/login');
      }, 2000);
      
    } catch (err) {
      setError(err.message || 'Registration failed');
    }
  };

  return (
    <div className="page-container">
      <h2>Create Account</h2>
      
      {success && (
        <div style={{ color: 'green', marginBottom: '1rem' }}>
          Registration successful! Redirecting to login...
        </div>
      )}
      
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
          type="email" 
          placeholder="Email" 
          value={email} 
          onChange={e => setEmail(e.target.value)}
          required 
        />
        <input 
          type="password" 
          placeholder="Password" 
          value={password} 
          onChange={e => setPassword(e.target.value)}
          required 
        />
        <input 
          type="password" 
          placeholder="Confirm Password" 
          value={confirmPassword} 
          onChange={e => setConfirmPassword(e.target.value)}
          required 
        />
        <button type="submit">Sign Up</button>
      </form>
      
      <p style={{ marginTop: '1rem' }}>
        Already have an account? <Link to="/login">Sign In</Link>
      </p>
    </div>
  );
} 