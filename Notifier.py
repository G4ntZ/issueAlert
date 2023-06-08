import requests
import json
import configparser
import logging

logging.basicConfig(format='%(asctime)s %(message)s', filename='notifier.log', level=logging.DEBUG)

class Plugin:
    def __init__(self, jiraUser, jiraPass, telegramToken, telegramChat):
        self.jiraUser = jiraUser
        self.jiraPass = jiraPass
        self.telegramToken = telegramToken
        self.telegramChat = telegramChat

    def jiraPendientes(self):
        url = "https://jira.afphabitat.net/rest/api/2/search"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {"jql": f"issuetype in (Tarea_QATecnico) AND Status = 'Por Hacer' OR status in ('Por Revisar QAT', 'Por Hacer QAT', 'Por Hacer QAT PROD')",
                "startAt": 0, "maxResults": 100, "fields": ["key"]}
        resp = requests.post(url, headers=headers, json=data,
                             auth=(self.jiraUser, self.jiraPass))
        response = json.loads(resp.text)
        if int(response['total']) >= 1:
            jiras = ""
            for jira in response['issues']:
                jiras = jiras + str(jira['key']) + "\n"
            self.sendTelegram(jiras)
        else:
            logging.debug("sin jiras pendientes")

    def sendTelegram(self, message):
        apiURL = f'https://api.telegram.org/bot{self.telegramToken}/sendMessage'
        try:
            response = requests.post(apiURL, json={'chat_id': self.telegramChat, 'text': message})
            logging.debug(response.status_code)
        except Exception as e:
            logging.debug(e)


config = configparser.ConfigParser()
config.read('notifier.properties')
user = config['jira']['user']
password = config['jira']['pass']
token = config['telegram']['token']
chatid = config['telegram']['chatid']

plugin = Plugin(user,password,token,chatid)
plugin.jiraPendientes()
