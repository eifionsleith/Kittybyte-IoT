import React, { useState } from 'react';
import '../../styles/common.css';
import { submitSchedule, feedNow } from '../../api';
import Navbar from '../Shared/Navbar';

export default function ScheduleDetails() {
  const [schedules, setSchedules] = useState([
    { id: 1, foodAmount: 50, feedTime: "08:00", repeat: false }
  ]);

  const handleFeedNow = async () => {
    const result = await feedNow();
    alert("Fed successfully at " + new Date(result.time).toLocaleTimeString());
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await submitSchedule(schedules);
    alert("Schedules saved!");
  };

  const addNewSchedule = () => {
    const newId = schedules.length > 0 ? Math.max(...schedules.map(s => s.id)) + 1 : 1;
    setSchedules([...schedules, { id: newId, foodAmount: 50, feedTime: "08:00", repeat: false }]);
  };

  const deleteSchedule = (id) => {
    setSchedules(schedules.filter(schedule => schedule.id !== id));
  };

  const updateSchedule = (id, field, value) => {
    setSchedules(schedules.map(schedule => {
      if (schedule.id === id) {
        return { ...schedule, [field]: value };
      }
      return schedule;
    }));
  };

  return (
    <div className="page-container">
      <h2>Set Feeding Schedule</h2>

      <form onSubmit={handleSubmit}>
        {schedules.map((schedule) => (
          <div key={schedule.id} style={{ 
            border: '1px solid #ddd', 
            borderRadius: '8px', 
            padding: '1rem', 
            marginBottom: '1rem' 
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0 }}>Feed Schedule {schedule.id}</h3>
              {schedules.length > 1 && (
                <button 
                  type="button" 
                  onClick={() => deleteSchedule(schedule.id)}
                  style={{ background: '007bff', 
                    color: 'white', 
                    border: 'none',
                    borderRadius: '4px', 
                    padding: '0.25rem 0.5rem' }}
                >
                  Delete
                </button>
              )}
            </div>
            
            <label>Food Amount (g)</label>
            <select 
              value={schedule.foodAmount} 
              onChange={e => updateSchedule(schedule.id, 'foodAmount', Number(e.target.value))}
              style={{ marginBottom: '1rem', width: '100%', padding: '0.5rem' }}
            >
              {[...Array(20)].map((_, i) => (
                <option key={i} value={(i + 1) * 5}>{(i + 1) * 5}g</option>
              ))}
            </select>

            <label>Feed Time</label>
            <input 
              type="time" 
              value={schedule.feedTime} 
              onChange={e => updateSchedule(schedule.id, 'feedTime', e.target.value)}
              style={{ marginBottom: '1rem',
                 width: '100%', 
                 padding: '0.5rem',
                 }}
            />

            <div style={{ marginTop: '0.5rem', textAlign: 'left', display: 'flex', alignItems: 'flex-start' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
              <input
              type="checkbox"
              id={`repeat-${schedule.id}`}
              checked={schedule.repeat}
              onChange={e => updateSchedule(schedule.id, 'repeat', e.target.checked)}
              style={{ margin: '0 8px 0 0' }}
              />
              <label htmlFor={`repeat-${schedule.id}`}>Repeat daily</label>
              </div>
            </div>



          </div>
        ))}

        <button 
          type="button" 
          onClick={addNewSchedule}
          style={{ 
            background: '#007bff', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px', 
            padding: '0.5rem 1rem', 
            marginBottom: '1rem' 
          }}
        >
          +
        </button>

        <div style={{ marginTop: '1rem' }}>
          <button 
            type="submit"
            style={{ 
              background: '#007bff', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              padding: '0.5rem 1rem' 
            }}
          >
            Save Feed Schedules
          </button>
        </div>
      </form>

      <button 
        style={{ 
          marginTop: '1rem', 
          backgroundColor: '#28a745', 
          color: 'white', 
          border: 'none', 
          borderRadius: '4px', 
          padding: '0.5rem 1rem' 
        }} 
        onClick={handleFeedNow}
      >
        Feed Now
      </button>
      
      <Navbar />
    </div>
  );
}