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
import africastalking  # For Africa's Talking SMS API

# Initialize pyttsx3
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Africa's Talking API credentials
username = "Kwepo"  # Replace with your Africa's Talking username
api_key = ""     # Replace with your Africa's Talking API key
africastalking.initialize(username, api_key)
sms = africastalking.SMS  # Initialize SMS service

# Simulated caregiver database
caregivers = [
    {"name": "John Doe", "specialty": "General Care", "phone": "+254714805460"},
    {"name": "Jane Smith", "specialty": "Elder Care", "phone": "+254799489045"},
    {"name": "Mike Johnson", "specialty": "Physical Therapy", "phone": "+254113015464"}
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

# Function to send SMS to the selected caregiver using Africa's Talking
def send_sms_to_caregiver(caregiver):
    phone_number = caregiver["phone"]
    speak(f"Sending SMS to {caregiver['name']} at {phone_number}")

    # SMS message content
    message = f"Hello {caregiver['name']}, you have been selected for a caregiving service by Liz Mwangi, Phone:+254714805460. Please respond if available."

    # Send SMS using Africa's Talking
    sender='AFTKNG'
    try:
        response = sms.send(message, [phone_number], sender)
        print(f"SMS sent: {response}")
        speak(f"SMS sent successfully to {caregiver['name']}")
    except Exception as e:
        print(f"Error sending SMS: {e}")
        speak("Unable to send SMS at the moment.")
    
    messagebox.showinfo("SMS Sent", f"SMS sent to {caregiver['name']} at {phone_number}")

# Function to handle the caregiver selection by voice
def choose_caregiver_by_voice():
    # List caregivers out loud
    speak("Here are the available caregivers:")
    for i, caregiver in enumerate(caregivers):
        speak(f"Caregiver {i+1}: {caregiver['name']}, Specialty: {caregiver['specialty']}")

    speak("Please say the name of the caregiver you want to select.")
    
    selected_caregiver_name = takeCommand().lower()

    # Try to find the caregiver based on the name spoken by the user
    selected_caregiver = None
    for caregiver in caregivers:
        if caregiver["name"].lower() in selected_caregiver_name:
            selected_caregiver = caregiver
            break
    
    if selected_caregiver:
        send_sms_to_caregiver(selected_caregiver)
    else:
        speak("Sorry, I couldn't find the caregiver by that name. Please try again.")
        choose_caregiver_by_voice()

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
# Function to login to a site using voice as password
def login_to_site():
    enrolled_password = enroll_voice_password()
    if enrolled_password:
        compare_passwords(enrolled_password)
    else:
        speak("Password not captured. Please try again.")

# Function to capture and enroll the voice password as text
def enroll_voice_password():
    speak("Please say your password.")
    password = takeCommand().lower()
    if password == "none":
        speak("Password not captured.")
        return None
    print(f"Password enrolled: {password}")
    return password

# Function to capture the voice for authentication
def capture_voice_for_authentication():
    speak("Please say your password for authentication.")
    password = takeCommand().lower()
    if password == "none":
        speak("Password not captured.")
        return None
    return password

# Function to compare the enrolled password with the spoken password
def compare_passwords(enrolled_password):
    spoken_password = capture_voice_for_authentication()
    
    if spoken_password == None:
        speak("Password not captured. Please try again.")
    elif spoken_password == enrolled_password:
        speak("Password matched. Login access granted.")
    else:
        speak("Password does not match.")


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
        choose_caregiver_by_voice()
    else:
        speak("I'm sorry, I didn't understand that command.")

# GUI setup
root = tk.Tk()
root.title("Virtual Assistant")
root.geometry("300x200")

label = tk.Label(root, text="Virtual Assistant")
label.pack(pady=10)

start_button = ttk.Button(root, text="Start Listening", command=handleCommand)
start_button.pack(pady=10)

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == '__main__':
    speak("Hello, I'm your virtual assistant. How can I help you?")
    root.mainloop()
