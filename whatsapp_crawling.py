# import packages
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

import time
import pandas as pd
from datetime import date

## Enter WhatsAPP
# source : https://youtu.be/FM8jYXYln70
driver = webdriver.Chrome()
driver.get("https://web.whatsapp.com")