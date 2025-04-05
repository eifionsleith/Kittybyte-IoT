
export async function login(username, password) {
  localStorage.setItem('token', 'mock-token');
  return { access_token: 'mock-token' };
}

export async function provisionDevice(deviceId) {
  return { success: true };
}

export async function getFoodStatus() {
  return {
    level: 90,
    lastFeed: new Date().toISOString(),
    feedsRemaining: 2,
  };
}

export async function feedNow() {
  return { success: true, time: new Date().toISOString() };
}

export async function submitSchedule(schedule) {
  console.log("Schedule submitted (mock):", schedule);
  return { success: true };
}
