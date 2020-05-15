import requests
import ctypes
import datetime
import time
from datetime import date
import schedule

import pystray
from pystray import MenuItem as item
from PIL import Image, ImageTk, ImageDraw
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

app = None
guiThread = None

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
    destroyGui()

# GUI ---------------------------------------------------
import tkinter as tk
from tkinter import filedialog
import threading

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        # Dark gray: #151819
        self.wallpaperDir = PICTURE_PATH

        self.master.title("WeatherDesk settings")
        self.master.iconphoto(False, tk.PhotoImage(file='WeatherDeskIcon.png'))
        # self.master.resizable(width=False, height=False)
        self.master.geometry('600x400')
        self.master['bg'] = "#151819"
        self.master.bind("<Escape>", lambda e: e.widget.quit())
        
        self.create_widgets()
        self.generateWallpaperThumbnails()

        # self.grid()
        self.pack()


    def create_widgets(self):
        self.quit = tk.Button(self, text="close", bg="white", fg="red",
                              command=self.master.destroy)
        self.quit.grid(row=0, column=1)
        # self.quit.pack()

        self.openWallpaperDir = tk.Button(self, text="Choose Wallpaper Folder", bg="white", fg="black",
                              command=self.chooseWallpaperDir)
        self.openWallpaperDir.grid(row=0, column=0)
        # self.openWallpaperDir.pack()

    def clearWallpaperCheckboxesAndThumbnails(self):
        self.wallpaperThumbnails = []
        if len(self.wallpaperLabels) > 0:
            for label in self.wallpaperLabels:
                label.destroy()
        if len(self.checkboxes) > 0:
            for check in self.checkboxes:
                check.destroy()

    def generateWallpaperThumbnails(self):
        if self.wallpaperDir is not None:
            self.wallpaperFiles = [f for f in os.listdir(self.wallpaperDir) if os.path.isfile(os.path.join(self.wallpaperDir, f)) and not f.endswith(".thumbnail") and f.find("Thumbnail") == -1]
            print("Found these Wallpapers:")
            self.checkboxes = []
            self.wallpaperThumbnails = []
            self.wallpaperLabels = []
            for (index, filename) in enumerate(self.wallpaperFiles):
                print(filename)
                filepath = os.path.join(self.wallpaperDir, filename)
                # Create thumbnail if none exists
                suffix = filename.split('.')[1]
                outfilename = filename.split('.')[0] + "Thumbnail." + suffix
                outfilepath = os.path.join(self.wallpaperDir, outfilename)
                thumbnailExists = True
                try:
                    Image.open(outfilepath)
                except FileNotFoundError:
                    thumbnailExists = False
                if not thumbnailExists:
                    print("Creating thumbnail for", filename)
                    try:
                        thumbnail = Image.open(filepath)
                        thumbnail.thumbnail((80, 80), Image.NEAREST)
                        thumbnail.save(outfilepath)
                    except:
                        print("could not create thumbnail for",filename)
                thumb = ImageTk.PhotoImage(Image.open(outfilepath))
                wallpaperLabel = tk.Label(self, image=thumb)
                wallpaperLabel.grid(row=index+1, column=1)
                # wallpaperLabel.pack(side = "bottom", fill = "both", expand = "yes")
                self.wallpaperLabels.append(wallpaperLabel)
                self.wallpaperThumbnails.append(thumb)
                checkbox = tk.Checkbutton(self, text=filename.split('.')[0])
                checkbox.grid(row=index+1, column=0)
                # checkbox.pack()
                self.checkboxes.append(checkbox)

    def chooseWallpaperDir(self):
        self.wallpaperDir = filedialog.askdirectory(title="Choose the folder which contain your Wallpapers",initialdir=os.path.join(USER_PATH,'Pictures'))
        print("Your Wallpaper directory now is:",self.wallpaperDir)
        PICTURE_PATH = self.wallpaperDir
        self.clearWallpaperCheckboxesAndThumbnails()
        self.generateWallpaperThumbnails()
            

def destroyGui():
    if guiThread is not None:
        app.destroy()
        guiThread.join()

def tkinterGui():
    global app
    root = tk.Tk()
    app = Application(master=root)
    root.mainloop()

def startGuiThread():
    global guiThread    
    guiThread = threading.Thread(target=tkinterGui)
    guiThread.start()
    # GUI.join()

# GUI END ---------------------------------------------------

# Tray Icon
icon = pystray.Icon("WeatherDeskTray", image, "WeatherDesk")
menu = (item('Settings', showSettings, default=True), item(getCurrentWeatherString, updateBackground), item('Refresh', updateBackground), item('Exit', exitProgram))
icon.menu = menu
icon.run(setupSchedule)

icon.stop()
schedule.clear()