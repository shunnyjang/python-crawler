import json
import urllib
from urllib.error import HTTPError

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from urllib.request import urlopen

import os

import tkinter
from tkinter import filedialog


def crawl_product_image(driver: webdriver, path: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/90.0.4430.212 Safari/537.36"
             }
    n = 1
    try:
        images = driver.find_element_by_id("partContents_3_0")
    except NoSuchElementException:
        print("No Element")
        driver.close()
        return
    for x in images.find_elements_by_xpath("./img"):
        img = x.get_attribute("src")
        # imgtype = str(img).split('.')[-1]
        try:
            req = urllib.request.Request(img, headers=headers)
            raw_image = urlopen(req).read()
            file = open(os.path.join(path, 'image' + '_' + str(n) + ".jpg"), "wb")
            file.write(raw_image)
            file.close()
            n += 1
        except:
            print("Error")

    print(str(n) + "개의 이미지 저장 완료")
    driver.close()
    return


item = input("item catalog number : ")
url = 'http://prod.danawa.com/info/?pcode=' + item

# 저장할 폴더 지정
root = tkinter.Tk()
root.withdraw()
path = filedialog.askdirectory(parent=root, initialdir=os.path, title='Please select a directory')

chrome_driver = webdriver.Chrome('./chromedriver')
chrome_driver.get(url)

crawl_product_image(driver=chrome_driver, path=path)

