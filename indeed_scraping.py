from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service

from bs4 import BeautifulSoup
import re
import sys
import requests


def setupDriver():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True) # So window doesn't close
    chrome_options.add_argument("--disable-single-click-autofill")
    chrome_options.add_argument("--ignore-autocomplete-on-autofill")
    s=Service('/Users/nadavskloot/Documents/GitHub/comp446/better_job_finder/chromedriver')
    driver = webdriver.Chrome(service=s, options=chrome_options) # add your path to chromedriver, mine is "/Users/nadavskloot/Documents/GitHub/comp446/better_job_finder/chromedriver"
    driver.get("https://www.indeed.com")
    return driver

def search(driver, kewWord, location):
    jobInput = driver.find_elements(By.ID, "text-input-what")[0]
    jobLocation = driver.find_elements(By.ID, "text-input-where")[0]
    # str(jobInput.is_displayed())
    jobInput.clear()
    jobInput.send_keys(kewWord)
    jobLocation.send_keys(Keys.TAB)
    while (jobLocation.get_attribute('value') != ""):
        jobLocation.send_keys(Keys.BACK_SPACE)
    jobLocation.send_keys(location)
    base = driver.find_element(By.TAG_NAME, "html")
    jobInput.send_keys(Keys.RETURN) # search

    
    waitForRefresh(driver, base)
    return driver
    

def scrape(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    jobTitles = soup.find_all("h2", attrs={'class': re.compile("jobTitle")})
    jobEmployers = soup.find_all("h4", attrs={'class': re.compile("base-search-card__subtitle")})
    jobLocations = soup.find_all("span", attrs={'class': re.compile("job-search-card__location")})
    

    # print(jobTitles)

    jobsDiv = soup.find_all("div", id=re.compile("mosaic-provider-jobcards"))[0]
    # print(jobsDiv.descendants)
    jobLinks = jobsDiv.find_all("a", href=True, recursive=False)
    print(len(jobLinks))

    jobs = {}
    for job in jobLinks:
        # print(job['href'])
        # base_url = "https://www.indeed.com" + job['href']
        # print(base_url)
        # r = requests.get(base_url)
        # soup = BeautifulSoup(r.content, 'html.parser')

        base_url = "https://www.indeed.com" + job['href']
        base = driver.find_element(By.TAG_NAME, "html")
        driver.get(base_url)
        
        waitForRefresh(driver, base)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # print(soup)
        jobTitle = soup.find("h1", attrs={'class': re.compile("jobsearch-JobInfoHeader-title")})
        jobEmployerDiv = soup.find("div", attrs={'class': re.compile("jobsearch-InlineCompanyRating")})
        jobEmployer = jobEmployerDiv.find(["a", "div"])
        jobLocation = jobEmployerDiv.next_sibling
        jobDescriptionDiv = soup.find("div", attrs={"class": re.compile("jobsearch-JobComponent-description")})
        detailsSection = jobDescriptionDiv.find("div", id="jobDetailsSection")
        salary = detailsSection.find(string=re.compile("$"))
        qualificationsSection = jobDescriptionDiv.find("div", id="qualificationsSection")

        print(jobTitle.string)
        print(jobEmployer.string)
        print(jobLocation.string)
        print(salary)
        print(jobDescriptionDiv.text)
        print()
        


    # print(jobTitles)

    # jobs = {}
    # for i in range(len(jobTitles)):
    #     for job in jobTitles[i].children:
    #         if job.string != "new":
    #             print(job.string)
    #     job = jobEmployers[i].text.strip() + " - " + jobTitles[i].text.strip()
    #     jobs[job] = {
    #         "title": jobTitles[i].text.strip(),
    #         "employer": jobEmployers[i].text.strip(),
    #         'location': jobLocations[i].text.strip()
    #     }
        
    # print(jobs)

def waitForRefresh(driver, base):
    try:
        element = WebDriverWait(driver, 20).until(
        EC.staleness_of(base)
    )
        return
    except TimeoutException:
        print("baddd")
        raise TimeoutError

if __name__ == "__main__":
    keyWord = sys.argv[1]
    location = sys.argv[2]
    driver = setupDriver()
    driver = search(driver, keyWord, location)
    scrape(driver)