// Simple Device Manager for raw data
class DeviceManager {
  constructor() {
    this.setupFirebase();
  }

  setupFirebase() {
    // Firebase configuration
    const firebaseConfig = {
      apiKey: "AIzaSyDOLLQJLTmkkdcV1baVPdPjZw9pO2jKLRQ",
      authDomain: "smartstrike-f66f6.firebaseapp.com",
      databaseURL: "https://smartstrike-f66f6-default-rtdb.firebaseio.com",
      projectId: "smartstrike-f66f6",
      storageBucket: "smartstrike-f66f6.appspot.com",
      messagingSenderId: "1060037410865",
      appId: "1:1060037410865:web:dfb5e23507191b94431510",
      measurementId: "G-XZNBH9157E"
    };

    // Initialize Firebase
    if (!firebase.apps.length) {
      firebase.initializeApp(firebaseConfig);
    }

    // Get database reference
    const db = firebase.database();
    const sensorDataRef = db.ref('sensorData');
    
    // Listen for data changes
    sensorDataRef.on('value', (snapshot) => {
      const data = snapshot.val();
      console.log('Data received:', data);
      
      if (data) {
        // Dispatch event with the data
        const event = new CustomEvent('sensorDataUpdate', {
          detail: {
            x: parseFloat(data.x || 0),
            y: parseFloat(data.y || 0),
            z: parseFloat(data.z || 0),
            magnitude: parseFloat(data.magnitude || 0),
            cap_raw: parseFloat(data.cap_raw || 0),
            cap_raw2: parseFloat(data.cap_raw2 || 0),
            timestamp: data.timestamp
          }
        });
        window.dispatchEvent(event);
      } else {
        console.warn('No data received from sensorData path');
      }
    }, (error) => {
      console.error('Firebase error:', error);
    });
  }
}

// Export the DeviceManager class
window.DeviceManager = DeviceManager; 