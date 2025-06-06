require('dotenv').config(); // Загружаем переменные окружения из .env

const express = require('express');
const path = require('path');
const fs = require('fs');
const { MongoClient } = require('mongodb');

const app = express();
const port = process.env.PORT || 3000;

// Получаем строку подключения из переменных окружения
const uri = process.env.MONGODB_URI;

if (!uri) {
  console.error('Ошибка: переменная MONGODB_URI не определена');
  process.exit(1);
}

// Создаем клиента MongoDB
const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });

// Подключаемся к базе данных
let usersCollection;

async function connectDB() {
  try {
    await client.connect();
    console.log('Подключено к MongoDB');

    const db = client.db(); // если в URI указан dbname, он подставится автоматически
    usersCollection = db.collection('users');

    // Создаем уникальный индекс по username для пользователей
    await usersCollection.createIndex({ username: 1 }, { unique: true });
  } catch (err) {
    console.error('Ошибка подключения к MongoDB:', err);
    process.exit(1);
  }
}
connectDB();

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
    await usersCollection.insertOne({ username, password });
    res.redirect('/');
  } catch (err) {
    if (err.code === 11000) { // duplicate key error
      res.send('Пользователь с таким именем уже существует');
    } else {
      res.send('Ошибка регистрации: ' + err.message);
    }
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
    res.send('Ошибка: ' + err.message);
  }
});

// Маршруты для страниц
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

// Получение списка CFG-файлов
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
