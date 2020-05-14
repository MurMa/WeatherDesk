import requests
import ctypes
import datetime
import time
from datetime import date
import schedule

import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import os
from dotenv import load_dotenv

# Thanks u/OpenSourcerer420 for the idea!
# https://www.reddit.com/r/Python/comments/gfkuez/my_first_python_program_changes_my_desktop/

# Configuration
load_dotenv()

USER_PATH = os.path.expanduser('~')
PICTURE_PATH = USER_PATH + os.getenv("BACKGROUND_PICTURE_PATH")
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
CITY = os.getenv("HOME_TOWN")
REFRESH_SECONDS = int(os.getenv("BACKGROUND_REFRESH_SECONDS"))
SPI_SETDESKWALLPAPER = 20

api_address='http://api.openweathermap.org/data/2.5/weather?appid='

weather_url = api_address + API_KEY + '&q=' + CITY
weather_state = "?"
showSettings = False

print("Started WeatherBackgroundChanger")
print("Picture Path:",PICTURE_PATH)
print("City:",CITY)
print("Refresh seconds:",REFRESH_SECONDS)

image = Image.open("WeatherDeskIcon.png")

def setupSchedule(icon):
    icon.visible = True
    updateBackground(icon)
    schedule.every(REFRESH_SECONDS).seconds.do(updateBackground, icon)
    runSchedule()

def runSchedule():
    while schedule.next_run() is not None:
        schedule.run_pending()

def updateBackground(icon):
    global weather_state
    print("Updating Background...")
    timestamp = datetime.datetime.now().time()
    start_night = datetime.time(18, 1)
    end_night = datetime.time(6, 0)
    start_day = datetime.time(6, 1)
    end_day = datetime.time(18, 0)
    json_data = requests.get(weather_url).json()
    print("data:",json_data)
    weather_state = json_data["weather"][0]["main"]
    icon_name = json_data["weather"][0]["icon"]

    icon.update_menu()
    image = Image.open("icons8/" + icon_name + ".png")
    icon.icon = image

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

def setBackground(pictureName):
    full_picture_path = PICTURE_PATH + pictureName
    # full_picture_path = r"C:\Users\mm\Pictures\DesktopWallpapers\SingaporeNightPano.jpg"
    print("Setting Background to:", full_picture_path)
    success = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, full_picture_path, 3)
    if not success:
        print(ctypes.WinError())

def getCurrentWeatherString(icon):
    return "Current: " + weather_state

def showSettings(icon):
    global showSettings
    print("Showing settings")
    startGuiThread()

def exitProgram():
    print("Exiting")
    schedule.clear()
    icon.stop()

# GUI ---------------------------------------------------
import tkinter as tk
import threading

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        # Dark gray: #151819

        self.master.title("WeatherDesk settings")
        self.master.iconphoto(False, tk.PhotoImage(file='WeatherDeskIcon.png'))
        # self.master.resizable(width=False, height=False)
        self.master.geometry('350x200')
        self.master['bg'] = "#151819"
        self.master.bind("<Escape>", lambda e: e.widget.quit())
        
        self.create_widgets()
        self.pack()

        # windowWidth = self.master.winfo_reqwidth()
        # windowHeight = self.master.winfo_reqheight()
        # print("Width",windowWidth,"Height",windowHeight)
        # Gets both half the screen width/height and window width/height
        # positionRight = int(self.master.winfo_screenwidth()/2 - windowWidth/2)
        # positionDown = int(self.master.winfo_screenheight()/2 - windowHeight/2)
        # self.master.geometry('+{}+{}'.format(positionRight, positionDown))


    def create_widgets(self):
        self.quit = tk.Button(self, text="QUIT", bg="white", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

def tkinterGui():
    root = tk.Tk()
    app = Application(master=root)
    root.mainloop()

def startGuiThread():    
    GUI = threading.Thread(target=tkinterGui)
    GUI.start()
    # GUI.join()

# GUI END ---------------------------------------------------

# Tray Icon
icon = pystray.Icon("WeatherDeskTray", image, "WeatherDesk")
menu = (item('Settings', showSettings, default=True), item(getCurrentWeatherString, updateBackground), item('Refresh', updateBackground), item('Exit', exitProgram))
icon.menu = menu
icon.run(setupSchedule)

icon.stop()
schedule.clear()