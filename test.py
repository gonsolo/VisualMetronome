import mido
import time
import sys

#midi_port_name = 'UM-ONE:UM-ONE MIDI 1 24:0'  # <-- Dieser Name ist korrekt!
midi_port_name = 'UM-ONE:UM-ONE MIDI 1 20:0'

# Die Namen aller verfügbaren Ports ausgeben
def list_ports():
    print("--- Verfügbare MIDI-Eingänge ---")
    ports = mido.get_input_names()
    if not ports:
        print("Kein MIDI-Eingang gefunden. Ist das UM-ONE angeschlossen?")
    else:
        for name in ports:
            print(f"- {name}")
    print("---------------------------------")
    print("Bitte den Namen oben in 'midi_port_name' eintragen und neu starten.")


def monitor_midi():
    print(f"\nVersuche Verbindung zu: '{midi_port_name}'...")
    
    inport = None
    try:
        # Port öffnen
        inport = mido.open_input(midi_port_name)
        print(f"**Verbunden mit {midi_port_name}. Warte auf MIDI-Nachrichten...**")
        print("Starte bitte jetzt die Rhythmus-Funktion (Metronom/Pattern) auf dem Yamaha CLP-535.")
        print("Drücke Strg+C zum Beenden.")
        
        # Endlosschleife zum Lesen der Nachrichten
        while True:
            for msg in inport.iter_pending():
                # Filtere 'clock'-Nachrichten, um die Ausgabe nicht zu überfluten
                if msg.type == 'clock':
                    print('.', end='', flush=True) # Zeigt Punkte für jede Takt-Nachricht
                else:
                    # Gibt alle anderen Nachrichten (start, stop, noten) vollständig aus
                    print(f'\n[Nachricht empfangen]: {msg}')
            time.sleep(0.01) # Kurze Pause

    except IOError as e:
        print(f"\n*** FEHLER beim Öffnen des Ports: '{midi_port_name}' ***")
        print(f"Details: {e}")
        print("--> Überprüfen Sie den Port-Namen und die Verbindung.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nTest beendet.")
    finally:
        if inport:
            inport.close()

# --- Hauptprogramm ---
list_ports()
monitor_midi()
