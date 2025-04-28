const express = require('express');
const path = require('path');
const { MongoClient } = require('mongodb');
const fs = require('fs');
const bcrypt = require('bcrypt');
const app = express();
const port = process.env.PORT || 3000;

// Подключение к MongoDB
const uri = "mongodb+srv://admin:password1488@cluster0.1d7m8rz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";
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

// Запускаем сервер только после успешного подключения к MongoDB
connectToMongoDB().then(() => {
    app.listen(port, () => {
        console.log(`Сервер запущен на http://localhost:${port}`);
    });
}).catch(err => {
    console.error('Не удалось запустить сервер из-за ошибки MongoDB:', err);
    process.exit(1);
});