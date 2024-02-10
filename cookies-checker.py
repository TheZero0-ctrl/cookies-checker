import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By

config = {
    "netflix": {
        "url": "https://www.netflix.com/",
        "domain": ".netflix.com",
        "directory": "./netflix-cookies",
        "className": "default-ltr-cache-1clcoym"
    },
}


def check_cookies(cookies):
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    driver.get(url)

    # Add cookies
    for cookie in cookies:
        driver.add_cookie(cookie)

    # Check if logged in
    driver.get(url)
    log_in = driver.find_elements(By.CLASS_NAME, className)
    if len(log_in) == 0:
        result = "working"
    else:
        result = "not_working"

    # Close the browser
    driver.quit()

    return result


def isLoggedIn(driver):
    try:
        driver.find_element_by_xpath('//*[@id="appMountPoint"]/div/div[3]/div/div/div[1]/form/button').click()
    except:
        return True
    return False


def parse_cookie_file(file_path):
    cookies = []
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            values = line.split('\t')

            if len(values) < 7:
                continue

            flag = values[1]
            path = values[2]
            secure = values[3]
            expiration = values[4]
            name = values[5]
            value = values[6]

            if flag == 'FALSE':
                flag = False
            else:
                flag = True

            if secure == 'FALSE':
                secure = False
            else:
                secure = True

            cookie = {
                'domain': domain,
                'flag': flag,
                'path': path,
                'secure': secure,
                'expiration': expiration,
                'name': name,
                'value': value
            }

            cookies.append(cookie)
    except Exception as e:
        print(f"An error occurred while parsing the cookie file: {e}")

    return cookies


if len(sys.argv) == 1:
    netflix_config = config['netflix']
    cookie_directory = netflix_config['directory']
    url = netflix_config['url']
    domain = netflix_config['domain']
    className = netflix_config['className']
elif len(sys.argv) == 2:
    required_config = config[sys.argv[1]]
    cookie_directory = required_config['directory']
    url = required_config['url']
    domain = required_config['domain']
    className = required_config['className']
elif len(sys.argv) == 3:
    required_config = config[sys.argv[1]]
    cookie_directory = sys.argv[2]
    url = required_config['url']
    domain = required_config['domain']
    className = required_config['className']

# Get the list of files in the directory
cookie_files = os.listdir(cookie_directory)


# Check each cookie file
for i, cookie_file in enumerate(cookie_files):
    cookie_file_path = os.path.join(cookie_directory, cookie_file)

    # Parse the cookies from the file
    cookies = parse_cookie_file(cookie_file_path)

    # Check the cookies and get the result
    result = check_cookies(cookies)

    if result == "working":
        result = "working"
        if cookie_file.startswith("working"):
            new_file_name = cookie_file
        else:
            new_file_name = f"working_{i+1}.txt"
        new_file_path = os.path.join(cookie_directory, new_file_name)

        os.rename(cookie_file_path, new_file_path)
        print(
            f"Cookie file '{cookie_file}' is {result}. Renamed to '{new_file_name}'.")
    else:
        os.remove(cookie_file_path)
        print(f"Cookie file '{cookie_file}' is {result}. Removed.")
