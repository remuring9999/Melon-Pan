# 어디까지나 재미로

import requests
import datetime
import asyncio
import eyed3
import time
from shazamio import Shazam
import math

from selenium import webdriver # 동적 사이트 수집
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By 
import pyautogui # 서드파티 로그인 보안정책 

class Melon:
    def __init__(self):
        self.content_length = 0
        self.content_range = 0
        self.session_name = ""
        self.session_artist = ""
        self.session_album = ""
        self.session_album_art = ""
        self.session_recording_date = ""
        self.driver = None
        self.shzam = Shazam()

    def _is_opened(self):
        try:
            response = requests.get("http://127.0.0.1:59152/", timeout=5)
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.RequestException:
            return False
        
    def _generate_timestamp(self):
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        second = datetime.datetime.now().second

        return f"{year}{month}{day}{hour}{minute}{second}000"
        
    async def get_session(self):
        try:
            response = requests.get(f"http://127.0.0.1:59152/streamSource?cId=4446485&bitrate=320&metaType=MP3&timestamp={self._generate_timestamp()}")
            if response.status_code == 206:
                song_result = await self.shzam.recognize(response.content)

                self.session_name = song_result['track']['title']
                self.session_artist = song_result['track']['subtitle']
                self.session_album_art = song_result['track']['images']['coverarthq']
                self.session_album = song_result['track']['sections'][0]['metadata'][0]['text']
                self.content_length = response.headers["content-length"]
                self.content_range = response.headers["content-range"]
                self.session_recording_date = song_result['track']['sections'][0]['metadata'][2]['text']

                print(f"Session Name: {self.session_name}")
                print(f"Session Artist: {self.session_artist}")
                print(f"Session Album Art: {self.session_album_art}")
                print(f"Session Album: {self.session_album}")
                print(f"Content Length: {self.content_length}")
                print(f"Content Range: {self.content_range}")

                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
        
    def download_song(self, track_num=1):
        if self.session_name == "":
            print("Session is not created.")
            return False
        try:
            total_size = int(self.content_range.split("/")[1])
            print(f"Total Size: {total_size} bytes ({total_size / 1048576} MB)")
            num_chunks = math.ceil(total_size / 1048576)
            print(f"Number of Chunks: {num_chunks}")
            headers = {}
            response = requests.get(f"http://127.0.0.1:59152/streamSource?cId=4446485&bitrate=320&metaType=MP3&timestamp={self._generate_timestamp()}")
            with open(f"MusicFolder/{self.session_artist}-{self.session_name}.mp3", "wb") as f:
                for chunk_num in range(num_chunks):
                    start_byte = chunk_num * 1048576
                    end_byte = min((chunk_num + 1) * 1048576 - 1, total_size - 1)
                    headers['Range'] = f'bytes={start_byte}-{end_byte}'
                    print(f"Downloading chunk {chunk_num + 1}/{num_chunks} ({start_byte}-{end_byte})")

                    response = requests.get(f"http://127.0.0.1:59152/streamSource?cId=4446485&bitrate=320&metaType=MP3&timestamp={self._generate_timestamp()}", headers=headers)

                    f.write(response.content)

                print(f"{self.session_name} has been downloaded successfully! ({num_chunks} chunks, {total_size / 1048576} MB)")

                print("Encoding ID3 Tags ..")

                audiofile = eyed3.load(f"MusicFolder/{self.session_artist}-{self.session_name}.mp3")
                audiofile.initTag(version=(2, 3, 0))
                audiofile.tag.artist = self.session_artist
                audiofile.tag.title = self.session_name
                audiofile.tag.album = self.session_album
                audiofile.tag.album_artist = self.session_artist
                audiofile.tag.recording_date = self.session_recording_date
                audiofile.tag.track_num = track_num
                audiofile.tag.images.set(3, requests.get(self.session_album_art).content, "image/jpeg", u"cover")
                audiofile.tag.save()

                print("Successfully encoded mp3 tags")

                print("Task All Done")

                return True
        except Exception as e:
            print(e)
            return False

if __name__ == "__main__":
    melon = Melon()
    if not melon._is_opened():
        print("Melon Player is not opened.")
        exit()

    asyncio.run(melon.get_session())
    # melon.download_song()
