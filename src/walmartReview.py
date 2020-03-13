from selenium import webdriver
import time

import urllib.request, json
import xlrd
import xlwt

wdata = xlwt.Workbook()
table = wdata.add_sheet('walmart_product')
header = [u'itemId', u'itemName']

num = 0
hisense_url = "http://api.walmartlabs.com/v1/search?query=TV+hisense&format=json&categoryId=3944_1060825_447913&apiKey=j3drdka3rbfeactxw3y4k4hg"

with urllib.request.urlopen(hisense_url) as url:
    data = json.loads(url.read().decode())
    print(data['start'])
    print(data['numItems'])
    num += data['numItems']
    for item in enumerate(data['items']):
        itemId = item['itemId']
        product = item['name']
    while data['numItems'] >= 10 :
        start = data['start'] + 10
        with urllib.request.urlopen(hisense_url + "&start=" + str(start)) as url:
            data = json.loads(url.read().decode())
            print(data['start'])
            print(data['numItems'])
            print(num)
            for row, item in enumerate(data['items']):
                table.write(row + num, 0, item['itemId'])
                table.write(row + num, 1, item['name'])
            num += data['numItems']


oldB = xlrd.open_workbook('example.xls', formatting_info=True)
prodS = oldB.sheet_by_name('walmart_product')
baseURL = "https://www.walmart.com/reviews/product/"
driver = webdriver.Chrome()
row_num = 0

review_table = wdata.add_sheet('walmart_review')
header = [u'itemName', u'poster', u'post_date', u'post_title', u'post_rate', u'post_text']

for row_idx in range(0, prodS.nrows):

    prod_id = str(round(prodS.cell(row_idx, 0).value))
    product = prodS.cell(row_idx, 1).value
    driver.get(baseURL + prod_id)
    try:
        dropDown = driver.find_element_by_xpath("//select[1]/option[text()='Newest to oldest']")
    except:
        continue
    else:
        dropDown.click()
    while True:
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        reviews = soup.find_all(class_="Grid ReviewList-content")
        for review in reviews:
            poster     = review.find(class_="review-footer-userNickname").contents
            post_date  = review.find(class_="review-footer-submissionTime").contents[0]
            post_text  = review.find(class_="review-body-text").contents[1]
            post_rate  = review.find(class_="stars-container")['alt']
            post_title = review.find(class_="review-title")
            if post_title == None:
                post_title = 'None'
            else:
                post_title = post_title.contents[0]
            review_table.write(row_num, 0, product)
            review_table.write(row_num, 1, poster)
            review_table.write(row_num, 2, post_date)
            review_table.write(row_num, 3, post_title)
            review_table.write(row_num, 4, post_rate)
            review_table.write(row_num, 5, post_text)
            row_num += 1
            print(row_num)
        try:
            next_page = driver.find_element_by_xpath("//button[@class='active']/../following-sibling::li/button[1]")
        except:
            break
        else:
            next_page.click()

wdata.save('example.xls')
