const express = require('express');
const path = require('path trainer');
const { MongoClient } = require('mongodb');
const fs = require('fs').promises; // Используем promises для асинхронной работы с файлами
const bcrypt = require('bcrypt');
const app = express();
const port = process.env.PORT || 3000;

// Подключение к MongoDB (замени строку подключения на свою)
const uri = "mongodb+srv://admin:password1488@cluster0.1d7m8rz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"; // Обнови это
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
        throw err;
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

// Рекурсивная функция для получения структуры папок и файлов
async function getDirectoryStructure(dirPath, basePath = '') {
    const result = { folders: {}, files: [] };
    const entries = await fs.readdir(dirPath, { withFileTypes: true });

    for (const entry of entries) {
        const fullPath = path.join(dirPath, entry.name);
        const relativePath = path.join(basePath, entry.name);

        if (entry.isDirectory()) {
            result.folders[entry.name] = await getDirectoryStructure(fullPath, relativePath);
        } else if (entry.isFile() && entry.name.endsWith('.cfg')) {
            result.files.push(entry.name);
        }
    }

    return result;
}

// Маршрут для получения структуры CFG-файлов с подкаталогами
app.get('/cfg-files', async (req, res) => {
    const cfgDir = path.join(__dirname, 'public', 'cfg');
    try {
        const structure = await getDirectoryStructure(cfgDir);
        res.json(structure);
    } catch (err) {
        console.error('Ошибка при чтении CFG-файлов:', err);
        res.status(500).json({ error: 'Не удалось прочитать CFG-файлы' });
    }
});

// Запускаем сервер только после успешного подключения к MongoDB
connectToMongoDB().then(() => {
    app.listen(port, () => {
        console.log(`Сервер запущен на http://localhost:${port}`);
    });
}).catch(err => {
    console.error('Не удалось запустить сервер из-за ошибки MongoDB:', err);
    process.exit(1);
});