import numpy as np
from PIL import Image
import PIL.Image
from pytesseract import image_to_string
import pyscreenshot as ImageGrab
import pytesseract
import cv2
import os
import json
import requests
import numpy as np
import pyautogui
import re


def get_items():
    url = "https://api.warframe.market/v1/items"
    res = requests.get(url)
    data = res.json()
    items = []
    items_raw = data['payload']['items']['en']
    for i in range(len(items_raw)):
        items.append(items_raw[i]["item_name"].lower())
    return items


def get_screen():
    image = pyautogui.screenshot()
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    cv2.imwrite("in_memory_to_disk.png", image)


def get_raw():
    pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'
    TESSDATA_PREFIX = 'C:/Program Files (x86)/Tesseract-OCR'

    # image = cv2.imread('src/endscreen.png')
    # gray = cv2.medianBlur(image, 3)
    # filename = "{}.png".format(os.getpid())
    # cv2.imwrite(filename, image)

    image = pyautogui.screenshot()  #cv2.imread('src/detect2.png') # pyautogui.screenshot()
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)  #cv2.COLOR_RGB2BGR)
    image = cv2.medianBlur(image, 1)
    image = cv2.bitwise_not(image)
    cv2.imwrite("in_memory_to_disk.png", image)
    # cv2.imwrite("detect2.png",image)

    output = pytesseract.image_to_string(Image.open('in_memory_to_disk.png'))  # filename))
    os.remove('in_memory_to_disk.png')  # filename)
    return output


def get_screen_items():
    items = get_items()
    raw = get_raw()
    data = raw.split("\n")
    print(data)
    screen_items = []
    for i in range(len(data)):
        name = data[i].lower()
        ducats_re = re.search(r'(?<=[a-zA-Z]) [0-9]+', name)
        num_re = re.search(r'[0-9]+ x ', name)
        if ducats_re:
            cutoff = len(ducats_re.group(0))
            name = name[:(len(name)-cutoff)]
        if num_re:
            cutoff = len(num_re.group(0))
            name = name[cutoff:]
        if name[(len(name)-9):] == "blueprint" and len(name.split(" ")) > 3:
            name = name[:(len(name)-10)]
        if name in items:
            screen_items.append(name)
    # print(screen_items)
    return screen_items


def get_item_market_value(url = ""):
    # get lowest plat value that is a sell order that is currently online
    url = "https://api.warframe.market/v1/items/" + url + "/orders"
    res = requests.get(url).json()
    orders = res['payload']['orders']
    lowest_plat = 999999999
    plat = []
    for i in range(len(orders)):
        if orders[i]['order_type'] == 'sell' and orders[i]['user']['status'] == 'ingame':
            plat.append(orders[i]['platinum'])
            if orders[i]['platinum'] < lowest_plat:
                lowest_plat = orders[i]['platinum']
    return plat, lowest_plat


def get_item_market_data(item=""):
    item = item.replace(" ", "_")
    url = "https://api.warframe.market/v1/items/" + item
    res = requests.get(url).json()

    index = 0
    items_in_set = res['payload']['item']['items_in_set']
    for i in range(len(items_in_set)):
        if item == items_in_set[i]['url_name']:
            index = i
            break
    item_value = items_in_set[index]
    ducats = item_value['ducats']
    plat, lowest_plat = get_item_market_value(item)

    return ducats, plat, lowest_plat


def update_ui():
    items = get_screen_items()
    items = list(dict.fromkeys(items))
    for i in range(len(items)):
        # hilight best one
        print("")
        print("name: " + items[i])
        ducats, plat, lowest_plat = get_item_market_data(items[i])
        print("ducats: " + str(ducats) + "\tplat: " + str(lowest_plat))
        print("plat/ducats: " + str(lowest_plat/ducats))


update_ui()
