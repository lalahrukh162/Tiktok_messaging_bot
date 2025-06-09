import time
import pandas as pd
import pickle
import os
import random
import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc


def sleeper():
    time.sleep(float("0." + random.choice("012") + random.choice("0123") + random.choice("0123456789")))

def get_driver(headless=False):
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=en-US")  
    return uc.Chrome(use_subprocess=True, options=options)


def load_csv(file):
    return pd.read_csv(file)


def login_tiktok(driver, username, password):
    cookies_file = f"cookies/{username}.pkl"

    driver.get("https://www.tiktok.com/login/phone-or-email/email")
    time.sleep(5)


    if os.path.exists(cookies_file):
        with open(cookies_file, "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(5)
        return True


    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email or username']"))).send_keys(username)
        sleeper()
        driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys(password)
        sleeper()
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(10)
    except:
        st.error("❌ Error: Login page not loaded correctly.")
        driver.quit()
        return False


    st.warning("🔄 Complete CAPTCHA verification if required...")
    input("Press ENTER after CAPTCHA verification...")


    os.makedirs("cookies", exist_ok=True)
    with open(cookies_file, "wb") as f:
        pickle.dump(driver.get_cookies(), f)

    return True

import random
import time
from selenium.webdriver.common.action_chains import ActionChains

def send_message(driver, recipient, message):
    driver.get(f"https://www.tiktok.com/@{recipient}")
    time.sleep(random.uniform(5, 8))  

    try:

        message_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div[2]/div[2]/a/button"))
        )
        message_button.click()
        time.sleep(random.uniform(3, 6))


        message_input_area = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div/div[2]/div[3]/div[4]/div"))
        )
        
        driver.execute_script("arguments[0].scrollIntoView();", message_input_area)
        time.sleep(random.uniform(1, 3))


        message_input_area.click()
        time.sleep(random.uniform(1, 2))
        message_input_area.click()
        time.sleep(random.uniform(1, 2))


        modified_message = randomize_message(message)


        actions = ActionChains(driver)
        for char in modified_message:
            actions.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))  
        actions.send_keys(Keys.ENTER)
        actions.perform()

        time.sleep(random.uniform(5, 10))

        st.success(f"✅ Message sent to {recipient}")

    except Exception as e:
        st.warning(f"⚠️ Failed to message {recipient}: {str(e)}")


def randomize_message(message):
    variations = [
        "Hey! 👋 " + message,
        "Hello! 😊 " + message,
        "Yo! 🚀 " + message,
        "Hii there! ✨ " + message,
        "Hey there! Hope you're doing well! " + message
    ]
    return random.choice(variations)




def process_account(account, users, message, headless):
    username, password = account['username'], account['password']
    driver = get_driver(headless)
    
    if not login_tiktok(driver, username, password):
        driver.quit()
        return

    for user in users:
        send_message(driver, user, message)

    driver.quit()


def start_messaging(accounts_file, users_file, message, headless):
    accounts = load_csv(accounts_file)
    users = load_csv(users_file)['username'].tolist()


    with ThreadPoolExecutor(max_workers=len(accounts)) as executor:
        executor.map(lambda account: process_account(account, users, message, headless), accounts.to_dict(orient='records'))

    st.success("✅ Messaging completed!")


def main():
    st.title("🚀 TikTok Mass Messaging Bot")

    accounts_file = st.file_uploader("📂 Upload Accounts CSV", type=["csv"])
    users_file = st.file_uploader("📂 Upload Usernames CSV", type=["csv"])
    message = st.text_area("💬 Enter Message")
    headless = st.checkbox("Enable Headless Mode (Run in Background)")

    if st.button("▶ Start Messaging"):
        if accounts_file and users_file and message:
            start_messaging(accounts_file, users_file, message, headless)
        else:
            st.error("⚠️ All fields are required!")

if __name__ == "__main__":
    main()
