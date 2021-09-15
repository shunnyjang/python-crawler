from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from pandas import DataFrame

from time import sleep
import os

import tkinter
from tkinter import filedialog

import re


def get_dataframe(index: int, product: str, category: str, star: str, review: str) -> DataFrame:
    dataframe = DataFrame(columns=['product', 'category', 'star', 'review'])
    dataframe.loc[index] = [product, category, star, review]
    return dataframe


def save_dataframe_to_csv(df: DataFrame, path: str):
    csv_save_path = path + '/keygam_output.csv'
    if not os.path.exists(csv_save_path):
        df.to_csv(csv_save_path, encoding='utf-8-sig', mode='w')
    else:
        df.to_csv(csv_save_path, encoding='utf-8-sig', mode='a', header=False)


def set_scroll_down_to_bottom(driver: webdriver) -> None:
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    sleep(5)


def get_only_em_tag(text):
    context = ""
    open_em_index_list = [i.start() for i in re.finditer('<p>', text)]
    close_em_index_list = [i.start() for i in re.finditer('</p>', text)]
    for index in range(0, len(open_em_index_list)):
        context += " " + text[open_em_index_list:close_em_index_list]
    return context


def crawl_mobile_review_context(product, driver, path):
    for i in range(1, 3):
        # li[1] : 포토&동영상 리뷰, li[2]: 일반 리뷰
        review_type_xpath = '/html/body/div/div/div[2]/div[1]/ul/li[{i}]'.format(i=i)
        driver.find_element_by_xpath(review_type_xpath).click()
        sleep(2)
        index = 1
        prev_height = 0
        current_height = 0
        while True:
            product_xpath = '/html/body/div/div/div[2]/div[4]/ul/li[{index}]/div/'.format(index=index)
            star_xpath = product_xpath + 'div[1]/div/span'
            review_xpath = product_xpath + 'div[2]/p/span'
            category_xpath = product_xpath + 'div[2]/div[1]'
            prev_height = driver.execute_script("return document.body.scrollHeight")
            try:
                star_element = driver.find_element_by_xpath(star_xpath)
                star = str(star_element.text)[2]
                review_element = driver.find_element_by_xpath(review_xpath)
                review = review_element.text
            except NoSuchElementException:
                # 다시 한 번 스크롤을 내리고 기다려본다.
                set_scroll_down_to_bottom(driver)
                current_height = driver.execute_script("return document.body.scrollHeight")
                # 그래도 무한 스크롤이 새로 생성되지 않으면 종료
                if prev_height == current_height:
                    break
                else:
                    continue
            try:
                category_element = driver.find_element_by_xpath(category_xpath)
                category = category_element.text
            except NoSuchElementException:
                category = ' '

            dataframe = get_dataframe(index=index, product=product, category=category, star=star, review=review)
            save_dataframe_to_csv(dataframe)

            # 네이버 쇼핑몰 모바일 버전은 한 번에 20개씩 보여줍니다. 가장 아래 리뷰에 스크롤 내리면 무한스크롤로 20개씩 새로 생성합니다.
            # 따라서 20번째 리뷰를 보고 있다면 가장 아래로 스크롤 내려서 새로운 리뷰 20개를 보여줍니다.
            if index % 20 == 0:
                set_scroll_down_to_bottom(driver)
            index += 1


def crawl_desktop_review_context(product: str, driver: webdriver, path: str):
    page = 1
    n = 1
    review_list_element = driver.find_element_by_class_name("review_section_review__1hTZD")
    keygam_element = review_list_element.find_element_by_xpath('./div[2]/div[2]/div/ul/li[5]/a')
    keygam_element.click()
    sleep(1)
    while True:
        if page == 11 and n < 221:
            page = 2
        if page == 12:
            page = 2
        for index in range(1, 21):
            try:
                product_element = review_list_element.find_element_by_xpath('./ul/li[{index}]'.format(index=index))
            except NoSuchElementException:
                print("NoSuchElementException : review")
                return

            star_element = product_element.find_element_by_class_name("reviewItems_average__16Ya-")
            star = str(star_element.text)[2]
            # /html/body/div/div/div[2]/div[2]/div[2]/div[3]/div[6]/ul/li[1]/div[2]/div/p
            # review_element = product_element.find_element_by_class_name("reviewItems_text__XIsTc")
            review_element = product_element.find_element_by_xpath('./div[2]/div/p')
            # print(review_element.text)
            review = get_only_em_tag(review_element.text)
            try:
                category_elements = product_element.find_elements_by_class_name("reviewItems_etc__1YqVF")
                category = category_elements[3].text
            except IndexError:
                category = ' '
            dataframe = get_dataframe(index=n, product=product, category=category, star=star, review=review)
            save_dataframe_to_csv(dataframe, path)
            print(str(n) + "번째 리뷰 저장 성공")
            n += 1

            if n == 2000:
                print("n == 2000")
                return

            if index == 20:  # 한 페이지에 리뷰 20개
                page += 1
                try:
                    page_element = review_list_element.find_element_by_class_name("pagination_pagination__2M9a4") \
                                                      .find_element_by_xpath("./a[{page}]".format(page=page))
                    page_element.click()
                    sleep(1)
                except NoSuchElementException:
                    print("NoSuchElementException : page : ", page)
                    return

# 사용하지 마세요 미완성
"""
네이버 쇼핑몰 리뷰 모바일 버전 웹크롤러입니다.
- item : 제품의 번호입니다. 각 제품마다 링크를 참고해서 수정하세요.

# item = input("item catalog number : ")
# url = 'https://msearch.shopping.naver.com/catalog/{item}/reviews?fromWhere=CATALOG'.format(item=item)
# 
# 
# # 저장할 폴더 지정
# root = tkinter.Tk()
# root.withdraw()
# path = filedialog.askdirectory(parent=root, initialdir=os.path, title='Please select a directory')
# 
# chrome_driver = webdriver.Chrome('./chromedriver')
# chrome_driver.get(url)

#
# crawl_mobile_review_context(product=product, driver=chrome_driver)
"""

"""
네이버 쇼핑몰 리뷰 웹 버전 크롤러입니다.
- item : 네이버 쇼핑 아이템의 고유 번호입니다. 링크에서 복사하세요.
"""
item = input("item catalog number : ")
url = 'https://search.shopping.naver.com/catalog/' + item

# 저장할 폴더 지정
root = tkinter.Tk()
root.withdraw()
path = filedialog.askdirectory(parent=root, initialdir=os.path, title='Please select a directory')

chrome_driver = webdriver.Chrome('./chromedriver')
chrome_driver.get(url)

product = chrome_driver.find_element_by_xpath('/html/body/div/div/div[2]/div[2]/div[1]/h2').text
crawl_desktop_review_context(product=product, driver=chrome_driver, path=path)
