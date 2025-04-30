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
            padding: '16px', 
            marginBottom: '16px' 
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1px' }}>
              <h3 style={{ margin: 0 }}>Feed Schedule {schedule.id}</h3>
              {schedules.length > 1 && (
                <button 
                  type="button" 
                  className='removebutton'
                  onClick={() => deleteSchedule(schedule.id)}
                >
                  x
                </button>
              )}
            </div>
            
            <label>Food Amount (g)</label>
            <select 
              value={schedule.foodAmount} 
              onChange={e => updateSchedule(schedule.id, 'foodAmount', Number(e.target.value))}
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
            />

            <div style={{ marginTop: '1px', textAlign: 'left', display: 'flex', alignItems: 'flex-start' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
              <input
              type="checkbox"
              id={`repeat-${schedule.id}`}
              checked={schedule.repeat}
              onChange={e => updateSchedule(schedule.id, 'repeat', e.target.checked)}
              />
              <label htmlFor={`repeat-${schedule.id}`}>Repeat daily</label>
              </div>
            </div>



          </div>
        ))}

        <button 
          type="button" 
          onClick={addNewSchedule}
        >
          +
        </button>

        <div style={{ marginTop: '10px' }}>
          <button 
            type="submit"
          >
            Save Feed Schedules
          </button>
          </div>
      </form>

      <button 
        style={{ 
          marginTop: '10px', 
          backgroundColor: '#28a745',  
        }} 
        onClick={handleFeedNow}
      >
        Feed Now
      </button>
      
      <Navbar />
    </div>
  );
}