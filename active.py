import mido
import time
import sys
import tkinter as tk
from tkinter.font import Font

# --- Konfiguration ---
midi_port_name = 'Midi Through:Midi Through Port-0 14:0' 
bpm = 80  # Ihr Tempo
beats_per_measure = 4
start_value = 0 

# Globale Variablen für MIDI-Status und GUI
outport = None 
total_beats_count = start_value
current_beat_in_measure = 0
is_connected = False
is_fullscreen = False
FONT_SIZE = 300 
running = False # Flag, um den Clock-Loop zu steuern

# --- Tkinter GUI Setup ---
root = tk.Tk()
root.title("Visuelles Metronom (Master Mode)")
root.geometry("1000x800") 
root.configure(bg="black")

beat_label = tk.Label(root, text="--", bg="black", fg="white")
beat_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# --- Funktionen ---

def update_font_size():
    current_height = root.winfo_height()
    new_size = int(current_height * 0.6) 
    if new_size < 100:
        new_size = 100
    custom_font = Font(family="Helvetica", size=new_size, weight="bold")
    beat_label.config(font=custom_font)

def update_gui_beat(beat_number_str, is_takt_anfang=False):
    beat_label.config(text=beat_number_str)
    update_font_size() 
    if is_takt_anfang:
        beat_label.config(fg="white") 
    else:
        beat_label.config(fg="gray")

def clear_gui():
    beat_label.config(text="--", fg="gray")
    update_font_size()

def toggle_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.attributes("-fullscreen", is_fullscreen)
    update_font_size()

# **KORRIGIERTE EXIT FUNKTION**
def exit_app(event=None):
    global outport, running
    print("Beende Anwendung und schließe MIDI-Ports...")
    
    running = False # Stoppt den send_midi_clock_loop

    if outport and outport.closed is False:
        try:
            outport.send(mido.Message('stop')) # Stopp-Befehl an SPD-SX senden
            outport.close()
            print("MIDI-Port erfolgreich geschlossen.")
        except Exception as e:
            print(f"Fehler beim Schließen des Ports: {e}")
            
    # Jetzt kann Tkinter sicher zerstört werden
    root.destroy()
    sys.exit(0) # Beendet das Python-Programm komplett

# --- MIDI Clock Sender Logik ---

ticks_pro_beat = 24
tick_interval = (60.0 / bpm) / ticks_pro_beat
last_tick_time = 0


def send_midi_clock_loop():
    global last_tick_time, total_beats_count, current_beat_in_measure, running

    if not running and is_connected:
        # Initial START senden
        outport.send(mido.Message('start'))
        running = True
        total_beats_count = start_value
        last_tick_time = time.time()
        # print("MIDI Clock gestartet.") # Info kam schon beim Start
        update_gui_beat(str(1), is_takt_anfang=True)

    if running and is_connected:
        current_time = time.time()
        if current_time - last_tick_time >= tick_interval:
            outport.send(mido.Message('clock')) 
            last_tick_time += tick_interval 

            if (total_beats_count % ticks_pro_beat) == 0:
                current_beat_in_measure = ((total_beats_count // ticks_pro_beat) % beats_per_measure) + 1
                update_gui_beat(str(current_beat_in_measure), is_takt_anfang=(current_beat_in_measure == 1))

            total_beats_count += 1
            
    # Plant den nächsten Aufruf (funktioniert auch, wenn running=False ist, dann passiert nichts im if-Block)
    root.after(1, send_midi_clock_loop)


# --- Tastatur-Bindungen (Keybindings) ---
root.bind("f", toggle_fullscreen)
root.bind("F", toggle_fullscreen)
root.bind("x", exit_app)
root.bind("X", exit_app)
root.bind("<Escape>", exit_app)
root.bind("<Configure>", lambda event: update_font_size())


# --- Hauptprogramm Start ---
try:
    outport = mido.open_output(midi_port_name)
    is_connected = True
    print(f"Sende MIDI Clock an {midi_port_name} bei {bpm} BPM.")
    print(f"Drücke 'f' für Fullscreen, 'x' oder 'Esc' zum Beenden.")

    update_font_size()
    root.after(10, send_midi_clock_loop) 
    root.mainloop()

except IOError as e:
    print(f"Fehler beim Öffnen des Output-Ports '{midi_port_name}': {e}")
    sys.exit(1)
except KeyboardInterrupt:
    # Falls man Strg+C im Terminal drückt, wird dies abgefangen
    exit_app() 

