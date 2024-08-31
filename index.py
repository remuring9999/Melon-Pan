import Melon
import time
import asyncio
import pyautogui
import requests

from selenium import webdriver # 동적 사이트 수집
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By 


def now_playing_download(track_num=1):
    melon = Melon.Melon()
    if melon._is_opened():
        if asyncio.run(melon.get_session()):
            melon.download_song(track_num)
        else:
            print("Failed to get session")
    else:
        print("Melon is not opened")

def initWebdriver():
        chrome_options = Options()
        chrome_options.add_argument("--disable-default-app")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)        
        driver.get("https://member.melon.com/muid/web/login/login_inform.htm")
        return driver

                
def download_chart():
    driver = initWebdriver()
    print("Please login to Melon.")
    print("Awaiting Login ..")

    id = open("user.txt", "r").read().split("\n")[0].split("=")[1]
    pwd = open("user.txt", "r").read().split("\n")[1].split("=")[1]

    driver.find_element(By.CSS_SELECTOR, ".kakao").click() # 카카오 로그인

    time.sleep(2) # 팝업 대기

    driver.switch_to.window(driver.window_handles[-1]) # 팝업 창으로 전환

    id_input = driver.find_element(By.XPATH, '//*[@id="loginId--1"]')
    id_input.click()
    id_input.send_keys(id)

    pw_input = driver.find_element(By.XPATH, '//*[@id="password--2"]')
    pw_input.click()
    pw_input.send_keys(pwd)

    driver.find_element(By.CSS_SELECTOR, "button.btn_g:nth-child(1)").click() # 로그인

    driver.switch_to.window(driver.window_handles[0]) # 메인 창으로 전환

    time.sleep(2) # 로그인 대기

    if driver.current_url == "https://www.melon.com/index.htm":
        print("Login Failed!")
        exit()

    print("Login Successful!")

    driver.get("https://www.melon.com/chart/index.htm")

    print("Fetching Chart ..")

    chart_updated_date = driver.find_element(By.CSS_SELECTOR, "#conts > div.multi_row > div.calendar_prid.mt12 > span.yyyymmdd > span")
    chart_updated_time = driver.find_element(By.CSS_SELECTOR, "#conts > div.multi_row > div.calendar_prid.mt12 > span.hhmm > span")

    print("Fetched Chart")
    print(f"Chart Updated: {chart_updated_date.text}:{chart_updated_time.text}")

    data_song_no = []

    tr_elements = driver.find_elements(By.CSS_SELECTOR, "#frm > div > table > tbody > tr")
    for tr in tr_elements:
        data_song_no.append(tr.get_attribute("data-song-no"))

    # 전체듣기 클릭
    driver.find_element(By.CSS_SELECTOR, "#frm > div > div > button:nth-child(2)").click();
    time.sleep(2) # 팝업 대기
    print("애플리케이션 요청")
    time.sleep(2)
    pyautogui.press('tab', presses=2) # alert 확인
    pyautogui.press('enter') # alert 확인

    for song_no in data_song_no:
        time.sleep(5)
        print(f"Downloading {data_song_no.index(song_no) + 1}/{len(data_song_no)}")
        melon = Melon.Melon()
        asyncio.run(melon.get_session())
        melon.download_song(track_num=data_song_no.index(song_no) + 1)
        print("다운로드 완료")

        pyautogui.hotkey('ctrl', 'right') #다음곡 (ctrl + →)
        print("next")   

    driver.quit()

    print("Task All Done")
        

# 계속 반복
# while True:
#     track_num = int(input("Enter the track number: "))
#     now_playing_download(track_num)

download_chart()