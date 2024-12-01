import customtkinter as ctk
import speech_recognition as sr
import pyttsx3
import threading
from tkinter import Text, END
from ollama import chat
import os
import fitz  # PyMuPDF
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.schema import Document  # Import the Document class
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever



# Step 1: Extract text from the entire PDF
pdf_dir = "PDF"
documents = []  # Initialize a list to store Document objects

# index = 0
if os.path.exists(pdf_dir) and os.path.isdir(pdf_dir):
    pdf_files = [file for file in os.listdir(pdf_dir) if file.endswith(".pdf")]

    for pdf_file in pdf_files:

        pdf_document = fitz.open("./PDF/" + pdf_file)


        total_pages = len(pdf_document)

        for page_number in range(total_pages):
            page = pdf_document[page_number]
            text_content = page.get_text()
            # index = index + 1
            if text_content.strip():  # Only process pages with text
                # Wrap text into a Document object
                documents.append(Document(page_content=text_content, metadata={"page": page_number + 1}))

            else:
                print(f"Page {page_number + 1} has no extractable text.")

        pdf_document.close()
else:
    print("PDF file not found or cannot be opened.")


# print(len(documents))
# print(index)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)

# Step 3: Set the environment variable for compatibility
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Step 4: Create a vector database using the extracted text
vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=OllamaEmbeddings(model="nomic-embed-text"),
    collection_name="local-rag"
)

print("Vector database created successfully.")

# Define the local LLM model
local_model = "llama3"
llm = ChatOllama(model=local_model)

# MultiQueryRetriever prompt template
QUERY_PROMPT = PromptTemplate(
    input_variables=["question"],
    template="""You are an AI language model assistant. Your task is to generate five
    different versions of the given user question to retrieve relevant documents from
    a vector database. By generating multiple perspectives on the user question, your
    goal is to help the user overcome some of the limitations of the distance-based
    similarity search. Provide these alternative questions separated by newlines.
    Original question: {question}""",
)

# Initialize MultiQueryRetriever
retriever = MultiQueryRetriever.from_llm(
    vector_db.as_retriever(),
    llm,
    prompt=QUERY_PROMPT
)

# RAG prompt template
template = """Answer the question based ONLY on the following context:
{context}
Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)






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

        # Create language selector
        self.create_language_selector()

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

    def change_language(self, lang):
        self.language = lang  # Update language variable
        self.display_message("System", f"Language switched to {lang}.", "system")

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

                    if self.language == 'en-US':
                        # stream = chat(
                        #     model='llama3',
                        #     messages=[{'role': 'user', 'content': MyText + ". response in short" }],
                        # )
                        response = chain.invoke(MyText + ". response in short")

                    else:
                        # stream = chat(
                        #     model='llama3',
                        #     messages=[{'role': 'user',
                        #                'content':  "always and only use " + self.language + "to response and make the response in short" + MyText }],
                        # )
                        response = chain.invoke(MyText + ". response in short always and only use " + self.language)

                    self.display_message("You (Voice)", MyText, "user")
                    # self.display_message("System", stream['message']['content'], "system")
                    # self.SpeakText(stream['message']['content'])

                    self.display_message("System", response, "system")
                    self.SpeakText(response)
                except sr.UnknownValueError:
                    self.display_message("System", "Sorry, I did not understand that.", "system")
                except sr.RequestError as e:
                    self.display_message("System", f"API error: {e}", "system")

    def SpeakText(self, command):
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')

        # Find a voice that matches the selected language
        matched_voice = None
        for voice in voices:
            if self.language in voice.languages or self.language in voice.id:
                matched_voice = voice.id
                break

        if not matched_voice:
            # Default fallback voice
            matched_voice = voices[0].id

        engine.setProperty('voice', matched_voice)
        engine.say(command)
        engine.runAndWait()


# Run the application
if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
