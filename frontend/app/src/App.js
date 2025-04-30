import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SignIn from './components/Auth/SignIn';
import SignUp from './components/Auth/SignUp';
import Home from './components/Dashboard/Home';
import ScheduleOverview from './components/Schedule/ScheduleOverview';
import ScheduleDetails from './components/Schedule/ScheduleDetails';
import NewCatForm from './components/Pets/NewCatForm';
import UserMenu from './components/Menu/UserMenu';
import BluetoothConnect from './components/Pairing/BluetoothConnect';
import Calibration from './components/Setup/Calibration';
import ImageFeed from './components/Pets/ImageFeed';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/login" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/pair" element={<BluetoothConnect />} />
        <Route path="/calibration" element={<Calibration />} />
        <Route path="/home" element={<Home />} />
        <Route path="/schedule" element={<ScheduleOverview />} />
        <Route path="/schedule/details" element={<ScheduleDetails />} />
        <Route path="/new-cat" element={<NewCatForm />} />
        <Route path="/menu" element={<UserMenu />} />
        <Route path="/imagefeed" element={<ImageFeed />} />
      </Routes>
    </Router>
  );
}
