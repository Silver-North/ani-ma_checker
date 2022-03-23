from requests import get
from bs4 import BeautifulSoup
from os import system, path
from time import strftime, localtime
from datetime import date
from json import dumps, load
from pyttsx3 import init
from shutil import copyfileobj
from PIL import Image


check = 0
flag = True
tts = init()
current_path = f'{path.dirname(path.realpath(__file__))}'


def checkURL(url, series):
    global check
    print(url)
    try:
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
            check += 1
            current_date = date.today()
            current_time = strftime("%H:%M", localtime())
            with open(f'{current_path}/setting.json', 'r') as js:
                to_json = load(js)
            to_json['anime']['notify'] = 'unchecked'
            with open(f'{current_path}/setting.json', 'w') as js:
                js.write(f"{dumps(to_json, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': '))}")
            with open(f'{current_path}/notify.txt', 'a') as d:
                d.write(f'[{current_date.day}/{current_date.month}/{current_date.year} - {current_time}] > {names[0]} - new series {series}\n')
        return names[0]
    except Exception as e:
        with open(f'{current_path}/setting.json', 'r') as reads:
            data = load(reads)
        data['anime']['log'] = f'Error: {e}'
        with open(f'{current_path}/setting.json', 'w') as js:
            js.write(f"{dumps(data, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': '))}")


def getDescription(url):
    try:
        link = get(url)
        soup = BeautifulSoup(link.text, 'html.parser')
        desc = soup.find_all('p')
        img = soup.find_all('img', class_='imgRadius')
        image = f'https://www.animevost.org{img[0]["src"]}'
        img = img[0]['src'].split('/')
        if not path.isdir(f'/home/north/data/projects/Python/IsDev/Anime-parser/description/'):
            system(f'mkdir "/home/north/data/projects/Python/IsDev/Anime-parser/description/"')
        r = get(image, stream=True)
        if r.status_code == 200:
            with open(f'{current_path}/description/{img[-1]}', 'wb') as f:
                r.raw.decode_content = True
                copyfileobj(r.raw, f)
        
        image = loadImage(img[-1])
        return image, desc[8].text
    except Exception as e:
        print('error:\n', e)


def loadImage(name):
    width = 90
    height = 110
    new_name = name.split('.')
    img = Image.open(f'{current_path}/description/{name}')
    resizing = img.resize((width, height), Image.ANTIALIAS)
    resizing.save(f'{current_path}/description/{name}')
    return name


def setDescription(urls):
    images = []
    descs = []
    for i in urls:
        img, desc = getDescription(i)
        images.append(img)
        descs.append(desc)

    with open(f'{current_path}/setting.json', 'r') as reads:
        data = load(reads)

    data['anime']['description'] = descs
    data['anime']['images'] = images
    
    with open(f'{current_path}/setting.json', 'w') as js:
        js.write(f"{dumps(data, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': '))}")


def checking(urls, numbers):
    global check, flag
    for i in enumerate(urls):
        if flag:
            series = numbers[i[0]] + 1
            checkURL(i[1], series)
    flag = True
    if check > 0:
        tts.say("Something new came out... check the natification log...")
        tts.runAndWait()
        system('notify-send "Вышло кое-что новенькое!!!"')
    check = 0
    print(True)


def checkingWrite(urls, numbers):
    global flag
    names = []
    for i in enumerate(urls):
        if flag:
            series = numbers[i[0]] + 1
            names.append(checkURL(i[1], series))
    flag = True
    print(True)

    with open(f'{current_path}/setting.json', 'r') as reads:
        data = load(reads)
    data['anime']['name'] = names
    with open(f'{current_path}/setting.json', 'w') as js:
        js.write(f"{dumps(data, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': '))}")
        

def stopCheck():
    global flag
    flag = False
