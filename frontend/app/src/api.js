const API_URL = 'http://localhost:8000';

// Utility function to get auth token
const getAuthToken = () => {
  // First try to get from user object
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  if (user.token) return user.token;
  
  // Fallback to direct token storage
  return localStorage.getItem('token');
};

// Utility function for authenticated requests
export async function authFetch(url, options = {}) {
  const token = getAuthToken();
  
  if (!token) {
    throw new Error('Authentication required');
  }
  
  const authOptions = {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  };
  
  return fetch(url, authOptions);
}

export async function login(username, password) {
  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        username,
        password,
      }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

export async function register(username, email, password) {
  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        email,
        password,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Registration failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
}

export async function provisionDevice(deviceId) {
  return { success: true };
}

export async function getFoodStatus() {
  // Use mock data since the '/device/food-status' endpoint doesn't exist yet
  console.info('Using mock food status data - endpoint not implemented in backend');
  return {
    level: 80,
    lastFeed: new Date().toISOString(),
    feedsRemaining: 3,
  };
}

export async function feedNow() {
  // Use mock data since the '/device/feed' endpoint doesn't exist yet
  console.info('Using mock feed data - endpoint not implemented in backend');
  return { 
    success: true, 
    time: new Date().toISOString() 
  };
}

export async function submitSchedule(schedule) {
  console.log("Schedule submitted (mock):", schedule);
  return { success: true };
}
