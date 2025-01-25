# gt.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_google_trends():
    # Set up the webdriver
    driver = webdriver.Chrome()  # Replace with the browser of your choice

    # Navigate to the webpage
    url = "https://trends.google.com/trending?geo=CO&hl=es"  # Replace with the actual URL
    driver.get(url)

    # Wait for the feed-list-wrapper element to load
    feed_list_wrapper = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#trend-table > div.enOdEe-wZVHld-zg7Cn-haAclf > table > tbody:nth-child(3)"))
    )
    # print(feed_list_wrapper.get_attribute('outerHTML'))
    
    # Extract the trending search data from the feed-list-wrapper element
    trending_searches = []
    feed_items = feed_list_wrapper.find_elements(By.TAG_NAME, "tr")
    for feed_item in feed_items:
        index = feed_item.get_attribute("data-row-id")
        image_url = feed_item.find_element(By.CSS_SELECTOR, "td.enOdEe-wZVHld-aOtOmf.jvkLtd > div.mZ3RIc").get_attribute("data-image-url")
        image_source = feed_item.find_element(By.CSS_SELECTOR, "td.enOdEe-wZVHld-aOtOmf.jvkLtd > div.mZ3RIc").get_attribute("data-image-source")
        search_count = feed_item.find_element(By.CSS_SELECTOR, "td.enOdEe-wZVHld-aOtOmf.jvkLtd > div.Rz403 > div.UFqBx > div.qNpYPd").text
        title = feed_item.find_element(By.CSS_SELECTOR, "td.enOdEe-wZVHld-aOtOmf.jvkLtd > div.mZ3RIc").text
        trending_searches.append({
            "index": index,
            "image_url": image_url,
            "image_source": image_source,
            "search_count": search_count,
            "title": title
        })

    # Close the webdriver
    driver.quit()

    return trending_searches

def print_google_trends(trends):
    for trend in trends:
        print(f"{trend['index']} ")
        # print(f"Image URL: {trend['image_url']}")
        print(f"Image Source: {trend['image_source']}")
        print(f"Search Count: {trend['search_count']}")
        print(f"Title: {trend['title']}")
        print("------------")