import pyttsx3
import speech_recognition as sr
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import webbrowser
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Initialize pyttsx3
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Simulated caregiver database
caregivers = [
    {"name": "John Doe", "specialty": "General Care", "phone": "123-456-7890"},
    {"name": "Jane Smith", "specialty": "Elder Care", "phone": "234-567-8901"},
    {"name": "Mike Johnson", "specialty": "Physical Therapy", "phone": "345-678-9012"}
]

# Function to make the assistant speak
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

# Function to take voice commands from the user
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        r.pause_threshold = 0.5
        print("Listening...")
        audio = r.listen(source)
    try:
        print('Recognizing...')
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception as e:
        print(e)
        print("Unable to recognize your voice.")
        speak("Unable to recognize your voice.")
        return "None"
    return query

# Function to handle user commands
def handleCommand():
    query = takeCommand().lower()
    if 'play music' in query:
        speak('What song would you like to play?')
        song = takeCommand()
        play_youtube_music(song)
    elif 'search the web for' in query:
        search_query = query.replace('search the web for', '').strip()
        speak(f"Searching the web for {search_query}")
        search_internet(search_query)
    elif 'login' in query:
        login_to_site()
    elif 'caregiver' in query:
        show_caregivers()
    else:
        speak("I'm sorry, I didn't understand that command.")

# Function to play music from YouTube
def play_youtube_music(song):
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        
        driver.get('https://www.youtube.com')
        
        search_box = driver.find_element(By.NAME, 'search_query')
        search_box.send_keys(song)
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(2)
        
        # Click on the first video
        first_video = driver.find_element(By.CSS_SELECTOR, '#contents ytd-video-renderer')
        first_video.click()
        
        speak(f"Now playing {song} on YouTube")
    except Exception as e:
        print(f"Error playing music: {e}")
        speak("Opening YouTube in your default browser.")
        webbrowser.open(f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}")

# Function to search the web
def search_internet(query):
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        
        driver.get('https://www.google.com')

        search_box = driver.find_element(By.NAME, 'q')
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        time.sleep(3)

        results = driver.find_elements(By.CSS_SELECTOR, 'h3')
        
        if results:
            speak(f"I found some results for {query}. Here are the top results:")
            for result in results[:3]:
                speak(result.text)
        else:
            speak(f"Sorry, I couldn't find any results for {query}.")
        
        driver.quit()
    except Exception as e:
        print(f"Error searching the web: {e}")
        speak("Opening Google in your default browser.")
        webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")

# Function to login to a site using voice as password
def login_to_site():
    enrolled_password = enroll_voice_password()
    if enrolled_password:
        compare_passwords(enrolled_password)

# Function to capture and enroll the voice password as text
def enroll_voice_password():
    speak("Please say your password.")
    password = takeCommand().lower()
    print(f"Password enrolled: {password}")
    return password

# Function to capture the voice for authentication
def capture_voice_for_authentication():
    speak("Please say your password for authentication.")
    return takeCommand().lower()

# Function to compare the enrolled password with the spoken password
def compare_passwords(enrolled_password):
    spoken_password = capture_voice_for_authentication()
    
    if spoken_password and spoken_password == enrolled_password:
        speak("Password matched.")
        speak("Login access granted")
    else:
        speak("Password does not match.")

# Function to show available caregivers
def show_caregivers():
    caregiver_window = tk.Toplevel(root)
    caregiver_window.title("Available Caregivers")
    caregiver_window.geometry("400x300")

    tree = ttk.Treeview(caregiver_window, columns=("Name", "Specialty", "Phone"), show="headings")
    tree.heading("Name", text="Name")
    tree.heading("Specialty", text="Specialty")
    tree.heading("Phone", text="Phone")

    for caregiver in caregivers:
        tree.insert("", "end", values=(caregiver["name"], caregiver["specialty"], caregiver["phone"]))

    tree.pack(expand=True, fill="both")

    def dial_caregiver():
        selected_item = tree.selection()[0]
        caregiver = tree.item(selected_item)["values"]
        speak(f"Dialing {caregiver[0]} at {caregiver[2]}")
        messagebox.showinfo("Dialing", f"Dialing {caregiver[0]} at {caregiver[2]}")

    dial_button = ttk.Button(caregiver_window, text="Dial Selected Caregiver", command=dial_caregiver)
    dial_button.pack(pady=10)

# GUI setup
root = tk.Tk()
root.title("Virtual Assistant")
root.geometry("300x200")

label = tk.Label(root, text="Virtual Assistant")
label.pack(pady=10)

start_button = ttk.Button(root, text="Start Listening", command=handleCommand)
start_button.pack(pady=10)

caregiver_button = ttk.Button(root, text="Show Caregivers", command=show_caregivers)
caregiver_button.pack(pady=10)

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == '__main__':
    speak("Hello, I'm your virtual assistant. How can I help you?")
    root.mainloop()