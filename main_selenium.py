from selenium import webdriver
from os import path, system, rename
from time import sleep, localtime, strftime
from json import dumps, load


path_down = f'{path.dirname(path.realpath(__file__))}/downloads'
current_path = f'{path.dirname(path.realpath(__file__))}'
prefs = {'download.default_directory': path_down, "download.prompt_for_download": False}
check_flag = False

option = webdriver.ChromeOptions()
option.add_argument('--headless')
option.add_experimental_option("prefs", prefs)

def allParsing():
    global check_flag
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    option.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(path.join(path.dirname(__file__), 'chromedriver'), options=option)
    url, numbers = listLinkOrNumbers()
    logs = []
    if len(url) > 0:
        for i in enumerate(url):
            try:
                series = numbers[i[0]] + 1
                print(i)
                driver.get(i[1])
                print(0)
                sleep(3)
                search_count_series = driver.find_elements_by_class_name('epizode')
                name = driver.find_element_by_class_name('shortstoryHead').text
                next = driver.find_element_by_class_name('next')
                name_dir = name.split(' /')

                print(name_dir[0])

                if len(search_count_series) == series:
                    if len(search_count_series) > 6:
                        next.click()
                        if len(search_count_series) > 12:
                            next.click()
                            if len(search_count_series) > 18:
                                next.click()
                                if len(search_count_series) > 24:
                                    next.click()
                    search_count_series[-1].click()
                    sleep(15)
                    frame = driver.find_elements_by_tag_name('iframe')
                    if len(frame) == 4:
                        driver.switch_to.frame(frame[-2])
                    elif len(frame) == 3:
                        driver.switch_to.frame(frame[-1])
                    sleep(3)
                    down = driver.find_elements_by_class_name('butt')
                    let = down[-2].get_attribute("href").split('?')
                    let = let[0].split('/')
                    sleep(3)
                    down[2].click()
                    print(100)
                    check_flag = False
                    checkUpload(let[-1], url, name_dir[0], i[1], name, series, numbers)
                    logs.append(f'{i[0]} - {name_dir[0]} - New series {series}\n')
                else:
                    logs.append(f'{i[0]} - {name_dir[0]} - No new < {series} > series\n')
                driver.switch_to.default_content()
                sleep(5)
            except Exception as e:
                logs.append(f'{i[0]} - !!! << Error: {e} >> !!!\n')

    driver.quit()

    with open(f'{current_path}/setting.json', 'r') as reads:
        data = load(reads)
    data['anime']['logs'] = logs
    with open(f'{current_path}/setting.json', 'w') as js:
        js.write(f"{dumps(data, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': '))}")


def listLinkOrNumbers():
    with open(f'{current_path}/setting.json', 'r') as reads:
        data = load(reads)
    return data['anime']['urls'], data['anime']['series']


def oneParsing(url, digit):
    global check_flag
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    option.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(path.join(path.dirname(__file__), 'chromedriver'), options=option)
    urls, numbers = listLinkOrNumbers()
    log = ''
    try:
        series = digit + 1
        print(url)
        driver.get(url)
        print(0)
        sleep(3)
        search_count_series = driver.find_elements_by_class_name('epizode')
        name = driver.find_element_by_class_name('shortstoryHead').text
        next = driver.find_element_by_class_name('next')
        name_dir = name.split(' /')

        print(name_dir[0])

        if len(search_count_series) == series:
            if len(search_count_series) > 6:
                next.click()
                if len(search_count_series) > 12:
                    next.click()
                    if len(search_count_series) > 18:
                        next.click()
                        if len(search_count_series) > 24:
                            next.click()
            print(search_count_series[-1].text)
            search_count_series[-1].click()
            sleep(15)
            frame = driver.find_elements_by_tag_name('iframe')
            if len(frame) == 4:
                driver.switch_to.frame(frame[-2])
            elif len(frame) == 3:
                driver.switch_to.frame(frame[-1])
            sleep(3)
            down = driver.find_elements_by_class_name('butt')
            let = down[-2].get_attribute("href").split('?')
            let = let[0].split('/')
            sleep(3)
            down[2].click()
            print(100)
            check_flag = False
            checkUpload(let[-1], urls, name_dir[0], url, name, series, numbers)
            log = f'{name_dir[0]} - New series {series}'
        else:
            log = f'{name_dir[0]} - No new < {series} > series'
        driver.switch_to.default_content()
    except Exception as e:
        driver.quit()
        log = f"!!! << Error: {e} >> !!!"

    driver.quit()
    with open(f'{current_path}/setting.json', 'r') as reads:
        data = load(reads)
    data['anime']['log'] = log
    with open(f'{current_path}/setting.json', 'w') as js:
        js.write(f"{dumps(data, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': '))}")


def checkUpload(f, url, dir, link, name, series, numbers):
    global check_flag
    if path.exists(path.join(f'{path.dirname(__file__)}/downloads', f'_{f}')) and check_flag == False:
        curent_time = strftime("%H:%M", localtime())
        system(f'notify-send "Вышла новая серия!{name}\n{curent_time}"')
        names_dir = '_'.join(dir.split())
        old = path.join(f'{path.dirname(__file__)}/downloads', f'_{f}')
        new = path.join(f'{path.dirname(__file__)}/downloads', f'{names_dir}-{series}.mp4')

        rename(old, new)

        if not path.isdir(f'/home/north/data/projects/Python/IsDev/Anime-parser/downloads/'):
            system(f'mkdir "/home/north/data/projects/Python/IsDev/Anime-parser/downloads/"')

        if path.isdir(f'/home/north/data/projects/Python/IsDev/Anime-parser/downloads/{names_dir}'):
            pass
        else:
            system(f'mkdir "/home/north/data/projects/Python/IsDev/Anime-parser/downloads/{names_dir}"')

        system(f'mv "{path_down}/{names_dir}-{series}.mp4" "{path_down}/{names_dir}/"')

        with open(f'{current_path}/setting.json', 'r') as reads:
            data = load(reads)
        data['anime']['series'][url.index(link)] = series
        with open(f'{current_path}/setting.json', 'w') as js:
            js.write(f"{dumps(data, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': '))}")
    elif check_flag == True:
        system(f'rm {current_path}/downloads/_{f}.crdownload')
    else:
        print('Wait!! Reconnect!!')
        sleep(5)
        checkUpload(f, url, dir, link, name, series, numbers)


def extraStopDownloading():
    global check_flag
    check_flag = True


def extraClose():
    system('killall chromedriver')
