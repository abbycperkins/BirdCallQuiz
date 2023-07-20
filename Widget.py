import contextlib
with contextlib.redirect_stdout(None):
    from pygame import mixer
import re
import requests
import random
import pathlib
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.Qt import Qt
import sys
import csv


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 ' \
             'Safari/537.36'
BASE_URL = 'https://www.bird-sounds.net/'
parent_directory = pathlib.Path('C:/Users/Abby/PycharmProjects/BirdCallQuiz')
directory = "Audio_Files"
DIRECTORY = parent_directory / directory
DIRECTORY.mkdir(parents=True, exist_ok=True)
BIRDS = []
data_array = []
with open(parent_directory / 'families and species.csv') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=",")
    next(csv_reader, None)
    for row in csv_reader:
        data_array.append({'family': row[0], 'species': row[1]})
families = []
for fam in data_array:
    if fam['family'] not in families:
        families.append(fam['family'])


class Window(QWidget):
    def __init__(self):
        super().__init__()
        tw = QTreeWidget()
        tw.itemChanged[QTreeWidgetItem,int].connect(self.change_list)
        grid = QGridLayout(self)
        grid.addWidget(tw)
        self.add_birds(tw)

    def new_item(self, text):
        item = QTreeWidgetItem()
        item.setText(0, text)
        item.setCheckState(0, Qt.Unchecked)
        return item

    def add_birds(self, p):
        for family in families:
            item = self.new_item(family)
            if isinstance(p, QTreeWidget):
                p.addTopLevelItem(item)
            item.setFlags(item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            for spec in data_array:
                if spec['family'] == family:
                    child = self.new_item(spec['species'])
                    child.setFlags(child.flags() | Qt.ItemIsUserCheckable)

    def change_list(self, item):
        if item.checkState() == Qt.Checked:
            BIRDS.append(item)
        if item.checkState() == Qt.Unchecked:
            BIRDS.remove(item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = Window()
    gui.show()
    app.exec()


# BIRDS = input('Enter your desired bird list, separated by commas: ').split(", ")
print(BIRDS)

# page = requests.get(url)

for bird in BIRDS:
    species_url = bird.replace(' ', '-').lower()
    url = f'{BASE_URL}{species_url}'
    file_name = f'{species_url}.mp3'
    if (DIRECTORY / file_name).is_file():
        continue
    print(f'Requesting: {url}')
    r = requests.get(
        url=url,
        headers={'User-Agent': USER_AGENT},
    )
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')

    for a in soup.find_all(name='source', src=re.compile(r'.*\.mp3')):
        mp3_file = requests.get(
            url=f'{BASE_URL}{a["src"]}',
            headers={'User-Agent': USER_AGENT},
        )

        with open((DIRECTORY / file_name), 'wb') as f:
            f.write(mp3_file.content)

# run quiz until no more birds
score = 0
BIRDS_unchanged = BIRDS.copy()
random.shuffle(BIRDS)
for bird in BIRDS:
    cb_sterile = bird.replace(' ', '-').lower()
    cb_file = f'{cb_sterile}.mp3'

    # play sound until player gives answer
    mixer.init()
    mixer.music.load(DIRECTORY / cb_file)
    mixer.music.play(-1)
    # time.sleep(5)

    # ask player for answer
    player_answer = input('The bird is a: ')
    player_answer = player_answer.replace("'", "")
    mixer.music.stop()

    if player_answer.lower() == bird.lower():
        print("Correct!")
        score = score + 1
    else:
        print(f'Incorrect. The bird is a {bird}.')

else:
    print(f'You have completed your bird list! Your score was {score}/{len(BIRDS_unchanged)}')