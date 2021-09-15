from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from pandas import DataFrame

from time import sleep
import os

import tkinter
from tkinter import filedialog


def get_dataframe(index: int, product: str, category: str, star: str, review: str) -> DataFrame:
    dataframe = DataFrame(columns=['product', 'category', 'star', 'review'])
    dataframe.loc[index] = [product, category, star, review]
    return dataframe


def save_dataframe_to_csv(df: DataFrame, path: str):
    csv_save_path = path + '/output.csv'
    if not os.path.exists(csv_save_path):
        df.to_csv(csv_save_path, encoding='utf-8-sig', mode='w')
    else:
        df.to_csv(csv_save_path, encoding='utf-8-sig', mode='a', header=False)


def crawl_desktop_review_context(product: str, driver: webdriver, path: str):
    page = 1
    n = 1
    while True:
        if page == 11 and n < 201:
            page = 3
        if page == 13:
            page = 3
        for index in range(1, 21):
            if n == 10001:
                return
            try:
                review_list_element = driver.find_element_by_class_name("review_list")
                product_element = review_list_element.find_element_by_xpath('./div[2]/ul/li[{index}]'.format(index=index))
            except NoSuchElementException:
                return

            star_element = product_element.find_element_by_class_name("_2V6vMO_iLm")
            star = str(star_element.text)[2]
            review_element = product_element.find_element_by_class_name("_3QDEeS6NLn")
            review = review_element.text

            try:
                category_elements = product_element.find_elements_by_class_name("_3QDEeS6NLn")
                category = category_elements[3].text
            except IndexError:
                category = ' '

            dataframe = get_dataframe(index=n, product=product, category=category, star=star, review=review)
            save_dataframe_to_csv(dataframe, path)
            print(str(n) + "번째 리뷰 저장 성공")
            n += 1

            if index == 20:  # 한 페이지에 리뷰 20개
                page += 1
                try:
                    page_element = review_list_element.find_element_by_class_name("_1HJarNZHiI _2UJrM31-Ry _3F77jPGGAN") \
                                                      .find_element_by_xpath("./a[{page}]".format(page=page))
                    webdriver.ActionChains(driver).move_to_element(page_element).click().perform()
                    sleep(1)
                except NoSuchElementException:
                    return


"""
네이버 쇼핑몰 리뷰 웹 (스마트스토어) 버전 크롤러입니다.
- item : 네이버 쇼핑 아이템의 고유 번호입니다. 링크에서 복사하세요.
"""
item = input("item catalog number : ")
url = 'https://smartstore.naver.com/nano/products/' + item

# 저장할 폴더 지정
root = tkinter.Tk()
root.withdraw()
path = filedialog.askdirectory(parent=root, initialdir=os.path, title='Please select a directory')

chrome_driver = webdriver.Chrome('./chromedriver')
chrome_driver.get(url)

product = chrome_driver.find_element_by_class_name('CxNYUPvHfB').text
crawl_desktop_review_context(product=product, driver=chrome_driver, path=path)
