const express = require('express');
const path = require('path');
const fs = require('fs');
const { MongoClient } = require('mongodb');

const app = express();
const port = process.env.PORT || 3000;

// Настройки MongoDB
const mongoUrl = process.env.MONGO_URL || 'mongodb://localhost:27017';
const dbName = 'minecraft-cheats-site';

let db;
let usersCollection;

// Подключение к MongoDB
MongoClient.connect(mongoUrl, { useUnifiedTopology: true })
  .then(client => {
    db = client.db(dbName);
    usersCollection = db.collection('users');
    console.log('Подключено к MongoDB');
  })
  .catch(err => {
    console.error('Ошибка подключения к MongoDB:', err);
    process.exit(1);
  });

// Middleware
app.use(express.static('public'));
app.use(express.urlencoded({ extended: true }));

// Главная страница (логин)
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Страница регистрации
app.get('/register', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'register.html'));
});

// Обработка регистрации
app.post('/register', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.send('Пожалуйста, заполните все поля');
  }

  try {
    const existingUser = await usersCollection.findOne({ username });
    if (existingUser) {
      return res.send('Пользователь с таким именем уже существует');
    }
    await usersCollection.insertOne({ username, password });
    res.redirect('/');
  } catch (err) {
    console.error(err);
    res.send('Ошибка регистрации: ' + err.message);
  }
});

// Обработка логина
app.post('/login', async (req, res) => {
  const { username, password } = req.body;

  try {
    const user = await usersCollection.findOne({ username, password });
    if (user) {
      res.redirect('/cheats');
    } else {
      res.send('Неверный логин или пароль');
    }
  } catch (err) {
    console.error(err);
    res.send('Ошибка: ' + err.message);
  }
});

// Остальные маршруты без изменений

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
    if (err) {
      return res.status(500).json({ error: 'Не удалось прочитать CFG-файлы' });
    }
    res.json(files);
  });
});

// Запуск сервера
app.listen(port, () => {
  console.log(`Сервер запущен на http://localhost:${port}`);
});
