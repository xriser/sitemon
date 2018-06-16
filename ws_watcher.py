import re
import requests
from slackclient import SlackClient
from datetime import datetime
import configparser
import json
import sys
import time
import os
import codecs

from requests_html import HTMLSession

from bs4 import BeautifulSoup  # Or from BeautifulSoup import BeautifulSoup


#notifier
#turl = 'https://api.telegram.org/bot563628596:AAHWIuaLsNbQCDBdEgmq_j7XsBUHH3ouqe8/sendMessage?chat_id=-1001237195737&text='


logfile = 'sitewatcher.log'
dir_path = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read(dir_path + "/" + 'config.ini', encoding="utf8")
sections = config.sections()


turl = 'https://api.telegram.org/bot' + config['settings']['telegram_bot_token'] + '/sendMessage?chat_id=' + config['settings']['telegram_channel_id'] +'&text='


def get_data(url,regex):
    print("Check response...")
    session = HTMLSession()
    r = session.get(url)
    r.html.render()

    text = r.html.find(regex, first=True).text

    print(text)
    print(regex)

    return text


def send2telegram(send_text):
    response = requests.get(turl + send_text + '&parse_mode=html', timeout=(15, 15))
    print(response)
    pass


today = datetime.now().strftime('%Y-%m-%d')


try:
   with open(dir_path + "/" + logfile, 'r') as f:
      file_content = f.read()
      print("read file")
   if not file_content:
      print("no data in file")
   else:
       print(file_content)


except IOError as e:
   print("I/O error({0}): {1}".format(e.errno, e.strerror))
   print("no file, will check")
   with open(dir_path + "/" + logfile, "w") as myfile:
       #dt = datetime.now().strftime('%Y-%m-%d')
       myfile.write('')
   #get_data()
except: #handle other exceptions such as attribute errors
   print("Unexpected error:", sys.exc_info()[0])
print("done")


log = configparser.ConfigParser()
log.read(dir_path + "/" + logfile, encoding="utf8")


for key in sections:
    print(key)
    if key not in ['settings']:
        if key not in log.sections():
            log.add_section(key)

        print(time.time())
        if not log.has_option(key, 'lastcheck'):
            log[key]['lastcheck'] = '0'

        if not log.has_option(key, 'data'):
            log[key]['data'] = ''

        print(float(log[key]['lastcheck']))

    #request site only if checkperiod
        if time.time() - float(log[key]['lastcheck']) > float(config[key]['check_period']):
            text = get_data(key, config[key]['regex'])
            if 'privat' in key:
                text = json.loads(text)
                del text[3]
            print('----------------------------------------------------')
            print(text)
            print('----------------------------------------------------')
            print(log[key]['data'])
            print('----------------------------------------------------')

            if str(log[key]['data']) != str(text):
                print('diff')

            if (time.time() - float(log[key]['lastcheck']) > float(config[key]['check_period']) and str(log[key]['data']) != str(text)):
                log[key]['data'] = str(text)
                if 'privat' in key:
                    print(config[key]['regex'])

                    #log[key]['data'] = text
                    post_text = "{0:<6} {1:<8} {2:<8} {3:<0}".format("cur", "base", "buy", "sale\n")
                    for k in text:
                        #print(k['ccy']);
                        ccy = "{0:<8}".format(k['ccy'])
                        base_ccy = k['base_ccy']
                        buy = ("%10.2f" % (round(float(k['buy']), 3)))
                        sale = str("%10.2f" % (round(float(k['sale']), 3)))
                        post_text = post_text + '' + ccy + '' + base_ccy + '' + buy + '' + sale + '\n'

                    print(post_text)
                    log[key]['lastsend'] = str(time.time())
                    send2telegram('<pre>' + post_text + '</pre>')

                else:
                    post_text = 'New data: ' + text + '\n' + key
                    send2telegram(post_text)


            log[key]['lastcheck'] = str(time.time())
            with open(dir_path + "/"
                      + logfile, 'w') as configfile:
                log.write(codecs.open(dir_path + "/" + logfile, 'wb+', 'utf-8'))
                #log.write(configfile)

