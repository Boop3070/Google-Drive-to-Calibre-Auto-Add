import shutil
import time
import os
import sys
import json
import queue
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pystray
from PIL import Image, ImageDraw
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

GDRIVE_FOLDER = r""
INBOX_FOLDER  = r""
STARTUP_DELAY = 30

EBOOK_EXTENSIONS = {".epub", ".mobi", ".pdf", ".azw", ".azw3", ".cbz", ".cbr", ".fb2"}
PROCESSED_LOG    = os.path.join(INBOX_FOLDER, ".processed.json")

CONFIG_PATH = os.path.join(
    os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)),
    "gdrive_watcher_config.json"
)

log_queue: queue.Queue = queue.Queue()


def load_config() -> None:
    global GDRIVE_FOLDER, INBOX_FOLDER, STARTUP_DELAY, PROCESSED_LOG
    if not os.path.exists(CONFIG_PATH):
        return
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        GDRIVE_FOLDER = cfg.get("gdrive_folder", GDRIVE_FOLDER)
        INBOX_FOLDER  = cfg.get("inbox_folder",  INBOX_FOLDER)
        STARTUP_DELAY = cfg.get("startup_delay", STARTUP_DELAY)
        PROCESSED_LOG = os.path.join(INBOX_FOLDER, ".processed.json")
    except (json.JSONDecodeError, IOError):
        pass


def save_config() -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "gdrive_folder": GDRIVE_FOLDER,
            "inbox_folder":  INBOX_FOLDER,
            "startup_delay": STARTUP_DELAY,
        }, f, indent=2)


def log(msg: str) -> None:
    entry = f"[{datetime.now().strftime('%H:%M:%S')}]  {msg}"
    print(entry)
    log_queue.put(entry)


