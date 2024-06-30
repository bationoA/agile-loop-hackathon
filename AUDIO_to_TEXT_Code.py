import time
import tkinter as tk
import wave
from concurrent.futures import ThreadPoolExecutor
from tkinter import scrolledtext, ttk
import speech_recognition as sr
import threading
import os
import pyaudio

# Function to add text to the text box
import yaml

from service import run


def add_user_text(text):
    text_box.config(state=tk.NORMAL)
    # Configure the tags for colored text
    text_spacing = 10
    text_box.tag_config("colored1", background="lightblue", font=("Helvetica", 16), spacing1=text_spacing,
                        spacing3=text_spacing)

    # text = text.strip().capitalize()

    text_to_add = f"👤User:\n {text}\n"

    text_box.insert(tk.END, text_to_add, "colored1")
    text_box.insert(tk.END, "\n")

    text_box.insert(tk.END, "\n")
    entry.delete(0, tk.END)  # Clear the placeholder text
    text_box.config(state=tk.DISABLED)  # Disable editing


def add_llm_text(text: str):
    time.sleep(5)
    text_box.config(state=tk.NORMAL)
    # Configure the tags for colored text
    text_spacing = 10
    text_box.tag_config("colored2", background="gray", font=("Helvetica", 16), spacing1=text_spacing,
                        spacing3=text_spacing)

    try:
        llm_message = run(query=text, scenario=os.environ['SCENARIO'])

        llm_message = llm_message.split("\n")[-1].split(":")[-1]
    except BaseException as e:
        print(f"ERROR: {str(e)}")
        llm_message = "An error occurred while executing the tasks. " \
                      "Please, reformulate your request, I'll be happy to help"

    llm_message = llm_message.strip().capitalize()

    text_to_add = f"👤Agent :\n {llm_message}\n"

    text_box.insert(tk.END, text_to_add, "colored2")
    text_box.insert(tk.END, "\n")

    text_box.insert(tk.END, "\n")
    entry.delete(0, tk.END)  # Clear the placeholder text
    text_box.config(state=tk.DISABLED)  # Disable editing


# def add_text_threads(params: tuple[str, str]):
#     query, source = params
#
#     if source == "user":
#         add_user_text(text=query)
#     else:
#         add_llm_text(text=query)


def add_text(query: str):
    if query != "Enter message...":
        threading.Thread(target=add_user_text, args=(query,)).start()

        threading.Thread(target=add_llm_text, args=(query,)).start()

def transcribe_audio(audio_file):
    # Initialize the recognizer
    recognizer = sr.Recognizer()

    # Use the audio file as the audio source
    with sr.AudioFile(audio_file) as source:
        # Adjust for ambient noise and record the audio
        recognizer.adjust_for_ambient_noise(source)
        audio_data = recognizer.record(source)
    # Recognize (transcribe) the speech in the audio file
    try:
        # Use Google Web Speech API to transcribe the audio
        text = recognizer.recognize_google(audio_data)
        # print("Transcription:", text)
        return text
    except sr.UnknownValueError:
        print("Google Web Speech API could not understand the audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech API; {e}")
        return None


def record():
    global recognizer, is_recording, stop_event, frames, audio_file
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt32, channels=2, rate=44100,
                        input=True, frames_per_buffer=1024)
    # frames = []
    while is_recording:
        mic_button.config(bg="red")
        data = stream.read(1024)
        frames.append(data)

    if not is_recording:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        recording_file = os.path.join(current_dir, "USER1.wav")
        with wave.open(recording_file, "wb") as sound_file:
            sound_file.setnchannels(2)
            sound_file.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt32))
            sound_file.setframerate(44100)
            sound_file.writeframes(b"".join(frames))
        sound_file.close()
        mic_button.config(bg="black")
        audio_file = "USER1.wav"
        frames = []


def handle_audio_recognition():
    global recognizer, is_recording, stop_event, frames, audio_file
    # Change button image based on is_recording flag
    if is_recording:
        is_recording = False
        record()
        # get the text version of the audio file
        audio_text = transcribe_audio(audio_file)
        # DISPLAYIN THE TRANSCRIBED AUDIO
        print("audio text", audio_text)
        add_text(audio_text)
    else:
        is_recording = True
        threading.Thread(target=record).start()


