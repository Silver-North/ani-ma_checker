from os import path, system
from sys import exit
from functools import partial
from time import sleep, localtime, strftime
from webbrowser import open as open_url
from json import dumps, load
from datetime import date
from shutil import copyfileobj
from threading import Thread
from urllib import request as url_request

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox as QMessage, QSystemTrayIcon, QComboBox
from PyQt5.QtGui import QIcon, QPixmap, QMovie
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from QLed import QLed
from requests import get
from selenium import webdriver
from selenium.webdriver.common.by import By
from validators import url as check_url
from alive_progress import alive_bar
from xlwt import Workbook

from design import Ui_MainWindow
from notifications import (checkURL, getDescription, loadImage, 
                           checkFixedOutput, parseRanobe, checkVoice)


dead = life = enable = checker_tag = True
down = while_var = tab_start = downloading = False
cache = ()
notify = 'empty'


def enableCheck(func):
    """ Tracking for execute and intersection of functions """
    def wrapper(*flag):
        global enable, while_var, dead, life
        if enable:
            enable = False
            while_var = life = dead = True
            func(*flag)
            while_var = False
            enable = dead = True
    return wrapper


class ThreadProgress(QThread):
    """ Checking or updating data of anime tracker """
    _signal = pyqtSignal(int)

    def __init__(self, data, flag=True):
        super(ThreadProgress, self).__init__()
        self.flag = flag
        self.data = data
        self.current_path = path.dirname(path.realpath(__file__))

    def __del__(self):
        self.wait()

    def run(self, check=0):
        global dead, checker_tag, tab_start, notify
        tab_start, checker_tag, fold = (0, False, 'description/')
        title = 'Checking ->' if self.flag else 'Updating ->'
        with alive_bar(len(self.data['anime']['urls']), title=title) as bar:
            for i in enumerate(self.data['anime']['urls']):
                try:
                    if dead == False: break 
                    series = self.data['anime']['series'][i[0]] + 1
                    ova = self.data['anime']['ova'][i[0]] + 1
                    name, check_output = checkURL(self.data, i[1], series, ova)
                    check += 1 if check_output else 0
                    if name == '': raise Exception('ERROR FOR URL_CHECK..')
                    if self.flag == False:
                        if 'icons/' in self.data['anime']['images'][i[0]]:
                            img, desc = getDescription(i[1])
                            self.data['anime']['images'][i[0]] = f'{fold}{img}'
                            self.data['anime']['description'][i[0]] = desc
                        self.data['anime']['name'][i[0]] = name
                    ind = i[0] + 1
                    percent = int(ind / len(self.data['anime']['urls']) * 100)
                    self._signal.emit(percent)
                except Exception as e:
                    system(f'notify-send "Error checking anime\n{e}"')
                bar()
        notify = self.data['notify']['notify'] = checkVoice(self.data, check)
        if isinstance(self.data, dict):
            with open(f'{self.current_path}/setting.json', 'w') as js:
                js.write(dumps(self.data, sort_keys=False, indent=4,
                               ensure_ascii=False, separators=(',', ': ')))
        sleep(1)
        percent, checker_tag = (0, True)
        self._signal.emit(percent)
        del(check)


