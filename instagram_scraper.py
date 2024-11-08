import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Set up Selenium WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def load_session_cookie(driver, sessionid):
    # Open Instagram to establish the domain
    driver.get("https://www.instagram.com")
    time.sleep(2)

    # Add sessionid cookie
    driver.add_cookie(
        {"name": "sessionid", "value": sessionid, "domain": ".instagram.com"}
    )
    driver.refresh()  # Refresh to apply the cookie
    time.sleep(2)


def scrape_bio_followers_mutuals(handle):
    # Go to the Instagram profile URL
    profile_url = f"https://www.instagram.com/{handle}/"
    driver.get(profile_url)
    time.sleep(3)  # Wait for the page to load

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
        mutuals_text = driver.find_element(
            By.XPATH, "//div[contains(text(), 'Followed by')]"
        ).text

        # Determine the case for mutual followers
        if "+" in mutuals_text:
            # Case 1: More than 3 mutual followers, e.g., "Followed by serena.sx.l, aagam_vakil + 82 more"
            main_mutuals = mutuals_text.split("Followed by ")[1].split(" +")[0]
            mutual_count = int(mutuals_text.split(" +")[1].split()[0]) + len(
                main_mutuals.split(", ")
            )
            mutual_handles = (
                main_mutuals + f" + {mutual_count - len(main_mutuals.split(', '))} more"
            )
        elif "and" in mutuals_text:
            # Case 2: 1-3 mutual followers, e.g., "Followed by 57.nyc, zzzeesh, and johnnyhwin"
            mutual_handles = mutuals_text.split("Followed by ")[1]
            mutual_count = mutual_handles.count(",") + 1
        else:
            # Case 3: No mutual followers
            mutual_handles = "No mutuals found"
            mutual_count = 0

    except:
        mutual_handles = "Mutuals not found"
        mutual_count = 0

    return {
        "Handle": handle,
        "Bio": bio,
        "Followers Count": followers,
        "Mutuals": mutual_handles,
        "Mutuals Count": mutual_count,
    }


# Usage example
sessionid = "351984017%3AmguYVs1ZFmSgDd%3A21%3AAYcEyQLPkZeP980KD3fQIZ1-4shf6D-aBbXChCyNgSo6"  # Replace with the actual session ID from your cookies
load_session_cookie(driver, sessionid)

# Test with a profile handle
handle = "diplo"  # Replace with the Instagram handle you want to test
profile_data = scrape_bio_followers_mutuals(handle)
print(profile_data)

driver.quit()
