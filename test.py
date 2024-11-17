import customtkinter as ctk

# Initialize CustomTkinter
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"


# Create the main app window
class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Text Messenger")
        self.geometry("400x500")

        # Chat display frame
        self.chat_frame = ctk.CTkFrame(self, width=380, height=400, corner_radius=10)
        self.chat_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Scrollable chat area
        self.chat_area = ctk.CTkTextbox(self.chat_frame, wrap="word", state="disabled")
        self.chat_area.pack(padx=10, pady=10, fill="both", expand=True)

        # Input frame for text entry
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", padx=10, pady=5)

        # Entry widget for text input
        self.message_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Type your message here...")
        self.message_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.message_entry.bind("<Return>", self.send_message)  # Enter key to send

        # Send button
        self.send_button = ctk.CTkButton(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side="right", padx=5, pady=5)

    def send_message(self, event=None):
        # Get message from the entry widget
        message = self.message_entry.get().strip()
        if message:  # Only send non-empty messages
            self.display_message("You", message)
            self.message_entry.delete(0, "end")  # Clear the entry field

            # Simulate a bot response
            self.after(1000, lambda: self.display_message("Bot", "Hello! How can I help?"))

    def display_message(self, sender, message):
        # Enable chat area, insert the message, and disable it again
        self.chat_area.configure(state="normal")
        self.chat_area.insert("end", f"{sender}: {message}\n")
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")  # Scroll to the bottom


# Run the app
if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
