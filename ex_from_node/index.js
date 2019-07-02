let TelegrafBot = require('telegraf');
let mongoose = require('mongoose');
let request = require('request');
const express = require('express');
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

const url = 'http://test-vm.mts-intercom.ru/api/values/';

let bot = new TelegrafBot(token);

mongoose.Promise = global.Promise;
mongoose.connect(mongooseToken, { useCreateIndex :  true, useNewUrlParser: true, promiseLibrary: global.Promise});

const stage = new Stage([
    register
]);

bot.use(session());
bot.use(stage.middleware());

bot.start((ctx) => {
    let userInfo = {
        firstName: ctx.from.first_name,
        telegramId:  ctx.from.id
    };
    console.log(userInfo);
    return ctx.reply('Привет ' + ctx.from.first_name + '!\n' +
        'Я чат-бот Голосовой почты 🙋 \n\n').then(() => {
        UserService.isNew(ctx.from.id, function (err, result) {
            if(result) {
                ctx.reply('Для того, что бы воспользоваться функционалом бота, необходимо пройти короткую регистрацию', Keyboards.registration);
            } else {
                ctx.reply('Чем могу помочь??', Keyboards.mainMenu);
            }
        });
    });
});
bot.action('allVoice', async (ctx) => {
    UserService.findOne({telegramId: ctx.from.id}, function (err, result){
        request({url: url + result.telephone}, async function (error, response, body) {
            let data = JSON.parse(body);
            console.log(data);
            for (let i = 0; i < data.length; i++) {
                VoiceMailService.findOne({
                    user_id: result._id,
                    path: data[i].url
                }, async function (err_voice, voiceMail) {
                    if (err_voice) {
                        return;
                    }
                    ctx.replyWithAudio({url: data[i].url}, {title: data[i].author, performer: 'Голосовая почта', caption: 'Время записи: ' + data[i].recordingDate});
                    //bot.telegram.sendAudio(ctx.from.id, 'http://skyeng-dictionary-audio.s3.eu-central-1.amazonaws.com/609938310fd3327c11b34d05b772c3fe.mp3');
                    //bot.telegram.sendVoice(ctx.from.id, data[i].url);
                    /*await ctx.reply('Автор: ' + result.telephone
                        + '\nВремя записи: ' + data[i].recordingDate
                        + '\nСсылка для скачивания: \n'
                        + data[i].url);*/
                    //bot.telegram.sendVoice(ctx.from.id, 'http://skyeng-dictionary-audio.s3.eu-central-1.amazonaws.com/609938310fd3327c11b34d05b772c3fe.mp3');
                });
            }
            if (!data.length) {
                await ctx.reply('Нет новых записей');
            }
        });
    });
});
bot.action('newVoice', async (ctx) => {
    //request.post({url:'http://service.com/upload', form: {key:'value'}}, function(err,httpResponse,body){ /* ... */ })
    UserService.findOne({telegramId: ctx.from.id}, function (err, result){
        request({url: url + result.telephone}, async function (error, response, body) {
            console.log(error);
            console.log(body);
            console.log(body);
            let data = JSON.parse(body);
            console.log(data);
            for (let i = 0; i < data.length; i++) {
                //flagEmpty += data[i].url;
                VoiceMailService.findOne({
                    user_id: result._id,
                    path: data[i].url
                }, async function (err_voice, voiceMail) {
                    if (err_voice) {
                        return;
                    }
                    if (voiceMail == null) {
                        VoiceMailService.saveVoiceMail({
                            user_id: result._id,
                            path: data[i].url,
                            author: data[i].author,
                            fileName: data[i].fileName,
                            recordingDate: moment(data[i].recordingDate, "DD.MM.YYYY HH:mm").format('YYYY-MM-DDTHH:mm')
                        });
                        /*await ctx.reply('Автор: ' + result.telephone
                            + '\nВремя записи: ' + data[i].recordingDate
                            + '\nСсылка для скачивания: \n'
                            + data[i].url);*/
                        //bot.telegram.sendVoice(ctx.from.id, data[i].url);
                        ctx.replyWithAudio({url: data[i].url}, {title: data[i].author, performer: 'Голосовая почта', caption: 'Время записи: ' + data[i].recordingDate});
                    }
                });
            }
        });
    });
});
bot.on('contact', (ctx) => {
    console.log(Keyboards.mainMenu);
    console.log(Keyboards.aboutMenu);
    UserService.register(ctx.message.contact, function (saveErr, result) {
        if (saveErr || result === false) {
            ctx.reply('Произошла ошибка, возможно вы уже зарегестрированы, введите /start');
        } else {
            ctx.reply('Вы успешно зарегестрировались. Чем могу помочь?', Keyboards.menu);
        }
    });
});
bot.hears('Меню', ctx => {
    ctx.reply('Меню', Keyboards.mainMenu);
});


bot.startPolling();