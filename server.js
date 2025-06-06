require('dotenv').config(); // Загрузка переменных окружения из .env

const express = require('express');
const path = require('path');
const { MongoClient } = require('mongodb');
const fs = require('fs');
const app = express();
const port = process.env.PORT || 3000;

// Проверка переменной окружения
const uri = process.env.MONGODB_URI;
if (!uri) {
    console.error("❌ Переменная MONGODB_URI не определена!");
    process.exit(1);
}

// Инициализация клиента MongoDB
const client = new MongoClient(uri, { useUnifiedTopology: true });
let usersCollection;

async function startServer() {
    try {
        // Подключение к базе
        await client.connect();
        const db = client.db('minecraft'); // имя базы данных
        usersCollection = db.collection('users');
        console.log('✅ Успешное подключение к MongoDB');

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
                const existing = await usersCollection.findOne({ username });
                if (existing) {
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

        // Страницы сайта
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
            console.log(`🚀 Сервер запущен: http://localhost:${port}`);
        });

    } catch (error) {
        console.error('❌ Ошибка подключения к MongoDB:+ у тебя пенис в жопе', error.message);
        process.exit(1);
    }
}

startServer();
