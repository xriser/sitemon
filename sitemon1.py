import re
import requests
from time import localtime, strftime
from slackclient import SlackClient

#prod
url = 'http://hotline.ua/computer/processory/'


def send2slack(chan, msg):
    #https://api.slack.com/custom-integrations/legacy-tokens
    slack_token = "tocken"
    #os.environ["slack-token"]
    sc = SlackClient(slack_token)
    sc.api_call(
        "chat.postMessage",
         channel=chan,
         text=msg
    )



def log(string):
    dt = strftime("[%d-%m-%Y %H:%M:%S] ", localtime())
    with open("sitemon.log", "a") as myfile:
        myfile.write(dt + string + "\r\n")
    pass

def get_data():
    print("Check response...")
    try:
        response = requests.get(url, timeout=(15, 15))
        response.raise_for_status()

    except requests.exceptions.ReadTimeout:
        print('Oops. Read timeout occured')

    except requests.exceptions.ConnectTimeout:
        print('Oops. Connection timeout occured!')

    except requests.exceptions.ConnectionError:
        print('Seems like dns lookup failed..')

    except requests.exceptions.HTTPError as err:
        print('Oops. HTTP Error occured')
        print('Response is: {content}'.format(content=err.response.content))

    print("Response status code: " + str(response.status_code))

    text = response.text

    match = re.search('Core i3-8xxx|Core i5-8xxx|Core i7-7xxx', text)

    if match:
        f = match.group(0)
        send2slack("#sitemon", ":rotating_light: Found new item - " + f)
    pass


get_data()
