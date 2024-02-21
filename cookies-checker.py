import os
import sys
import asyncio
import aiohttp

config = {
    "netflix": {
        "url": "https://www.netflix.com/",
        "domain": ".netflix.com",
        "directory": "./netflix-cookies",
        "login_indicator": [
            "list-profiles",
            "watching?",
            "notifications-menu",
            "Sign out of Netflix",
        ],
    },
}


async def check_cookies(url, cookies, login_indicator):
    jar = aiohttp.CookieJar(unsafe=False)
    async with aiohttp.ClientSession(cookie_jar=jar) as session:
        for cookie in cookies:
            session.cookie_jar.update_cookies({cookie['name']: cookie['value']})
        async with session.get(url) as response:
            text = await response.text()
            for indicator in login_indicator:
                if indicator in text:
                    return "working"
            return "not_working"


def parse_cookie_file(file_path, domain):
    cookies = []
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                print(f"Skipping line: {file_path}")
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
                'name': name,
                'domain': domain,
                'path': path,
                'secure': secure,
                'flag': flag,
                'expiration': expiration,
                'value': value
            }

            cookies.append(cookie)
    except Exception as e:
        print(f"An error occurred while parsing the cookie file: {e}")

    return cookies


def cookies_jar(cookies):
    jar = aiohttp.CookieJar(unsafe=False)
    for cookie in cookies:
        jar.update_cookies(cookie)
    return jar


async def main():
    if len(sys.argv) == 1:
        netflix_config = config['netflix']
        cookie_directory = netflix_config['directory']
        url = netflix_config['url']
        domain = netflix_config['domain']
        login_indicator = netflix_config['login_indicator']
    elif len(sys.argv) == 2:
        required_config = config[sys.argv[1]]
        cookie_directory = required_config['directory']
        url = required_config['url']
        domain = required_config['domain']
        login_indicator = required_config['login_indicator']
    elif len(sys.argv) == 3:
        required_config = config[sys.argv[1]]
        cookie_directory = sys.argv[2]
        url = required_config['url']
        domain = required_config['domain']
        login_indicator = required_config['login_indicator']

    cookie_files = os.listdir(cookie_directory)

    for i, cookie_file in enumerate(cookie_files):
        cookie_file_path = os.path.join(cookie_directory, cookie_file)
        cookies = parse_cookie_file(cookie_file_path, domain)
        result = await check_cookies(url, cookies, login_indicator)

        if result == "working":
            if cookie_file.startswith("working"):
                new_file_name = cookie_file
            else:
                new_file_name = f"working_{i+1}.txt"
            new_file_path = os.path.join(cookie_directory, new_file_name)
            os.rename(cookie_file_path, new_file_path)
            print(
                f"Cookie file '{cookie_file}' is {result}. Renamed to '{new_file_name}'."
            )
        else:
            os.remove(cookie_file_path)
            print(f"Cookie file '{cookie_file}' is {result}. Removed.")

if __name__ == "__main__":
    asyncio.run(main())
