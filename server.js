const express = require('express');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const app = express();
const port = process.env.PORT || 3000;

// Подключение к базе данных SQLite
const db = new sqlite3.Database('users.db', (err) => {
    if (err) {
        console.error('Ошибка подключения к базе данных:', err.message);
    } else {
        console.log('Подключено к базе данных SQLite');
        db.run(`CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )`);
    }
});

// Middleware
app.use(express.static('public'));
app.use(express.urlencoded({ extended: true }));

// Маршрут для главной страницы (логин)
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Маршрут для страницы регистрации
app.get('/register', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'register.html'));
});

// Обработка регистрации
app.post('/register', (req, res) => {
    const { username, password } = req.body;
    if (!username || !password) {
        return res.send('Пожалуйста, заполните все поля');
    }
    db.run(`INSERT INTO users (username, password) VALUES (?, ?)`, [username, password], function(err) {
        if (err) {
            if (err.message.includes('UNIQUE constraint failed')) {
                return res.send('Пользователь с таким именем уже существует');
            }
            return res.send('Ошибка регистрации: ' + err.message);
        }
        res.redirect('/');
    });
});

// Обработка логина
app.post('/login', (req, res) => {
    const { username, password } = req.body;
    db.get(`SELECT * FROM users WHERE username = ? AND password = ?`, [username, password], (err, row) => {
        if (err) {
            return res.send('Ошибка: ' + err.message);
        }
        if (row) {
            res.redirect('/cheats');
        } else {
            res.send('Неверный логин или пароль');
        }
    });
});

// Маршрут для страницы с читами
app.get('/cheats', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'cheats.html'));
});

// Маршрут для страницы "О нас"
app.get('/about', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'about.html'));
});

// Маршрут для страницы "Вирусы"
app.get('/viruses', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'viruses.html'));
});

// Маршрут для страницы "Клиенты"
app.get('/clients', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'clients.html'));
});

// Маршрут для страницы "CFG"
app.get('/cfg', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'cfg.html'));
});

// Маршрут для получения списка CFG-файлов
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