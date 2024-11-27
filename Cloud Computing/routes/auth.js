const express = require('express');
const jwt = require('jsonwebtoken');
const User = require('../models/User');

const router = express.Router();
const JWT_SECRET = process.env.JWT_SECRET || 'supersecretkey'; // Ganti dengan kunci rahasia yang aman

// Registrasi
router.post('/register', async (req, res) => {
  const { name, email, password } = req.body;

  try {
    const existingUser = await User.findOne({ email });
    if (existingUser) return res.status(400).json({ message: 'Email sudah terdaftar!' });

    const user = new User({ name, email, password });
    await user.save();

    res.status(201).json({ message: 'Registrasi berhasil!' });
  } catch (error) {
    res.status(500).json({ message: 'Terjadi kesalahan', error });
  }
});

// Login
router.post('/login', async (req, res) => {
  const { email, password } = req.body;

  try {
    const user = await User.findOne({ email });
    if (!user) return res.status(404).json({ message: 'Pengguna tidak ditemukan!' });

    const isPasswordValid = await user.isPasswordValid(password);
    if (!isPasswordValid) return res.status(401).json({ message: 'Password salah!' });

    const token = jwt.sign({ id: user._id, email: user.email }, JWT_SECRET, { expiresIn: '1d' });

    res.status(200).json({ message: 'Login berhasil!', token });
  } catch (error) {
    res.status(500).json({ message: 'Terjadi kesalahan', error });
  }
});

module.exports = router;
