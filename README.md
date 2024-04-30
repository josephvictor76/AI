import requests
import json
import nltk
import re
from nltk.stem import WordNetLemmatizer
import csv
from pathlib import Path

nltk.download('punkt')
lemmatizer = WordNetLemmatizer()
nltk.download('wordnet')
headers = {
    'Content-Type': 'application/json',
}
api_key = Path('apikey.txt').read_text()

ticket_file = 'tickets.csv'

rows = []

with open(ticket_file, encoding='utf-8-sig') as f:
    csvreader = csv.reader(f)
    for row in csvreader:
        rows.append(row)


def clean_noise(text):
    text = re.sub(r'[^a-zA-Z\s\U0001F600-\U0001F64F]', '', text)
    text = text.lower()
    text = ' '.join([lemmatizer.lemmatize(w) for w in nltk.word_tokenize(text)])
    return text


def get_grouplist():
    desc_response = requests.get(
        'https://cityofgso.freshservice.com/api/v2/groups?workspace_id=2',
        headers=headers,
        auth=(api_key, 'X'),
    )
    groupdict = {}

    with open('grouplist.json', 'wb') as f:
        f.write(desc_response.content)

    with open('grouplist.json', encoding='utf-8-sig') as f:
        desc_data = json.load(f)

    for i in range(len(desc_data['groups'])):
        groupdict.update({desc_data['groups'][i]['id']: desc_data['groups'][i]['name']})

    return groupdict


group_dict = get_grouplist()


def get_conversation(tick_id):
    tick_file = str(tick_id) + '.json'
    conv_response = requests.get(
        'https://cityofgso.freshservice.com/api/v2/tickets/{}/conversations'.format(tick_id),
        headers=headers,
        auth=(api_key, 'X'),
    )

    with open(tick_file, 'wb') as f:
        f.write(conv_response.content)

    with open(tick_file, encoding='utf-8-sig') as f:
        conv_data = json.load(f)

    desc_response = requests.get(
        'https://cityofgso.freshservice.com/api/v2/tickets/{}'.format(tick_id),
        headers=headers,
        auth=(api_key, 'X'),
    )

    with open(tick_file, 'wb') as f:
        f.write(desc_response.content)

    with open(tick_file, encoding='utf-8-sig') as f:
        desc_data = json.load(f)

    desc_text = json.dumps(desc_data['ticket']['description_text'])

    try:
        bodytext = json.dumps(conv_data['conversations'][0]['body_text'])
        conv_text = (json.dumps(bodytext, indent=4))

    except IndexError:
        conv_text = "null "

    ticket_info = "Description:" + desc_text + "\n" + "Conversation text:" + conv_text

    return ticket_info

def get_ticket(tick_id):
        tick_file = str(tick_id) + '.json'
        tick_response = requests.get(
            'https://cityofgso.freshservice.com/api/v2/tickets/{}'.format(tick_id),
            headers=headers,
            auth=(api_key, 'X'),
        )

        with open(tick_file, 'wb') as f:
            f.write(tick_response.content)

        with open(tick_file, encoding='utf-8-sig') as f:
            tick_data = json.load(f)

        title = ('Title: ' + tick_data['ticket']['subject'] + ': ').append(tick_data)
        group_id = ('Group: ' + tick_data['ticket']['group_id'] + ': ').append(tick_data)

        if tick_data['ticket']['type'] == 'Incident':
            details = 'Details: ' + tick_data['ticket']['description_text']

        else:
            serv_response = requests.get(
                'https://cityofgso.freshservice.com/api/v2/tickets/{}/requested_items'.format(tick_id),
                headers=headers,
                auth=(api_key, 'X'),
            )

            with open(tick_file, 'wb') as f:
                f.write(serv_response.content)

            with open(tick_file, encoding='utf-8-sig') as f:
                serv_data = json.load(f)

            serv_request = serv_data['requested_items']['request']

        with open(tick_file, encoding='utf-8-sig') as f:
            desc_data = json.load(f)

        desc_text = json.dumps(desc_data['ticket']['description_text'])

        try:
            for i in range(len(desc_data['conversations'])):
                sure_text = (desc_data['conversations'][i]['body_text'])
                json.dump(sure_text, f, indent=4)
            bodytext = json.dumps(desc_data['conversations'][0]['body_text'])
            conv_text = (json.dumps(bodytext, indent=4))

        except IndexError:
            conv_text = "null "

        ticket_info = "Description:" + desc_text + "\n" + "Conversation text:" + conv_text

        ticket_info = clean_noise(ticket_info)

        return ticket_info

for i in range(len(rows)):
    tick_id = rows[i][0]
    tick_info = get_ticket(tick_id)
    conv_info = get_conversation(tick_id)
    tick_file = tick_id + '.json'
    with open(tick_file, 'w') as f:
        f.write(tick_info + conv_info)
