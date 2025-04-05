
import React, { useState } from 'react';
import '../../styles/common.css';
import { FaCat } from 'react-icons/fa';

import Navbar from '../Shared/Navbar';

export default function NewCatForm() {
  const [name, setName] = useState('');
  const [years, setYears] = useState('');
  const [months, setMonths] = useState('');
  const [weight, setWeight] = useState('');
  const [image, setImage] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    const catData = {
      name,
      age: `${years}y ${months}m`,
      weight,
      image
    };
    console.log("Submitting cat:", catData);
    // TODO: API call to backend
  };

  return (
    <div className="page-container">
      <h2><FaCat /> Add New Cat</h2>
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="Name" value={name} onChange={e => setName(e.target.value)} required />
        <div style={{ display: 'flex', gap: '10px' }}>
          <input type="number" placeholder="Years" value={years} onChange={e => setYears(e.target.value)} required />
          <input type="number" placeholder="Months" value={months} onChange={e => setMonths(e.target.value)} required />
          <Navbar />
</div>
        <input type="number" placeholder="Weight (kg)" value={weight} onChange={e => setWeight(e.target.value)} required />
        <input type="file" accept="image/*" onChange={e => setImage(e.target.files[0])} />
        <button type="submit">Meow</button>
      </form>
    </div>
  );
}
