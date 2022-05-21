import pandas as pd
from tqdm import tqdm
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from time import sleep
from random import randint



def accept_cookie(driver):
     sleep(6)
     driver.find_element(By.XPATH,'//*[@aria-label="Accept our cookies"]').click()
     return driver
 
def get_driver(URL):
    options = webdriver.ChromeOptions()
    options.headless = False
    DRIVER_PATH = r'C:\Users\PATH\Documents\chromedriver\chromedriver.exe'
    driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
    driver.get(URL)
    if driver.find_element(By.XPATH,'.//div[contains(@class, "cookie-notification__header")]'):
        accept_cookie(driver)
    return driver


def get_product_categories(driver, searched_category):
    parent_elem = driver.find_element(By.XPATH,'.//li[contains(@data-category-group, "{}")]'.format(searched_category))
    child_elements = parent_elem.find_elements(By.XPATH, './/div/div/ul/li/span/a')
    global product_category_titles
    product_category_titles = []
    for child in child_elements:
        product_category_titles.append(child.get_attribute('href'))
    if product_category_titles:
        return product_category_titles
    else:
        pass 

def get_amount_of_pages(driver):
    try:
        if driver.find_element(By.XPATH,'//a[contains(@aria-label, "Go to the next page")]'):
            amount_of_pages = driver.find_elements(By.XPATH, '//a[contains(@aria-label, "Go to page ")]')[-1].text.strip()
            return int(amount_of_pages)
            print("returned {} of pages".format(amount_of_pages))
    except:
        return 1

def get_product_cards(driver):
    product_cards = driver.find_elements(By.XPATH,'//div[contains(@class, "product-card__details product-card__custom-breakpoint js-product-details")]')
    return product_cards


def get_product_url(product_card):
    product_url_temp = product_card.find_element(By.XPATH, './/div/a')
    product_url = product_url_temp.get_attribute('href')
    return product_url


def readReview(review):
    sleep_for_random_interval()
    check_for_specialist_rating = review.find_elements(By.XPATH,'.//span[contains(@class, "icon-with-text__text")]')
    if check_for_specialist_rating:
        if check_for_specialist_rating[0].text.strip() == "Our expert review":
            return '0', 'expert review', ['expert review'], 'expert review'
    rating_score = review.find_element(By.XPATH,'.//span[contains(@class, "review-rating__reviews")]').text.strip()
    review_title = review.find_element(By.XPATH,'.//strong[contains(@class, "reviews__item-title")]').text.strip()
    review_content_procons_temp = review.find_elements(By.XPATH,'.//span[contains(@class, "icon-with-text__text")]')
    list_of_procons = []
    for x in review_content_procons_temp:
        list_of_procons.append(x.text.strip())
    review_content = review.find_element(By.XPATH,'.//div[contains(@class, "curtain__content-inner-wrapper")]').text.strip()
    return rating_score, review_title, list_of_procons, review_content

def amountOfReviewPages(product_review_amount):
    if product_review_amount <= 15:
        return 1
    check = int(round((product_review_amount / 10) - 1, 0))
    if check >= 7:
        return 7
    return int(round((product_review_amount / 10) - 1, 0))
    

def get_product_details(driver_category, product_category, url_product):
    global review_df_final
    review_df_final = pd.DataFrame()
    sleep_for_random_interval()
    general_product_page = driver_category.find_element(by=By.CLASS_NAME, value="product-page")
    product_name = general_product_page.find_element(By.XPATH,'.//h1[contains(@class, "js-product-name")]').text.strip()
    product_price = general_product_page.find_element(By.XPATH,'.//strong[contains(@class, "sales-price__current")]').text.strip()
    driver_category.implicitly_wait(3)
    no_reviews_check = general_product_page.find_element(By.XPATH,'.//span[contains(@class, "review-rating__reviews")]').text.strip()
    if no_reviews_check[0] == "0":
        return review_df_final
    driver_category.find_element(By.CSS_SELECTOR, ".call-to-action.js-review-entrance.call-to-action__link").click()
    product_review_amount_string = driver_category.find_element(By.XPATH,'.//div[contains(@class, "review-rating__count")]').text.strip()
    product_review_amount = int(product_review_amount_string.split( )[2])
    product_review_pages = amountOfReviewPages(product_review_amount)
    general_review_flex_container = driver_category.find_element(By.CSS_SELECTOR, '.review-list-container.js-review-list-container')
    
    for review_page in range(0, product_review_pages):
    #for review_page in range(0, 1):
        sleep_for_random_interval()
        print("Scanning review page {}/{} for product {}".format(review_page,product_review_pages,product_name))
        reviews_list = general_review_flex_container.find_elements(By.CSS_SELECTOR, '.gap-x--4.gap-y--3.reviews__content-wrapper')
        for review in reviews_list:
            review_read_before_df = readReview(review)
            review_read_df = pd.DataFrame(review_read_before_df).transpose().reset_index(drop=True)
            review_df_final = pd.concat([review_df_final, review_read_df], axis=0)
            print(review_df_final)
        if product_review_pages > 1:
            try:
                general_review_flex_container.find_element(By.XPATH,'//*[@aria-label="Go to the next page"]').click()
            except:
                pass
    review_df_final['productName'] = product_name
    review_df_final['productCategory'] = product_category
    review_df_final['productPrice'] = product_price
    review_df_final['productURL'] = url_product
    return review_df_final


def sleep_for_random_interval():
    return sleep(randint(1,5))

def dataframe_to_excel(dataframe):
    dataframe.to_excel(r'C:PATH{}_coolblue_raw_data_{}.xlsx'.format(datetime.now().strftime("%Y%m%d"), searched_category_file_name.lower()), index=False, header=True)

def run_script(general_url_website, searched_category):
    global dataframe
    dataframe = pd.DataFrame()
    driver = get_driver(general_url_website)
    for url in get_product_categories(driver, searched_category): #not a big deal, just to put in categorisation in df
        print("printing this url : {}".format(url))
        product_category = url.split("/", 3)[-1]
        print(product_category)
        driver_category = get_driver(url+"/filter")
        for page in tqdm(range(0, get_amount_of_pages(driver_category))):
            url_list_products = []
            driver_category.get(url+"/filter/?page={}".format(page))
            product_cards = get_product_cards(driver_category)
            for product_card in product_cards:
                url_list_products.append(get_product_url(product_card))
            for url_product in url_list_products:
                print("checking the following url : {}".format(url_product))
                driver_category.execute_script("window.open('{}')".format(url_product))
                driver_category.implicitly_wait(1)
                driver_category.switch_to.window(driver_category.window_handles[1])
                driver_category.implicitly_wait(2)
                product_details = get_product_details(driver_category, product_category, url_product)
                driver_category.close()
                driver_category.switch_to.window(driver_category.window_handles[0])
                driver_category.implicitly_wait(2)
                dataframe = pd.concat([dataframe, product_details], axis=0)
                sleep_for_random_interval()
                
                  
        driver_category.quit()
    driver.quit()
    
    dataframe = dataframe.rename(columns={0: "productName", 1: "ratingScore", 2: "reviewTitle", 3: "proAndCon"})
    dataframe["productClass"] = searched_category.lower()
    dataframe["scrapeDate"] = datetime.now()
    dataframe_to_excel(dataframe)

    
if __name__ == '__main__':
    categories_to_search = ["Kitchen"]
    for category in categories_to_search:
        searched_category = category
        searched_category_file_name = category.replace(" ", "")
        run_script('https://www.coolblue.nl/en/?pagina={}', searched_category)
