import mido
import time
import sys
import tkinter as tk

# --- Konfiguration ---
midi_port_name = 'Midi Through:Midi Through Port-0 14:0' 
beats_per_measure = 4
start_value = 0 # Offset für das Timing

# Globale Variablen für MIDI-Status und GUI
inport = None
total_beats_count = start_value
ticks_received = 0
current_beat_in_measure = 0
is_connected = False
is_fullscreen = False

# --- Tkinter GUI Setup ---
root = tk.Tk()
root.title("Visuelles Metronom")
root.geometry("600x400") 
root.configure(bg="black")

beat_label = tk.Label(root, text="--", font=("Helvetica", 250, "bold"), 
                       bg="black", fg="white")
beat_label.pack(expand=True, fill='both')

# --- Funktionen ---

def update_gui_beat(beat_number_str, is_takt_anfang=False):
    beat_label.config(text=beat_number_str)
    if is_takt_anfang:
        beat_label.config(fg="white") 
    else:
        beat_label.config(fg="gray")

def clear_gui():
    beat_label.config(text="--", fg="gray")

def toggle_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.attributes("-fullscreen", is_fullscreen)

def exit_app(event=None):
    """Beendet die Anwendung sauber."""
    global inport
    if inport:
        # Kein is_open Check notwendig, close() kann sicher aufgerufen werden
        inport.close() 
    root.destroy() # Schließt das Tkinter-Fenster und beendet mainloop

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


# --- Hauptprogramm Start ---
try:
    # Port öffnen
    inport = mido.open_input(midi_port_name)
    is_connected = True
    print(f"Verbunden mit {midi_port_name}. Drücke 'f' für Fullscreen, 'x' oder 'Esc' zum Beenden.")

    ticks_pro_beat = 24

    root.after(10, check_midi_messages)
    root.mainloop()

except IOError as e:
    print(f"Fehler beim Öffnen des Ports '{midi_port_name}': {e}")
    sys.exit(1)
except KeyboardInterrupt:
    pass # exit_app wird das Aufräumen übernehmen, wenn mainloop beendet wird
finally:
    # Aufräumen, wenn mainloop beendet ist
    if inport:
        inport.close() # is_open Check entfernt
    print("Skript beendet.")



