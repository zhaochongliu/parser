from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from datetime import date
from datetime import timedelta

productsURL = "https://www.amazon.com/stores/page/91BC1940-51D9-4456-8B19-34927EE38C9D?ingress=2&visitId=60312336-c246-4ca6-a222-1cfd6fea3d0b&ref_=bl_dp_s_web_6263534011"
baseURL = "https://www.amazon.com/"
urlAppend = "ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber=1"


driver  = webdriver.Chrome()
driver.get(productsURL)
productLinks = []
products = driver.find_elements_by_xpath("//li[@class='style__itemOuter__2dxew']")
monthDic = {"January":1, "February":2, "March":3, "April":4, "May":5, "June":6, "July":7, "August":8, "September":9, "October":10, "November":11, "December":12}
today = date.today()

def lookAhead(iterable):
    it = iter(iterable)
    last = next(it)
    for val in it:
        yield last, True
        last = val
    yield last, False


# get the product details page links
for product in products:
    productLink = product.find_element_by_xpath("./a").get_attribute("href")
    print(productLink)
    productLinks.append(productLink)

for productLink in productLinks:
    driver.get(productLink + "#customerReviews")
    try:

        # get the product review page link
        reviewLink = driver.find_element_by_xpath("//a[@class='a-link-emphasis a-text-bold']").get_attribute("href")
        mostRecent = reviewLink.split('ref')[0] + urlAppend
        print(mostRecent)
        driver.get(mostRecent)

        # get current rating of the product
        rating = driver.find_element_by_xpath("//div[@class='a-text-left a-fixed-left-grid-col reviewNumericalSummary celwidget a-col-left']//span[@class='a-size-medium a-color-base']").text
        print("rating: " + rating)


        # get reviews from the revew page
        reviews = driver.find_elements_by_xpath("//div[@class='a-section review aok-relative']")
        for reviewDiv, nextFlag in lookAhead(reviews):
            time = reviewDiv.find_element_by_xpath("./div/div/span").text.split("on ")[-1]
            print(time)
            year = int(time.split(" ")[-1])
            postDate = int(time.split(" ")[1][:-1])
            month = monthDic[time.split(" ")[0]]

            d = date(year, month, postDate)
            print(d)

            if d > today - timedelta(days = 7):
                name = reviewDiv.find_element_by_xpath(".//span[@class='a-profile-name']").text
                rate = reviewDiv.find_element_by_xpath(".//div[@class='a-section celwidget']/div/a[@class='a-link-normal']").get_attribute("title")
                ## todo: check if this is a critical review or a positive review
                title = reviewDiv.find_element_by_xpath(".//a[@data-hook='review-title']/span").text
                review = reviewDiv.find_element_by_xpath(".//div[@class='a-row a-spacing-small review-data']/span/span").text
                print("\n\nname: " + name + "\nrate: " + rate + "\ntitle: " + title + "\ntime: " + time + "\nreview: " + review)
            else:
                break
            if not nextFlag:
                nextPage = driver.find_element_by_xpath("//div[@class='a-form-actions a-spacing-top-extra-large']/span/div/ul/li[@class='a-last']/a").get_attribute('href')
                driver.get(nextPage)
                reviews = driver.find_elements_by_xpath("//div[@class='a-section review aok-relative']")

    except NoSuchElementException:
        pass

driver.close()