from os import system, path
from datetime import date
from time import strftime, localtime
from shutil import copyfileobj
from json import dumps

from requests import get
from bs4 import BeautifulSoup
from pyttsx3 import init
from PIL import Image


check = False
current_path = f'{path.dirname(path.realpath(__file__))}'


def checkVoice(data, check):
    if check > 0:
        data['notify']['notify'] = 'unchecked'
        system('notify-send "Вышло кое-что новенькое!!!"')
        tts = init()
        tts.say("Something new came out... check the natification log...")
        tts.runAndWait()
    return data['notify']['notify']


def parseRanobe(link):
    try:
        url = get(link)
        soup = BeautifulSoup(url.text, "html.parser")
        if 'tl.rulate.ru' in link:
            name = soup.find('h1').text.split(' / ')[1]
            description_start = soup.find('div', id="Info")
            desi = description_start.find_all('div')[2]
            img = f"https://tl.rulate.ru{desi.find('img')['src']}"

            ran = 12
            while True:
                dess = description_start.find_all('div')[ran]
                ran += 1
                descriptions = dess.find_all('p')
                if len(descriptions) == 0 or descriptions is None:
                    continue
                description = []
                for i in descriptions:
                    if len(i.text) > 1:
                        description.append(i.text)
                break
            description = "\n".join(description)
            
            table = soup.find('table', 
                class_="table table-condensed table-striped").find_all('tr')
            toms = soup.find_all('tr', class_="volume_helper")

            tr = []
            tom = []
            set_class = [] 
            chapters = []

            for i in table:
                tr.append(i.get('class'))

            if len(toms) == 0:
                tom = 1
                for i in tr:
                    if isinstance(i, list) and 'chapter_row' in i:
                        if " ".join(i) in set_class:
                            continue
                        else:
                            set_class.append(" ".join(i))
            elif len(toms) > 1:
                for i in tr:
                    if isinstance(i, list) and len(i) > 1:
                        if " ".join(i) in set_class:
                            continue
                        else:
                            set_class.append(" ".join(i))
                for i in toms:
                    if i is not None and len(i.text) > 1:
                        tom.append(i.text.split()[1])
            
            for i in enumerate(set_class):
                chapter = len(soup.find_all('tr', class_=i[1]))
                if isinstance(tom, int):
                    chapters.append(f'{tom}.{chapter}')
                else:
                    chapters.append(f'{tom[i[0]]}.{chapter}')
            all = chapter = chapters[-1]
            print(f'{name}\n{img}\n{description}\n{chapter}')

        elif 'https://xn--80ac9aeh6f.xn--p1ai' in link:
            n_head = 'cursor-default md:cursor-pointer font-bold text-2xl'
            n_body = ' md:text-3xl sm:leading-7 lg:leading-10 xl:leading-9 pt-1 '
            n_footer = 'text-black-0 dark:text-grayNormal-200 truncate'
            name = soup.find('h1', class_=f"{n_head}{n_body}{n_footer}").text
            description = soup.find('div', class_="BookPage_desc__2rsZC").text
            img = soup.find('img',
                class_="xs:rounded-md md:w-[180px] lg:w-[220px]")['src']
            c_head = 'text-black-0 dark:text-grayNormal-200 hover:text-primary '
            c_body = 'cursor-default md:cursor-pointer dark:hover:text-primary '
            c_footer = 'truncate text-sm md:text-base'
            chapters = soup.find_all('a', class_=f"{c_head}{c_body}{c_footer}")
            all = []
            for i in chapters[0].text:
                if i.isnumeric():
                    all.append(i)

            print(f'{name}\n{description}\n{img}\n{0}\n{"".join(all)}')
            
        elif 'ranobehub.org' in link:
            name = soup.find('h1', class_="ui huge header").text
            img = soup.find('img', class_="image")['data-src']
            description = soup.find('div', class_="book-description__text").text
            chapters = soup.find('div', class_="book-meta-value book-stats")
            chapter = chapters.find('strong').text
            print(f'{name}\n{img}\n{description[2:-2:]}\n{chapter}')

        elif 'ruranobe.ru' in link:
            name = soup.find('span', class_="headline__text").text
            url_p = 'https://ruranobe.ru/'
            img = f'{url_p}{soup.find_all("img", class_="detail__image")[0]["src"]}'
            description = soup.find('div', class_="read-more").text
            chapters = soup.find('div', class_="detail__actions")
            chapter = chapters.find('a').text
            chapters = soup.find_all('a', class_="list__item")
            for i in chapters:
                tom = i.find('span', 
                    class_="list__item-number").text.split()[1].split(":")[0]
                desc = i.find('span', class_="list__name").text
                if chapter == desc[1:-1:]:
                    print(tom)
                    break
            print(f'{name}\n{img}\n{description[1:-1:]}\n{tom}')
        return name, img, description, chapter, all
    except Exception as e:
        system(f'notify-send "ERRor for parse Ranobe {link}\n{e}"')


