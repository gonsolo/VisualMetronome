import time
import sys
import tkinter as tk
from tkinter.font import Font

# --- Konfiguration ---
bpm = 80  # Ihr Tempo
beats_per_measure = 4
# start_value is now always 0 for internal counting
total_beats_count = 0
current_beat_in_measure = 0

is_fullscreen = False
FONT_SIZE = 300 
running = True # Clock should run automatically

# --- Timing Variables (for accurate clock calculation) ---
beat_interval_seconds = 60.0 / bpm
last_beat_time = 0

# --- Tkinter GUI Setup ---
root = tk.Tk()
root.title("Visuelles Metronom")
root.geometry("1000x800") 
root.configure(bg="black")

beat_label = tk.Label(root, text="--", bg="black", fg="white")
beat_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# --- Funktionen ---

def update_font_size():
    # Dynamisch die Schriftgröße anpassen, wenn das Fenster in der Größe geändert wird
    current_height = root.winfo_height()
    new_size = int(current_height * 0.6) 
    if new_size < 100:
        new_size = 100
    custom_font = Font(family="Helvetica", size=new_size, weight="bold")
    beat_label.config(font=custom_font)

def update_gui_beat(beat_number_str, is_takt_anfang=False):
    # Aktualisiert die Anzeige des Labels
    beat_label.config(text=beat_number_str)
    # update_font_size() # This is handled by the <Configure> binding now
    if is_takt_anfang:
        beat_label.config(fg="white") # Beat 1 is white
    else:
        beat_label.config(fg="gray") # Other beats are gray

def toggle_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.attributes("-fullscreen", is_fullscreen)
    update_font_size()

def exit_app(event=None):
    # Einfache Exit Funktion, da keine Ports mehr geschlossen werden müssen
    print("Beende Anwendung.")
    root.destroy()
    sys.exit(0)

# --- Visual Metronome Clock Logic ---

def visual_clock_loop():
    global last_beat_time, total_beats_count, current_beat_in_measure, running

    if running:
        current_time = time.time()
        # Check if enough time has passed since the last beat
        if current_time - last_beat_time >= beat_interval_seconds:
            
            # Calculate the current beat number (1 through 4)
            current_beat_in_measure = (total_beats_count % beats_per_measure) + 1
            is_downbeat = (current_beat_in_measure == 1)

            # Update the GUI
            update_gui_beat(str(current_beat_in_measure), is_takt_anfang=is_downbeat)

            # Update timing variables for the next iteration
            last_beat_time += beat_interval_seconds # Use this method for consistent timing
            total_beats_count += 1
            
    # Schedule the next check very soon (1ms)
    root.after(1, visual_clock_loop)


# --- Tastatur-Bindungen (Keybindings) ---
root.bind("f", toggle_fullscreen)
root.bind("F", toggle_fullscreen)
root.bind("x", exit_app)
root.bind("X", exit_app)
root.bind("<Escape>", exit_app)
root.bind("<Configure>", lambda event: update_font_size()) # Update font on window resize

# --- Hauptprogramm Start ---

print(f"Starte visuelles Metronom bei {bpm} BPM.")
print(f"Drücke 'f' für Fullscreen, 'x' oder 'Esc' zum Beenden.")

# Initialize the time reference and start the loop
last_beat_time = time.time() 
update_font_size()
root.after(10, visual_clock_loop) # Start the loop shortly after Tkinter initializes
root.mainloop()


