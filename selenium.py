from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import os
import time

def click_social_button(driver, icon_class, network_name):
    """Helper function to click social media buttons"""
    try:
        print(f"Looking for {network_name} button...")
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                f"//div[contains(@class, 'flex-grow-0')]//i[contains(@class, 'fa-{icon_class}')]/ancestor::div[contains(@class, 'cursor-pointer')]"
            ))
        )
        
        if "opacity-50" in button.get_attribute("class"):
            print(f"{network_name} button appears disabled. Skipping click.")
            return
        
        print(f"Scrolling into view for {network_name} button...")
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(1)
        
        print(f"Hovering over and clicking {network_name} button...")
        action = ActionChains(driver)
        action.move_to_element(button).click(button).perform()
        time.sleep(1)
        
    except Exception as e:
        print(f"Error clicking {network_name} button: {str(e)}")

def test_metricool_login():
    load_dotenv()
    email = os.getenv('METRICOOL_EMAIL')
    password = os.getenv('METRICOOL_PASSWORD')
    
    if not email or not password:
        print("Error: Please set METRICOOL_EMAIL and METRICOOL_PASSWORD in your .env file")
        return False
    
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print("Navigating to Metricool homepage...")
        driver.get("https://metricool.com/")
        
        print("Looking for login button...")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "cta-blanco-login"))
        )
        login_button.click()
        
        time.sleep(3)
        
        print(f"Current URL: {driver.current_url}")
        
        email_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "j_username"))
        )
        email_input.clear()
        email_input.send_keys(email)
        
        password_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "j_password"))
        )
        password_input.clear()
        password_input.send_keys(password)
        
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "loginFormSubmit"))
        )
        submit_button.click()
        
        planner_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/planner'] .fa-calendar-days"))
        )
        planner_button.click()
        
        time.sleep(10)
        
        create_post_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.v-btn.primary .fa-plus"))
        )
        create_post_button.click()
        
        time.sleep(7)
        
        content_editor = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.editor-box[contenteditable='true']"))
        )
        driver.execute_script("arguments[0].innerHTML = 'hola'", content_editor)
        time.sleep(2)
        
        social_networks = [
            ('x-twitter', 'Twitter'),
            ('facebook', 'Facebook'),
            ('linkedin', 'LinkedIn')
        ]
        
        for icon_class, network_name in social_networks:
            try:
                click_social_button(driver, icon_class, network_name)
            except Exception as e:
                print(f"Error with {network_name}: {str(e)}")
                continue
        
        print("All social media buttons processed! Keeping browser open...")
        
        while True:
            time.sleep(1)
            
    except TimeoutException as e:
        print(f"Timeout error: Element not found - {str(e)}")
        return False
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Closing browser...")
        driver.quit()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    test_metricool_login()
