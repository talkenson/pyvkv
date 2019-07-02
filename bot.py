import telegram
import requests as req
bot = telegram.Bot(token='894597530:AAG2NYHtxh0H580HmbAmnQ3vErWZbmnlPYs')
print(bot.get_me())
req.get('https://api.vk.com/method/messages.send',
        params={'random_id':str(random.randint(0,20000000)),
                        'peer_id':'111612348',
                        'message':'started',
                        'v':'5.95',
                        'access_token':'820a937919b3a84c3b84c07a7e66df6e501fcb59e2fa1f083aea54149c6cd95c14552068c643a081924d9'})