def on_entry_click(event):
    if entry.get() == 'Enter message...':
        entry.delete(0, tk.END)  # Clear the placeholder text  
        entry.config(fg='black')


def on_focusout(event):
    if entry.get() == '':
        entry.insert(0, 'Enter message...')
        entry.config(fg='#5c5a5a')


def change_background(btn_name, color):
    btn_name.config(bg=color)


# Create the main window
root = tk.Tk()
root.title("Team Unfold AI Agent")
root.geometry("500x600")
root.configure(bg="#0A1727")

# init vars
current_dir = os.path.dirname(os.path.abspath("__file__"))
audio_file = ""
frames = []

# Create a banner label
##################################################################################################################################
# Create a frame to hold the banner and combobox
# frame = tk.Frame(root, bg="#0A1727",)
# frame.pack(fill=tk.X, pady=10)

# Create a banner label
banner = tk.Label(root, text="Team Unfold: Synapse-Copylot scenarios", font=("Helvetica", 12, "bold"), bg="#0A1727", fg="white")
banner.pack(fill=tk.X, pady=10)

##################################################################################################################################
def on_select(event):
    selected_option = combobox.get()
    os.environ['SCENARIO'] = selected_option
    print(f"Selected option: {selected_option}")

# Create a Combobox
config = yaml.load(open("config.yaml", "r"), Loader=yaml.FullLoader)
options = config["SCENARIOS_LIST"]  # ["facebook", "trello", "asana", "todolist"]
combobox = ttk.Combobox(root, values=options)
combobox.pack(pady=10)
# Bind the combobox to the selection event
combobox.bind("<<ComboboxSelected>>", on_select)

##################################################################################################################################

# Initialize recognizer and other variables
recognizer = sr.Recognizer()
is_recording = False
stop_event = False

# Create a frame for the main content
main_frame = tk.Frame(root, bg="#0A1727")
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Create a scrolled text box
text_box = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD)
text_box.pack(fill=tk.BOTH, expand=True)
text_box.config(state=tk.DISABLED)  # Disable editing initially

# Define a tag with padding
text_box.tag_configure("padded", lmargin1=10, lmargin2=10, spacing3=10)

# Create a frame for the entry and buttons
input_frame = tk.Frame(root, bg="white")
input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
input_frame.grid_columnconfigure(0, weight=1)

# Create an entry widget
entry = tk.Entry(input_frame, font=("Helvetica", 14), relief=tk.FLAT, bg="white", fg='#5c5a5a')
entry.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="ew")
entry.insert(0, 'Enter message...')
entry.config(fg='#5c5a5a')

# Bind focus events to the entry widget
entry.bind('<FocusIn>', on_entry_click)
entry.bind('<FocusOut>', on_focusout)

# Create a button to add text
send_button = tk.Button(input_frame, text="➤", font=("Helvetica", 18), bg="black", fg="white", relief=tk.FLAT,
                        command=lambda: add_text(entry.get()))
# send_button = tk.Button(input_frame, text="➤", font=("Helvetica", 18), bg="black", fg="white", relief=tk.FLAT,
#                         command=lambda: add_text(entry.get()))
send_button.grid(row=0, column=1, padx=5, pady=5)
send_button.bind("<Enter>", lambda e: change_background(send_button, 'red'))
send_button.bind("<Leave>", lambda e: change_background(send_button, 'black'))

# Create another button for the microphone (non-functional placeholder)
mic_button = tk.Button(input_frame, text="Aud", font=("Helvetica", 18), bg="black", fg="white", relief=tk.FLAT,
                       command=lambda: handle_audio_recognition())
mic_button.grid(row=0, column=2, padx=(0, 5), pady=5)
mic_button.bind("<Enter>", lambda e: change_background(mic_button, 'red'))
mic_button.bind("<Leave>", lambda e: change_background(mic_button, 'black'))

# Start the Tkinter event loop
root.mainloop()
