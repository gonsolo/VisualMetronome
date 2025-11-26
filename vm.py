import mido
import time
import sys

midi_port_name = 'Midi Through:Midi Through Port-0 14:0'
beats_per_measure = 4 

try:
    with mido.open_input(midi_port_name) as inport:
        print(f"Lausche auf MIDI-Port: {midi_port_name}")
        print("Warten auf Start-Signal von Ardour...")

        ticks_pro_beat = 24
        ticks_received = 0
        # Starten Sie den Zähler mit einem Offset von -1 Beat
        start_value = 0
        total_beats_count = start_value
        current_beat_in_measure = 0

        while True:
            msg = inport.receive()
            
            if msg.type == 'start':
                # Bei Start zurücksetzen, der Offset wird beim ersten Takt greifen
                total_beats_count = start_value
                ticks_received = 0
                print("\n--- Ardour Wiedergabe gestartet (warte auf 1. Beat) ---\n")

            elif msg.type == 'clock':
                ticks_received += 1
                if ticks_received % ticks_pro_beat == 0:
                    
                    # Dies ist der Punkt, an dem ein neuer Beat beginnt
                    total_beats_count += 1
                    
                    # Nur positive Beat-Zahlen anzeigen (wenn der Offset aufgebraucht ist)
                    if total_beats_count >= 0:
                        current_beat_in_measure = (total_beats_count % beats_per_measure) + 1
                        
                        if current_beat_in_measure == 1:
                            print(f"[{time.strftime('%H:%M:%S')}] BEAT {current_beat_in_measure} (Taktanfang)")
                        else:
                            print(f"[{time.strftime('%H:%M:%S')}] Beat {current_beat_in_measure}")
                        
                        # HIER: Visuelle Darstellung auslösen
            
            elif msg.type == 'stop':
                print("\n--- Ardour Wiedergabe gestoppt ---\n")
                total_beats_count = start_value


except KeyboardInterrupt:
    print("\nSkript beendet.")
except IOError as e:
    print(f"Fehler beim Öffnen des Ports: {e}")
    sys.exit(1)


