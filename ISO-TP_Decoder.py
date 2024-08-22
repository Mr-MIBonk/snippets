#NOT FOR COMMERCIAL USE - IF YOU BOUGHT THIS YOU GOT RIPPED OFF
# ISO-TP_Decoder.py
# V 1.0.0 2024-08-21 by MIBonk

import sys
import os

# Definiere Konstanten für das Frame-Parsing
SF_MESSAGE_OFFSET = 5
FF_MESSAGE_START = 7
CF_MESSAGE_START = 5
FF_MESSAGE_LEN = 12
CF_MESSAGE_LEN = 14
ECU_HEADER_START = 0
ECU_HEADER_LEN = 3
FRAME_TYPE_INDEX = 3
FF_MSGLEN_START = 4
FF_MSGLEN_LEN = 3
FCF_ALLOWED_IND = 4
FCF_BLOCKSIZE_IND = 5
FCF_BLOCKSIZE_LEN = 2
FCF_ST_IND = 5
FCF_ST_LEN = 2

def hex_string_to_int(s):
    """Konvertiert eine Hex-String in eine Ganzzahl."""
    try:
        return int(s, 16)
    except ValueError:
        print(f"Fehler bei der Umwandlung von Hex-String: {s}", file=sys.stderr)
        return 0

def parse_single_frame(frame):
    """Parst einen Einzel-Frame."""
    try:
        message_len_chars = int(frame[4]) * 2
        if SF_MESSAGE_OFFSET + message_len_chars <= len(frame):
            return frame[SF_MESSAGE_OFFSET:SF_MESSAGE_OFFSET + message_len_chars]
        else:
            print(f"Fehler: Frame-Länge ist kürzer als erwartet. Frame: {frame}", file=sys.stderr)
            return ""
    except IndexError as e:
        print(f"IndexError in parse_single_frame: {e}", file=sys.stderr)
        return ""

def parse_first_frame(frame):
    """Parst einen ersten Frame."""
    try:
        message_len = hex_string_to_int(frame[FF_MSGLEN_START:FF_MSGLEN_START + FF_MSGLEN_LEN])
        message_len_chars_left = message_len * 2
        message = frame[FF_MESSAGE_START:FF_MESSAGE_START + FF_MESSAGE_LEN]
        message_len_chars_left -= FF_MESSAGE_LEN
        return message_len_chars_left, message
    except IndexError as e:
        print(f"IndexError in parse_first_frame: {e}", file=sys.stderr)
        return 0, ""

def parse_flow_control(frame):
    """Parst einen Flow-Control-Frame."""
    try:
        block_size = hex_string_to_int(frame[FCF_BLOCKSIZE_IND:FCF_BLOCKSIZE_IND + FCF_BLOCKSIZE_LEN])
        separation_time = hex_string_to_int(frame[FCF_ST_IND:FCF_ST_IND + FCF_ST_LEN])
#        print(f"Flow control frame received with Block Size: {block_size}, Separation Time: {separation_time}", file=sys.stderr)
        if frame[FCF_ALLOWED_IND] == '0':
            pass
        elif frame[FCF_ALLOWED_IND] == '1':
            pass
        elif frame[FCF_ALLOWED_IND] == '2':
            pass
    except IndexError as e:
        print(f"IndexError in parse_flow_control: {e}", file=sys.stderr)

def parse_consecutive_frame(frame, message, message_len_left):
    """Parst einen aufeinanderfolgenden Frame."""
    if message is None:
        message = ""
    if message_len_left > CF_MESSAGE_LEN:
        message += frame[CF_MESSAGE_START:CF_MESSAGE_START + CF_MESSAGE_LEN]
        message_len_left -= CF_MESSAGE_LEN
    else:
        message += frame[CF_MESSAGE_START:CF_MESSAGE_START + message_len_left]
        message_len_left = 0
    return message, message_len_left

