import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import pygame
import time

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YakToDo List")
        
        self.tasks_todo = []
        self.tasks_doing = []
        self.tasks_done = []
        self.start_times = {}  # To store start times of tasks in the "Doing" column
        
        # Initialize Pygame mixer for audio playback
        pygame.mixer.init()
        
        # Load tasks from file
        self.load_tasks()
        
        # Create main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10)
        
        # Create frames for each column
        self.frame_todo = tk.Frame(self.main_frame)
        self.frame_todo.grid(row=1, column=0, padx=10)
        
        self.frame_buttons1 = tk.Frame(self.main_frame)
        self.frame_buttons1.grid(row=1, column=1, padx=5)
        
        self.frame_doing = tk.Frame(self.main_frame)
        self.frame_doing.grid(row=1, column=2, padx=10)
        
        self.frame_buttons2 = tk.Frame(self.main_frame)
        self.frame_buttons2.grid(row=1, column=3, padx=5)
        
        self.frame_done = tk.Frame(self.main_frame)
        self.frame_done.grid(row=1, column=4, padx=10)
        
        # Bold font
        bold_font = ("Helvetica", 10, "bold")
        
        # Titles
        tk.Label(self.main_frame, text="To-Do", font=bold_font).grid(row=0, column=0)
        tk.Label(self.main_frame, text="Doing", font=bold_font).grid(row=0, column=2)
        tk.Label(self.main_frame, text="Done", font=bold_font).grid(row=0, column=4)
        
        # To-Do Text widget and scrollbar
        self.text_todo = tk.Text(self.frame_todo, height=15, width=30, cursor="arrow", selectbackground="blue", selectforeground="white")
        self.text_todo.pack(side=tk.LEFT)
        self.text_todo.config(state=tk.DISABLED)
        
        self.scrollbar_todo = tk.Scrollbar(self.frame_todo, orient=tk.VERTICAL)
        self.scrollbar_todo.config(command=self.text_todo.yview)
        self.scrollbar_todo.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_todo.config(yscrollcommand=self.scrollbar_todo.set)
        
        # Doing Text widget and scrollbar
        self.text_doing = tk.Text(self.frame_doing, height=15, width=30, cursor="arrow", selectbackground="blue", selectforeground="white")
        self.text_doing.pack(side=tk.LEFT)
        self.text_doing.config(state=tk.DISABLED)
        
        self.scrollbar_doing = tk.Scrollbar(self.frame_doing, orient=tk.VERTICAL)
        self.scrollbar_doing.config(command=self.text_doing.yview)
        self.scrollbar_doing.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_doing.config(yscrollcommand=self.scrollbar_doing.set)
        
        # Done Text widget and scrollbar
        self.text_done = tk.Text(self.frame_done, height=15, width=30, cursor="arrow", selectbackground="blue", selectforeground="white")
        self.text_done.pack(side=tk.LEFT)
        self.text_done.config(state=tk.DISABLED)
        
        self.scrollbar_done = tk.Scrollbar(self.frame_done, orient=tk.VERTICAL)
        self.scrollbar_done.config(command=self.text_done.yview)
        self.scrollbar_done.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_done.config(yscrollcommand=self.scrollbar_done.set)
        
        # Input Entry for To-Do
        self.todo_entry_frame = tk.Frame(self.root)
        self.todo_entry_frame.pack(pady=10, side=tk.LEFT)
        
        self.todo_entry = tk.Entry(self.todo_entry_frame, width=30)
        self.todo_entry.pack(side=tk.LEFT, padx=5)
        self.todo_entry.bind("<Return>", lambda event: self.add_task())
        self.todo_entry.insert(0, "Type tasks here and press enter")
        self.todo_entry.bind("<FocusIn>", self.clear_placeholder)
        self.todo_entry.bind("<FocusOut>", self.set_placeholder)
        
        # Bind Delete key
        self.text_todo.bind("<Delete>", lambda event: self.delete_task(self.text_todo, self.tasks_todo))
        self.text_doing.bind("<Delete>", lambda event: self.delete_task(self.text_doing, self.tasks_doing))
        self.text_done.bind("<Delete>", lambda event: self.delete_task(self.text_done, self.tasks_done))
        
        # Bind single click to select text
        self.text_todo.bind("<Button-1>", self.select_text)
        self.text_doing.bind("<Button-1>", self.select_text)
        self.text_done.bind("<Button-1>", self.select_text)
        
        # Buttons
        self.right_button1 = tk.Button(self.frame_buttons1, text="→", command=self.move_todo_to_doing)
        self.right_button1.pack(pady=5)
        
        self.left_button1 = tk.Button(self.frame_buttons1, text="←", command=self.move_doing_to_todo)
        self.left_button1.pack(pady=5)

        self.right_button2 = tk.Button(self.frame_buttons2, text="→", command=self.move_doing_to_done)
        self.right_button2.pack(pady=5)
        
        self.left_button2 = tk.Button(self.frame_buttons2, text="←", command=self.move_done_to_doing)
        self.left_button2.pack(pady=5)
        
        # Audio player controls
        self.audio_frame = tk.Frame(self.root)
        self.audio_frame.pack(pady=10, side=tk.LEFT, padx=20)
        
        self.audio_file_label = tk.Label(self.audio_frame, text="No file selected", width=30)
        self.audio_file_label.pack(side=tk.TOP, padx=5)
        
        self.browse_button = tk.Button(self.audio_frame, text="Browse background audio", command=self.browse_audio)
        self.browse_button.pack(side=tk.LEFT, padx=5)
        
        self.play_button = tk.Button(self.audio_frame, text="Play", command=self.play_audio, state=tk.DISABLED)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = tk.Button(self.audio_frame, text="Pause", command=self.pause_audio, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        # Info button (using text instead of an icon)
        self.info_button = tk.Button(self.root, text="info", command=self.show_info)
        self.info_button.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=290)
        
        # Update text widgets with loaded tasks
        self.update_text_widgets()

        # Ticker
        self.ticker_position = 0
        self.scroll_speed = 200  # Adjust the speed as needed

    def add_task(self):
        task = self.todo_entry.get()
        if task and task != "Type tasks here and press enter":
            self.tasks_todo.append(task)
            self.update_text_widgets()
            self.todo_entry.delete(0, tk.END)
            self.save_tasks()
        else:
            messagebox.showwarning("Warning", "You must enter a task.")
    
    def delete_task(self, text_widget, task_list):
        try:
            index = text_widget.index(tk.INSERT).split(".")[0]
            index = int(index) - 1
            task_list.pop(index)
            self.update_text_widgets()
            self.save_tasks()
        except IndexError:
            messagebox.showwarning("Warning", "You must select a task to delete.")

    def update_text_widgets(self):
        self.update_text_widget(self.text_todo, self.tasks_todo)
        self.update_text_widget(self.text_doing, self.tasks_doing)
        self.update_text_widget(self.text_done, self.tasks_done)

    def update_text_widget(self, text_widget, task_list):
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        for task in task_list:
            text_widget.insert(tk.END, task + "\n")
        text_widget.config(state=tk.DISABLED)

    def move_todo_to_doing(self):
        self.move_task(self.text_todo, self.tasks_todo, self.tasks_doing)
    
    def move_doing_to_todo(self):
        self.move_task(self.text_doing, self.tasks_doing, self.tasks_todo)

    def move_doing_to_done(self):
        self.move_task(self.text_doing, self.tasks_doing, self.tasks_done)

    def move_done_to_doing(self):
        self.move_task(self.text_done, self.tasks_done, self.tasks_doing)

    def move_task(self, text_widget, from_list, to_list):
        try:
            index = text_widget.index(tk.INSERT).split(".")[0]
            index = int(index) - 1
            task = from_list.pop(index)
            
            # Handle timer
            if from_list == self.tasks_doing:
                self.start_times[task] = time.time()
            elif from_list == self.tasks_done:
                start_time = self.start_times.pop(task, None)
                if start_time is not None:
                    elapsed_time = time.time() - start_time
                    minutes, seconds = divmod(int(elapsed_time), 60)
                    task = f"{task} - {minutes}m {seconds}s"
            
            to_list.append(task)
            self.update_text_widgets()
            self.save_tasks()
        except IndexError:
            messagebox.showwarning("Warning", "You must select a task to move.")

    def load_tasks(self):
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as f:
                data = json.load(f)
                self.tasks_todo = data.get("tasks_todo", [])
                self.tasks_doing = data.get("tasks_doing", [])
                self.tasks_done = data.get("tasks_done", [])
                self.start_times = data.get("start_times", {})

    def save_tasks(self):
        data = {
            "tasks_todo": self.tasks_todo,
            "tasks_doing": self.tasks_doing,
            "tasks_done": self.tasks_done,
            "start_times": self.start_times
        }
        with open("tasks.json", "w") as f:
            json.dump(data, f)

    def select_text(self, event):
        widget = event.widget
        index = widget.index(f"@{event.x},{event.y}")
        line_start = f"{index} linestart"
        line_end = f"{index} lineend"
        widget.tag_remove("sel", "1.0", tk.END)
        widget.tag_add("sel", line_start, line_end)
        widget.mark_set(tk.INSERT, index)
        widget.focus()
        return "break"

    def clear_placeholder(self, event):
        if self.todo_entry.get() == "Type tasks here and press enter":
            self.todo_entry.delete(0, tk.END)
            self.todo_entry.config(fg="black")

    def set_placeholder(self, event):
        if not self.todo_entry.get():
            self.todo_entry.insert(0, "Type tasks here and press enter")
            self.todo_entry.config(fg="grey")

    def browse_audio(self):
        audio_file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav")])
        if audio_file:
            self.audio_file = audio_file
            self.audio_file_label.config(text=os.path.basename(audio_file))
            self.play_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.NORMAL)
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play(loops=-1)
            self.start_ticker()

    def play_audio(self):
        pygame.mixer.music.unpause()

    def pause_audio(self):
        pygame.mixer.music.pause()

    def start_ticker(self):
        self.ticker_position = 0
        self.audio_file_name = os.path.basename(self.audio_file)
        self.update_ticker()

    def update_ticker(self):
        display_text = self.audio_file_name[self.ticker_position:] + " " + self.audio_file_name[:self.ticker_position]
        self.audio_file_label.config(text=display_text[:30])
        self.ticker_position = (self.ticker_position + 1) % len(self.audio_file_name)
        self.root.after(self.scroll_speed, self.update_ticker)

    def show_info(self):
        info_text = "YakToDo List\n2020 Version: 1.0\nDeveloped by: Thupten Chakrishar aka @vajradog"
        messagebox.showinfo("About", info_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
