#!/usr/bin/env python3

# FIX: Read PEP8 for how imports should be structured (I fixed this already)

import csv
import pathlib
import sys
from collections import defaultdict

# FIX: Star imports are the worst, you should explicitly call out what you want (I fixed this already)

from PyQt5.Qt import Qt
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton

BIRD_CSV = pathlib.Path('~/Downloads/families_and_species.csv').expanduser()


class BirdQuiz(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bird Quiz")

        layout = QVBoxLayout()
        tree = self.create_tree()
        layout.addWidget(tree)

        button = QPushButton('Close')
        button.pressed.connect(self.close)
        layout.addWidget(button)

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
                species.setCheckState(0, QtCore.Qt.Unchecked)  # Checkboxes wont show up until you set a checkState
                species.setText(0, species_name)

        return tree


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = BirdQuiz()
    main.show()
    sys.exit(app.exec_())