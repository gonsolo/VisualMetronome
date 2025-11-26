import mido
import time
import sys
import tkinter as tk
from tkinter.font import Font

# --- Konfiguration ---
midi_port_name = 'Midi Through:Midi Through Port-0 14:0' 
beats_per_measure = 4
start_value = 0 

# Globale Variablen für MIDI-Status und GUI
inport = None
total_beats_count = start_value
ticks_received = 0
current_beat_in_measure = 0
is_connected = False
is_fullscreen = False
FONT_SIZE = 300 # Realistische, aber große Standardgröße

# --- Tkinter GUI Setup ---
root = tk.Tk()
root.title("Visuelles Metronom")
root.geometry("1000x800") 
root.configure(bg="black")

# Label für die Beat-Anzeige
beat_label = tk.Label(root, text="--", bg="black", fg="white")
# Verwenden Sie place, um das Label absolut im Zentrum zu positionieren
# relx=0.5 und rely=0.5 positionieren den Ankerpunkt des Labels in der Mitte des Fensters
# anchor=CENTER stellt sicher, dass der Ankerpunkt des Labels auch wirklich seine eigene Mitte ist.
beat_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)


# --- Funktionen ---

def update_font_size():
    """Passt die Schriftgröße basierend auf der aktuellen Fensterhöhe an."""
    # Dies versucht, die Größe dynamisch anzupassen, falls nötig.
    current_height = root.winfo_height()
    # Eine einfache Heuristik: 60% der Fensterhöhe
    new_size = int(current_height * 0.6) 
    # Mindestgröße sicherstellen
    if new_size < 100:
        new_size = 100
        
    # Die Schriftart muss jedes Mal neu definiert werden, um die Größe zu ändern
    custom_font = Font(family="Helvetica", size=new_size, weight="bold")
    beat_label.config(font=custom_font)


def update_gui_beat(beat_number_str, is_takt_anfang=False):
    beat_label.config(text=beat_number_str)
    # Sicherstellen, dass die Schriftgröße aktuell ist, wenn ein neuer Beat kommt
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
    # Nach dem Umschalten die Schriftgröße sofort anpassen
    update_font_size()

def exit_app(event=None):
    global inport
    if inport:
        inport.close() 
    root.destroy()

# ... (check_midi_messages Funktion bleibt gleich) ...
def check_midi_messages():
    global total_beats_count, ticks_received, current_beat_in_measure

    if is_connected and inport:
        for msg in inport.iter_pending():
            
            if msg.type == 'start':
                total_beats_count = start_value
                ticks_received = 0
                clear_gui()
            elif msg.type == 'stop':
                clear_gui()
                total_beats_count = start_value
            elif msg.type == 'clock':
                ticks_received += 1
                if ticks_received % ticks_pro_beat == 0:
                    total_beats_count += 1
                    if total_beats_count >= 0:
                        current_beat_in_measure = (total_beats_count % beats_per_measure) + 1
                        update_gui_beat(str(current_beat_in_measure), 
                                        is_takt_anfang=(current_beat_in_measure == 1))

    root.after(10, check_midi_messages)


# --- Tastatur-Bindungen (Keybindings) ---
root.bind("f", toggle_fullscreen)
root.bind("F", toggle_fullscreen)
root.bind("x", exit_app)
root.bind("X", exit_app)
root.bind("<Escape>", exit_app)
# Event-Bindung, um die Größe anzupassen, wenn das Fenster manuell in der Größe geändert wird
root.bind("<Configure>", lambda event: update_font_size())


# --- Hauptprogramm Start ---
try:
    inport = mido.open_input(midi_port_name)
    is_connected = True
    print(f"Verbunden mit {midi_port_name}. Drücke 'f' für Fullscreen, 'x' oder 'Esc' zum Beenden.")

    ticks_pro_beat = 24
    
    # Initial die Schriftgröße setzen
    update_font_size()
    root.after(10, check_midi_messages)
    root.mainloop()

except IOError as e:
    print(f"Fehler beim Öffnen des Ports '{midi_port_name}': {e}")
    sys.exit(1)
except KeyboardInterrupt:
    pass 
finally:
    if inport:
        inport.close()
    print("Skript beendet.")


