import csv
import time
import random
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# Set up Selenium WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


# Function to load the session cookie to avoid logging in each time
def load_session_cookie(driver, sessionid):
    driver.get("https://www.instagram.com")
    time.sleep(2)
    driver.add_cookie(
        {"name": "sessionid", "value": sessionid, "domain": ".instagram.com"}
    )
    driver.refresh()
    time.sleep(2)


# Function to scrape bio, followers, and mutuals
def scrape_bio_followers_mutuals(handle):
    profile_url = f"https://www.instagram.com/{handle}/"
    driver.get(profile_url)
    time.sleep(3)

    # Scrape bio
    try:
        bio = driver.find_element(
            By.XPATH,
            "//span[contains(@class, '_ap3a') and contains(@class, '_aaco') and contains(@class, '_aacu') and contains(@class, '_aacx') and contains(@class, '_aad7') and contains(@class, '_aade')]",
        ).text
    except:
        bio = "Bio not found"

    # Scrape followers count
    try:
        followers = driver.find_element(
            By.XPATH, "//a[contains(@href,'followers')]/span"
        ).get_attribute("title")
    except:
        followers = "Followers not found"

    # Scrape mutual followers
    try:
        mutuals_element = driver.find_element(
            By.XPATH,
            "//span[contains(@class, 'x1lliihq') and contains(text(), 'Followed by')]",
        )
        mutuals_text = mutuals_element.text
        if "+" in mutuals_text:
            handles_part = mutuals_text.split("Followed by ")[1].split(" +")[0]
            additional_count = int(mutuals_text.split("+")[1].split()[0])
            mutual_handles = handles_part + f" + {additional_count} more"
            mutual_count = handles_part.count(",") + 1 + additional_count
        else:
            mutual_handles = mutuals_text.split("Followed by ")[1]
            mutual_count = mutual_handles.count(",") + 1
    except:
        mutual_handles = "No mutuals found"
        mutual_count = 0

    return {
        "Handle": handle,
        "Bio": bio,
        "Followers Count": followers,
        "Mutuals": mutual_handles,
        "Mutuals Count": mutual_count,
    }


# Function to read handles from CSV
def read_handles_from_csv(filename):
    with open(filename, "r") as file:
        csv_reader = csv.reader(file)
        return [
            row[0] for row in csv_reader
        ]  # Assumes the handle is in the first column


# Function to write scraped data to a CSV file
def write_data_to_csv(data, output_filename="output.csv"):
    import os

    # Check if the file exists to determine whether to write the header
    file_exists = os.path.isfile(output_filename)

    with open(output_filename, "a", newline="") as file:
        writer = csv.writer(file)

        # Write the header only if the file does not already exist
        if not file_exists:
            writer.writerow(
                ["Handle", "Bio", "Followers Count", "Mutuals", "Mutuals Count"]
            )

        for entry in data:
            writer.writerow(
                [
                    entry["Handle"],
                    entry["Bio"],
                    entry["Followers Count"],
                    entry["Mutuals"],
                    entry["Mutuals Count"],
                ]
            )


# Function to scrape multiple profiles with rate limiting
def scrape_multiple_profiles(
    handles,
    output_csv="output.csv",
    delay_low=4,
    delay_high=8,
    batch_size_range=(50, 100),  # Randomized batch size range
    batch_pause_low=30,
    batch_pause_high=60,
    long_batch_threshold=2000,
    long_batch_pause_low=35 * 60,
    long_batch_pause_high=55 * 60,
):
    scraped_data = []
    count = 0
    current_batch_size = random.randint(*batch_size_range)  # Initial random batch size

    for handle in handles:
        profile_data = scrape_bio_followers_mutuals(handle)
        scraped_data.append(profile_data)
        print(f"Scraped data for {handle}: {profile_data}")

        count += 1

        # Check if we reached the current batch size
        if count % current_batch_size == 0:
            # Randomize batch pause
            batch_pause = random.uniform(batch_pause_low, batch_pause_high)
            print(
                f"Pausing for {batch_pause:.2f} seconds after processing {current_batch_size} accounts."
            )
            time.sleep(batch_pause)

            # Set a new random batch size for the next batch
            current_batch_size = random.randint(*batch_size_range)
            print(f"Next batch size will be {current_batch_size} accounts.")

        # Add another level of batching for every 2000 accounts
        if count % long_batch_threshold == 0:
            long_batch_pause = random.uniform(
                long_batch_pause_low, long_batch_pause_high
            )
            # Ensure it ends in a float (non-round) second
            long_batch_pause += random.uniform(0.01, 0.99)
            print(
                f"Pausing for {long_batch_pause:.2f} seconds after {long_batch_threshold} accounts."
            )
            time.sleep(long_batch_pause)

        # Random delay between individual scrapes
        delay = random.uniform(delay_low, delay_high)
        print(f"Waiting for {delay:.2f} seconds before scraping the next profile.")
        time.sleep(delay)

    write_data_to_csv(scraped_data, output_csv)
    print(f"Scraping completed. Data saved to {output_csv}")


# Main function to handle command-line arguments and initiate scraping
def main():
    parser = argparse.ArgumentParser(
        description="Scrape Instagram profiles for bio, followers count, and mutual followers."
    )
    parser.add_argument(
        "-f", "--file", help="Path to the input CSV file with Instagram handles."
    )
    parser.add_argument(
        "-l", "--list", help="Space-separated list of Instagram handles.", nargs="*"
    )
    args = parser.parse_args()

    # Determine handles from CSV or list
    if args.file:
        handles = read_handles_from_csv(args.file)
    elif args.list:
        handles = args.list
    else:
        print("Please provide either a CSV file or a list of handles.")
        return

    # Provide your session ID here (replace with actual sessionid value)
    sessionid = (
        "351984017%3AmguYVs1ZFmSgDd%3A21%3AAYclMNFTJ5FGrQqEbOqYykxmOMli1Lf5wbT1OVkS2pWS"
    )
    load_session_cookie(driver, sessionid)

    # Run the scraping with default delay and batch parameters
    scrape_multiple_profiles(handles)


# Entry point
if __name__ == "__main__":
    main()
    driver.quit()
