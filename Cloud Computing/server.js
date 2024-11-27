require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const authRoutes = require('./routes/auth');

const app = express();
const PORT = process.env.PORT || 5000;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/stunting-app';

// Middleware
app.use(bodyParser.json());

// Routes
app.use('/api/auth', authRoutes);

// Koneksi MongoDB
mongoose
  .connect(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('MongoDB Connected'))
  .catch((error) => console.error('MongoDB Connection Error:', error));

// Start server
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
