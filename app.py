import pyttsx3
import speech_recognition as sr
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json
import random
import hashlib
import re
from cryptography.fernet import Fernet

# Simulated database
with open('insurance_data.json', 'r') as f:
    INSURANCE_DATA = json.load(f)

# Encryption key (in a real scenario, this would be securely stored)
ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

class InsuranceAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Insurance Assistant")
        self.root.configure(bg='#1E90FF')

        self.setup_ui()
        self.setup_tts_stt()

        self.current_user = None
        self.conversation_history = []

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#1E90FF')
        style.configure('TLabel', background='#1E90FF', foreground='white')
        style.configure('TButton', background='#4CAF50', foreground='white')

        self.frame = ttk.Frame(self.root)
        self.frame.pack(pady=20, padx=20, fill='both', expand=True)

        self.label = ttk.Label(self.frame, text="Advanced Insurance Assistant", font=("Arial", 24))
        self.label.pack(pady=20)

        self.text_area = tk.Text(self.frame, height=10, width=50)
        self.text_area.pack(pady=10)

        self.speak_button = ttk.Button(self.frame, text="Speak to Assistant", command=self.handle_command)
        self.speak_button.pack(pady=10)

        self.speaker_canvas = tk.Canvas(self.frame, width=50, height=50, bg='#1E90FF', highlightthickness=0)
        self.speaker_canvas.pack(pady=10)
        self.speaker_rect = self.speaker_canvas.create_rectangle(0, 0, 50, 50, fill="red")

    def setup_tts_stt(self):
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "female" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

        self.recognizer = sr.Recognizer()

    def speak(self, audio):
        self.text_area.insert(tk.END, f"Assistant: {audio}\n")
        self.engine.say(audio)
        self.engine.runAndWait()

    def listen(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.update_speaker_icon(True)
            audio = self.recognizer.listen(source)
            self.update_speaker_icon(False)

        try:
            query = self.recognizer.recognize_google(audio, language='en-US')
            self.text_area.insert(tk.END, f"You: {query}\n")
            return query.lower()
        except sr.UnknownValueError:
            self.speak("Sorry, I didn't catch that. Could you please repeat?")
            return None
        except sr.RequestError:
            self.speak("Sorry, there was an error processing your request. Please try again.")
            return None

    def update_speaker_icon(self, listening):
        color = "green" if listening else "red"
        self.speaker_canvas.itemconfig(self.speaker_rect, fill=color)

    def handle_command(self):
        query = self.listen()
        if query:
            self.process_query(query)

    def process_query(self, query):
        self.conversation_history.append(("user", query))

        if 'quote' in query:
            self.get_insurance_quote()
        elif 'claim' in query:
            self.file_insurance_claim()
        elif 'policy' in query:
            self.check_policy_details()
        elif 'login' in query or 'sign in' in query:
            self.user_login()
        elif 'register' in query or 'sign up' in query:
            self.user_registration()
        elif 'thank you' in query:
            self.speak("You're welcome. Is there anything else I can help you with?")
        else:
            self.speak("I'm sorry, I didn't understand that command. Could you please try again?")

        self.conversation_history.append(("assistant", self.conversation_history[-1][1]))

    def get_insurance_quote(self):
        if not self.current_user:
            self.speak("Please log in or register to get a quote.")
            return

        self.speak("What type of insurance are you interested in? We offer auto, home, and life insurance.")
        insurance_type = self.listen()

        if insurance_type in INSURANCE_DATA:
            questions = INSURANCE_DATA[insurance_type]['questions']
            answers = {}

            for question in questions:
                self.speak(question)
                answer = self.listen()
                answers[question] = answer

            # Simulate quote calculation
            base_premium = INSURANCE_DATA[insurance_type]['base_premium']
            multiplier = random.uniform(0.8, 1.2)
            quote = round(base_premium * multiplier, 2)

            self.speak(f"Based on your responses, I've calculated a preliminary {insurance_type} insurance quote for you.")
            self.speak(f"Your estimated monthly premium would be ${quote}. Would you like more details about this quote?")
        else:
            self.speak("I'm sorry, I didn't recognize that insurance type. Could you please try again?")

    def file_insurance_claim(self):
        if not self.current_user:
            self.speak("Please log in to file a claim.")
            return

        self.speak("What type of claim would you like to file?")
        claim_type = self.listen()

        self.speak("Please describe what happened.")
        description = self.listen()

        # Generate a unique claim number
        claim_number = hashlib.md5(f"{self.current_user}{claim_type}{description}".encode()).hexdigest()[:10]

        self.speak(f"Thank you for providing that information. I've initiated your claim. Your claim number is {claim_number}.")
        self.speak("A claims adjuster will contact you within 24 hours for further details.")

    def check_policy_details(self):
        if not self.current_user:
            self.speak("Please log in to check your policy details.")
            return

        # In a real scenario, this would fetch actual policy details from a database
        self.speak("Here's a summary of your current policy:")
        self.speak("You have a comprehensive auto insurance policy.")
        self.speak("Your coverage includes: Liability, Collision, and Comprehensive.")
        self.speak("Your current premium is $150 per month.")
        self.speak("Your policy renewal date is December 31, 2024.")
        self.speak("Would you like more detailed information about your coverage?")

    def user_login(self):
        self.speak("Please enter your username.")
        username = self.listen()
        self.speak("Please enter your password.")
        password = self.listen()

        # In a real scenario, this would verify against a secure database
        if username == "testuser" and password == "password":
            self.current_user = username
            self.speak("Login successful. Welcome back!")
        else:
            self.speak("Invalid username or password. Please try again.")

    def user_registration(self):
        self.speak("Let's get you registered. Please choose a username.")
        username = self.listen()
        self.speak("Please choose a password.")
        password = self.listen()
        self.speak("Please provide your email address.")
        email = self.listen()

        # Validate email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.speak("Invalid email format. Please try again.")
            return

        # In a real scenario, this would securely store the user info in a database
        encrypted_password = cipher_suite.encrypt(password.encode())
        self.speak("Registration successful! You can now log in with your new account.")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = InsuranceAssistant(root)
    app.run()