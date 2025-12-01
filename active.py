import mido
import time
import sys
import tkinter as tk
from tkinter.font import Font

# --- Konfiguration ---
# Dies muss der NAME des OUTPUT-PORTS Ihres Roland UM-ONE sein,
# damit der Computer Signale AN das UM-ONE senden kann.
# Auf Linux/Mac könnte das 'Roland UM-ONE' oder ähnlich heißen.
# Auf Windows oft 'UM-ONE (Port 1)'.
midi_port_name = 'Midi Through:Midi Through Port-0 14:0' 

bpm = 80  # Gewünschtes Tempo, das gesendet wird
beats_per_measure = 4
start_value = 0 

# Globale Variablen für MIDI-Status und GUI
outport = None # Jetzt ein Output-Port
total_beats_count = start_value
current_beat_in_measure = 0
is_connected = False
is_fullscreen = False
FONT_SIZE = 300 

# --- Tkinter GUI Setup ---
root = tk.Tk()
root.title("Visuelles Metronom (Master Mode)")
root.geometry("1000x800") 
root.configure(bg="black")

beat_label = tk.Label(root, text="--", bg="black", fg="white")
beat_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# --- Funktionen ---

def update_font_size():
    # ... (Funktion bleibt gleich wie in Ihrem Originalskript) ...
    current_height = root.winfo_height()
    new_size = int(current_height * 0.6) 
    if new_size < 100:
        new_size = 100
    custom_font = Font(family="Helvetica", size=new_size, weight="bold")
    beat_label.config(font=custom_font)

def update_gui_beat(beat_number_str, is_takt_anfang=False):
    # ... (Funktion bleibt gleich wie in Ihrem Originalskript) ...
    beat_label.config(text=beat_number_str)
    update_font_size() 
    if is_takt_anfang:
        beat_label.config(fg="white") 
    else:
        beat_label.config(fg="gray")

def clear_gui():
    # ... (Funktion bleibt gleich wie in Ihrem Originalskript) ...
    beat_label.config(text="--", fg="gray")
    update_font_size()

def toggle_fullscreen(event=None):
    # ... (Funktion bleibt gleich wie in Ihrem Originalskript) ...
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.attributes("-fullscreen", is_fullscreen)
    update_font_size()

def exit_app(event=None):
    global outport, running # Stopp-Signal senden
    running = False
    if outport:
        outport.send(mido.Message('stop')) # Stopp-Befehl an SPD-SX senden
        outport.close() 
    root.destroy()

# --- MIDI Clock Sender Logik ---

ticks_pro_beat = 24
# Zeitintervall in Sekunden zwischen jedem der 24 Ticks, basierend auf BPM
# 60 Sekunden pro Minute / BPM = Sekunden pro Viertelnote
# Sekunden pro Viertelnote / 24 Ticks = Sekunden pro Tick
tick_interval = (60.0 / bpm) / ticks_pro_beat
running = False
last_tick_time = 0

def send_midi_clock_loop():
    global last_tick_time, total_beats_count, current_beat_in_measure, running

    if not running and is_connected:
        outport.send(mido.Message('start'))
        running = True
        total_beats_count = start_value
        last_tick_time = time.time()
        print("MIDI Clock gestartet.")
        update_gui_beat(str(1), is_takt_anfang=True) # Startet auf Beat 1

    if running and is_connected:
        current_time = time.time()
        if current_time - last_tick_time >= tick_interval:
            # Sende einen Clock-Tick (System Common Message, kein mido.Message Objekt benötigt, nur Byte-Wert)
            outport.send(mido.Message('clock')) 
            last_tick_time += tick_interval # Nächsten Zeitpunkt planen

            # GUI Update Logik (für jeden 24. Tick)
            # Wir müssen die Ticks zählen, die die GUI anzeigt, auch wenn wir sie selbst senden
            ticks_since_start = int((current_time - last_tick_time) / tick_interval) + 1 # Hacky way to count beats
            
            # Da wir die Zeitbasis nutzen, müssen wir Beats anders zählen
            # Die GUI-Logik aus Ihrem alten Skript ist schwieriger 1:1 zu mappen
            # Wir vereinfachen die GUI-Anzeige hier, um mit der Clock zu synchronisieren
            
            # Bessere Methode: Ein separates GUI-Timer-Callback nutzen, 
            # aber für die einfache Metronom-Ansicht können wir das hier tun:

            if (total_beats_count % ticks_pro_beat) == 0:
                current_beat_in_measure = ((total_beats_count // ticks_pro_beat) % beats_per_measure) + 1
                update_gui_beat(str(current_beat_in_measure), is_takt_anfang=(current_beat_in_measure == 1))

            total_beats_count += 1
            

    # Das Tkinter after-System ruft diese Funktion kontinuierlich auf, 
    # um sicherzustellen, dass die GUI responsiv bleibt und die Clock gesendet wird.
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
    # Öffnet einen Output-Port
    outport = mido.open_output(midi_port_name)
    is_connected = True
    print(f"Sende MIDI Clock an {midi_port_name} bei {bpm} BPM.")
    print(f"Drücke 'f' für Fullscreen, 'x' oder 'Esc' zum Beenden.")

    # Initial die Schriftgröße setzen
    update_font_size()
    # Startet den Clock-Sender-Loop
    root.after(10, send_midi_clock_loop) 
    root.mainloop()

except IOError as e:
    print(f"Fehler beim Öffnen des Output-Ports '{midi_port_name}': {e}")
    print("Stellen Sie sicher, dass das Roland UM-ONE angeschlossen ist und der Portname oben im Skript korrekt gesetzt ist.")
    sys.exit(1)
except KeyboardInterrupt:
    pass 
finally:
    if outport:
        outport.send(mido.Message('stop'))
        outport.close()
    print("Skript beendet.")

