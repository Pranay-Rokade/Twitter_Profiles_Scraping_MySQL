import time
import mysql.connector
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Database Configuration loaded from environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

def connect_db():
    """Connect to MySQL and create the database if not exists."""
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS twitter_scraper")
    cursor.close()
    conn.close()

    return mysql.connector.connect(**DB_CONFIG)

def create_table(conn):
    """Create table if it doesn't exist."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS twitter_profiles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(255) UNIQUE,
            bio TEXT,
            follower_count VARCHAR(50),
            following_count VARCHAR(50),
            location VARCHAR(255),
            website VARCHAR(255)
        )
    """)
    conn.commit()
    cursor.close()
    
def save_to_db(conn, url, profile_data):
    """Save scraped data to MySQL database."""
    cursor = conn.cursor()
    query = """
        INSERT INTO twitter_profiles (url, bio, follower_count, following_count, location, website)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            bio = VALUES(bio),
            follower_count = VALUES(follower_count),
            following_count = VALUES(following_count),
            location = VALUES(location),
            website = VALUES(website)
    """
    cursor.execute(query, (url, profile_data["Bio"], profile_data["Follower count"],
                           profile_data["Following count"], profile_data["Location"], profile_data["Website"]))
    conn.commit()
    cursor.close()

def load_links(file_path):
    """Load and process links from a file."""
    with open(file_path, 'r') as file:
        links = [line.strip().strip('"') for line in file.readlines()]
        return ["https://" + url if not url.startswith("http") else url for url in links]

def setup_driver():
    """Configure and initialize the WebDriver."""
    service = Service(GeckoDriverManager().install())
    firefox_options = Options()
    firefox_options.add_argument("--detach")
    return webdriver.Firefox(options=firefox_options, service=service)


def scrape_profile(driver, url):
    """Scrape profile information from a given URL."""
    driver.get(url)
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, './/div[@data-testid="UserName"]'))
        )
    except TimeoutException:
        print(f"Skipping {url}: Account not found.")
        return None
    
    driver.execute_script("window.stop();")
    
    data = {}
    
    try:
        data["Bio"] = driver.find_element(By.XPATH, './/div[@data-testid="UserDescription"]/span').text
    except NoSuchElementException:
        data["Bio"] = ""
    
    try:
        data["Following count"] = driver.find_element(By.XPATH, './/div[@class="css-175oi2r r-13awgt0 r-18u37iz r-1w6e6rj"]/div[1]/a/span[1]/span').text
        data["Follower count"] = driver.find_element(By.XPATH, './/div[@class="css-175oi2r r-13awgt0 r-18u37iz r-1w6e6rj"]/div[2]/a/span[1]/span').text
    except NoSuchElementException:
        data["Following count"] = data["Follower count"] = ""
    
    try:
        data["Location"] = driver.find_element(By.XPATH, './/span[@data-testid="UserLocation"]/span/span').text
    except NoSuchElementException:
        data["Location"] = ""
    
    try:
        data["Website"] = driver.find_element(By.XPATH, './/a[@data-testid="UserUrl"]').get_attribute('href')
    except NoSuchElementException:
        data["Website"] = ""
    
    return data
def main():
    """Main function to orchestrate scraping."""
    link_list = load_links("twitter_links.csv")
    driver = setup_driver()
    conn = connect_db()
    create_table(conn)

    for url in link_list:
        profile_data = scrape_profile(driver, url)
        if profile_data:
            save_to_db(conn, url, profile_data)
        time.sleep(5)

    driver.quit()
    conn.close()
    print("Scraping completed. Data saved to MySQL database.")

if __name__ == "__main__":
    main()