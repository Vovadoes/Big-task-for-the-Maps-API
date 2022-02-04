import sys
from io import BytesIO

import requests as requests
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.coords = (47.247691, 56.147098)
        self.delta = 0.006
        uic.loadUi('untitled.ui', self)  # Загружаем дизайн
        self.setImage()

    def getImage(self):

        # Собираем параметры для запроса к StaticMapsAPI:
        map_params = {
            "ll": ",".join(map(str, self.coords)),
            "spn": ",".join([str(self.delta), str(self.delta)]),
            "l": "map"
        }

        map_api_server = "http://static-maps.yandex.ru/1.x/"
        # ... и выполняем запрос
        response = requests.get(map_api_server, params=map_params)

        return Image.open(BytesIO(
            response.content))

    def setImage(self):
        pixmap = QPixmap.fromImage(
            ImageQt(self.getImage().resize((self.width(), self.height()), Image.LANCZOS)))
        self.label.setPixmap(pixmap)

    def keyPressEvent(self, key):
        if key.key() == Qt.Key_Escape:
            self.close()
        if key.key() == Qt.Key_Up:
            self.delta += 0.01
            self.delta = round(self.delta, 3)
            self.setImage()
            print("UP", f'{self.delta=}')
        if key.key() == Qt.Key_Down:
            self.delta -= 0.01
            self.delta = round(max(0.001, self.delta), 3)
            self.setImage()
            print("Down", f'{self.delta=}')
        if key.key() in (Qt.Key_W, Qt.Key_S, Qt.Key_A, Qt.Key_D):
            d = 0.0005
            if key.key() == Qt.Key_W:
                self.coords = (self.coords[0], round(self.coords[1] + d, 6))
            if key.key() == Qt.Key_S:
                self.coords = (self.coords[0], round(self.coords[1] - d, 6))
            if key.key() == Qt.Key_A:
                self.coords = (round(self.coords[0] - d, 6), self.coords[1])
            if key.key() == Qt.Key_D:
                self.coords = (round(self.coords[0] + d, 6), self.coords[1])
            self.setImage()
            print(f'{self.coords=}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
