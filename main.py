import sys
from io import BytesIO

import requests as requests
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.coords = (0.0, 0.0)
        uic.loadUi('untitled.ui', self)  # Загружаем дизайн
        self.setImage()

    def getImage(self):
        delta = "0.005"

        # Собираем параметры для запроса к StaticMapsAPI:
        map_params = {
            "ll": ",".join(map(str, self.coords)),
            "spn": ",".join([delta, delta]),
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
