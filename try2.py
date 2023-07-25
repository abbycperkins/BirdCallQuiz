import csv
import re
import pathlib
import sys
import requests
import random
from bs4 import BeautifulSoup
import contextlib
with contextlib.redirect_stdout(None):
    from pygame import mixer
from collections import defaultdict
import pandas as pd

from PyQt5.Qt import Qt
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QWidget, QMainWindow, QApplication, QVBoxLayout, QTreeWidget,
    QTreeWidgetItem, QPushButton, QInputDialog, QMessageBox,
)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 ' \
             'Safari/537.36'
BASE_URL = 'https://www.bird-sounds.net/'
parent_directory = pathlib.Path('C:/Users/Abby/PycharmProjects/BirdCallQuiz')
directory = "Audio_Files"
DIRECTORY = parent_directory / directory
DIRECTORY.mkdir(parents=True, exist_ok=True)
BIRD_CSV = pathlib.Path('C:/Users/Abby/PycharmProjects/BirdCallQuiz/families and species.csv').expanduser()


class BirdQuiz(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bird_list = []
        self.setWindowTitle("Bird Quiz")

        layout = QVBoxLayout()
        self.tree = self.create_tree()
        layout.addWidget(self.tree)

        button = QPushButton('Submit List')
        layout.addWidget(button)
        button.pressed.connect(lambda: self.submit_list())
        button.pressed.connect(lambda: self.run_quiz())

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def create_tree(self):
        tree = QTreeWidget()
        tree.setColumnCount(1)

        data_array = defaultdict(list)
        with BIRD_CSV.open(newline='') as csvfile:
            for row in csv.reader(csvfile, delimiter=","):
                data_array[row[0]].append(row[1])

        for family_name, species_list in data_array.items():
            family = QTreeWidgetItem(tree)
            family.setFlags(family.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            family.setText(0, family_name)

            for species_name in species_list:
                species = QTreeWidgetItem(family)
                species.setFlags(species.flags() | Qt.ItemIsUserCheckable)
                species.setCheckState(0, QtCore.Qt.Unchecked)
                species.setText(0, species_name)

        tree.setHeaderHidden(True)
        return tree

    def submit_list(self):
        self.bird_list.clear()
        root = self.tree.invisibleRootItem()
        for index in range(root.childCount()):
            parent = root.child(index)
            if parent.checkState(0) == Qt.Unchecked:
                continue
            else:
                for row in range(parent.childCount()):
                    child = parent.child(row)
                    if child.checkState(0) == Qt.Checked:
                        self.bird_list.append(child.text(0))
        print(self.bird_list)

    def run_quiz(self):
        for bird in self.bird_list:
            species_url = bird.replace(' ', '-').replace("'", "").lower()
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
        random.shuffle(self.bird_list)
        score = 0

        for bird in self.bird_list:
            df = pd.read_csv('C:/Users/Abby/PycharmProjects/BirdCallQuiz/species codes.csv',
                             usecols=['Species', 'Species Code'])
            df.set_index('Species', inplace=True)
            species_code = df.at[bird, 'Species Code'].lower()
            cb_sterile = bird.replace(' ', '-').lower()
            cb_file = f'{cb_sterile}.mp3'
            # play sound until player gives answer
            mixer.init()
            mixer.music.load(DIRECTORY / cb_file)
            mixer.music.play(-1)
            # time.sleep(5)

            # ask player for answer
            dialog = QInputDialog(self)
            player_answer, ok = dialog.getText(self, 'Input Dialog', 'The bird is a: ')
            player_answer = player_answer.replace("'", "").lower()
            if player_answer == bird.lower() or player_answer == species_code:
                score = score + 1

            if ok:
                mixer.music.stop()
                msg = QMessageBox()
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setWindowTitle('Answer')
                if player_answer == bird.lower() \
                        or player_answer == species_code:
                    msg.setText("Correct!")
                else:
                    msg.setText(f'Incorrect. The bird is a {bird} ({species_code.upper()}).')
                msg.exec_()

        msg.setText(f'You have completed your bird list! Your score was {score}/{len(self.bird_list)}')
        msg.setWindowTitle('Quiz complete!')
        msg.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = BirdQuiz()
    main.show()
    sys.exit(app.exec_())