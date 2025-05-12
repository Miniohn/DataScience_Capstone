# import packages
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import time
import pandas as pd
from datetime import date

## Enter WhatsAPP
# source : https://youtu.be/FM8jYXYln70
# source : https://github.com/GabriellBP/whatsapp-web-scraping
# reddit : https://www.reddit.com/r/learnpython/comments/s3ptpj/is_there_a_way_to_automate_whatsapp_web_with/
# https://youtu.be/H8jW8ibgzRI?feature=shared
# https://stackoverflow.com/questions/77045724/python-selenium-open-whatsapp-without-using-qr-code-every-time

# profile path : /Users/haley/Library/Application Support/Google/Chrome/Default
# user_data_dir = "/Users/haley/Library/Application Support/Google/Chrome"
options = Options()
options.add_argument("--user-data-dir=/Users/haley/Library/Application Support/Google/Chrome/Default")
# options.add_argument(f"--user-data-dir={user_data_dir}")
# options.add_argument("--profile-directory=Profile 1")
driver = webdriver.Chrome(options=options)

# driver = webdriver.Chrome()
driver.get("https://web.whatsapp.com/")

# scan the QR code

time.sleep(10)
# log in complete

# If you enter first time -> to remove modal, must click button
button_1 = driver.find_element(By.CSS_SELECTOR, "#app > div > span:nth-child(3) > div > div > div > div > div > div > div.x78zum5.x8hhl5t.x13a6bvl.xp4054r.xuxw1ft.x1cnzs8.xc73u3c.xx6bls6.x5ib6vp.x16w0wmm > div > button")
button_1.click()


# 1. scroll -> how many chats?

# 2. one by one -> 