import keyboard
from tkinter import Tk, Frame, Label, Button, Checkbutton, BooleanVar, LEFT
from config import COLORS, HOTKEY
from capture_overlay import ScreenCaptureApp

class DashboardWindow:
    def __init__(self):
        self.root = Tk()
        self.root.title("Screen Capture OCR")
        self.root.geometry("480x460")
        self.root.resizable(False, False)
        self.colors = COLORS
        self.is_running = False
        self.show_notifications = True
        self.show_errors = True
        self.create_widgets()

    def create_widgets(self):
        main_container = Frame(self.root, bg=self.colors['bg'], padx=30, pady=20)
        main_container.pack(fill='both', expand=True)
        title = Label(main_container, 
                     text="Screen Capture OCR",
                     font=("Segoe UI", 24, "bold"),
                     bg=self.colors['bg'],
                     fg=self.colors['fg'])
        title.pack(pady=(0, 20))
        subtitle = Label(main_container,
                     text="Extract text from anywhere on your screen",
                     font=("Segoe UI", 10),
                     bg=self.colors['bg'],
                     fg=self.colors['fg'])
        subtitle.pack(pady=(0, 25))
        instructions_frame = Frame(main_container, bg=self.colors['button_bg'],
                                 padx=20, pady=15)
        instructions_frame.pack(fill='x', pady=(0, 20))
        instructions = """1. Click 'Start' to enable screen capture\n2. Press Ctrl+Shift+X to start capture\n3. Click and drag to select text area\n4. Text will be copied to clipboard\n5. Press 'Stop' to disable"""
        Label(instructions_frame, 
              text=instructions,
              justify=LEFT,
              font=("Segoe UI", 9),
              bg=self.colors['button_bg'],
              fg=self.colors['fg']).pack()
        toggle_frame = Frame(main_container, bg=self.colors['bg'])
        toggle_frame.pack(fill='x', pady=(0, 15))
        self.notif_var = BooleanVar(value=True)
        self.error_var = BooleanVar(value=True)
        Checkbutton(toggle_frame,
                    text="Show success notifications",
                    variable=self.notif_var,
                    font=("Segoe UI", 9),
                    bg=self.colors['bg'],
                    fg=self.colors['fg'],
                    selectcolor=self.colors['button_bg'],
                    activebackground=self.colors['bg'],
                    activeforeground=self.colors['fg']).pack(pady=(0, 5))
        Checkbutton(toggle_frame,
                    text="Show error messages",
                    variable=self.error_var,
                    font=("Segoe UI", 9),
                    bg=self.colors['bg'],
                    fg=self.colors['fg'],
                    selectcolor=self.colors['button_bg'],
                    activebackground=self.colors['bg'],
                    activeforeground=self.colors['fg']).pack()
        self.status_label = Label(main_container,
                                text="Status: Stopped",
                                font=("Segoe UI", 10, "bold"),
                                bg=self.colors['bg'],
                                fg=self.colors['red'])
        self.status_label.pack(pady=(0, 20))
        button_frame = Frame(main_container, bg=self.colors['bg'])
        button_frame.pack(fill='x', pady=(1, 1), expand=False)
        self.toggle_btn = Button(button_frame,
                              text="Start",
                              command=self.toggle_capture,
                              font=("Segoe UI", 12, "bold"),
                              width=15,
                              height=2,
                              relief="solid",
                              bd=5,
                              bg=self.colors['green'],
                              fg='black',
                              activebackground='#66bb6a',
                              activeforeground='white',
                              cursor="hand2")
        self.toggle_btn.pack(fill='x', expand=True, padx=10, pady=10)

    def toggle_capture(self):
        if not self.is_running:
            self.start_capture()
        else:
            self.stop_capture()

    def start_capture(self):
        self.is_running = True
        self.status_label.config(text="Status: Running", fg=self.colors['green'])
        self.toggle_btn.config(text="Stop", bg=self.colors['button_bg'])
        self.root.iconify()
        keyboard.add_hotkey(HOTKEY, lambda: self.launch_overlay())

    def launch_overlay(self):
        ScreenCaptureApp(self).run()

    def stop_capture(self):
        self.is_running = False
        self.status_label.config(text="Status: Stopped", fg=self.colors['red'])
        self.toggle_btn.config(text="Start", bg=self.colors['accent'])
        keyboard.remove_all_hotkeys()

    def run(self):
        self.root.mainloop() 