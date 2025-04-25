const express = require('express');
const path = require('path');
const { MongoClient } = require('mongodb');
const fs = require('fs');
const bcrypt = require('bcrypt');
const app = express();
const port = process.env.PORT || 3000;

// Подключение к MongoDB (замени строку подключения на свою)
const uri = "mongodb+srv://admin:password1488@cluster0.1d7m8rz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"; // Замени на свою строку подключения
const client = new MongoClient(uri, { serverSelectionTimeoutMS: 5000 });

let db, usersCollection;

// Функция для подключения к MongoDB
async function connectToMongoDB() {
    try {
        await client.connect();
        console.log('Подключено к MongoDB');
        db = client.db('elitecheats');
        usersCollection = db.collection('users');
    } catch (err) {
        console.error('Ошибка подключения к MongoDB:', err);
        throw err; // Останавливаем сервер, если не удалось подключиться
    }
}

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
app.post('/register', async (req, res) => {
    if (!usersCollection) {
        return res.status(500).send('База данных недоступна');
    }
    const { username, password } = req.body;
    if (!username || !password) {
        return res.send('Пожалуйста, заполните все поля');
    }
    try {
        const existingUser = await usersCollection.findOne({ username });
        if (existingUser) {
            return res.send('Пользователь с таким именем уже существует');
        }
        // Хешируем пароль
        const hashedPassword = await bcrypt.hash(password, 10);
        await usersCollection.insertOne({ username, password: hashedPassword });
        res.redirect('/');
    } catch (err) {
        console.error('Ошибка регистрации:', err);
        res.send('Ошибка регистрации: ' + err.message);
    }
});

// Обработка логина
app.post('/login', async (req, res) => {
    if (!usersCollection) {
        return res.status(500).send('База данных недоступна');
    }
    const { username, password } = req.body;
    try {
        const user = await usersCollection.findOne({ username });
        if (user && await bcrypt.compare(password, user.password)) {
            res.redirect('/cheats');
        } else {
            res.send('Неверный логин или пароль');
        }
    } catch (err) {
        console.error('Ошибка логина:', err);
        res.send('Ошибка: ' + err.message);
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

// Запускаем сервер только после успешного подключения к MongoDB
connectToMongoDB().then(() => {
    app.listen(port, () => {
        console.log(`Сервер запущен на http://localhost:${port}`);
    });
}).catch(err => {
    console.error('Не удалось запустить сервер из-за ошибки MongoDB:', err);
    process.exit(1); // Останавливаем процесс, если не удалось подключиться
});
