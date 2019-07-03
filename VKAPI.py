import requests as req
import random
import json

class VKAPI:
    def __init__(self, token):
        self.token = str(token)
        self.cPeers = [] #cached Peers
        self.cPeersId = [] #cahed Peer ids, for speed improvements
        self.cConvs = [] #cached Conversations

        # На случай вопроса, чем отличаются cPeers и cConvs
        # cPeers - хранит всевозможных адресатов, засветившихся людей
        #           для которых возможно потребуется получение полей
        # cConvs - список диалогов, закешированных при вызове getConvs

    def send(self, peer, message='',keyboard={}, additional=''):
        sr = req.get('https://api.vk.com/method/messages.send',
                params={'random_id':str(random.randint(0,20000000)),
                        'peer_id':str(peer),
                        'message':message,
                        'v':'5.95',
                        'keyboard':json.dumps(keyboard),
                        'access_token':self.token})
        #print(sr.text)
        print('[API] \tMessage sent, check manually.')

    def getPeer(self, peer, force=False):
        res = {}

        #print(self.cPeers)
        #print(self.cPeersId)
        if force == False:
            if peer in self.cPeersId:
                try:
                    res = [i for i in self.cPeers if i['id'] == peer][0]
                except IndexError:
                    print('[WARNING] \t Getting peer from cache is unavailable! (getPeer)')
                return res
        print('[API] \tCaching new peers...')

        got_raw = req.get('https://api.vk.com/method/messages.getConversationsById',
                          params={'peer_ids':str(peer),
                                  'extended':1,
                                  'v':'5.95',
                                  'access_token':self.token}).json()['response']

        got = got_raw['items'][0]
        self.cPeersId.append(got['peer']['id'])
        if 'profiles' in got_raw.keys():
            for prof in got_raw['profiles']:
                name = prof['first_name']+' '+prof['last_name']
                self.cPeersId.append(prof['id'])
                self.cPeers.append({'id': prof['id'],
                            'type': 'user',
                            'title': name})



        self.cPeers.append({'id': got['peer']['id'],
                            'type': got['peer']['type'],
                            'title': [got['chat_settings']['title']
                                      if got['peer']['type']=='chat'
                                      else self.getPeer(got['peer']['id'])][0]})
        res = [i for i in self.cPeers if i['id'] == peer]
        #print(self.cPeers)
        #print(self.cPeersId)
        return res[0]

    def getConvs(self, reload=True, offset=0, count=20, fields="first_name,last_name,id"):

        if reload or len(self.cConvs)<1:
            print('[API] \tRefreshing conversations...')
            res = []
            got_raw = req.get('https://api.vk.com/method/messages.getConversations',
                          params={'offset':offset,
                                  'extended':1,
                                  'count':count,
                                  'fields':fields,
                                  'v':'5.95',
                                  'access_token':self.token}).json()['response']

            if 'profiles' in got_raw.keys():
                for prof in got_raw['profiles']:
                    name = prof['first_name']+' '+prof['last_name']
                    self.cPeersId.append(prof['id'])
                    self.cPeers.append({'id': prof['id'],
                                'type': 'user',
                                'title': name})

            if 'groups' in got_raw.keys():
                for grp in got_raw['groups']:
                    title = grp['name']
                    self.cPeersId.append(grp['id'])
                    self.cPeers.append({'id': grp['id']*(-1),
                                'type': 'group',
                                'title': title})

            got = got_raw['items']

            for item in got:
                conv = item['conversation']
                last = item['last_message']
                res.append({'id':conv['peer']['id'],
                            'type':conv['peer']['type'],
                            'date':last['date'],
                            'last_from':last['from_id'],
                            'text':last['text'],
                            'title':self.getPeer(conv['peer']['id'])['title']})

            self.cConvs = res

        return self.cConvs

    def printConvs(self):
        print('[CB] \tДиалоги')
        convs = self.getConvs(reload=False)
        counter = 0
        ans = ''
        for conv in convs:
            ans += ('\t%s) [Диалог с %s] %s: %s\n' %
                  (counter, conv['title'],self.getPeer(conv['last_from'])['title'],conv['text']))
            counter+=1
        print(ans, '\t---')
        return ans

    def printChat(self,cid):
        conv_inf = self.getConvs(reload=False)[cid]
        print('[CB] \tДиалог c',conv_inf['title'])

    def getConvById(self,cid,cnt,auto_format=False):
        print('[CB] \tПолучение списка сообщений из диалога',cid)
        rmsg = []
        #https://api.vk.com/method/messages.getHistory?count=1&peer_id=133318282&extended=0&v=5.95&access_token=
        conv_raw = req.get('https://api.vk.com/method/messages.getHistory',
                          params={'peer_id':str(cid),
                                  'extended':0,
                                  'v':'5.95',
                                  'count':str(cnt),
                                  'access_token':self.token}).json()['response']

        msgs_raw = conv_raw['items']
        for msg in msgs_raw:
            rmsg.append({'date':msg['date'],
                         'from':msg['from_id'],
                         'text':msg['text'],
                         'fwds':msg['fwd_messages'],
                         'attachs':msg['attachments']})

        if auto_format == True:
            for i in range(len(rmsg)):
                rmsg[i] = self.getPeer(rmsg[i]['from'])['title']+': '+rmsg[i]['text']

        return rmsg

        print('[CB] \tПолучение списка сообщений из диалога',cid)