def parse_frames_and_print_messages(transcript):
    """Parst alle Frames und druckt die Nachrichten."""
    message_len_left = -1
    message = None
    for frame in transcript:
        frame = frame.strip()
        frame = frame.lstrip('0')
        if not frame:
            continue  # Überspringe leere Zeilen

        if len(frame) <= FRAME_TYPE_INDEX:
            print(f"Fehler: Frame ist nach dem Entfernen der Nullen zu kurz: {frame}", file=sys.stderr)
            continue

        # Überprüfen, ob der Frame mit '17F' beginnt
        if frame.startswith('17F'):
            continue  # Frame überspringen, wenn es mit '17F' beginnt

        # Überprüfen, ob der Frame mit '700' beginnt         
        if frame.startswith('700'):
            continue  # Frame überspringen, wenn es mit '700' beginnt

        frame_type = frame[FRAME_TYPE_INDEX]

        if frame_type == '0':
            message = parse_single_frame(frame)
            print(f"0{frame[:3]}:{message}")
        elif frame_type == '1':
            message_len_left, message = parse_first_frame(frame)
        elif frame_type == '2':
            message, message_len_left = parse_consecutive_frame(frame, message, message_len_left)
            if message_len_left == 0:
                print(f"0{frame[ECU_HEADER_START:ECU_HEADER_START + ECU_HEADER_LEN]}:{message}")
        elif frame_type == '3':
            parse_flow_control(frame)
        else:
            print(f"Warnung: Ungültiger Typ des Frames erkannt: {frame_type}. Frame-Daten: {frame}", file=sys.stderr)

def convert_new_format_to_old(input_filename, output_filename):
    """Konvertiert das neue Format in das alte Format."""
    try:
        with open(input_filename, 'r', encoding='utf-8') as infile, open(output_filename, 'w', encoding='utf-8') as outfile:
            for line in infile:
                line = line.strip()
                
                if not line or line.startswith(';'):
                    continue
                
                parts = line.split()
                if len(parts) < 10:
                    print(f"Überspringe ungültige Zeile (nicht genug Teile): {line}", file=sys.stderr)
                    continue
                
                id_hex = parts[3]
                data_bytes = ''.join(parts[-8:])
                
                old_format_line = f"{id_hex}{data_bytes}\n"
                outfile.write(old_format_line)

        print(f"Die Datei wurde erfolgreich konvertiert und in {output_filename} gespeichert.", file=sys.stderr)

    except FileNotFoundError:
        print(f"Fehler: Datei '{input_filename}' wurde nicht gefunden.", file=sys.stderr)
    except PermissionError:
        print(f"Fehler: Keine Berechtigung zum Schreiben in '{output_filename}'.", file=sys.stderr)
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}", file=sys.stderr)

def main():
    """Hauptfunktion des Skripts."""
    if len(sys.argv) < 2:
        print("Usage: python ISO-TP_Decoder.py <input_filename> [-o --for no delete transfile output]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = 'output.tmp'  # Festgelegte Ausgabedatei für die Konvertierung

    # Überprüfen, ob der Parameter '-o' übergeben wurde
    keep_temp_file = '-o' in sys.argv

    # Definiere den Namen der Ausgabedatei für die Bildschirmausgabe
    screen_output_file = input_file.rsplit('.', 1)[0] + '_ISO-TP.txt'
    
    # Umleiten der Bildschirmausgabe
    original_stdout = sys.stdout
    try:
        with open(screen_output_file, 'w', encoding='utf-8') as screen_file:
            sys.stdout = screen_file
            convert_new_format_to_old(input_file, output_file)
            
            # Verarbeite die konvertierte Datei und leite die Ausgabe um
            with open(output_file, "r") as transcript:
                parse_frames_and_print_messages(transcript)
				
        # Stelle sicher, dass sys.stdout zurückgesetzt wird
        sys.stdout = original_stdout
            
        print(f"Die Verarbeitete Datei wurde erfolgreich in {screen_output_file} gespeichert.")
    except FileNotFoundError:
        print(f"Fehler: Datei '{input_file}' wurde nicht gefunden.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Fehler: Keine Berechtigung zum Schreiben in '{screen_output_file}' oder '{output_file}'.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Lösche die temporäre Datei, wenn der Parameter '-o' nicht angegeben wurde
        if not keep_temp_file and os.path.exists(output_file):
            os.remove(output_file)
            print(f"Die temporäre Datei '{output_file}' wurde gelöscht.")

if __name__ == "__main__":
    main()
