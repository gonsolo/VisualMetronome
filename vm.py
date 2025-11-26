import mido
import time
import sys
import tkinter as tk

midi_port_name = 'Midi Through:Midi Through Port-0 14:0'
beats_per_measure = 4
start_value = 0 # Offset, der das Timing korrigiert hat

# --- Tkinter GUI Setup ---
root = tk.Tk()
root.title("Visuelles Metronom")
root.geometry("400x300")
# Label für die Beat-Zahl
beat_label = tk.Label(root, text="--", font=("Helvetica", 150, "bold"), bg="white")
beat_label.pack(expand=True, fill='both')

def update_gui_beat(beat_number_str, is_takt_anfang=False):
    """Aktualisiert das Label im Tkinter-Fenster."""
    beat_label.config(text=beat_number_str)
    if is_takt_anfang:
        # Hervorhebung für den ersten Schlag (z.B. rote Farbe)
        beat_label.config(fg="red")
    else:
        beat_label.config(fg="black")

def clear_gui():
    """Setzt das Fenster zurück, wenn die Wiedergabe stoppt."""
    beat_label.config(text="--", fg="gray")

# --- MIDI Logic ---

# Diese Funktion wird aus der Tkinter-Mainloop heraus aufgerufen
def check_midi_messages(inport):
    global total_beats_count, ticks_received, current_beat_in_measure

    # Lesen Sie alle verfügbaren Nachrichten im Puffer, ohne zu blockieren (poll)
    for msg in inport.iter_pending():
        
        if msg.type == 'start':
            total_beats_count = start_value
            ticks_received = 0
            clear_gui()
            print("--- Wiedergabe gestartet ---")

        elif msg.type == 'stop':
            print("--- Wiedergabe gestoppt ---")
            clear_gui()
            total_beats_count = start_value

        elif msg.type == 'clock':
            ticks_received += 1
            if ticks_received % ticks_pro_beat == 0:
                
                total_beats_count += 1
                
                if total_beats_count >= 0:
                    current_beat_in_measure = (total_beats_count % beats_per_measure) + 1
                    
                    # Hier rufen wir die GUI-Update-Funktion auf
                    update_gui_beat(str(current_beat_in_measure), 
                                    is_takt_anfang=(current_beat_in_measure == 1))
                    
                    # Konsolenausgabe beibehalten (optional)
                    # print(f"Beat: {current_beat_in_measure}")

    # Wichtig: Diese Funktion muss sich selbst immer wieder aufrufen
    # Die Zahl (hier 10ms) bestimmt die Polling-Rate für MIDI-Nachrichten
    root.after(10, check_midi_messages, inport)


# --- Hauptprogramm Ablauf ---
try:
    # Den Port öffnen, aber das 'with'-Statement hier weglassen, 
    # da wir das Port-Objekt global benötigen und Tkinter die Hauptschleife steuert.
    inport = mido.open_input(midi_port_name)
    print(f"Lausche auf MIDI-Port: {midi_port_name}")

    ticks_pro_beat = 24
    ticks_received = 0
    total_beats_count = start_value
    current_beat_in_measure = 0

    # Startet den Polling-Mechanismus für MIDI-Nachrichten
    root.after(10, check_midi_messages, inport)
    
    # Startet die Tkinter-Hauptschleife (blockiert hier bis das Fenster geschlossen wird)
    root.mainloop()

except IOError as e:
    print(f"Fehler beim Öffnen des Ports: {e}")
    sys.exit(1)
except KeyboardInterrupt:
    print("\nSkript beendet.")
finally:
    # Aufräumen, wenn mainloop beendet ist (Fenster geschlossen oder Strg+C)
    if 'inport' in locals() and inport is not None:
        inport.close()

