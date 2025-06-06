require('dotenv').config(); // подключаем .env
const express = require('express');
const path = require('path');
const fs = require('fs');
const { MongoClient } = require('mongodb');

const app = express();
const port = process.env.PORT || 3000;

const mongoUrl = process.env.MONGO_URL; // берем URL из .env
const client = new MongoClient(mongoUrl);
let usersCollection;

client.connect()
  .then(() => {
    const db = client.db('minecraft'); // имя базы данных
    usersCollection = db.collection('users'); // коллекция users
    console.log('✅ Успешно подключено к MongoDB');
  })
  .catch(err => console.error('❌ Ошибка подключения к MongoDB:', err));

// Middleware
app.use(express.static('public'));
app.use(express.urlencoded({ extended: true }));

// Главная
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Регистрация
app.get('/register', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'register.html'));
});

app.post('/register', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) return res.send('Заполни все поля');
  try {
    const existing = await usersCollection.findOne({ username });
    if (existing) return res.send('Такой пользователь уже есть');
    await usersCollection.insertOne({ username, password });
    res.redirect('/');
  } catch (err) {
    console.error(err);
    res.send('Ошибка регистрации');
  }
});

// Вход
app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  try {
    const user = await usersCollection.findOne({ username, password });
    if (user) res.redirect('/cheats');
    else res.send('Неверный логин или пароль');
  } catch (err) {
    console.error(err);
    res.send('Ошибка входа');
  }
});

// Другие страницы
app.get('/cheats', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'cheats.html'));
});
app.get('/about', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'about.html'));
});
app.get('/viruses', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'viruses.html'));
});
app.get('/clients', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'clients.html'));
});
app.get('/cfg', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'cfg.html'));
});
app.get('/cfg-files', (req, res) => {
  const cfgDir = path.join(__dirname, 'public', 'cfg');
  fs.readdir(cfgDir, (err, files) => {
    if (err) return res.status(500).json({ error: 'Ошибка чтения файлов' });
    res.json(files);
  });
});

// Запуск сервера
app.listen(port, () => {
  console.log(`🚀 Сервер запущен на http://localhost:${port}`);
});
