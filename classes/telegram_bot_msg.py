import requests

class TelegramBotMsg:
    def __init__(self,token):
        self.token = token
        self.api = 'https://api.telegram.org/bot'
        self.path = '/sendMessage'
        self.header = {'Content-Type' : 'application/json'}

    def sendMsg(self, to, msg):
        url = '{}{}{}'.format(self.api,self.token,self.path)
        data = {
            'chat_id' : to,
            'text' : msg,
            'disable_web_page_preview' : 'true',
            'disable_notification' : 'false'
        }

        result = requests.post(url=url,json=data,headers=self.header)

        return result.text