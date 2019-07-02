let TelegrafBot = require('telegraf');
let mongoose = require('mongoose');
let request = require('request');
const express = require('express');
let bodyParser = require("body-parser");
const moment = require('moment');
let Keyboards = require('./utils/keyboards');
let UserService = require('./services/user-service');
let VoiceMailService = require('./services/voicemail-service');
const register = require('./scenes/register');
const session = require("telegraf/session");
const Stage = require("telegraf/stage");
const Scene = require('telegraf/scenes/base');
const { enter, leave } = Stage;

let token = process.env.TOKEN_TELEGRAM;
let mongooseToken = process.env.TOKEN_MONGO_MLAB;

mongoose.Promise = global.Promise;
mongoose.connect(mongooseToken, { useCreateIndex :  true, useNewUrlParser: true, promiseLibrary: global.Promise});

const app = express();
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
let bot = new TelegrafBot(token);

app.get('/', (req, res) => res.send('Hello World!'));
app.post('/push', function(req, res) {
    console.log(req.body);
    let data = req.body;
    for(let i= 0; i < data.length; i++ ){
        UserService.findOne({telephone: data[i].receiver}, function(err, receiver){
            console.log(data[i].receiver);
            console.log(receiver);
           bot.telegram.sendAudio(receiver.telegramId, {url: data[i].url}, {title: data[i].author, performer: 'Голосовая почта', caption: 'Время записи: ' + data[i].recordingDate});
        });
    }
    //console.log(res);
    res.send('Hello World!')
});
//app.use(bot.webhookCallback('/secret-path'))
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log('Example app listening on port 5000!');
});