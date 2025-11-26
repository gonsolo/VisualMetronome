import mido
import time
import sys

# Der Name des Ports, den wir gerade identifiziert haben
midi_port_name = 'Midi Through:Midi Through Port-0 14:0'

try:
    # Port zum Lesen öffnen
    inport = mido.open_input(midi_port_name)
    print(f"Lausche auf MIDI-Port: {midi_port_name}")
    print("Starten Sie jetzt die Wiedergabe in Ardour...")

    ticks_pro_beat = 24  # MIDI Clock sendet 24 Ticks pro Viertelnote
    ticks_received = 0
    beat_count = 0
    
    # Zustand für die visuelle Darstellung (ersetzen Sie dies später durch Pygame/Tkinter)
    is_on_beat = False

    while True:
        # Auf MIDI-Nachrichten warten (blockiert, bis eine Nachricht kommt)
        msg = inport.receive()
        
        if msg.type == 'clock':
            ticks_received += 1
            if ticks_received % ticks_pro_beat == 0:
                beat_count += 1
                is_on_beat = True
                # Hier passiert der "Klick" im Takt
                print(f"[{time.strftime('%H:%M:%S')}] KLICK! Beat: {beat_count}")
                # HIER: Fügen Sie Ihren Code für die visuelle Darstellung ein
                
        elif msg.type == 'start':
            beat_count = 0
            ticks_received = 0
            print("\n--- Ardour Wiedergabe gestartet ---\n")
        
        elif msg.type == 'stop':
            print("\n--- Ardour Wiedergabe gestoppt ---\n")

except IOError:
    print(f"Fehler: Konnte MIDI-Port '{midi_port_name}' nicht öffnen.")
    sys.exit(1)
except KeyboardInterrupt:
    print("\nSkript beendet.")
finally:
    if 'inport' in locals() and inport.is_open:
        inport.close()



