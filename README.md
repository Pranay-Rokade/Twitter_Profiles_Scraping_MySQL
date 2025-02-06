# Twitter_Profiles_Scraping_MySQL

## Overview
This project scrapes Twitter profile data using Selenium and stores the extracted information in a MySQL database. The script fetches user details such as bio, followers, following count, location, and website from provided Twitter profile links.

## Project Structure
```
📂 Twitter-Scraper/
├── 📄 twitter.py                # Python script for scraping and database insertion
├── 📄 twitter_links.csv         # CSV file containing Twitter profile links
├── 🖼️ MySQL Database Result.png # Screenshot of stored data in MySQL
├── 📄 README.md                 # Project documentation
```

## Features
✅ Automates the scraping of Twitter profile information
✅ Uses Selenium WebDriver for browser automation
✅ Stores data in a MySQL database
✅ Handles missing elements gracefully
✅ Updates existing records to prevent duplicates

## Requirements
Before running the script, ensure you have the following installed:

- Python 3.x
- Selenium
- WebDriver Manager
- MySQL Server & MySQL Workbench
- dotenv (for environment variables)

### View Scraped Data in MySQL
```sql
USE twitter_scraper;
SELECT * FROM twitter_profiles;
```

## Expected Output
After running the script, the scraped data will be stored in MySQL, and you can view it using MySQL Workbench or via a SQL query. The `MySQL Database Result.png` file shows an example of the stored data.
