import mido
import time
import sys
import tkinter as tk

# --- Konfiguration ---
# Der Portname, der in 'mido.get_input_names()' gefunden wurde:
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
# Fenstergröße für den Start, bevor Fullscreen aktiviert wird
root.geometry("600x400") 

# Hintergrundfarbe auf Schwarz setzen
root.configure(bg="black")

# Label für die Beat-Anzeige (Schrift: Weiß auf Schwarz)
beat_label = tk.Label(root, text="--", font=("Helvetica", 250, "bold"), 
                       bg="black", fg="white")
beat_label.pack(expand=True, fill='both')

# --- Funktionen ---

def update_gui_beat(beat_number_str, is_takt_anfang=False):
    """Aktualisiert das Label im Tkinter-Fenster."""
    beat_label.config(text=beat_number_str)
    if is_takt_anfang:
        # Hervorhebung für den ersten Schlag (z.B. helleres Weiß/Silber)
        beat_label.config(fg="white") 
    else:
        beat_label.config(fg="gray") # Etwas gedämpfter für die Zählzeiten 2, 3, 4

def clear_gui():
    """Setzt das Fenster zurück, wenn die Wiedergabe stoppt."""
    beat_label.config(text="--", fg="gray")

def toggle_fullscreen(event=None):
    """Wechselt zwischen Fenster- und Vollbildmodus."""
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    # Tkinter-Befehl, der den Fenstermanager anweist, in den Vollbildmodus zu wechseln
    root.attributes("-fullscreen", is_fullscreen)

def exit_app(event=None):
    """Beendet die Anwendung sauber."""
    if inport and inport.is_open:
        inport.close()
    root.destroy() # Schließt das Tkinter-Fenster und beendet mainloop

def check_midi_messages():
    """Polls MIDI messages in a non-blocking way and updates GUI."""
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

    # Plant den nächsten Aufruf dieser Funktion nach 10ms
    root.after(10, check_midi_messages)

# --- Tastatur-Bindungen (Keybindings) ---

# Taste 'f' für Fullscreen
root.bind("f", toggle_fullscreen)
root.bind("F", toggle_fullscreen) # Auch Großbuchstaben abfangen

# Taste 'x' und 'Escape' für Beenden
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

    # Startet den Polling-Mechanismus für MIDI-Nachrichten
    root.after(10, check_midi_messages)
    
    # Startet die Tkinter-Hauptschleife (blockiert hier bis das Fenster geschlossen wird)
    root.mainloop()

except IOError as e:
    print(f"Fehler beim Öffnen des Ports '{midi_port_name}': {e}")
    sys.exit(1)
except KeyboardInterrupt:
    pass # Wird jetzt durch exit_app() oder root.bind('<Escape>') gehandhabt
finally:
    # Aufräumen, wenn mainloop beendet ist
    if inport and inport.is_open:
        inport.close()
    print("Skript beendet.")


