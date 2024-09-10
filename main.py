import tkinter as tk
from tkinter import ttk, messagebox
import pyttsx3
import threading
import platform

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Text-to-Speech Converter')
        self.root.geometry('600x600')  # Increased height for driver selection
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle window close event

        self.stop_event = threading.Event()  # Event to signal threads to stop
        self.is_busy = False  # Flag to check if TTS engine is busy

        # Available drivers based on OS
        os_system = platform.system()
        if os_system == 'Windows':
            self.drivers = ['sapi5']
        elif os_system == 'Darwin':  # macOS
            self.drivers = ['nsss']
        elif os_system == 'Linux':
            self.drivers = ['espeak']
        else:
            self.drivers = []

        # Initialize with the default driver (first one)
        self.selected_driver = self.drivers[0]
        self.engine = pyttsx3.init(driverName=self.selected_driver)

        # Get available voices
        self.voices = self.engine.getProperty('voices')

        self.setup_ui()

    def setup_ui(self):
        # Create and configure styles
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 12), padding=6)

        # Create and place widgets
        ttk.Label(self.root, text='Enter text to convert:').pack(pady=5)

        # Frame to hold the Text widget and Scrollbar
        text_frame = ttk.Frame(self.root)
        text_frame.pack(pady=5)

        # Create the Text widget
        self.text_input = tk.Text(text_frame, height=15, width=60, wrap="word")
        self.text_input.pack(side="left", fill="both", expand=True)

        # Create the Scrollbar and attach it to the Text widget
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_input.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the Text widget to use the Scrollbar
        self.text_input.config(yscrollcommand=scrollbar.set)

        # Filename input
        filename_frame = ttk.Frame(self.root)
        filename_frame.pack(pady=5)
        ttk.Label(filename_frame, text='Output filename:').pack(side='left')
        self.filename_input = ttk.Entry(filename_frame, width=25)
        self.filename_input.insert(0, "output")
        self.filename_input.pack(side='left', padx=5)
        ttk.Label(filename_frame, text='.mp3').pack(side='left')

        # Driver selection
        if len(self.drivers) > 1:
            ttk.Label(self.root, text='Select Speech Driver:').pack(pady=5)
            self.driver_combobox = ttk.Combobox(self.root, state="readonly")
            self.driver_combobox['values'] = self.drivers
            self.driver_combobox.current(0)  # Default to the first driver
            self.driver_combobox.pack(pady=5)
            self.driver_combobox.bind('<<ComboboxSelected>>', self.update_driver)  # Update driver on selection

        # Voice selection
        ttk.Label(self.root, text='Select Voice:').pack(pady=5)
        self.voice_combobox = ttk.Combobox(self.root, state="readonly")
        self.voice_combobox['values'] = [voice.name for voice in self.voices]
        self.voice_combobox.current(0)  # Set default to the first voice
        self.voice_combobox.pack(pady=5)

        # Speech Rate controls
        ttk.Label(self.root, text='Speech Rate:').pack(pady=5)
        rate_frame = ttk.Frame(self.root)
        rate_frame.pack(pady=5)
        self.rate_entry = ttk.Entry(rate_frame, width=5)
        self.rate_entry.pack(side='left', padx=5)
        self.rate_entry.bind('<Return>', self.update_rate_from_entry)

        self.rate_label = ttk.Label(rate_frame, text='100')  # Default rate
        self.rate_label.pack(side='left', padx=10)

        self.rate_slider = ttk.Scale(self.root, from_=50, to=200, orient='horizontal', length=200)
        self.rate_slider.set(100)
        self.rate_slider.pack(pady=5)
        self.rate_slider.bind('<Motion>', self.update_rate_label)

        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text='Preview', command=self.preview).pack(side='left', padx=5)
        ttk.Button(button_frame, text='Save', command=self.save).pack(side='left', padx=5)
        ttk.Button(button_frame, text='Exit', command=self.on_closing).pack(side='left', padx=5)


    def update_rate_from_entry(self, *args):
        try:
            new_rate = int(self.rate_entry.get())
            self.rate_slider.set(new_rate)
        except ValueError:
            pass  # If the input is not an integer, do nothing

    def update_rate_label(self, event):
        """Update the rate label when the slider is adjusted."""
        current_rate = int(self.rate_slider.get())
        self.rate_label.config(text=str(current_rate))
        self.rate_entry.delete(0, tk.END)
        self.rate_entry.insert(0, str(current_rate))

    def update_driver(self, event):
        """Update the speech driver and reload available voices."""
        self.selected_driver = self.driver_combobox.get()  # Get the selected driver
        self.engine = pyttsx3.init(driverName=self.selected_driver)  # Reinitialize with the selected driver
        self.voices = self.engine.getProperty('voices')  # Reload voices
        self.voice_combobox['values'] = [voice.name for voice in self.voices]  # Update voice combobox
        self.voice_combobox.current(0)  # Default to the first voice

    def preview(self):
        """Preview the text-to-speech conversion."""
        if self.is_busy:
            messagebox.showwarning('Warning', 'Text-to-Speech engine is busy. Please wait.')
            return

        text = self.text_input.get('1.0', 'end-1c')
        rate = self.rate_slider.get()
        selected_voice = self.voices[self.voice_combobox.current()]
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('voice', selected_voice.id)
        self.is_busy = True  # Set flag to busy
        threading.Thread(target=self.run_tts, args=(text, False)).start()  # False for preview

    def save(self):
        """Save the text-to-speech conversion as an audio file."""
        if self.is_busy:
            messagebox.showwarning('Warning', 'Text-to-Speech engine is currently running. Please wait.')
            return

        text = self.text_input.get('1.0', 'end-1c')
        filename = self.filename_input.get()
        if not filename:
            filename = 'output'
        filename = filename + '.mp3'
        if text:
            self.is_busy = True  # Set flag to busy
            threading.Thread(target=self.run_tts, args=(text, True, filename)).start()  # True for saving
            messagebox.showinfo('Success', f'Audio is being saved as {filename}')
        else:
            messagebox.showwarning('Error', 'Please enter text to convert')

    def run_tts(self, text, save, filename=None):
        """Run the TTS process in a separate thread."""
        selected_voice = self.voices[self.voice_combobox.current()]
        rate = self.rate_slider.get()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('voice', selected_voice.id)

        if save and filename:
            self.engine.save_to_file(text, filename)
        else:
            self.engine.say(text)
        
        def run_engine():
            self.engine.runAndWait()
            self.is_busy = False

        threading.Thread(target=run_engine).start()

    def stop_speech(self):
        """Stop the current speech."""
        if self.is_busy:
            self.engine.stop()
            self.is_busy = False

    def on_closing(self):
        """Handle the window closing event."""
        self.stop_event.set()  # Signal threads to stop
        self.stop_speech()  # Stop any ongoing speech
        self.root.destroy()  # Close the GUI

if __name__ == '__main__':
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()
