import tkinter as tk
from tkinter import messagebox, Label, Frame, Button
import time
import random
import csv
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TypingTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Developer Stress Detector")
        self.root.geometry("900x600")
        self.root.configure(bg="#1e1e1e")  # Dark background
        
        # UI for stats
        self.stats_frame = Frame(root, bg="#1e1e1e")
        self.stats_frame.pack(pady=10)
        
        self.label_speed = Label(self.stats_frame, text="Speed: 0 CPM", font=("Arial", 12), fg="white", bg="#1e1e1e")
        self.label_speed.grid(row=0, column=0, padx=10)
        
        self.label_errors = Label(self.stats_frame, text="Errors: 0", font=("Arial", 12), fg="white", bg="#1e1e1e")
        self.label_errors.grid(row=0, column=1, padx=10)
        
        self.label_pauses = Label(self.stats_frame, text="Last Pause: 0s", font=("Arial", 12), fg="white", bg="#1e1e1e")
        self.label_pauses.grid(row=0, column=2, padx=10)
        
        self.label_accuracy = Label(self.stats_frame, text="Accuracy: 100%", font=("Arial", 12), fg="white", bg="#1e1e1e")
        self.label_accuracy.grid(row=0, column=3, padx=10)
        
        self.label_fatigue = Label(self.stats_frame, text="Fatigue Level: High", font=("Arial", 12), fg="red", bg="#1e1e1e")
        self.label_fatigue.grid(row=0, column=4, padx=10)
        
        # Text area for typing
        self.text_area = tk.Text(root, wrap="word", font=("Arial", 12), bg="#252526", fg="white", insertbackground="white")
        self.text_area.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.text_area.bind("<KeyPress>", self.start_typing)
        self.text_area.bind("<KeyRelease>", self.track_typing)
        
        # Reset button
        self.reset_button = Button(root, text="Reset Stats", font=("Arial", 12), command=self.reset_stats, bg="#3a3a3a", fg="white")
        self.reset_button.pack(pady=5)
        
        # Variables
        self.start_time = None
        self.last_key_time = None
        self.errors = 0
        self.typing_speed = 0
        self.char_count = 0
        self.correct_chars = 0
        self.total_chars = 1  # Avoid division by zero
        self.fatigue_level = "High"
        
        # Logging setup
        self.data_log = "typing_data.csv"
        self.create_log_file()
        
        # Matplotlib Graph
        self.fig, self.ax = plt.subplots()
        self.fig.patch.set_facecolor("#1e1e1e")  # Dark mode
        self.ax.set_facecolor("#252526")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(pady=10)
        
        # Start tracking systems
        self.check_break_reminder()
        self.check_fatigue()
        self.plot_typing_data()
    
    def create_log_file(self):
        if not os.path.exists(self.data_log):
            with open(self.data_log, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Time", "Speed", "Errors", "Last Pause", "Accuracy", "Fatigue"])
    
    def log_data(self):
        with open(self.data_log, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([time.strftime("%H:%M:%S"), int(self.typing_speed), self.errors, self.label_pauses.cget("text"), f"{(self.correct_chars / self.total_chars) * 100:.2f}%", self.fatigue_level])
    
    def start_typing(self, event):
        if self.start_time is None:
            self.start_time = time.time()
        if self.last_key_time:
            pause_duration = time.time() - self.last_key_time
            self.label_pauses.config(text=f"Last Pause: {pause_duration:.2f}s")
            if pause_duration > 5:
                self.show_motivation_popup()
        self.last_key_time = time.time()
    
    def track_typing(self, event):
        if event.char.isalpha() or event.char.isdigit():
            self.char_count += 1
            self.correct_chars += 1
        elif event.keysym == "BackSpace":
            self.errors += 1
            self.correct_chars = max(0, self.correct_chars - 1)
            self.label_errors.config(text=f"Errors: {self.errors}")
        
        self.total_chars += 1
        elapsed_time = time.time() - self.start_time if self.start_time else 1
        self.typing_speed = self.char_count / (elapsed_time / 60)
        self.label_speed.config(text=f"Speed: {int(self.typing_speed)} CPM")
        
        accuracy = (self.correct_chars / self.total_chars) * 100
        self.label_accuracy.config(text=f"Accuracy: {accuracy:.2f}%")
        
        self.check_fatigue()
        self.log_data()
        self.plot_typing_data()
    
    def show_motivation_popup(self):
        messages = ["You're doing great! Keep going!", "Stay focused! You're improving!", "Believe in yourself, you got this!"]
        messagebox.showinfo("Motivation Boost!", random.choice(messages))
    
    def check_break_reminder(self):
        if self.start_time and (time.time() - self.start_time) > 300:
            messagebox.showwarning("Take a Break!", "You've been typing for a while. Take a short break!")
            self.start_time = None
        self.root.after(60000, self.check_break_reminder)  # Check every minute
    
    def check_fatigue(self):
        if self.errors > 10 and self.typing_speed < 20:
            self.fatigue_level = "High"
        elif self.errors > 5 or self.typing_speed < 40:
            self.fatigue_level = "Moderate"
        else:
            self.fatigue_level = "Low"
        
        self.label_fatigue.config(text=f"Fatigue Level: {self.fatigue_level}", fg="red" if self.fatigue_level == "High" else "yellow" if self.fatigue_level == "Moderate" else "green")
        if self.fatigue_level == "High":
            self.show_motivation_popup()
    
    def plot_typing_data(self):
        if not os.path.exists(self.data_log):
            return  # No data to plot
        
        times, speeds = [], []
        with open(self.data_log, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                times.append(row[0])  
                speeds.append(int(row[1]))  

        if not speeds:
            return

        self.ax.clear()
        self.ax.plot(times, speeds, marker="o", linestyle="-", color="cyan", label="Typing Speed")
        self.ax.set_title("Typing Speed Over Time", color="white")
        self.ax.set_xlabel("Time", color="white")
        self.ax.set_ylabel("Speed (CPM)", color="white")
        self.ax.legend()
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')

        self.canvas.draw()
    
    def reset_stats(self):
        self.start_time = None
        self.last_key_time = None
        self.errors = 0
        self.typing_speed = 0
        self.char_count = 0
        self.correct_chars = 0
        self.total_chars = 1
        self.label_speed.config(text="Speed: 0 CPM")
        self.label_errors.config(text="Errors: 0")
        self.label_pauses.config(text="Last Pause: 0s")
        self.label_accuracy.config(text="Accuracy: 100%")
        self.label_fatigue.config(text="Fatigue Level: High", fg="red")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = TypingTracker(root)
    root.mainloop()
