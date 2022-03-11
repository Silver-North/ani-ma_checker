from requests import get
from bs4 import BeautifulSoup
from os import system
from time import strftime, localtime
from datetime import date
from json import dumps, load


def checkURL(url, series):
    link = get(url)
    soup = BeautifulSoup(link.text, 'html.parser')
    names = soup.find_all('div', class_='shortstoryHead')
    name = names[0].text[22:-18:]
    names = name.split(' /')
    mass = names[1].split('[')
    arr = []

    if len(mass) == 2:
        mass = name.split(' ')
        arr = mass[-3].split('-')
    elif len(mass) == 3:
        mass = name.split(' ')
        arr = mass[-8].split('-')
    
    num = int(arr[-1])

    if num == series:
        current_date = date.today()
        current_time = strftime("%H:%M", localtime())
        system('notify-send "Вышло кое-что новенькое!!!"')
        with open('setting.json', 'r') as js:
            to_json = load(js)
        to_json['notify'] = 'unchecked'
        with open('setting.json', 'w') as js:
            js.write(f"{dumps(to_json, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': '))}")
        with open('notify.txt', 'a') as d:
            d.write(f'[{current_date.day}/{current_date.month}/{current_date.year} - {current_time}] > {names[0]} - new series {series}\n')
    return names[0]


def checking(urls, numbers):
    for i in enumerate(urls):
        series = numbers[i[0]] + 1
        checkURL(i[1], series)
    print(True)


def checkingWrite(urls, numbers):
    names = []
    for i in enumerate(urls):
        series = numbers[i[0]] + 1 
        names.append(checkURL(i[1], series))
    print(True)
    
    with open('setting.json', 'r') as reads:
        data = load(reads)
    data['name'] = names
    with open('setting.json', 'w') as js:
        js.write(f"{dumps(data, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': '))}")