def load_log() -> set:
    if os.path.exists(PROCESSED_LOG):
        try:
            with open(PROCESSED_LOG, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except (json.JSONDecodeError, IOError):
            log("Warning: could not read log file, starting fresh.")
    return set()


def save_log(processed: set) -> None:
    tmp = PROCESSED_LOG + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(sorted(processed), f, indent=2)
        os.replace(tmp, PROCESSED_LOG)
    except IOError as e:
        log(f"Warning: could not save log file: {e}")


def copy_to_inbox(src: str, rel_path: str, processed: set, *, save: bool = True) -> bool:
    if rel_path in processed:
        return False
    filename = os.path.basename(src)
    dest     = os.path.join(INBOX_FOLDER, filename)
    if os.path.exists(dest):
        processed.add(rel_path)
        if save:
            save_log(processed)
        return False
    try:
        shutil.copy2(src, dest)
        processed.add(rel_path)
        if save:
            save_log(processed)
        log(f"Copied:  {filename}")
        return True
    except IOError as e:
        log(f"Failed to copy {filename}: {e}")
        return False


def scan_gdrive(processed: set, *, seed_only: bool = False) -> None:
    if seed_only:
        log("First run — seeding existing files into log (nothing will be copied)...")
    else:
        log("Running startup scan...")
    count = 0
    for root, _dirs, files in os.walk(GDRIVE_FOLDER):
        for filename in files:
            if os.path.splitext(filename)[1].lower() not in EBOOK_EXTENSIONS:
                continue
            src      = os.path.join(root, filename)
            rel_path = os.path.relpath(src, GDRIVE_FOLDER)
            if seed_only:
                processed.add(rel_path)
                count += 1
            else:
                if copy_to_inbox(src, rel_path, processed, save=False):
                    count += 1
    save_log(processed)
    if seed_only:
        log(f"Seeded {count} file(s). Watching for new books only.")
    elif count:
        log(f"Startup scan complete — {count} missed file(s) copied.")
    else:
        log("Startup scan complete — nothing missed.")


class NewBookHandler(FileSystemEventHandler):
    def __init__(self, processed: set):
        super().__init__()
        self.processed = processed

    def on_created(self, event):
        if event.is_directory:
            return
        src = event.src_path
        if os.path.splitext(src)[1].lower() not in EBOOK_EXTENSIONS:
            return
        rel_path = os.path.relpath(src, GDRIVE_FOLDER)
        time.sleep(5)
        if not os.path.exists(src):
            log(f"File disappeared before copy: {os.path.basename(src)}")
            return
        copy_to_inbox(src, rel_path, self.processed)


def make_tray_icon() -> Image.Image:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return Image.open(os.path.join(base, "GDrive Watcher.png")).resize((64, 64))


def run_tray(window: tk.Tk, stop_event: threading.Event, watcher: dict) -> None:
    def on_show(icon, item):
        window.after(0, window.deiconify)

    def on_settings(icon, item):
        window.after(0, lambda: open_settings(window, watcher))

    def on_quit(icon, item):
        stop_event.set()
        icon.stop()
        window.after(0, window.destroy)
        os._exit(0) 


    menu = pystray.Menu(
        pystray.MenuItem("Show log",   on_show,     default=True),
        pystray.MenuItem("Settings",   on_settings),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit",       on_quit),
    )
    pystray.Icon("GDrive Watcher", make_tray_icon(), "GDrive Watcher", menu).run()


BG        = "#0f1117"
FG        = "#d4d4d4"
ACCENT    = "#4A90D9"
DIM       = "#555e6e"
FONT_MONO = ("Consolas", 10)
FONT_HEAD = ("Segoe UI", 11, "bold")
FONT_UI   = ("Segoe UI", 9)


def open_settings(parent: tk.Tk, watcher: dict) -> None:
    win = tk.Toplevel(parent)
    win.title("Settings")
    win.geometry("540x280")
    win.resizable(False, False)
    win.configure(bg=BG)
    win.grab_set()

    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    ico  = os.path.join(base, "GDrive Watcher.ico")
    if os.path.exists(ico):
        win.iconbitmap(ico)

    gdrive_var = tk.StringVar(value=GDRIVE_FOLDER)
    inbox_var  = tk.StringVar(value=INBOX_FOLDER)
    delay_var  = tk.IntVar(value=STARTUP_DELAY)

    def row(label_text, var, row_idx):
        tk.Label(win, text=label_text, bg=BG, fg=DIM, font=FONT_UI, anchor="w").grid(
            row=row_idx, column=0, padx=(20, 8), pady=(12, 0), sticky="w"
        )
        entry = tk.Entry(
            win, textvariable=var, bg="#1c2030", fg=FG, insertbackground=FG,
            relief="flat", font=FONT_MONO, width=42
        )
        entry.grid(row=row_idx + 1, column=0, padx=(20, 4), pady=(4, 0), sticky="ew")
        btn = tk.Button(
            win, text="Browse",
            bg="#2a3045", fg=FG, activebackground="#3a4060", activeforeground=FG,
            relief="flat", bd=0, padx=10, font=FONT_UI, cursor="hand2",
            command=lambda v=var: v.set(filedialog.askdirectory(initialdir=v.get()) or v.get())
        )
        btn.grid(row=row_idx + 1, column=1, padx=(0, 20), pady=(4, 0))

    row("Google Drive folder", gdrive_var, 0)
    row("Calibre inbox folder", inbox_var, 2)

    tk.Label(win, text="Startup delay (seconds)", bg=BG, fg=DIM, font=FONT_UI, anchor="w").grid(
        row=4, column=0, padx=(20, 8), pady=(12, 0), sticky="w"
    )
    tk.Spinbox(
        win, from_=0, to=300, textvariable=delay_var, width=6,
        bg="#1c2030", fg=FG, buttonbackground="#2a3045",
        relief="flat", font=FONT_MONO
    ).grid(row=5, column=0, padx=(20, 4), pady=(4, 0), sticky="w")

    def on_save():
        global GDRIVE_FOLDER, INBOX_FOLDER, STARTUP_DELAY, PROCESSED_LOG
        GDRIVE_FOLDER = gdrive_var.get()
        INBOX_FOLDER  = inbox_var.get()
        STARTUP_DELAY = delay_var.get()
        PROCESSED_LOG = os.path.join(INBOX_FOLDER, ".processed.json")
        save_config()
        win.destroy()
        restart_watcher(watcher, skip_delay=True)
        log(f"Settings saved. Now watching: {GDRIVE_FOLDER}")

    btn_frame = tk.Frame(win, bg=BG)
    btn_frame.grid(row=6, column=0, columnspan=2, pady=(16, 0), padx=20, sticky="e")

    tk.Button(
        btn_frame, text="Cancel",
        bg="#1c2030", fg=DIM, activebackground="#2a3045", activeforeground=FG,
        relief="flat", bd=0, padx=14, pady=4, font=FONT_UI, cursor="hand2",
        command=win.destroy
    ).pack(side="right", padx=(8, 0))

    tk.Button(
        btn_frame, text="Save & Restart Watcher",
        bg=ACCENT, fg="white", activebackground="#3a7ac8", activeforeground="white",
        relief="flat", bd=0, padx=14, pady=4, font=FONT_UI, cursor="hand2",
        command=on_save
    ).pack(side="right")

    win.columnconfigure(0, weight=1)


def build_window(watcher: dict) -> tk.Tk:
    root = tk.Tk()
    root.title("GDrive Watcher")
    root.geometry("680x420")
    root.minsize(500, 300)
    root.configure(bg=BG)

    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    ico  = os.path.join(base, "GDrive Watcher.ico")
    if os.path.exists(ico):
        root.iconbitmap(ico)

    header = tk.Frame(root, bg=BG, pady=8)
    header.pack(fill="x", padx=16)
    tk.Label(header, text="📚  GDrive Watcher", bg=BG, fg=ACCENT, font=FONT_HEAD).pack(side="left")

    tk.Button(
        header, text="⚙ Settings",
        bg="#1c2030", fg=DIM, activebackground="#2a3045", activeforeground=FG,
        relief="flat", bd=0, padx=10, pady=3, font=FONT_UI, cursor="hand2",
        command=lambda: open_settings(root, watcher)
    ).pack(side="right", padx=(8, 0))

    tk.Label(header, text="● Watching", bg=BG, fg="#4ec94e", font=FONT_UI).pack(side="right", padx=4)

    tk.Frame(root, bg=DIM, height=1).pack(fill="x", padx=16)

    log_box = scrolledtext.ScrolledText(
        root, bg=BG, fg=FG, font=FONT_MONO,
        relief="flat", borderwidth=0, wrap="word",
        state="disabled", insertbackground=ACCENT,
    )
    log_box.pack(fill="both", expand=True, padx=16, pady=(10, 0))
    log_box.tag_config("timestamp", foreground=DIM)
    log_box.tag_config("copy",      foreground="#4ec94e")
    log_box.tag_config("warn",      foreground="#e5a020")
    log_box.tag_config("info",      foreground=FG)

    bottom = tk.Frame(root, bg="#0a0c10", pady=6)
    bottom.pack(fill="x")
    path_text = GDRIVE_FOLDER if len(GDRIVE_FOLDER) < 60 else "..." + GDRIVE_FOLDER[-57:]
    tk.Label(bottom, text=f"Watching:  {path_text}", bg="#0a0c10", fg=DIM, font=("Consolas", 8)).pack(side="left", padx=16)
    tk.Button(
        bottom, text="Clear",
        bg="#1c2030", fg=DIM, activebackground="#2a3045", activeforeground=FG,
        relief="flat", bd=0, padx=10, pady=2, font=FONT_UI, cursor="hand2",
        command=lambda: _clear_log(log_box)
    ).pack(side="right", padx=16)

    def poll_queue():
        try:
            while True:
                _append(log_box, log_queue.get_nowait())
        except queue.Empty:
            pass
        root.after(200, poll_queue)

    root.after(200, poll_queue)
    root.protocol("WM_DELETE_WINDOW", root.withdraw)
    return root


def _append(log_box: scrolledtext.ScrolledText, msg: str) -> None:
    log_box.configure(state="normal")
    if msg.startswith("[") and "]" in msg:
        ts, rest = msg.split("]", 1)
        ts += "]"
    else:
        ts, rest = "", msg
    tag = "copy" if "Copied" in rest else "warn" if any(w in rest for w in ("Warning", "Failed", "disappeared")) else "info"
    log_box.insert("end", ts, "timestamp")
    log_box.insert("end", rest + "\n", tag)
    log_box.configure(state="disabled")
    log_box.see("end")


def _clear_log(log_box: scrolledtext.ScrolledText) -> None:
    log_box.configure(state="normal")
    log_box.delete("1.0", "end")
    log_box.configure(state="disabled")


def run_watcher(stop_event: threading.Event, skip_delay: bool = False) -> None:
    if not skip_delay and STARTUP_DELAY > 0:
        log(f"Waiting {STARTUP_DELAY}s before starting...")
        if stop_event.wait(STARTUP_DELAY):
            return
    os.makedirs(INBOX_FOLDER, exist_ok=True)
    is_first_run = not os.path.exists(PROCESSED_LOG)
    processed    = load_log()
    scan_gdrive(processed, seed_only=is_first_run)
    observer = Observer()
    observer.schedule(NewBookHandler(processed), GDRIVE_FOLDER, recursive=True)
    observer.start()
    log(f"Watching:  {GDRIVE_FOLDER}")
    stop_event.wait()
    log("Stopping watcher...")
    observer.stop()
    observer.join()


def restart_watcher(watcher: dict, skip_delay: bool = False) -> None:
    if watcher.get("stop_event"):
        watcher["stop_event"].set()
    stop_event = threading.Event()
    watcher["stop_event"] = stop_event
    threading.Thread(target=run_watcher, args=(stop_event, skip_delay), daemon=True).start()


if __name__ == "__main__":
    load_config()

    watcher: dict = {}

    window = build_window(watcher)

    restart_watcher(watcher)

    global_stop = threading.Event()
    threading.Thread(target=run_tray, args=(window, global_stop, watcher), daemon=True).start()

    window.mainloop()