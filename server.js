const express = require('express');
const path = require('path');
const app = express();
const port = process.env.PORT || 3000;

// Middleware для обработки статических файлов (HTML, CSS и т.д.)
app.use(express.static('public'));
app.use(express.urlencoded({ extended: true }));

// Маршрут для главной страницы
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Маршрут для обработки логина
app.post('/login', (req, res) => {
    const { username, password } = req.body;
    // Простая проверка (замени на свою логику)
    if (username === 'admin' && password === 'password') {
        res.redirect('/cheats');
    } else {
        res.send('Неверный логин или пароль');
    }
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

// Запуск сервера
app.listen(port, () => {
    console.log(`Сервер запущен на http://localhost:${port}`);
});