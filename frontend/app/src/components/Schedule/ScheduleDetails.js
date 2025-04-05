
import React, { useState } from 'react';
import '../../styles/common.css';
import { submitSchedule, feedNow } from '../../api';

import Navbar from '../Shared/Navbar';

export default function ScheduleDetails() {
  const [foodAmount, setFoodAmount] = useState(50);
  const [feedTime, setFeedTime] = useState("08:00");
  const [repeat, setRepeat] = useState(false);

  const handleFeedNow = async () => {
    const result = await feedNow();
    alert("Fed successfully at " + new Date(result.time).toLocaleTimeString());
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const schedule = {
      foodAmount,
      feedTime,
      repeat
    };
    await submitSchedule(schedule);
    alert("Schedule saved!");
  };

  return (
    <div className="page-container">
      <h2>Set Feeding Schedule</h2>
      <form onSubmit={handleSubmit}>
        <label>Food Amount (g)</label>
        <select value={foodAmount} onChange={e => setFoodAmount(e.target.value)}>
          {[...Array(20)].map((_, i) => (
            <option key={i} value={(i+1)*5}>{(i+1)*5}g</option>
          ))}
        </select>
        <label>Feed Time</label>
        <input type="time" value={feedTime} onChange={e => setFeedTime(e.target.value)} />
        <label>
          <input type="checkbox" checked={repeat} onChange={e => setRepeat(e.target.checked)} />
          Repeat daily
        </label>
        <button type="submit">Save Schedule</button>
      </form>
      <button style={{ marginTop: '1rem', backgroundColor: '#28a745' }} onClick={handleFeedNow}>
        Feed Now
      </button>
      <Navbar />
</div>
  );
}
