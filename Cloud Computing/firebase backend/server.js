const express = require('express');
const admin = require('firebase-admin');
const bodyParser = require('body-parser');
const cors = require('cors');
require('dotenv').config();

// **1. Inisialisasi Firebase Admin**
const serviceAccount = require('./firebase-adminsdk.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: 'https://auth-zerostunt.firebaseio.com', // Ganti <YOUR_PROJECT_ID> dengan ID proyek Firebase Anda
});

const db = admin.firestore();
const app = express();

// **2. Middleware**
app.use(cors());
app.use(bodyParser.json());

// **3. Rute untuk Autentikasi dan CRUD Data Pengguna**
// **a. Daftar Akun**
app.post('/register', async (req, res) => {
  const { email, password, name } = req.body;
  if (!email || !password || !name) {
    return res.status(400).json({ error: 'Email, password, and name are required!' });
  }

  try {
    const user = await admin.auth().createUser({
      email,
      password,
      displayName: name,
    });
    await db.collection('users').doc(user.uid).set({ email, name, createdAt: new Date() });
    res.status(201).json({ message: 'User registered successfully!', uid: user.uid });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// **b. Login Akun**
app.post('/login', async (req, res) => {
  const { email } = req.body;
  if (!email) {
    return res.status(400).json({ error: 'Email is required!' });
  }

  try {
    const userRecord = await admin.auth().getUserByEmail(email);
    const token = await admin.auth().createCustomToken(userRecord.uid);
    res.status(200).json({ token });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// **c. Verifikasi Token**
app.post('/verify-token', async (req, res) => {
  const { token } = req.body;
  if (!token) {
    return res.status(400).json({ error: 'Token is required!' });
  }

  try {
    const decodedToken = await admin.auth().verifyIdToken(token);
    res.status(200).json({ uid: decodedToken.uid, message: 'Token is valid!' });
  } catch (error) {
    res.status(401).json({ error: 'Invalid token!' });
  }
});

// **d. Mendapatkan Data Pengguna**
app.get('/user/:uid', async (req, res) => {
  const { uid } = req.params;

  try {
    const userDoc = await db.collection('users').doc(uid).get();
    if (!userDoc.exists) {
      return res.status(404).json({ error: 'User not found!' });
    }
    res.status(200).json(userDoc.data());
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// **e. Update Data Pengguna**
app.put('/user/:uid', async (req, res) => {
  const { uid } = req.params;
  const updates = req.body;

  try {
    await db.collection('users').doc(uid).update(updates);
    res.status(200).json({ message: 'User updated successfully!' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// **f. Hapus Akun Pengguna**
app.delete('/user/:uid', async (req, res) => {
  const { uid } = req.params;

  try {
    await admin.auth().deleteUser(uid);
    await db.collection('users').doc(uid).delete();
    res.status(200).json({ message: 'User deleted successfully!' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// **4. Jalankan Server**
const PORT = process.env.PORT || 5000; // Ganti jika ada konflik port
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
