from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup
import time
import re
import sys



def setupDriver():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True) # So window doesn't close
    chrome_options.add_argument("--disable-single-click-autofill")
    driver = webdriver.Chrome("/Users/nadavskloot/Documents/GitHub/comp446/better_job_finder/chromedriver", options=chrome_options) # add your path to chromedriver, mine is "/Users/nadavskloot/Documents/GitHub/comp446/better_job_finder/chromedriver"
    driver.get("https://www.glassdoor.com/Search/")
    #cookie for username: rroczbikpplzvhotou@mrvpt.com, pass: hebedebe
    # cookie = {'name': "li_at",'value':"AQEDATiE-woDvY3iAAABfRYyfewAAAF9Oj8B7E4AySbBRJeEri4Uig-2B1hlS4dhO7btpUwcnJljINARdtGB6IUdmWiWhDxpSWc0P9rhH5wlCx_2ugoDz0lvQumpl-gOuHVp-7uBGeYDhEkwXVi9ETBn"}
    # driver.add_cookie(cookie)
    return driver

def search(driver, kewWord, location):
    jobInput = driver.find_elements(By.ID, "sc.keyword")[0]
    jobLocation = driver.find_elements(By.ID, "sc.location")[0]
    # str(jobInput.is_displayed())
    jobInput.clear()
    jobInput.send_keys(kewWord + " Jobs")
    jobLocation.clear()
    jobLocation.send_keys(location)
    jobInput.send_keys(Keys.RETURN) # search

    # time.sleep(10)
    base = driver.find_element_by_tag_name("html")
    try:
        element = WebDriverWait(driver, 1).until(
        EC.staleness_of(base)
    )
        return driver.page_source
    except TimeoutException:
        print("baddd")

def scrape(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')

    # jobPosts = soup.find_all("a", attrs={'class': re.compile("job-tile")})
    jobTitles = soup.find_all("p", attrs={'class': re.compile("css-forujw")})
    jobEmployers = soup.find_all("p", attrs={'class': re.compile("css-1xznj1f")})
    jobLocations = soup.find_all("p", attrs={'class': re.compile("css-56kyx5 small")})
    

    # print(jobPosts)
    # print(jobTitles)
    # print(jobEmployers)
    # print(jobLocations)

    jobs = {}
    for i in range(len(jobTitles)):
        job = jobEmployers[i].text.strip() + " - " + jobTitles[i].text.strip()
        jobs[job] = {
            "title": jobTitles[i].text.strip(),
            "employer": jobEmployers[i].text.strip(),
            'location': jobLocations[i].text.strip()
        }
        
    print()
    print(jobs)


if __name__ == "__main__":
    keyWord = sys.argv[1]
    location = sys.argv[2]
    driver = setupDriver()
    page_source = search(driver, keyWord, location)
    scrape(page_source)
