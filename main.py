import contextlib
with contextlib.redirect_stdout(None):
    from pygame import mixer
import re
import requests
import random
import pathlib
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.Qt import Qt
import sys


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 ' \
             'Safari/537.36'
BASE_URL = 'https://www.bird-sounds.net/'
parent_directory = pathlib.Path('C:/Users/Abby/PycharmProjects/BirdCallQuiz')
directory = "Audio_Files"
DIRECTORY = parent_directory / directory
DIRECTORY.mkdir(parents=True, exist_ok=True)
BIRDS = []


def bird_choice_window():
    app = QApplication(sys.argv)
    tree = QTreeWidget()
    header_item = QTreeWidgetItem()
    item = QTreeWidgetItem()
    import csv
    data_array = []
    output = []
    with open(parent_directory / 'families and species.csv') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        next(csv_reader, None)
        for row in csv_reader:
            data_array.append({'family': row[0], 'species': row[1]})
    # families = ['Wrens (Troglodytidae)', 'Thrushes (Turdidae)', 'Towhees and Sparrows (Passerellidae)',
    # 'Wood-Warblers (Parulidae)']

    families = []
    for fam in data_array:
        if fam['family'] not in families:
            families.append(fam['family'])

    for family in families:
        parent = QTreeWidgetItem(tree)
        parent.setText(0, family)
        parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        for spec in data_array:
            if spec['family'] == family:
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, spec['species'])
                child.setCheckState(0, Qt.Unchecked)
    tree.setWindowTitle("Abby's Bird Sounds Quiz")

    tree.setHeaderHidden(True)
    tree.show()
    app.exec()


if __name__ == '__main__':
    bird_choice_window()

# BIRDS = input('Enter your desired bird list, separated by commas: ').split(", ")
# print(BIRDS)

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