import tkinter as tk
from tkinter import ttk, messagebox
import pyttsx3
import threading

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Text-to-Speech Converter')
        self.root.geometry('600x500')  # Increased width to accommodate wider text input
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle window close event

        self.stop_event = threading.Event()  # Event to signal threads to stop
        self.engine = pyttsx3.init()

        self.setup_ui()

    def setup_ui(self):
        # Create and configure styles
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 12), padding=6)

        # Create and place widgets
        ttk.Label(self.root, text='Enter text to convert:').pack(pady=5)
        self.text_input = tk.Text(self.root, height=15, width=60)  # Increased width
        self.text_input.pack(pady=5)

        filename_frame = ttk.Frame(self.root)
        filename_frame.pack(pady=5)
        ttk.Label(filename_frame, text='Output filename:').pack(side='left')
        self.filename_input = ttk.Entry(filename_frame, width=25)  # Slightly wider entry box
        self.filename_input.insert(0, "output")  # Set default text
        self.filename_input.pack(side='left', padx=5)
        ttk.Label(filename_frame, text='.mp3').pack(side='left')

        ttk.Label(self.root, text='Speech Rate:').pack(pady=5)

        # Display and control speech rate
        rate_frame = ttk.Frame(self.root)
        rate_frame.pack(pady=5)

        # Manual entry for speech rate
        self.rate_entry = ttk.Entry(rate_frame, width=5)
        self.rate_entry.pack(side='left', padx=5)
        self.rate_entry.bind('<Return>', self.update_rate_from_entry)

        # Label to show current rate
        self.rate_label = ttk.Label(rate_frame, text='100')  # Default rate
        self.rate_label.pack(side='left', padx=10)

        # Slider to control speech rate
        self.rate_slider = ttk.Scale(self.root, from_=50, to=200, orient='horizontal', length=200)
        self.rate_slider.set(100)
        self.rate_slider.pack(pady=5)
        self.rate_slider.bind('<Motion>', self.update_rate_label)

        # Create and place buttons in a separate frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        # Styled buttons with less space at the end
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

    def preview(self):
        """Preview the text-to-speech conversion."""
        text = self.text_input.get('1.0', 'end-1c')
        rate = self.rate_slider.get()
        self.engine.setProperty('rate', rate)
        self.engine.say(text)
        threading.Thread(target=self.engine.runAndWait).start()  # Use threading for preview

    def save(self):
        """Save the text-to-speech conversion as an audio file."""
        text = self.text_input.get('1.0', 'end-1c')
        filename = self.filename_input.get()
        if not filename:  # Use a default filename if empty
            filename = 'output'
        filename = filename + '.mp3'
        rate = self.rate_slider.get()
        if text:
            # Run the text-to-speech save operation in a separate thread
            threading.Thread(target=self.text_to_speech, args=(text, filename, rate)).start()
            messagebox.showinfo('Success', f'Audio is being saved as {filename}')
        else:
            messagebox.showwarning('Error', 'Please enter text to convert')

    def text_to_speech(self, text, filename, rate):
        """Convert text to speech and save as an audio file."""
        self.engine.setProperty('rate', rate)
        self.engine.save_to_file(text, filename)
        self.engine.runAndWait()

    def on_closing(self):
        """Handle the window closing event."""
        self.stop_event.set()  # Signal threads to stop
        self.root.destroy()  # Close the GUI

if __name__ == '__main__':
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()
