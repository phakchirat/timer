import tkinter as tk
from tkinter import font

class FloatingTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Timer")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.8)  # 80% Opacity
        
        # Window size
        self.width = 160
        self.height = 100
        self.root.geometry(f"{self.width}x{self.height}+100+100")
        
        self.root.config(bg="black")
        self.root.attributes("-transparentcolor", "black")

        self.offset_x = 0
        self.offset_y = 0

        self.initial_time = 480
        self.time_left = 480
        self.running = False
        self.timer_id = None
        self.current_session = "Presentation"

        self.main_font = font.Font(family="Helvetica", size=32, weight="bold")
        self.btn_font = font.Font(family="Helvetica", size=8, weight="bold")

        self.main_frame = tk.Frame(self.root, bg="#2e2e2e", highlightthickness=0)
        self.main_frame.place(x=0, y=0, width=self.width, height=self.height)

        self.canvas = tk.Canvas(self.main_frame, width=self.width, height=self.height, 
                                bg="black", highlightthickness=0)
        self.canvas.pack()
        
        # Main rounded background
        self.draw_rounded_rect(0, 0, self.width, self.height, 20, fill="#2e2e2e", outline="")

        self.setup_ui()

        # Bind dragging
        for widget in (self.main_frame, self.canvas):
            widget.bind("<ButtonPress-1>", self.on_press)
            widget.bind("<B1-Motion>", self.on_drag)

    def draw_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def draw_gradient_button(self, x1, y1, x2, y2, radius, color1, color2, text):
        # Draw gradient by lines (simpler than many polygons)
        for i in range(int(x2 - x1)):
            r = int(int(color1[1:3], 16) * (1 - i/(x2-x1)) + int(color2[1:3], 16) * (i/(x2-x1)))
            g = int(int(color1[3:5], 16) * (1 - i/(x2-x1)) + int(color2[3:5], 16) * (i/(x2-x1)))
            b = int(int(color1[5:7], 16) * (1 - i/(x2-x1)) + int(color2[5:7], 16) * (i/(x2-x1)))
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(x1 + i, y1, x1 + i, y2, fill=color)
        
        # Overlay a mask to make it rounded (draw 4 corners of the background color)
        # Or more simply, just draw the rounded rect and then the text.
        # Since standard Canvas doesn't support easy clipping, we'll use a single vibrant color for the "rounded" buttons.
        pass

    def setup_ui(self):
        # Close Button
        self.close_btn = tk.Button(
            self.main_frame, text="✕", command=self.root.destroy,
            bg="#2e2e2e", fg="#ffffff", bd=0, highlightthickness=0,
            activebackground="#444444", activeforeground="#ffffff", font=("Arial", 7)
        )
        self.close_btn.place(x=140, y=5, width=15, height=15)

        # Time Display
        self.label = tk.Label(
            self.main_frame, text="08:00", font=self.main_font,
            bg="#2e2e2e", fg="#ffffff"
        )
        self.label.place(relx=0.5, y=35, anchor="center")

        # START Button (Blue to Purple Gradient inspired)
        # We'll use a vibrant purple-blue solid color that looks like a gradient mix for simplicity in Tkinter
        self.start_btn_bg = self.draw_rounded_rect(20, 70, 95, 92, 10, fill="#6a11cb", outline="") # Vibrant Purple-Blue
        self.start_text = self.canvas.create_text(57, 81, text="START", fill="white", font=self.btn_font)
        
        # RESET Button
        self.reset_btn_bg = self.draw_rounded_rect(105, 70, 145, 92, 10, fill="#444444", outline="")
        self.reset_text = self.canvas.create_text(125, 81, text="RESET", fill="white", font=self.btn_font)

        # Bind clicks
        for item in (self.start_btn_bg, self.start_text):
            self.canvas.tag_bind(item, "<Button-1>", lambda e: self.toggle_timer())
        for item in (self.reset_btn_bg, self.reset_text):
            self.canvas.tag_bind(item, "<Button-1>", lambda e: self.set_timer(self.initial_time, is_reset=True))

        # Dragging for label
        self.label.bind("<ButtonPress-1>", self.on_press)
        self.label.bind("<B1-Motion>", self.on_drag)

    def on_press(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def on_drag(self, event):
        x = self.root.winfo_x() + event.x - self.offset_x
        y = self.root.winfo_y() + event.y - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    def set_timer(self, seconds, is_reset=False):
        self.stop_timer()
        self.time_left = seconds
        if not is_reset:
            self.initial_time = seconds
            if seconds == 480:
                self.current_session = "Presentation"
            elif seconds == 300:
                self.current_session = "Q&A"
        self.update_display()

    def update_display(self):
        mins, secs = divmod(self.time_left, 60)
        self.label.config(text=f"{mins:02d}:{secs:02d}")
        if self.time_left <= 60:
            self.label.config(fg="#ff5555")
        else:
            self.label.config(fg="#ffffff")

    def toggle_timer(self):
        if self.running:
            self.stop_timer()
        else:
            self.start_timer()

    def start_timer(self):
        if not self.running:
            self.running = True
            self.canvas.itemconfigure(self.start_text, text="PAUSE")
            self.canvas.itemconfigure(self.start_btn_bg, fill="black")
            self.tick()

    def stop_timer(self):
        self.running = False
        self.canvas.itemconfigure(self.start_text, text="START")
        self.canvas.itemconfigure(self.start_btn_bg, fill="#6a11cb")
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def tick(self):
        if self.running and self.time_left > 0:
            self.time_left -= 1
            self.update_display()
            self.timer_id = self.root.after(1000, self.tick)
        elif self.time_left <= 0:
            self.running = False
            self.canvas.itemconfigure(self.start_text, text="START")
            if self.current_session == "Presentation":
                self.root.after(3000, lambda: self.set_timer(300))
                self.root.after(3001, self.start_timer)
            self.flash_timer()

    def flash_timer(self):
        current_color = self.label.cget("fg")
        next_color = "#ffffff" if current_color == "#ff5555" else "#ff5555"
        self.label.config(fg=next_color)
        if not self.running and self.time_left <= 0:
            self.root.after(500, self.flash_timer)

if __name__ == "__main__":
    root = tk.Tk()
    app = FloatingTimer(root)
    root.mainloop()
