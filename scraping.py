# Dependencies
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

def scrape_all():
   # Initiate headless driver for deployment
   browser = Browser("chrome", executable_path="chromedriver", headless=True)

   news_title, news_paragraph = mars_news(browser)

   # Run all scraping function and store results in dictionary
   data = {
       "news_title": news_title,
       "news_paragraph": news_paragraph,
       "featured_image": featured_image(browser),
       "facts": mars_facts(),
       "hemispheres": hemispheres(browser),
       "last_modified": dt.datetime.now()
   }
   # stop webdriver and return data
   browser.quit()
   return data

## Nasa Mars article scraping
def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # try/except for error handling
    try:
        # Scrape the title of the first article
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        # Use parent elememt to find first 'a' tag and save it
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None
    return news_title, news_p

## Nasa JPL Image Scraping
def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()
    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # try/except error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

# Mars facts scraping
def mars_facts():
    # try/except error handling
    try:
        # use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None

    # assign columns and set index
    df.columns = ['Description','Mars']
    df.set_index('Description', inplace=True)
    # convert df into html format, add bootstrap
    return df.to_html(classes="table table-bordered table-condensed table-hover")

def hemispheres(browser):

    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul li", wait_time=1)

    # Create list to hold the url and title list of dicts.
    hemisphere_image_urls = []

    # Parse the HTML
    html = browser.html
    mhemi_list = soup(html, 'html.parser')
    # find the list of results
    items = mhemi_list.find_all('div', class_='item')

    base_part_url = 'https://astrogeology.usgs.gov'

    for item in items:
        url = item.find("a")['href']
        browser.visit(base_part_url+url)
        # Parse individual hemi page
        hemi_item_html = browser.html
        hemi_soup = soup(hemi_item_html, 'html.parser')
        # Scrape title of hemi
        title = hemi_soup.find('h2', class_ = 'title').text
        # Scrape URL of JPG image
        downloads = hemi_soup.find('div', class_ = 'downloads')
        image_url = downloads.find('a')['href']
        # append dict to empty list
        hemisphere_image_urls.append({"title": title, "img_url": image_url})

    return hemisphere_image_urls

if __name__ == "__main__":
    # if running as script, print scraped data
    print(scrape_all()