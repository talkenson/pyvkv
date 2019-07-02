import requests as req
import time
import random
import atexit
import configparser
import re
import sys, os
import json
import _thread
from datetime import datetime

from flask import Flask, request, Response
from flask_cors import CORS

from VKAPI import VKAPI ## LOCAL MODULE
import Keyboards

def quit():
    #input('Some reasons asked us to quit')
    save_prefs(inc_ts=True)
atexit.register(quit)

app = Flask(__name__)
CORS(app)
plugins = {}

#import logging
#log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)

VOMAIL = 'http://test-vm.mts-intercom.ru/api/values/'

bot_token = 'a4a6e03953950b3786e2287357a511e6d04357faf2d951e35a5a88c69dc350d7534b6fcaecaff7fb1ba21'
bot_id = ''
savefile_name = 'lp_pref.ini'
pref = {'server': 'https://lp.vk.com/wh' + bot_id,
        'key': 'sample_but_not_empty',
        'ts': 0}

def save_prefs(inc_ts=False):
# inc_ts - увеличение итогового счетчика на 1, для случаев, когда не выгодно
# обновлять переменные (завершение работы бота)
    global pref
    print('[HOST] \tSaving preferences...')

    config = configparser.ConfigParser()
    config.add_section("PREF")
    config.set("PREF", "server", pref['server'])
    config.set("PREF", "key", pref['key'])
    config.set("PREF", "group_id", bot_id)
    if inc_ts:
        config.set("PREF", "ts", str(1+int(pref['ts'])))
    else:
        config.set("PREF", "ts", str(pref['ts']))
    config.set("PREF", "bot_token", bot_token)

    with open(savefile_name, 'w') as configfile:    # save
        config.write(configfile)

    print('[HOST] \tPreferences saved')

def load_prefs():
    global pref
    global bot_token
    global bot_id
    print('[HOST] \tLoading preferences...')

    config = configparser.ConfigParser()
    config.read('lp_pref.ini')
    pref['server'] = config['PREF']['server']
    pref['key'] = config['PREF']['key']
    pref['ts'] = config['PREF']['ts']
    bot_token = config['PREF']['bot_token']
    bot_id = config['PREF']['group_id']

    print('[HOST] \tPreferences loaded')



class BOT_MANAGER:
    def __init__(self):
        self.inChat = False
        self.inChatId = ''
        self.checkout = False

    def mMessage(self, ob):
        if 'payload' in ob.keys():
            action = json.loads(ob['payload'])['act']
            if action == 'exit':
                VK.send(ob['peer_id'], 'Вы попросили меня уйти, и я ухожу')
                exit()
            elif action == 'sendAll':
                VK.send(ob['peer_id'], 'Высылаю все')

            elif action == 'checkNew':
                VK.send(ob['peer_id'], 'Проверяю на наличие новых сообщений, если что - высылаю')
                




        text = ob['text'].lower()

        if text == "привет":
            VK.send(ob['peer_id'], 'Привет! \nЯ чудный бот!')
            return

        if text == "умри":
            VK.send(ob['peer_id'], 'сдохх')
            exit()
            return

        if text == "клава":
            VK.send(ob['peer_id'], 'Выберите действие на клавиатуре', keyboard=Keyboards.mainMenu)
            return



        #m = re.search('сох[a-zа-я]*', text)
        #if m:
        #    VK.send(ob['peer_id'], 'Сохранено')
        #    save_prefs(inc_ts=True)
        #    return

        #m = re.search(r'выкл[а-я]* ([a-z-_]+)', text)
        #if m:
        #    try:
        #        found = str(m.group(1))
        #    except ValueError:
        #        VK.send(ob['peer_id'], 'Ошибка в чтении')
        #        return
        #    VK.send(ob['peer_id'], 'Выключение модуля ' + found)
        #    hub_add({'target':'control','action':'stop','proc':found,'from': me})
        #    return

VK = VKAPI(bot_token)
BOT = BOT_MANAGER()

load_prefs()

print('\n[HOST] \tLongpoll starting...')


def gupd():
    global pref
    global bot_token

    tick = datetime.now()

    while True:
        try:
            r = req.get('%s?act=a_check&key=%s&ts=%s&wait=25&mode=2&version=3' % (pref['server'],pref['key'],pref['ts'])).json()
        except req.exceptions.RequestException:
            continue

        print(r)

        if 'failed' in r:
            if r['failed']==1:
                print('[HOST] Refreshing TS')
                pref['ts']=r['ts']
                continue
            if r['failed']==2:
                print('[HOST] Refreshing KEY')
                urla = 'https://api.vk.com/method/groups.getLongPollServer?group_id='+bot_id+'&lp_version=3&v=5.95&access_token=' + bot_token
                #print(urla)
                new = req.get(urla).json()

                #print(new)
                pref['key']=new['response']['key']
                pref['ts']=new['response']['ts']

                save_prefs()
                #print(pref)
                continue
            if r['failed']==3:
                print('[HOST] Refresh KEY, TS (User data corrupted)')
                continue
            if r['failed']==4:
                print('[HOST] Unallowable VERSION')
                break
            continue

        pref['ts']=r['ts']

        for evn in r['updates']:
            if evn['type'] in ['message_new','message_edit']:
                obj = evn['object']

                if evn['type'] == 'message_new':
                    #print('[BOT] \t('+datetime.utcfromtimestamp(obj['date']).strftime('%H:%M:%S')+'): Message from',VK.getPeer(obj['peer_id'])['title'])
                    BOT.mMessage(obj)

        if int((datetime.now() - tick).total_seconds()) > 300:
            tick = datetime.now()
            save_prefs()

gupd()

#if __name__ == '__main__':
#    gupd()
    #_thread.start_new_thread(gupd, ())
    #app.run('0.0.0.0', port=12102, debug=False, threaded=True)
    ## FLASK - currently isn't working
