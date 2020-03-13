import urllib.request, json
from datetime import date, timedelta
from selenium import webdriver
import xlrd
import xlwt


wdata = xlwt.Workbook()

api_url  = "https://api.bestbuy.com/v1/products((search=hisense)&(categoryPath.id=abcat0101000))?apiKey=cut5th4m6p8v2v8rgq44dxd8&sort=sku.asc&show=sku,name,modelNumber,url&pageSize=20&format=json"
monthDic = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
models   = []
skus     = []
products = []

def lookAhead(iterable):
    it = iter(iterable)
    last = next(it)
    for val in it:
        yield last, True
        last = val
    yield last, False

with urllib.request.urlopen(api_url) as url:
    data = json.loads(url.read().decode())
    for i, item in enumerate(data['products']):
        skus.append(item['sku'])
        products.append(item['name'])
        models.append(item['modelNumber'])

driver  = webdriver.Chrome()
baseURL = "https://www.bestbuy.com/site/reviews/hisense-55-class-led-h8f-series-2160p-smart-4k-uhd-tv-with-hdr/"
apiKey  = "?ds_rl=1266837&gclid=CjwKCAiAws7uBRAkEiwAMlbZjn0m7Ofhq13KtiYJsF-jKH4VU7YvUDni-96oXDuiV_VDj-m5rq6IIRoCSwgQAvD_BwE"
params  = "&gclsrc=aw.ds&loc=1&ref=212&sort=MOST_RECENT"

today = date.today()

for i in range(0, len(skus)):

    table = wdata.add_sheet(models[i])
    # header = [u'reviewer', u'reviewTitle', u'submissionTime', u'review', u'rate']
    row_num = 0
    driver.get(baseURL + str(skus[i]) + apiKey + params)
    print(baseURL + str(skus[i]) + apiKey + params)

    rating = driver.find_element_by_xpath("//span[@class='overall-rating']").text
    print("rating: " + rating)
    table.write(row_num , 4, rating)

    reviews = driver.find_elements_by_xpath("//li[@class='review-item']")
    for review, nextFlag in lookAhead(reviews):
        submission = review.find_element_by_xpath(".//time[@class='submission-date']")
        submission_time = submission.get_attribute("title")
        year = int(submission_time.split(" ")[2])
        day = int(submission_time.split(" ")[1][:-1])
        month = monthDic[submission_time.split(" ")[0]]
        d = date(year, month, day)
        print(d)
        if d > today - timedelta(days = 7):
            # print("add")
            name = review.find_element_by_xpath(".//div['review-item-header hidden-xs hidden-sm col-md-4 col-lg-3']//button/div/strong").text
            print(name)
            title = review.find_element_by_xpath(".//h4[@class='review-title c-section-title heading-5 v-fw-medium  ']").text
            review_text = review.find_element_by_xpath(".//div[@class='ugc-review-body body-copy-lg']/p").text
            rating = review.find_element_by_xpath(".//div[@class='c-ratings-reviews-v2 v-small']/p").text
                
            table.write(row_num + 1, 0, name)
            table.write(row_num + 1, 1, title)
            table.write(row_num + 1, 2, d)
            table.write(row_num + 1, 3, review_text)
            table.write(row_num + 1, 4, rating.split(" ")[1])
            row_num = row_num + 1
        else:
             break
        

        if not nextFlag:
            next = driver.find_elements_by_link_text('next Page')
            URL = next[0].get_attribute('href')
            print(URL)
            driver.get(URL)
            reviews = driver.find_elements_by_xpath("//li[@class='review-item']")



driver.close()
wdata.save('BestBuy.xls')