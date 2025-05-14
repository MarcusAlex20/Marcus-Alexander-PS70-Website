const { initializeApp } = require('firebase/app');
const { getAuth, signInWithEmailAndPassword } = require('firebase/auth');
const { getDatabase, ref, set } = require('firebase/database');

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
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const database = getDatabase(app);

// Replace these with your admin credentials
const adminEmail = "Marcusalexander@college.harvard.edu";
const adminPassword = "Alexander5!";
const adminName = "Marcus Alexander";

async function setupAdmin() {
  try {
    // Sign in with the admin account
    const userCredential = await signInWithEmailAndPassword(auth, adminEmail, adminPassword);
    const user = userCredential.user;

    // Set up the admin user in the database
    await set(ref(database, `users/${user.uid}`), {
      name: adminName,
      email: adminEmail,
      isAdmin: true,
      createdAt: Date.now()
    });

    console.log('Admin user set up successfully!');
    console.log('User ID:', user.uid);
  } catch (error) {
    console.error('Error setting up admin:', error);
  }
}

setupAdmin(); 