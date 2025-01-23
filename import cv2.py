import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

PROFILE_DIR = "linkedin_profiles"
os.makedirs(PROFILE_DIR, exist_ok=True)

# LinkedIn credentials
LINKEDIN_EMAIL = "your email"  # Replace with your LinkedIn email
LINKEDIN_PASSWORD = "your password"        # Replace with your LinkedIn password

PROFILE_LINKS_FILE = "linkedin_profiles.txt"

SEARCH_QUERY = 'site:linkedin.com/in/ ("developer") (croatia")'


def scrape_google_for_profiles():
    """Scrape Google search results for LinkedIn profile links."""
    options = webdriver.ChromeOptions()
    service = Service("C:\\your\path\chromedriver.exe")  # Update path to ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.google.com/")

        try:
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept all')]"))
            )
            accept_button.click()
            print("Accepted Google cookie consent.")
        except Exception:
            print("No cookie consent dialog found.")

        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys(SEARCH_QUERY)
        search_box.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.yuRUbf a"))
        )

        profile_links = []
        results = driver.find_elements(By.CSS_SELECTOR, "div.yuRUbf a")
        for result in results:
            href = result.get_attribute("href")
            if "linkedin.com/in/" in href:
                profile_links.append(href)

        print(f"Found {len(profile_links)} LinkedIn profile links.")
        
        with open(PROFILE_LINKS_FILE, "w") as file:
            for link in profile_links:
                file.write(link + "\n")
        print(f"Saved LinkedIn profile links to {PROFILE_LINKS_FILE}.")
    finally:
        driver.quit()


def login_to_linkedin(driver):
    """Log in to LinkedIn using Selenium."""
    driver.get("https://www.linkedin.com/login")
    time.sleep(3)
    driver.find_element(By.ID, "username").send_keys(LINKEDIN_EMAIL)
    driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
    driver.find_element(By.ID, "password").submit()
    print("Logged in to LinkedIn.")
    time.sleep(5)  


def download_profile_picture(driver, profile_url, profile_name):
    """Download the profile picture from a LinkedIn profile."""
    try:
        driver.get(profile_url)
        time.sleep(5)  

        profile_image_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//img[contains(@class, 'profile-photo')] | //img[contains(@class, 'pv-top-card-profile-picture__image')]")
            )
        )
        image_url = profile_image_element.get_attribute("src")
        print(f"Found profile picture for {profile_name}: {image_url}")

        response = requests.get(image_url)
        response.raise_for_status() 
        image_path = os.path.join(PROFILE_DIR, f"{profile_name}.jpg")
        with open(image_path, "wb") as image_file:
            image_file.write(response.content)
        print(f"Saved profile picture: {image_path}")

    except Exception as e:
        print(f"Could not download profile picture for {profile_url}: {e}")


def process_profiles():
    """Process the LinkedIn profile links and download their pictures."""
    if not os.path.exists(PROFILE_LINKS_FILE):
        print(f"No file found: {PROFILE_LINKS_FILE}")
        return

    with open(PROFILE_LINKS_FILE, "r") as file:
        profile_links = [line.strip() for line in file.readlines()]

    if not profile_links:
        print("No LinkedIn profile links found in the file.")
        return

    options = webdriver.ChromeOptions()
    service = Service("C:\\Windows\\chromedriver.exe")  # Update path to ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)

    try:
        login_to_linkedin(driver)

        for idx, profile_url in enumerate(profile_links):
            print(f"Processing profile {idx + 1}/{len(profile_links)}: {profile_url}")

            profile_name = profile_url.split("/")[-1]  
            download_profile_picture(driver, profile_url, profile_name)

    finally:
        driver.quit()
        print("Finished processing profiles.")


if __name__ == "__main__":
    print("Scraping Google for LinkedIn profile links...")
    scrape_google_for_profiles()

    print("Processing LinkedIn profiles...")
    process_profiles()
