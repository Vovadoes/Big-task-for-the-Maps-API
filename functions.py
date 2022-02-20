import requests
import json


def find_name(name, ischeck):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={name}&format=json"

    # Выполняем запрос.
    response = requests.get(geocoder_request)
    try:
        # Преобразуем ответ в json-объект
        json_response = response.json()
        with open('data.json', 'w') as outfile:
            json.dump(json_response, outfile)
        # Получаем первый топоним из ответа геокодера.
        # Согласно описанию ответа, он находится по следующему пути:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # Полный адрес топонима:
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]
        # Печатаем извлечённые из ответа поля:
        print(toponym_address, "имеет координаты:", toponym_coodrinates)
        if ischeck:
            return toponym_coodrinates, toponym_address + ', ' + \
                   toponym["metaDataProperty"]["GeocoderMetaData"]['Address']['postal_code']
        else:
            return toponym_coodrinates, toponym_address
    except:
        print("Ошибка выполнения запроса:")
        return 1


def find_object(x, y):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={x},{y}&format=json"

    # Выполняем запрос.
    response = requests.get(geocoder_request)
    try:
        # Преобразуем ответ в json-объект
        json_response = response.json()
        with open('data.json', 'w', encoding='utf-8') as outfile:
            json.dump(json_response, outfile)
        s1 = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject'][
            'metaDataProperty']['GeocoderMetaData']['Address']['formatted']
        return s1
    except:
        print('не получилось')
