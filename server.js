// Загрузка переменных окружения из .env
require('dotenv').config();

const express = require('express');
const path = require('path');
const { MongoClient } = require('mongodb');
const fs = require('fs');

const app = express();
const port = process.env.PORT || 3000;
const uri = process.env.MONGODB_URI;

if (!uri) {
    console.error("❌ Переменная MONGODB_URI не определена!");
    process.exit(1);
}

const client = new MongoClient(uri, { useUnifiedTopology: true });
let usersCollection;

async function startServer() {
    try {
        await client.connect();
        const db = client.db('minecraft');
        usersCollection = db.collection('users');
        console.log('✅ Подключено к MongoDB');

        // Middleware
        app.use(express.static(path.join(__dirname, 'public')));
        app.use(express.urlencoded({ extended: true }));

        // ===== Статические HTML-страницы =====
        const staticPages = ['/', '/register', '/login', '/cheats', '/about', '/viruses', '/clients', '/cfg'];
        staticPages.forEach(route => {
            const fileName = route === '/' ? 'index.html' : route.substring(1) + '.html';
            app.get(route, (req, res) => {
                res.sendFile(path.join(__dirname, 'public', fileName));
            });
        });

        // ===== Обработка регистрации =====
        app.post('/register', async (req, res) => {
            const { username, password } = req.body;
            if (!username || !password) return res.send('⚠️ Заполните все поля');

            try {
                const existing = await usersCollection.findOne({ username });
                if (existing) return res.send('⚠️ Пользователь уже существует');

                await usersCollection.insertOne({ username, password });
                res.redirect('/login');
            } catch (err) {
                console.error(err);
                res.status(500).send('❌ Ошибка при регистрации: ' + err.message);
            }
        });

        // ===== Обработка логина =====
        app.post('/login', async (req, res) => {
            const { username, password } = req.body;
            try {
                const user = await usersCollection.findOne({ username, password });
                if (user) {
                    res.redirect('/cheats');
                } else {
                    res.send('❌ Неверный логин или пароль');
                }
            } catch (err) {
                console.error(err);
                res.status(500).send('❌ Ошибка при входе: ' + err.message);
            }
        });

        // ===== Список CFG-файлов =====
        app.get('/cfg-files', (req, res) => {
            const cfgDir = path.join(__dirname, 'public', 'cfg');
            fs.readdir(cfgDir, (err, files) => {
                if (err) {
                    return res.status(500).json({ error: '❌ Ошибка чтения CFG-файлов' });
                }
                res.json(files);
            });
        });

        // ===== Запуск сервера =====
        app.listen(port, () => {
            console.log(`🚀 Сервер запущен: http://localhost:${port}`);
        });

    } catch (error) {
        console.error('❌ Ошибка подключения к MongoDB:', error.message);
        process.exit(1);
    }
}

startServer();
