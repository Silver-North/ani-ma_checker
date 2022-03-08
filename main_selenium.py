from selenium import webdriver
from os import path, system, rename
from time import sleep, localtime, strftime




path_down = f'{path.dirname(path.realpath(__file__))}/downloads'
prefs = {'download.default_directory': path_down, "download.prompt_for_download": False}

option = webdriver.ChromeOptions()
option.add_experimental_option("prefs", prefs)
option.add_argument('--headless')

def allParsing():
    driver = webdriver.Chrome(path.join(path.dirname(__file__), 'chromedriver'), options=option)
    url, numbers = listLinkOrNumbers()

    if len(url) > 0:

        with open('log.txt', 'w') as w:
            for i in enumerate(url):
                try:
                    series = numbers[i[0]] + 1
                    print(i)
                    driver.get(i[1])
                    print(0)
                    sleep(3)
                    print(1)
                    search_count_series = driver.find_elements_by_class_name('epizode')
                    name = driver.find_element_by_class_name('shortstoryHead').text
                    next = driver.find_element_by_class_name('next')
                    name_dir = name.split(' /')

                    print(name_dir)

                    if len(search_count_series) == series:
                        if len(search_count_series) > 6:
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
                        print(len(down))
                        let = down[-2].get_attribute("href").split('?')
                        let = let[0].split('/')
                        sleep(3)
                        print(10)
                        down[2].click()
                        print(100)
                        checkUpload(let[-1], url, name_dir[0], i[1], name, series, numbers)
                        w.write(f'{i[0]} - {name_dir[0]} - New series {series}\n')
                    else:
                        print('No new series!')
                        w.write(f'{i[0]} - {name_dir[0]} - No new < {series} > series\n')
                    driver.switch_to.default_content()
                    sleep(5)
                except:
                    print("!!! << Error >> !!!")
                    w.write(f'{i[0]} - !!! << Error >> !!!\n')

    driver.quit()


def listLinkOrNumbers():
    urls = []
    numbers = []
    listing = []

    with open('list.txt', 'r') as f:
        data = f.readlines()

    for i in data:
        listing.append(i.split(','))

    for i in listing:
        urls.append(i[0])
        numbers.append(int(i[1][:-1:]))

    return urls, numbers


def oneParsing(url, digit):
    driver = webdriver.Chrome(path.join(path.dirname(__file__), 'chromedriver'), options=option)
    urls, numbers = listLinkOrNumbers()

    with open('loger.txt', 'w') as w:
        try:
            series = digit + 1
            print(url)
            driver.get(url)
            print(0)
            sleep(3)
            print(1)
            search_count_series = driver.find_elements_by_class_name('epizode')
            name = driver.find_element_by_class_name('shortstoryHead').text
            next = driver.find_element_by_class_name('next')
            name_dir = name.split(' /')

            print(name_dir)

            if len(search_count_series) == series:
                if len(search_count_series) > 6:
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
                print(len(down))
                let = down[-2].get_attribute("href").split('?')
                let = let[0].split('/')
                sleep(3)
                print(10)
                down[2].click()
                print(100)
                checkUpload(let[-1], urls, name_dir[0], url, name, series, numbers)
                w.write(f'{name_dir[0]} - New series {series}')
            else:
                print('No new series!')
                w.write(f'{name_dir[0]} - No new < {series} > series')
            driver.switch_to.default_content()
            sleep(5)
        except:
            w.write("!!! << Error >> !!!")
            print("!!! << Error >> !!!")
    driver.quit()


def checkUpload(f, url, dir, link, name, series, numbers):
    if path.exists(path.join(f'{path.dirname(__file__)}/downloads', f'_{f}')):
        curent_time = strftime("%H:%M", localtime())
        system(f'notify-send "Вышла новая серия!{name}\n{curent_time}"')
        names_dir = '_'.join(dir.split())
        old = path.join(f'{path.dirname(__file__)}/downloads', f'_{f}')
        new = path.join(f'{path.dirname(__file__)}/downloads', f'{names_dir}-{series}.mp4')

        rename(old, new)

        if path.isdir(f'/home/north/data/projects/Python/IsDev/Anime-parser/downloads/{names_dir}'):
            pass
        else:
            system(f'mkdir "/home/north/data/projects/Python/IsDev/Anime-parser/downloads/{names_dir}"')

        system(f'mv "{path_down}/{names_dir}-{series}.mp4" "{path_down}/{names_dir}/"')
        with open('list.txt', 'w') as ff:
            for el in enumerate(url):
                if url[el[0]] == link:
                    ff.write(f'{link},{series}\n')
                else:
                    ff.write(f'{el[1]},{numbers[el[0]]}\n')
    else:
        print('Wait!! Reconnect!!')
        sleep(40)
        checkUpload(f, url, dir, link, name, series, numbers)


def extraClose():
    system('killall chromedriver')


# allParsing()
# oneParsing('https://animevost.am/tip/tv/2754-genjitsu-shugi-yuusha-no-oukoku-saikenki-2nd-season.html', 9)