def checkFixedOutput(dicts, count=0):
    link = get('https://animevost.org')
    soup = BeautifulSoup(link.text, 'html.parser')
    raspisanie = soup.find_all('ul', class_='raspis_fixed')
    links = raspisanie[0].find_all("a")
    txt = [i.split(' / ') for i in raspisanie[0].text.split('\n')[1:-1:]]
    link = [links[i[0]]["href"] for i in enumerate(txt)]
    for i,v in enumerate(link):
        for j in dicts['anime']['urls']:
            if v == j:
                mass = txt[i][1].split('[')
                check = numCheck(dicts, mass,
                            dicts['anime']['ova'][dicts['anime']['urls'].index(v)]+1,
                            dicts['anime']['series'][dicts['anime']['urls'].index(v)]+1,
                            txt[i][0])
                count += 1 if check else 0
    dicts['notify']['notify'] = checkVoice(dicts, count)
    if isinstance(dicts, dict):
        with open(f'{current_path}/setting.json', 'w') as js:
            js.write(dumps(dicts, sort_keys=False, indent=4,
                       ensure_ascii=False, separators=(',', ': ')))
    else:
        system('notify-send "Error for write notify <anime>"')
    txt = [' / '.join(i) for i in txt]
    return txt, link, dicts['notify']['notify']


def numCheck(data, mass, ova, series, name, check=False):
    inti = mass[-1].split()
    ind = -1 if len(mass) == 2 else -2 if len(mass) == 3 else -2
    if len(mass) == 2:
        arr = int(mass[-1].split()[0]) if '-' not in mass[-1] else -1 if \
              'Анонс' in mass[-1] else int(mass[-1].split()[0].split('-')[1])
    else:
        arr = int(mass[ind].split()[0].split('-')[1]) if '-' in mass[ind] else \
              -1 if 'Анонс' in mass[ind] else mass[ind][:1:]
    int_i = int(inti[1]) if ova == 1 and 'OVA' in mass[-1] else \
            int(inti[1].split('-')[1]) if 'OVA' in mass[-1] else 0

    num = arr if isinstance(arr, int) else int(arr[-1].split()[0])
    c_d = date.today()
    c_t = strftime("%H:%M", localtime())
    note = f'[A][{c_d.day}/{c_d.month}/{c_d.year} - {c_t}] > {name}'
    txt = f'{note} - new series {num} & new ova-{int_i}\n' if num >= series and \
          ova <= int_i else f'{note} - new series {num}\n' if num >= series and \
          ova != int_i else f'{note} - new ova-{int_i}\n' if ova <= int_i and \
          series != num else ""
    if txt != "":
        data['notify']['anime'].append(txt)
        if isinstance(data, dict):
            with open(f'{current_path}/setting.json', 'w') as js:
                js.write(dumps(data, sort_keys=False, indent=4,
                            ensure_ascii=False, separators=(',', ': ')))
        else:
            system('notify-send "Error for write notify <anime>"')
        check = True
    return check



def checkURL(data, url, series, ova, check=False):
    try:
        soup = BeautifulSoup(get(url).text, 'html.parser')
        names = soup.find('div', class_='shortstoryHead').text[22:-18:].split(' / ')
        name = names[0]
        mass = names[1].split('[')
        check = numCheck(data, mass, ova, series, name)
    except Exception as e:
        name = ''
        print(f'notify-send "error ===>\n{e}"')
    return name, check


def getDescription(url):
    try:
        soup = BeautifulSoup(get(url).text, 'html.parser')
        desc = soup.find_all('p')
        description = desc[7].text if len(desc) == 10 else desc[8].text
        img = soup.find_all('img', class_='imgRadius')[0]["src"]
        image = f'https://www.animevost.org{img}'
        img = img.split('/')
        if not path.isdir(f'{current_path}/description/'):
            system(f'mkdir "{current_path}/description/"')
        r = get(image, stream=True)
        if r.status_code == 200:
            with open(f'{current_path}/description/{img[-1]}', 'wb') as f:
                r.raw.decode_content = True
                copyfileobj(r.raw, f)

        image = loadImage(img[-1])
        return image, description
    except Exception as e:
        print('error:\n', e)


def loadImage(name):
    width, height = (90, 110)
    img = Image.open(f'{current_path}/description/{name}')
    resizing = img.resize((width, height), Image.ANTIALIAS)
    resizing.save(f'{current_path}/description/{name}')
    return name
