import requests
import ctypes
import datetime
import time
from datetime import date

# Thanks u/OpenSourcerer420 for the idea!
# https://www.reddit.com/r/Python/comments/gfkuez/my_first_python_program_changes_my_desktop/

# settings.py
from dotenv import load_dotenv
load_dotenv()

import os
USER_PATH = os.path.expanduser('~')
PICTURE_PATH = USER_PATH + os.getenv("BACKGROUND_PICTURE_PATH")
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
CITY = os.getenv("HOME_TOWN")
REFRESH_SECONDS = int(os.getenv("BACKGROUND_REFRESH_SECONDS"))

SPI_SETDESKWALLPAPER = 20
# path_to_folder = r"C:\Users\Simon\Documents\Folders\Photos\Backgrounds\Python"

api_address='http://api.openweathermap.org/data/2.5/weather?appid='

weather_url = api_address + API_KEY + '&q=' + CITY

print("Started WeatherBackgroundChanger")
print("Picture Path:",PICTURE_PATH)
print("City:",CITY)

def main():
    while True:
        timestamp = datetime.datetime.now().time()
        start_night = datetime.time(18, 1)
        end_night = datetime.time(6, 0)
        start_day = datetime.time(6, 1)
        end_day = datetime.time(18, 0)
        json_data = requests.get(weather_url).json()
        print("data:",json_data)
        weather_state = json_data["weather"][0]["main"]

        # Sunday
        # if date.today().weekday() == 6:
        #     setBackground()
        #     print("Sunday")
        # Rain
        if weather_state == "Rain":
            print("Rain")
            setBackground("MilfordSoundPano2.jpg")
        # Thunderstorm
        elif weather_state == "Thunderstorm":
            print("Storm")
            setBackground("PancakeRocksPano.jpg")
        # Drizzle (nieseln)
        elif weather_state == "Drizzle":
            print("Drizzle")
            setBackground("MoerakiBouldersPano.jpg")

        # Night, clear
        elif weather_state == "Clear" and start_night <= timestamp or timestamp <= end_night:
            print("Night")
            setBackground("SingaporeNightPano.jpg")
        # Day, clear
        elif weather_state == "Clear" and start_day <= timestamp <= end_day:
            print("Day")
            setBackground("TaranakiEveningPano.jpg")
        # Clouds
        elif weather_state == "Clouds":
            print("Clouds")
            setBackground("TekapoPano.jpg")
        # Other
        else:
            print("Other")
            setBackground("LakeMathesonPano.jpg")
        
        print("Now sleeping " + str(REFRESH_SECONDS) + "s...")
        time.sleep(REFRESH_SECONDS)
        print("Looped")

def setBackground(pictureName):
    full_picture_path = PICTURE_PATH + pictureName
    # full_picture_path = r"C:\Users\mm\Pictures\DesktopWallpapers\SingaporeNightPano.jpg"
    print("Setting Background to:", full_picture_path)
    success = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, full_picture_path, 3)
    print("success:",success)
    if not success:
        print(ctypes.WinError())

main()
