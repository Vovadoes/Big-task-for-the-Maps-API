import sys
from io import BytesIO
import json
import requests as requests
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import *
from functions import find_name, find_object, find_organisation


# 47.152165, 56.131877

# 0.013691 0.006
class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.map_file = "map.png"
        self.coords = (47.247691, 56.147098)
        self.points = [(47.247691, 56.147098)]
        self.points_2 = [(47.247691, 56.147098)]
        self.delta = 0.006
        self.size_img = 441
        uic.loadUi('untitled.ui', self)  # Загружаем дизайн
        self.map_layer = 'map'
        self.label_2.setText("Чебоксарский залив, Чебоксары, Чувашская Республика, Россия")
        self.name_coords = ['Чебоксарский залив, Чебоксары, Чувашская Республика, Россия']
        self.pushButton.clicked.connect(self.run)
        self.pushButton_2.clicked.connect(self.run_2)
        self.pushButton_3.clicked.connect(self.resetting_the_search_result)
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(False)
        self.button_group.addButton(self.radioButton)
        self.button_group.buttonClicked.connect(self.stop_ever)
        self.setImage()

    def geo_find_obj(self, x, y):
        name = find_name(find_object(x, y), self.radioButton_2.isChecked())
        if name != 1:
            name1 = name[0].split()
            name2 = name[1]
            self.coords = (float(name1[0]), float(name1[1]))
            self.points = self.points[:-1]
            self.points.append(self.coords)
            self.points_2.append(self.coords)
            self.setImage()
            self.label_2.setText(name2)
            self.name_coords.append(name2)

    def geo_find_obj_2(self, x, y):
        text = find_name(find_object(x, y), self.radioButton_2.isChecked())
        name = find_organisation(x, y, text)
        if name != 0:
            name, coord = name[0], name[1]
            self.coords = coord
            self.points = self.points[:-1]
            self.points.append(self.coords)
            self.points_2.append(self.coords)
            self.setImage()
            self.label_2.setText(name)
            self.name_coords.append(name)

    def mousePressEvent(self, event):  # нужно сделать!!!!
        x = event.pos().x()
        y = event.pos().y()
        if 20 <= x <= 490 and 50 <= y <= 490:
            x, y = x - 20, y - 50
            x, y = x - self.size_img // 2, y - self.size_img // 2
            # изменяем систему координат
            #      ^
            #      |
            #      |
            # ----------->
            #      |
            #      |
            # где середина ноль x, y
            k = self.delta / (self.size_img // 2)  # Количество радиан в 1 пикселе
            print(x, y)  # пиксели на изображении!
            coords = (round(self.coords[0] + k * x, 6),
                      round(self.coords[1] - k * y,
                            6))  # Высчитываем координаты, - + как направления осей
            print(f"{coords=}")
            if event.button() == Qt.LeftButton:
                self.geo_find_obj(coords[0], coords[1])
            else:
                self.geo_find_obj_2(coords[0], coords[1])

    def resetting_the_search_result(self):
        if len(self.points_2) != 1:
            self.points_2 = self.points_2[:-1]
            self.coords = self.points_2[-1]
            self.points = [self.points_2[-1]]
            self.name_coords = self.name_coords[:-1]
            self.label_2.setText(self.name_coords[-1])
        self.setImage()

    def stop_ever(self, button):
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.radioButton.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.radioButton_2.setEnabled(False)

    def run_2(self):
        name, ok_pressed = QInputDialog.getText(self, "Выбор точек",
                                                "Введите название объекта")
        if ok_pressed:
            name = find_name(name, self.radioButton_2.isChecked())
            if name != 1:
                name1 = name[0].split()
                name2 = name[1]
                self.coords = (float(name1[0]), float(name1[1]))
                if len(self.points) != 0:
                    self.points = self.points[:-1]
                self.points.append(self.coords)
                self.points_2.append(self.coords)
                self.setImage()
                self.label_2.setText(name2)
                self.name_coords.append(name2)

    def run(self):
        country, ok_pressed = QInputDialog.getItem(
            self, "Выберите слой карты", "Слой карты?",
            ('map', 'sat', 'skl'), 1, False)
        if ok_pressed:
            if country == 'map':
                self.map_layer = 'map'
            elif country == 'sat':  # не работает
                self.map_layer = 'sat'
            else:
                self.map_layer = 'skl'
            self.setImage()

    def getImage(self):
        # Собираем параметры для запроса к StaticMapsAPI:
        map_params = {
            "ll": ",".join(map(str, self.coords)),
            "spn": ",".join([str(self.delta), str(self.delta)]),
            "l": self.map_layer,
            'size': f'{self.size_img},{self.size_img}',
            'pt': "~".join([f'{i[0]},{i[1]}' for i in self.points]),
        }

        map_api_server = "http://static-maps.yandex.ru/1.x/"
        # ... и выполняем запрос
        response = requests.get(map_api_server, params=map_params)

        with open(self.map_file, "wb") as file:
            file.write(response.content)
        # return Image.open(BytesIO(
        #     response.content))

    def setImage(self):  # вызываем фото и показываем
        self.getImage()
        self.pixmap = QPixmap(self.map_file)
        self.label.setPixmap(self.pixmap)

    def keyPressEvent(self, key):
        if key.key() == Qt.Key_Space:
            for button in self.button_group.buttons():
                button.setChecked(False)
            self.pushButton.setEnabled(True)
            self.pushButton_2.setEnabled(True)
            self.radioButton.setEnabled(True)
            self.pushButton_3.setEnabled(True)
            self.radioButton_2.setEnabled(True)
        if key.key() == Qt.Key_Escape:
            self.close()
        if key.key() == Qt.Key_Up:  # увеличиваем размер
            self.delta += 0.01
            self.delta = round(self.delta, 3)
            self.setImage()
            print("UP", f'{self.delta=}')
        if key.key() == Qt.Key_Down:  # уменьшаем размер
            self.delta -= 0.01
            self.delta = round(max(0.001, self.delta), 3)
            self.setImage()
            print("Down", f'{self.delta=}')
            # if key.key() in (Qt.Key_W, Qt.Key_S, Qt.Key_A, Qt.Key_D):
        d = 0.0005
        if key.key() == Qt.Key_W:
            self.coords = (self.coords[0], round(self.coords[1] + d, 6))
            self.setImage()
        if key.key() == Qt.Key_S:
            self.coords = (self.coords[0], round(self.coords[1] - d, 6))
            self.setImage()
        if key.key() == Qt.Key_A:
            self.coords = (round(self.coords[0] - d, 6), self.coords[1])
            self.setImage()
        if key.key() == Qt.Key_D:
            self.coords = (round(self.coords[0] + d, 6), self.coords[1])
            self.setImage()
        print(f'{self.coords=}')


# def searchByMapClick(self, coords_mouse):
#     x_size, y_size = (float(self.mashtab.toPlainText()) / 641,
#                       float(self.mashtab.toPlainText()) / 441)
#     new_ask = ','.join(
#         (str((float(self.edit_x.toPlainText()) - float(self.mashtab.toPlainText())) -
#              x_size * (coords_mouse[0] - 10)),
#          str((float(self.edit_y.toPlainText()) - float(self.mashtab.toPlainText())) -
#              y_size * (coords_mouse[1] - 10))))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