class GlobalParser(QtWidgets.QMainWindow):
    """ Parsing data under the terms """
    def __init__(self):
        super(GlobalParser, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.current_path = path.dirname(path.realpath(__file__))
        self.setGeometry(*self.uploadGlobalSettings()['geometry'])

        self.flag = True
        self.click = self.percent = self.percent_all_anime = self.color = 0
        self.percent_all_manga = self.percent_desc_manga = 0
        self.ranobe_percent = 0
        self.ui.tabWidget.setCurrentIndex(0)
        self.path_down = f'{self.current_path}/downloads'
        self.option = webdriver.ChromeOptions()
        self.option.add_argument('--headless')
        self.icon = f'{self.current_path}/icons'
        self.movie = QMovie(f"{self.icon}/free.gif")
        self.sheme = (('dark', 'background: #313131', 'background: #888888'),
                      ('lamp', 'background: #FFFFFF', 'background: #FFFFFF'))
        self.up = (self.ui.toolButton_20, self.ui.toolButton_17,
                   self.ui.toolButton_26, self.ui.toolButton_31)
        self.comboboxes = (self.ui.comboBox, self.ui.comboBox_2,
                           self.ui.comboBox_6, self.ui.comboBox_7)
        self.dict_funcs = {0: self.wrapperData, 1: self.wrapperEnable,
                           2: self.wrapperCheckbox, 4: self.wrapperUpdate,
                           8: lambda e: self.ui.progressBar.setValue(e),
                           9: lambda e: self.ui.progressBar_3.setValue(e),
                           10: lambda e: self.ui.progressBar_7.setValue(e)}
        bar = (self.ui.progressBar.setStyleSheet,
               self.ui.progressBar_2.setStyleSheet,
               self.ui.progressBar_3.setStyleSheet,
               self.ui.progressBar_7.setStyleSheet)
        labels_movie = (self.ui.label_2, self.ui.label_3, self.ui.label_8,
                        self.ui.label_9, self.ui.label_10, self.ui.label_11)
        gen = (self.ui.toolButton_2, self.ui.toolButton_19,
            self.ui.toolButton_29,self.ui.toolButton_8, self.ui.toolButton_13,
            self.ui.toolButton_27, self.ui.toolButton_21,
            self.ui.toolButton_30, self.ui.toolButton, self.ui.toolButton_15,
            self.ui.toolButton_32, self.ui.toolButton_12)
        new_box = (*self.comboboxes[:3:],self.ui.comboBox_3,self.ui.comboBox_4)
        tuple_none = (self.ui.toolButton_24,self.ui.toolButton_10,
                      self.ui.toolButton_11,self.ui.toolButton_25)
        buts =(self.ui.pushButton,self.ui.toolButton_3,self.ui.toolButton_5,
            self.ui.toolButton_6,self.ui.toolButton_10,self.ui.toolButton_11,
            self.ui.toolButton_14,self.ui.toolButton_18,self.ui.toolButton_24)
        funcs = (self.startExport,self.closed,self.oneDown,self.stoped,
                 self.notifyCheck,self.modeColorSheme,self.openPlayer,
                 self.openURL,self.aboutInfo)
        cl = ('#00e916', '#8BC6EC;', '#FFE53B;', '#FF3CAC;')
        func_time = (self.everySecond, self.tracked)

        self.ui.dockWidget.hide()
        self.ui.dockWidget.setGeometry(555,75, 164,80)

        self.timer = [QTimer() for _ in range(2)]
        [self.timer[i].timeout.connect(v) for i,v in enumerate(func_time)]
        [self.timer[i].start(v) for i,v in enumerate((1000, 420_000))]
        self.tracked()
        
        self.tray = QSystemTrayIcon(self)
        self.tray.activated.connect(self.trayExecute)
        self.tray.show()

        self.led = QLed(self, onColour=QLed.Green, shape=QLed.Circle)
        self.led.setGeometry(370, 135, 12, 12)

        self.defaultIcon()
        self.checkModeSheme()

        [i.setMovie(self.movie) for i in labels_movie]
        [i.setStyleSheet('border: none;') for i in tuple_none]
        [bar[i](f'selection-background-color: {v}') for i,v in enumerate(cl)]
        [self.showed(*i) for i in enumerate(self.comboboxes)]
        [(self.changed(i), v.activated.connect(partial(self.changed, i)))
            for i,v in enumerate(new_box)]

        [v.clicked.connect(funcs[i]) for i,v in enumerate(buts)]
        for i in enumerate(gen):
            match i[0]:
                case 0 | 1 | 2: i[1].clicked.connect(self.deleted)
                case 3 | 4 | 5: i[1].clicked.connect(self.loged)
                case 6 | 7: i[1].clicked.connect(self.edited)
                case 8 | 9 | 10: i[1].clicked.connect(self.saved)
                case _: i[1].clicked.connect(self.checkItems)
        [j.clicked.connect(partial(self.checkingItems, (True if i % 2 == 1 
            else False, i))) for i,j in enumerate(self.up)]

    def keyPressEvent(self, QKeyEvent):
        self.hidded() if QKeyEvent.key() == 16777216 else None

    def uploadGlobalSettings(self):
        try:
            with open(f'{self.current_path}/setting.json', 'r') as reads:
                data = load(reads)
        except Exception:
            data = self.uploadGlobalSettings()
        return data

    def setGlobalSettings(self, to_json, tab, mode, var,
                                flag=False, state=False):
        if not state:
            if flag:
                to_json[mode].append(var) if tab == "" else \
                    to_json[tab][mode].append(var)
            else:
                if not tab: to_json[mode] = var
                else: to_json[tab][mode] = var
        if isinstance(to_json, dict):
            with open(f'{self.current_path}/setting.json', 'w') as js:
                js.write(dumps(to_json, sort_keys=False, indent=4,
                        ensure_ascii=False, separators=(',', ': ')))
        else: system(f'notify-send "No writing file <setting.json>"')

    def startExport(self):
        """ Export data in selected format """
        mode = self.ui.comboBox_5.currentText()
        format = self.ui.comboBox_8.currentText()
        data = self.uploadGlobalSettings()['history']
        saved = f'{self.current_path}/history.{format}'
        if len(data[mode]) > 0:
            if format in ('md', 'txt'):
                with open(saved, 'w') as f:
                    [f.write(f'{i}\n') for i in data[mode]]
            elif format == 'json':
                with open(saved, 'w') as f:
                    f.write(dumps(data[mode], sort_keys=False, indent=4,
                                   ensure_ascii=False, separators=(',', ': ')))
            elif format == 'xlsx':
                writing_book = Workbook()
                writing = writing_book.add_sheet(f'export history {mode}')
                [writing.write(i[0],0,i[1]) for i in enumerate(data[mode])]
                writing_book.save(saved)
        self.ui.dockWidget.close()

    def stoped(self):
        """ Forced ending work of functions """
        global while_var
        if while_var:
            rezult = self.message('Do you really want to finished process?',
                                  (541, 107, 200, 200), True, True)
            if rezult == QMessage.Ok: self.extraClose()
        else:
            self.message('No active process for ending!',(541, 107, 200, 200))

    def hidded(self):
        self.hide()
        self.click += 1

    def extraClose(self):
        """ Kill process of active working functions """
        global dead, life
        dead = life = False
        system('killall -s 9 chromedriver')
        self.defaultIcon()

    def closed(self):
        """Shutdown of application """
        rezult = self.message('Do you really want to leave?',
                              (541, 107, 200, 200), True, True)
        (self.extraClose(),self.close()) if rezult == QMessage.Ok else None

    def aboutInfo(self):
        """ Getting small info about working of application """
        self.message(self.uploadGlobalSettings()['about'],(600, 75, 300, 100))

    def getValueForSecond(self):
        global checker_tag, enable, tab_start, down, while_var, notify 
        index = self.ui.tabWidget.currentIndex()
        updates = False if self.ui.checkBox_3.isChecked() else True
        checkbox = True if self.ui.checkBox_2.isChecked() else False   
        self.flag = False if while_var else True
        return (notify, enable, checkbox, checker_tag, updates,
                index, tab_start, self.percent_all_anime,
                self.percent, self.percent_all_manga, self.ranobe_percent,
                while_var, down)

    def everySecond(self): self.checkCache(self.getValueForSecond())

    def checkCache(self, gets, indexes=(5, 6, 11, 12)):
        """ Checking caching of functions """
        global cache
        check = [i for i,v in enumerate(gets) if not cache or cache[i] != v]
        if check:
            for i in check:
                self.iconTab(*gets[5:7:], *gets[-2::]) if i in indexes else \
                self.wrapperBar(gets[3], gets[7]) if i in (3, 7) else \
                self.dict_funcs[i](gets[i])
            cache = gets

    def iconTab(self, index, tab, while_var=False, down=False):
        """ Installing dinamic of icons """
        pre = {0: 'AnimeVost tracker', 1: 'Manga tracker',
               2: 'Ranobe tracker', 3: 'View descriptions'}
        if self.flag:
            ico = 'animevost' if index == 0 else 'mask' if index == 1 else \
                  'ranobe' if index == 2 else 'a-desc'
        else:
            ico = 'dow' if while_var and down and tab == 0 else \
                    'animevost-new' if tab == 0 else 'mask-0' \
                                       if tab == 1 else 'ranobe-0'
        tool = 'Download file..' if down else pre[index]
        self.tray.setToolTip(tool)
        self.tray.setIcon(QIcon(f'{self.icon}/{ico}.png'))

    def wrapperData(self, data):
        """ Checking and setting icon of notifications """
        ico = 'notification' if data == 'checked' else 'notify' \
                             if data == 'unchecked' else 'bell'
        self.ui.toolButton_10.setIcon(QIcon(f'{self.icon}/{ico}.png'))

    def wrapperEnable(self, enable):
        """ Starting processes for execute main of functions """
        self.movie.stop() if enable else self.movie.start()
        self.led.value = False if enable else True
        self.led.setToolTip('Not Working..' if enable else 'Working..')
        self.visibled() if enable else None

    def wrapperCheckbox(self, checkbox):
        """ Switch for one or all of downloads anime """
        ico = 'all-click' if checkbox else 'click'
        tool = 'Download All Items' if checkbox else 'Download Current Item'
        self.ui.toolButton_5.setIcon(QIcon(f'{self.icon}/{ico}.png'))
        self.ui.toolButton_5.setToolTip(tool)
    
    def wrapperBar(self, check, anime_percent):
        """ Setting value for progresBar_2"""
        self.percent_all_anime = anime_percent if check else 0
        self.ui.progressBar_2.setValue(anime_percent) if check else False

    def wrapperUpdate(self, checkbox):
        """ Switch for check or update of anime tracker """
        ico = 'checking' if checkbox else 'circle'
        tool = 'Tracking Elements' if checkbox else 'Update Elements'
        self.ui.toolButton_12.setIcon(QIcon(f'{self.icon}/{ico}.png'))
        self.ui.toolButton_12.setToolTip(tool)

    def editLineEdit(self, edit, bg="background: "):
        """ Setting default color sheme for all QLineEdit"""
        sleep(2.5)
        edit.setText('')
        data = self.uploadGlobalSettings()['mode']
        edit.setStyleSheet(f'{bg}' '#888888' if "dark" in data else "#dcdcdc") 

    def notifyCheck(self):
        """ Show all notifications """
        global notify
        data = self.uploadGlobalSettings()
        notify = data['notify']['notify'] = 'empty' \
                if self.emptyNotify(data) else 'checked'
        name = ('No notify..',(600, 95, 300, 100)) if self.emptyNotify(data) \
            else ("\n".join([''.join(data['notify'][i]) 
                    for i in data['notify'] if i not in 'notify' or 
                        not data['notify'][i]]),(420, 95, 300, 100))
        self.setGlobalSettings(data, '', '', '', False, True)
        self.message(*name)

    def modeColorSheme(self):
        """ Switch color sheme """
        mode = 'darkmode' if self.color % 2 == 0 else 'lightmode'
        self.changeSheme(*self.sheme[0 if self.color % 2 == 0 else 1])
        self.setGlobalSettings(self.uploadGlobalSettings(), '', 'mode', mode)
        self.color += 1

    def checkModeSheme(self):
        """ Checking color sheme from global settings """
        reads = self.uploadGlobalSettings()['mode']
        self.color = 0 if reads == 'lightmode' else 1
        self.changeSheme(*self.sheme[0 if self.color % 2 == 1 else 1])

    def changeSheme(self, ico, window, bg, tip=('Lightmode', 'Darktmode')):
        """ Setting color sheme """
        self.setStyleSheet(window)
        lbg = (self.ui.lineEdit, self.ui.lineEdit_2, self.ui.lineEdit_3,
            self.ui.textEdit, *self.comboboxes, self.ui.comboBox_3,
            self.ui.comboBox_4, self.ui.comboBox_5, self.ui.comboBox_8,
            self.ui.spinBox, self.ui.doubleSpinBox, self.ui.doubleSpinBox_2,
            self.ui.lcdNumber, self.ui.lcdNumber_2, self.ui.lcdNumber_3,
            self.ui.lcdNumber_4, self.ui.lcdNumber_5, self.ui.lcdNumber_6,
            self.ui.toolButton_11, self.ui.toolButton_24, self.ui.pushButton,
            self.ui.pushButton_2)
        licon = (f'{self.icon}/{ico}.png', f'{self.icon}/{ico}-about.png')
        lcheck = (self.ui.checkBox,self.ui.checkBox_2,
                  self.ui.checkBox_3,self.ui.checkBox_4)
        tool = {'lamp': (tip[0], '#0b76ef'), 'dark': (tip[1], '#8B33B5')}
        [v.setStyleSheet(bg) for i,v in enumerate(lbg) if i not in (21,22)]
        [v.setIcon(QIcon(licon[i])) for i,v in enumerate(lbg[21:23:])]
        [lbg[i].setToolTip(v) for i,v in {22:'About', 21:tool[ico][0]}.items()]
        [i.setStyleSheet(f'background-color:{tool[ico][1]};') for i in lcheck]

    def defaultIcon(self):
        """ Setting default values for all icons """
        list_tab = ('animevost.png', 'mask.png', 'ranobe.png', 'a-desc.png')
        for i,v in enumerate(list_tab):
            self.ui.tabWidget.setTabIcon(i, QIcon(f'{self.icon}/{v}'))
            if i < 3:
                self.ui.comboBox_4.setItemIcon(i, QIcon(f'{self.icon}/{v}'))
        list_tool = (self.ui.toolButton_2, self.ui.toolButton_19,
            self.ui.toolButton_29, self.ui.toolButton_26,
            self.ui.toolButton_20, self.ui.toolButton_8, self.ui.toolButton_27,
            self.ui.toolButton_13, self.ui.toolButton, self.ui.toolButton_15,
            self.ui.toolButton_32, self.ui.toolButton_17,
            self.ui.toolButton_31, self.ui.toolButton_21,
            self.ui.toolButton_30, self.ui.toolButton_7, self.ui.toolButton_4,
            self.ui.toolButton_18, self.ui.toolButton_3, self.ui.toolButton_6,
            self.ui.toolButton_14, self.ui.toolButton_16,
            self.ui.toolButton_25)
        lists = ('trash', 'circle', 'log-one', 'diskette', 'checking', 'edit',
                 'checkbox-1', 'checkbox-2', 'web', 'close', 'lose', 'player',
                 'checkbox-3', 'history')
        licon = [QIcon(f'{self.current_path}/icons/{i}.png') for i in lists]
        list_tool[18].setToolTip('Exit')
        for i,v in enumerate(list_tool):
            match i:
                case 0 | 1 | 2: value = 0
                case 3 | 4: value = 1
                case 5 | 6 | 7: value = 2
                case 8 | 9 | 10: value = 3
                case 11 | 12: value = 4
                case 13| 14: value = 5
                case _: value += 1
            v.setIcon(licon[value])

    def trayExecute(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show() if self.click % 2 == 0 else self.hide()
            self.click += 1

    def openPlayer(self):
        """ Open video player MPV """
        index = self.ui.lcdNumber.intValue() \
            if self.ui.spinBox.value() == 0 else self.ui.spinBox.value()
        name = "_".join(self.ui.comboBox.currentText().split())
        if index > 0 and index <= self.ui.lcdNumber.intValue():
            link = f"{self.path_down}/{name}/{name}-{index} серия.mp4"
            Thread(target=system, args=(f'mpv "{link}"',)).start()
        else:
            self.message('No file..', (514, 107, 200, 200))

    def openURL(self):
        """ Open URL in browser for view info """
        tab = self.ui.tabWidget.currentIndex()
        data = self.uploadGlobalSettings()
        child = 'track-link' if tab == 0 and \
                                self.ui.checkBox.isChecked() else 'urls'
        index = self.comboboxes[-1].currentIndex() if tab == 0 and \
                self.ui.checkBox.isChecked() else \
                self.comboboxes[tab].currentIndex()
        mode = 'anime' if tab == 0 else 'manga' if tab == 1 else 'ranobe'
        open_url(data[mode][child][index]) if data[mode][child] else \
            system(f'notify-send "List <{mode}> is empty"')

    @enableCheck
    def deleted(self, flag=None):
        """ Delete one item from lists: anime, manga or ranobe """
        global notify
        data = self.uploadGlobalSettings()
        tab = self.ui.tabWidget.currentIndex()
        catch = 'log' if tab in (0,2) else 'logs'
        throw = 'names' if tab in (1,2) else 'name'
        mode = 'anime' if tab == 0 else 'manga' if tab == 1 else 'ranobe'
        ico = 'animevost' if tab == 0 else 'mask' if tab == 1 else 'ranobe'
        index = self.comboboxes[tab].currentIndex()
        icon = f'icons/{ico}.png'
        rezult = self.message('Are you sure you want to delete this entry?',
                              (514, 107, 200, 200), True, True)
        if rezult == QMessage.Ok:
            save_to_history = self.message('Save to history?',
                                           (544, 107, 200, 200), True, True)
            dirs = "_".join(data[mode][throw][index].split())
            if save_to_history == QMessage.Ok:
                data['history'][mode].append(data[mode][throw][index])
                mv = 'mv "{0}/{1}" "{0}/history/"'.format(self.path_down, dirs)
            rm = f'rm -r "{self.path_down}/{dirs}"'
            system(mv if save_to_history == QMessage.Ok else rm) \
                    if tab == 0 else None
            remove = f'rm {self.current_path}/{data[mode]["images"][index]}'
            system(remove) if  data[mode]["images"][index] != icon else True
            data = self.checkNotify(data, mode, data[mode][throw][index])
            notify = data['notify']['notify'] = 'empty' \
                if self.emptyNotify(data) else data['notify']['notify']
            [data[mode][i].pop(index) for i in data[mode] if i not in catch]
            self.setGlobalSettings(data, '', '', '', False, True)
            if self.ui.comboBox_4.currentIndex() == tab:
                self.ui.comboBox_3.clear()
                self.ui.comboBox_4.setCurrentIndex(tab)
            self.showed(tab, self.comboboxes[tab])

    def loged(self):
        """ Show log file """
        tab = self.ui.tabWidget.currentIndex()
        data = self.uploadGlobalSettings()
        log = 'logs' if tab == 1 else 'log'
        mode = 'anime' if tab == 0 else 'manga' if tab == 1 else 'ranobe'
        txt = '\n'.join(data[mode][log]) if tab == 1 and data[mode][log] \
              else data[mode][log] if data[mode][log] else 'No file exist...'
        self.message(txt, (420, 95, 300, 100))

    def edited(self):
        """ Editing value for list manga or ranobe """
        global notify
        tab = self.ui.tabWidget.currentIndex()
        data = self.uploadGlobalSettings()
        child = ('manga','numbers') if tab == 1 else ('ranobe','chapters')
        index = self.ui.comboBox_2.currentIndex() if tab == 1 else \
                self.ui.comboBox_6.currentIndex()
        text = self.ui.comboBox_2.currentText() if tab == 1 else \
                self.ui.comboBox_6.currentText()
        value = self.ui.doubleSpinBox.value() if tab == 1 else \
                self.ui.doubleSpinBox_2.value()
        if value != 0.0:
            decimal = int(str(value).split('.')[1])
            value = int(value) if decimal == 0 else float(value)
            data[child[0]][child[1]][index] = value
            data = self.checkNotify(data, child[0], text, value)
            notify = data['notify']['notify'] = 'empty' \
                if self.emptyNotify(data) else data['notify']['notify']
            self.setGlobalSettings(data, '', '', '', False, True)
            self.ui.doubleSpinBox.setValue(0) if child[0] == 'manga' else \
            self.ui.doubleSpinBox_2.setValue(0)
            self.changed(tab)

    def checkNotify(self, data, ch, text, value=None, check=True):
        """ Childing check of notifications for it deleting """
        char = 'chapter' if check else 'series'
        tmp = f'{text} - new ' if value is None else \
              f'{text} - new {char} {value}'
        temp = f'{text} - new ova' if ch in 'anime' else 'NOT CHECK'
        data['notify'][ch] = [i for i in data['notify'][ch] if tmp not in i]
        data['notify'][ch] = [i for i in data['notify'][ch] if temp not in i]
        return data

    def emptyNotify(self, data):
        """ Checking cont of notifications """
        el = [len(data['notify'][i]) for i in data['notify'] if i != 'notify']
        return True if sum(el) == 0 else False

    @enableCheck
    def saved(self, flag=None):
        """ Saving URL in one from lists: anime, manga or ranobe """
        tab = self.ui.tabWidget.currentIndex()
        data = self.uploadGlobalSettings()
        name = 'names' if tab in (1,2) else 'name'
        mode = 'anime' if tab == 0 else 'manga' if tab == 1 else 'ranobe'
        mask = 'animevost' if tab == 0 else 'mask' if tab == 1 else 'ranobe'
        icon = QIcon(f'{self.icon}/{mask}.png')
        catch = ('log', 'track-name', 'track-link') if tab == 0 else \
                 '' if tab == 1 else 'log'
        series = self.ui.spinBox.value() if tab == 0 else \
                 self.ui.doubleSpinBox.value() if tab == 1 else \
                 self.ui.doubleSpinBox_2.value()
        edit = (self.ui.lineEdit, self.ui.lineEdit_2, self.ui.lineEdit_3)
        track = self.ui.comboBox_7.currentIndex()
        url = data['anime']['track-link'][track] if tab == 0 \
                  and self.ui.checkBox.isChecked() else edit[tab].text()
        title = self.ui.comboBox_7.currentText().split(' / ')[0] if tab == 0 \
                  and self.ui.checkBox.isChecked() else ''
        ico = f'icons/{mask}.png'
        dicts = {0: url, 1: series, 2: 0, 3: title, 5: '', 6: ico} \
            if tab == 0 else \
                {0: url, 1: series, 2: 0, 3: '', 4: '', 6: '', 5: ico} \
            if tab == 1 else \
                {0: url, 2: series, 3: 0, 4: 0, 1: '', 5: '', 6: ico}
        if check_url(url):
            edit[tab].setStyleSheet('background: rgb(98, 255, 59)')
            [data[mode][v].append(dicts[i]) for i,v in enumerate(data[mode])
                if v not in catch]
            self.comboboxes[tab].addItem(title)
            self.comboboxes[tab].setItemIcon(len(data[mode][name])-1, icon)
            self.setGlobalSettings(data, '', '', '', False, True)
        else:
            system(f'notify-send "Error add {mode}"')
            edit[tab].setStyleSheet('background: rgb(236, 0, 0)')
            edit[tab].setText('  ERROR check URL..')
        Thread(target=self.editLineEdit, args=(edit[tab],)).start()

    def showed(self, index, combo):
        """ Show items in comboboxes """
        name = 'name' if index == 0 else 'names' if index in (1,2) else \
               'track-name'
        child = 'anime' if index in (0,3) else 'manga' if index == 1 else \
                'ranobe'
        ico = 'animevost' if index in (0,3) else 'mask' if index == 1 else \
              'ranobe'
        combo.clear()
        data = self.uploadGlobalSettings()[child][name]
        for i in enumerate(data):
            combo.addItem(i[1])
            combo.setItemIcon(i[0], QIcon(f'{self.icon}/{ico}.png'))

    def changed(self, tab, stop = False):
        """ Changing values in comboboxes """
        data = self.uploadGlobalSettings()
        mode = 'anime' if tab == 0 else 'manga' if tab == 1 else \
               'ranobe' if tab == 2 else self.ui.comboBox_4.currentText()
        name = 'name' if  mode in 'anime' else 'names'
        child = 'series' if tab == 0 else 'numbers' if tab == 1 else \
                                          'chapters' if tab == 2 else name
        stop = False if len(data[mode][child]) == 0 else True
        twin = 'change_numbers' if mode in 'manga' else 'access-chapters' \
                if mode in 'ranobe' else 'series'
        index = self.comboboxes[tab].currentIndex() if tab in (0,1,2) else \
                self.ui.comboBox_3.currentIndex() if tab == 3 else \
                self.ui.comboBox_4.currentIndex()
        lcd = (self.ui.lcdNumber, self.ui.lcdNumber_2, self.ui.lcdNumber_3,
               self.ui.lcdNumber_4, self.ui.lcdNumber_5, self.ui.lcdNumber_6)
        lcd_check = lcd[:1:] if tab == 0 else lcd[1:3:] if tab == 1 else \
                    lcd[3::] if tab == 2 else None if tab == 3 else False
        if stop == False and tab == 4:
            self.ui.comboBox_3.clear()
            self.ui.label_5.setPixmap(QPixmap())
        elif stop:
            digit = data['anime']['series'][index] if tab == 0 else 0
            fraction = data['anime']['ova'][index] if tab == 0 else 0
            num = float(f"{digit}.{fraction}")
            current = data[mode][child][index] if tab in (1,2) else num
            but = self.ui.toolButton_21 if tab == 1 else self.ui.toolButton_30
            if lcd_check is None:
                self.ui.label_5.setPixmap(QPixmap(
                    f'{self.current_path}/{data[mode]["images"][index]}'))
                self.ui.textEdit.setHtml(data[mode]['description'][index])
            elif lcd_check == False:
                self.ui.comboBox_3.clear()
                ico = 'animevost' if index == 0 else 'mask' \
                                  if index == 1 else 'ranobe'
                for i,v in enumerate(data[mode][name]):
                    self.ui.comboBox_3.addItem(v)
                    self.ui.comboBox_3.setItemIcon(i, QIcon(
                                                    f'{self.icon}/{ico}.png'))
                self.changed(3)
            else:
                for i,v in enumerate(lcd_check):
                    v.display(current if i == 0 else data[mode][twin][index] \
                          if i == 1 else data[mode]['future-chapters'][index])
                one, two = (data[mode][child][index], data[mode][twin][index])
                back = ('rgb(50, 233, 37)', False) if one == two else \
                       ('rgb(192, 16, 16)', True)
                [i.setStyleSheet(f'background: {back[0]}') for i in lcd_check
                    if i != lcd_check[0]]
                tup = (1,2) if tab == 1 else (3,4) if tab == 2 else False
                False if tup == False else but.setEnabled(True) if \
                    lcd[tup[0]].value() < lcd[tup[1]].value() else \
                    but.setEnabled(False)

    def visibled(self):
        """ Setting visible buttons """
        visible = (self.ui.toolButton_5, self.ui.toolButton_12, *self.up)
        [i.show() for i in visible]

    def checkingItems(self, tup):
        """ Check or update lists manga or ranobe """
        data = self.uploadGlobalSettings()
        self.up[tup[1]].hide()
        func = self.upUrls if tup[1] in (0,1) else self.setRanobe
        args = (data, not tup[0]) if tup[1] in (0,1) else (tup[0], data)
        Thread(target=func, args=args).start()

    def message(self, txt, geo, ico=False, but=False):
        """ Global function for alert """
        al = QMessage()
        al.setIcon(QMessage.Information) if ico else None
        al.setText(txt)
        al.setGeometry(*geo)
        al.setStandardButtons(QMessage.Ok | QMessage.Cancel) if but else None
        return al.exec()

    @enableCheck
    def oneParsing(self, data, url, digit):
        """ Download series of anime for URL """
        global dead, tab_start
        tab_start = 0
        driver = webdriver.Chrome(path.join(path.dirname(__file__),
                                    'chromedriver'), options=self.option)
        urls = data['anime']['urls']
        try:
            self.percent_all_anime = 5
            driver.get(url)
            self.percent_all_anime = 15
            sleep(3)
            count_series = driver.find_elements(By.CLASS_NAME, 'epizode')
            name = driver.find_element(By.CLASS_NAME, 'shortstoryHead').text
            next = driver.find_element(By.CLASS_NAME, 'next')
            name_dir = name.split(' /')
            self.percent_all_anime = 35
            series = digit + 1 + data['anime']['ova'][urls.index(url)]

            def continueDownload(count=0, repeat=False):
                """ Getting all arguments for starting download """
                nonlocal count_series, series, name, \
                          next, name_dir, data, log
                count = series
                while count > 0:
                    if series <= 6: break
                    next.click()
                    count -= 6
                self.percent_all_anime = 40
                step = -1 if count == 0 else series - 1
                if data['anime']['ova'][urls.index(url)] > 0:
                    step = -(data['anime']['ova'][urls.index(url)]+1)
                while True:
                    click_i = count_series[step].text
                    if click_i != '': break
                count_series[step].click()
                sleep(15)
                iframe = driver.find_elements(By.TAG_NAME, 'iframe')
                for item in range(len(iframe)):
                    driver.switch_to.frame(iframe[item])
                    down = driver.find_elements(By.CLASS_NAME, 'butt')
                    if len(down) == 4: break
                    driver.switch_to.default_content()
                down = down[3 if self.ui.checkBox_4.isChecked() else 2]
                let = down.get_attribute("href").split('?')[0].split('/')
                self.percent_all_anime = 65
                self.Download(down.get_attribute('href'), let[-1], urls,
                              name_dir[0], url, name, series, data, click_i)
                self.percent_all_anime = 97
                log = f'{name_dir[0]} - New series {series}'
                driver.switch_to.default_content()
                if repeat:
                    series += 1
                    fl = True if len(count_series) - series > 0 else False
                    continueDownload(len(count_series) - series, fl)

            length = len(count_series)
            continueDownload(length - series, True) if length > series else \
            continueDownload()
        except Exception as e:
            system(f'notify-send "Error one-down\n<< {e} >>"')
            log = f"!!! << Error: {e} >> !!!"

        driver.quit()
        self.setGlobalSettings(data, 'anime', 'log', log)
        self.percent_all_anime = 100
        self.ui.progressBar_2.setFormat('Completed')
        sleep(1.2)
        self.percent_all_anime = 0
        self.ui.progressBar_2.setFormat('%p%')

    def checkUpload(self, f, url, dirs, link, name, series, data, search):
        """ Final step after download of series:

            creating folders, renaming file, moving file in folder

        """
        curent_time = strftime("%H:%M", localtime())
        names_dir = '_'.join(dirs.split())
        child = 'series' if 'серия' in search else 'ova'
        data['anime'][child][url.index(link)] += 1
        ova = data['anime']['ova'][url.index(link)] if 'О' in search else None
        series = f"ova-{ova}" if 'ОВА' in search else f'{series} серия'
        system(f'notify-send "Вышла {series}! {name}\n{curent_time}"')
        False if path.isdir(f'{self.path_down}') else \
            system(f'mkdir "{self.path_down}"') 
        if not path.isdir(f'{self.path_down}/{names_dir}'):
            system(f'mkdir "{self.path_down}/{names_dir}"')
        system(f'mv "{self.path_down}/_{f}" \
                    "{self.path_down}/{names_dir}/{names_dir}-{series}.mp4"')
        self.setGlobalSettings(data, '', '', '', False, True)

    def handleProgress(self, blocknum, blocksize, totalsize):
        """ Getting value for progress bar of download """
        global dead, down
        readed_data = blocknum * blocksize
        if totalsize > 0:
            down = True
            self.percent = int(readed_data * 100 / totalsize)
            if dead == False:
                raise Exception("Sorry, no numbers below zero")
            QtWidgets.QApplication.processEvents()

    def Download(self, dow, f, urls, dirs, link, name, serie, data, search):
        """ Starting download """
        global dead, down, downloading, notify
        save_loc = f'{self.current_path}/downloads/_{f}'
        txt = f'Download:\n{dirs} -> {serie}'
        try:
            self.ui.progressBar.setToolTip(txt)
            self.ui.progressBar.setFormat('Complete %p%')
            url_request.urlretrieve(dow, save_loc, self.handleProgress)
            downloading = True
            self.ui.progressBar.setFormat('Completed')
            data = self.checkNotify(data, 'anime', dirs, serie, False)
            notify = data['notify']['notify'] = 'empty' \
                if self.emptyNotify(data) else data['notify']['notify']
            self.checkUpload(f, urls, dirs, link, name, serie, data, search)
        except Exception as e:
            downloading = False
            rm = f'rm {self.current_path}/downloads/_{f}'
            system(f'notify-send "Error download: {dirs}\n{e}" && {rm}')
            self.ui.progressBar.setToolTip(f'Error {txt}')
        down = False
    
    def setProgressBar(self, percent): self.ui.progressBar_2.setValue(percent)

    def tracked(self): Thread(target=self.checkingOfTrackerAnime).start()

    @enableCheck
    def checkingOfTrackerAnime(self):
        """ Checking tracker of my data and getting all data """
        global tab_start, notify
        tab_start = 0
        data = self.uploadGlobalSettings()
        try:
            names, links, notify = checkFixedOutput(data, 0)
            self.setGlobalSettings(data, 'anime', 'track-name', names)
            self.setGlobalSettings(data, 'anime', 'track-link', links)
        except Exception as e:
            system(f'notify-send "Error for update Checker Anime:\n{e}"')
        self.showed(3, self.ui.comboBox_7)

    def checkItems(self, fl=False):
        """ Starting check or update of anime tracker """
        data = self.uploadGlobalSettings()
        self.ui.toolButton_12.hide()
        flag = True if fl else False if self.ui.checkBox_3.isChecked() else \
               True
        Thread(target=self.selectingMode, args=(data, not flag)).start()

    @enableCheck
    def selectingMode(self, data, check=True):
        """ Selecting mode for function checkItems. Start check or update. """
        self.thread_class = ThreadProgress(data, not check)
        self.thread_class._signal.connect(self.setProgressBar)
        self.thread_class.start()
        self.thread_class.wait()

    def oneDown(self):
        """ Start one or all downloads of anime """
        data = self.uploadGlobalSettings()
        self.ui.toolButton_5.hide()
        el = [i.split(' > ')[1].split(' - new')[0] 
                    for i in data['notify']['anime']]
        seti = list(set([data['anime']['name'].index(i) for i in el]))
        value = self.ui.lcdNumber.intValue()
        index = self.ui.comboBox.currentIndex()
        args = (data, seti) if self.ui.checkBox_2.isChecked() else \
               (data, data['anime']['urls'][index], value)
        func = self.downloadAll if len(args) < 3 else self.oneParsing
        thread = Thread(target=func, args=args)
        thread.start() if index in seti and len(args) > 2 or \
                          len(seti) > 0 and len(args) < 3 else \
            (self.message('No data for update..', (560, 75, 100, 100),
                          True, False), self.visibled())

    def downloadAll(self, data, seti):
        """ Checking of download all anime """
        global life, downloading
        while len(seti) > 0:
            url = data['anime']['urls'][seti[0]]
            series = data['anime']['series'][seti[0]]
            self.oneParsing(data, url, series)
            seti.remove(seti[0]) if downloading else False
            life  = (None, True)[1] if life else (seti.clear(), True)[1]

    @enableCheck
    def upUrls(self, data, update_check=False):
        """ Check or update data of manga """
        global dead, tab_start, notify
        tab_start, msg = (1, [])
        length = len(data['manga']['urls'])
        title = 'Update ' if update_check else 'Check '
        driver = webdriver.Chrome(path.join(path.dirname(__file__),
                                        'chromedriver'), options=self.option)
        for i in enumerate(data['manga']['urls']):
            try:
                with alive_bar(5, title=f'{title}{i[0]} -> ') as bar:
                    bar()
                    if dead == False: break
                    ii = i[0] + 1
                    self.percent_all_manga = int(ii / length * 100)
                    driver.get(i[1])
                    sleep(2)
                    bar()
                    if 'https://manga-chan.me' in i[1]:
                        manga = driver.find_elements(By.CLASS_NAME,
                            'manga2')[0].text.split(' Глава ')[1].split()[0]
                        if '.' in manga:
                            manga = float(manga)
                        else:
                            manga = int(manga)
                        name = driver.find_element(By.CLASS_NAME,
                            'title_top_a').text.split('(')[-1][:-1:]
                        img = driver.find_element(By.ID,
                                                'cover').get_attribute('src')
                        desc = driver.find_element(By.ID, 'description').text
                    else:
                        manga = driver.find_element(By.CLASS_NAME,
                                    'mt-3').text.split()
                        manga = manga[-2 if 'новое' in manga[-1] else -1]
                        if 'Экстра' in manga:
                            manga = float(
                                f"{data['manga']['numbers'][i[0]]}.1")
                        elif '.' not in manga:
                            manga = int(manga)
                        else:
                            manga = float(manga)
                        name = driver.find_element(By.CLASS_NAME, 'name').text
                        img = driver.find_elements(By.CLASS_NAME,
                            'fotorama__img')[0].get_attribute('src')
                        desc = driver.find_element(By.CLASS_NAME,
                            'manga-description').text
                    bar()
                    data['manga']['change_numbers'][i[0]] = manga
                    log = f'{name} = {manga}'
                    if data['manga']['numbers'][i[0]] < manga:
                        c_d = date.today()
                        c_t = strftime("%H:%M", localtime())
                        log = f'{name} → {manga}'
                        head = f'[M][{c_d.day}/{c_d.month}/{c_d.year} - {c_t}]'
                        body = f'{head} > {name} - new chapter {manga}\n'
                        msg.append(body)
                    data['manga']['logs'][i[0]] = log
                    bar()
                    if update_check:
                        if 'description/' not in data['manga']['images'][i[0]]:
                            image = ('description/', img.split('/')[-1])
                            r = get(img, stream=True)
                            if r.status_code == 200:
                                with open(
                                    f'{self.current_path}/{"".join(image)}',
                                    'wb') as f:
                                    r.raw.decode_content = True
                                    copyfileobj(r.raw, f)
                            loadImage(image[1])
                            data['manga']['images'][i[0]] = "".join(image)
                            data['manga']['description'][i[0]] = desc
                        data['manga']['names'][i[0]] = name
                    bar()
            except Exception as e:
                system(f'notify-send "Error check manga\n{e}"')
        driver.quit()
        data['notify']['manga'] += msg if len(msg) > 0 else []
        notify = data['notify']['notify'] = checkVoice(data, len(msg))
        self.setGlobalSettings(data, '', '', '', False, True)
        self.showed(1, self.ui.comboBox_2) if update_check else None
        sleep(0.8)
        self.percent_all_manga = 0

    @enableCheck
    def setRanobe(self, check, data):
        """ Check or update data of ranobe """
        global tab_start, dead, notify
        tab_start = 2
        msg = self.ranobe_percent = 0
        length = len(data['ranobe']['urls'])
        for i in enumerate(data['ranobe']['urls']):
            try:
                if dead == False: break
                name, img, description, chapter, all = parseRanobe(i[1])
                image = img.split('/')[-1]
                if data['ranobe']['chapters'][i[0]] < float(chapter):
                    c_d = date.today()
                    c_t = strftime("%H:%M", localtime())
                    msg += 1
                    head = f'[R][{c_d.day}/{c_d.month}/{c_d.year} - {c_t}]'
                    body = f'> {name} - new chapter {chapter}\n'
                    note = f'{head} {body}'
                    data['notify']['ranobe'].append(note)
                if check == False:
                    r = get(img, stream=True)
                    if r.status_code == 200:
                        with open(f'{self.current_path}/description/{image}',
                            'wb') as f:
                            r.raw.decode_content = True
                            copyfileobj(r.raw, f)
                        loadImage(image)
                    data['ranobe']['images'][i[0]] = f'description/{image}'
                    data['ranobe']['names'][i[0]] = name
                    data['ranobe']['description'][i[0]] = description
                data['ranobe']['access-chapters'][i[0]] = chapter
                data['ranobe']['future-chapters'][i[0]] = all
                self.ranobe_percent = int((i[0] + 1) / length * 100)
            except Exception as e:
                data['ranobe']['log'] = f'Error ==>\n{e}' 
                system(f'notify-send "Error for get data about <ranobe>\n{e}"')
        data['ranobe']['log'] = ''
        notify = data['notify']['notify'] = checkVoice(data, msg)
        sleep(1.2)
        self.ranobe_percent = 0
        self.setGlobalSettings(data, '', '', '', False, True)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    application = GlobalParser()
    exit(app.exec())
