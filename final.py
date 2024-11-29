import customtkinter as ctk
import speech_recognition as sr
from gtts import gTTS
import os
from playsound import playsound
import threading
from tkinter import Text, END
from ollama import chat

# Initialize CustomTkinter
ctk.set_appearance_mode("Dark")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"


# Main application class
class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Voice-Enabled Chat App")
        self.geometry("500x600")

        # Default language
        self.language = "en-US"

        # Chat display frame
        self.chat_frame = ctk.CTkFrame(self, width=480, height=450, corner_radius=10)
        self.chat_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Scrollable chat area using Tkinter's Text widget
        self.chat_area = Text(self.chat_frame, wrap="word", state="normal", bg="#2b2b2b", fg="white", font=("Arial", 12))
        self.chat_area.pack(padx=10, pady=10, fill="both", expand=True)

        # Configure tags for message styling
        self.chat_area.tag_configure("user", justify="right", background="blue", foreground="white", font=("Arial", 12), lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_area.tag_configure("system", justify="left", background="grey", foreground="white", font=("Arial", 12), lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_area.configure(state="disabled")

        # Input frame for text entry
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", padx=10, pady=5)

        # Entry widget for text input
        self.message_entry = ctk.CTkEntry(
            self.input_frame, placeholder_text="Type your message here..."
        )
        self.message_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.message_entry.bind("<Return>", self.send_message)  # Send message on Enter key

        # Send button
        self.send_button = ctk.CTkButton(
            self.input_frame, text="Send", command=self.send_message
        )
        self.send_button.pack(side="right", padx=5, pady=5)

        # Create language selector (after initializing chat_area)
        self.create_language_selector()

        # Start voice recognition in a separate thread
        self.voice_thread = threading.Thread(target=self.voice_recognition_loop, daemon=True)
        self.voice_thread.start()


    def create_language_selector(self):
        # Language selection dropdown
        self.language_var = ctk.StringVar(value="en-US")  # Default English
        self.language_menu = ctk.CTkOptionMenu(
            self, 
            values=["en-US", "zh-CN", "vi-VN", "ja-JP"],  # Available languages
            variable=self.language_var,
            command=self.change_language  # Callback when language changes
        )
        self.language_menu.pack(pady=5)

        # Display current language
        self.display_message("System", "Default language is English (US). You can change it using the dropdown menu.", "system")

    def change_language(self, lang):
        self.language = lang  # Update language variable
        language_map = {
            "en-US": "English (United States)",
            "zh-CN": "Chinese (Simplified)",
            "vi-VN": "Vietnamese",
            "ja-JP": "Japanese"
        }
        language_name = language_map.get(lang, lang)
        self.display_message("System", f"Language switched to {language_name}.", "system")

    def send_message(self, event=None):
        # Get message from the entry widget
        message = self.message_entry.get().strip()

        if message:
            self.display_message("You", message, "user")
            self.message_entry.delete(0, "end")  # Clear the entry field

            self.SpeakText(message)

            # Simulate a bot response
            self.after(1000, lambda: self.display_message("Bot", "I heard you!", "system"))

    def display_message(self, sender, message, tag):
        # Enable chat area, insert the message, and disable it again
        self.chat_area.configure(state="normal")
        formatted_message = f"{message}\n"
        self.chat_area.insert("end", formatted_message, tag)
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")  # Scroll to the bottom

    def voice_recognition_loop(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.display_message("System", "Voice recognition started. Speak now!", "system")

            while True:
                try:
                    # Listen for user speech
                    audio = recognizer.listen(source)

                    # Recognize speech using the selected language
                    MyText = recognizer.recognize_google(audio, language=self.language).lower()

                    # Use Ollama API for response in the selected language
                    response = chat(
                        model='llama3',
                        messages=[{'role': 'user', 'content': f"{MyText}. Please respond in {self.language}"}]
                    )

                    # Extract and display response
                    bot_message = response['message']['content']
                    self.display_message("You (Voice)", MyText, "user")
                    self.display_message("Bot", bot_message, "system")

                    # Speak the response
                    self.SpeakText(bot_message)

                except sr.UnknownValueError:
                    self.display_message("System", "Sorry, I did not understand that.", "system")
                except sr.RequestError as e:
                    self.display_message("System", f"API error: {e}", "system")

    def SpeakText(self, command):
        try:
            # Use gTTS to generate speech
            tts = gTTS(text=command, lang=self.language.split('-')[0])  # Use the first part of the language code
            audio_file = "temp_audio.mp3"
            tts.save(audio_file)

            # Play the audio
            playsound(audio_file)

            # Clean up the temporary audio file
            os.remove(audio_file)
        except Exception as e:
            self.display_message("System", f"Error in text-to-speech: {str(e)}", "system")


# Run the application
if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
