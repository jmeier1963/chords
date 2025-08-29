#!/usr/bin/env python3
"""
Flask App for Chord Generation
Takes user input for chords and generates audio using FluidSynth
"""

from flask import Flask, render_template, request, jsonify, send_file
import platform
import os
import time
import tempfile
import json
from pathlib import Path

app = Flask(__name__)

# MIDI note to note name mapping
NOTE_NAMES = {
    0: "C", 1: "C#", 2: "D", 3: "D#", 4: "E", 5: "F", 
    6: "F#", 7: "G", 8: "G#", 9: "A", 10: "A#", 11: "B"
}

def get_note_name(midi_note):
    """Convert MIDI note number to note name with octave"""
    note_name = NOTE_NAMES[midi_note % 12]
    octave = (midi_note // 12) - 1
    return f"{note_name}{octave}"

def get_driver():
    """Smart driver selection for cross-platform compatibility"""
    system = platform.system().lower()
    if system == "darwin": 
        return "coreaudio"
    elif system == "linux":
        return "alsa" if os.path.exists("/dev/snd") else "pulseaudio"
    elif system == "windows": 
        return "dsound"
    else: 
        return "pulseaudio"

def generate_chord_audio(chord_notes, duration=2.5, velocity=96):
    """Generate audio for a chord using FluidSynth"""
    try:
        import fluidsynth
        
        # Get best driver for platform
        driver = get_driver()
        print(f"🎯 Using {driver} driver")
        
        # Initialize FluidSynth
        sf2 = "./piano.sf2"
        fs = fluidsynth.Synth()
        fs.start(driver=driver)
        
        # Load SoundFont
        sfid = fs.sfload(sf2)
        fs.program_select(0, sfid, 0, 0)
        
        # Play chord
        print("🎵 Playing chord...")
        for note in chord_notes:
            fs.noteon(0, note, velocity)
        
        time.sleep(duration)
        
        # Stop notes
        for note in chord_notes:
            fs.noteoff(0, note)
        
        fs.delete()
        return {"success": True, "method": "audio", "driver": driver}
        
    except Exception as e:
        print(f"⚠️ Audio failed: {e}")
        return {"success": False, "error": str(e), "method": "audio"}

def create_midi_file(chord_notes, duration=2.5, velocity=96):
    """Create MIDI file as fallback when audio fails"""
    try:
        import mido
        
        # Create MIDI file
        mid = mido.MidiFile()
        track = mido.MidiTrack()
        mid.tracks.append(track)
        
        # Set tempo
        track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120)))
        
        # Add note on messages
        for note in chord_notes:
            track.append(mido.Message("note_on", note=note, velocity=velocity, time=0))
        
        # Calculate time for note duration (in MIDI ticks)
        note_duration = int(mido.bpm2tempo(120) * duration / 60)
        
        # Add note off messages
        track.append(mido.Message("note_off", note=chord_notes[0], velocity=0, time=note_duration))
        for note in chord_notes[1:]:
            track.append(mido.Message("note_off", note=note, velocity=0, time=0))
        
        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        midi_path = os.path.join(temp_dir, "chord_output.mid")
        mid.save(midi_path)
        
        return {"success": True, "method": "midi", "file_path": midi_path}
        
    except Exception as e:
        return {"success": False, "error": str(e), "method": "midi"}

def get_chord_notes(chord_type, root_note="C"):
    """Get MIDI note numbers for common chord types"""
    # Root note to MIDI number mapping (C4 = 60)
    root_notes = {"C": 60, "C#": 61, "D": 62, "D#": 63, "E": 64, "F": 65, 
                  "F#": 66, "G": 67, "G#": 68, "A": 69, "A#": 70, "B": 71}
    
    root = root_notes.get(root_note.upper(), 60)
    
    chord_patterns = {
        "major": [0, 4, 7],           # Root, Major 3rd, Perfect 5th
        "minor": [0, 3, 7],           # Root, Minor 3rd, Perfect 5th
        "diminished": [0, 3, 6],      # Root, Minor 3rd, Diminished 5th
        "augmented": [0, 4, 8],       # Root, Major 3rd, Augmented 5th
        "major7": [0, 4, 7, 11],     # Major 7th chord
        "minor7": [0, 3, 7, 10],     # Minor 7th chord
        "dominant7": [0, 4, 7, 10],  # Dominant 7th chord
        "diminished7": [0, 3, 6, 9], # Diminished 7th chord
        "power": [0, 7],              # Power chord (root + 5th)
    }
    
    if chord_type not in chord_patterns:
        chord_type = "major"  # Default to major
    
    return [root + interval for interval in chord_patterns[chord_type]]

@app.route('/')
def index():
    """Main page with chord input form"""
    return render_template('index.html')

@app.route('/generate_chord', methods=['POST'])
def generate_chord():
    """Generate chord audio based on user input"""
    try:
        data = request.get_json()
        root_note = data.get('root_note', 'C')
        chord_type = data.get('chord_type', 'major')
        duration = float(data.get('duration', 2.5))
        velocity = int(data.get('velocity', 96))
        
        # Get chord notes
        chord_notes = get_chord_notes(chord_type, root_note)
        note_names = [get_note_name(note) for note in chord_notes]
        
        # Try to generate audio first
        audio_result = generate_chord_audio(chord_notes, duration, velocity)
        
        if audio_result["success"]:
            # Audio succeeded
            result = {
                "success": True,
                "chord_notes": chord_notes,
                "note_names": note_names,
                "chord_type": chord_type,
                "root_note": root_note,
                "method": "audio",
                "driver": audio_result.get("driver", "unknown"),
                "message": f"Successfully played {root_note} {chord_type} chord: {', '.join(note_names)}"
            }
        else:
            # Audio failed, try MIDI
            midi_result = create_midi_file(chord_notes, duration, velocity)
            
            if midi_result["success"]:
                result = {
                    "success": True,
                    "chord_notes": chord_notes,
                    "note_names": note_names,
                    "chord_type": chord_type,
                    "root_note": root_note,
                    "method": "midi",
                    "file_path": midi_result["file_path"],
                    "message": f"Audio failed, created MIDI file for {root_note} {chord_type} chord: {', '.join(note_names)}"
                }
            else:
                # Both failed
                result = {
                    "success": False,
                    "chord_notes": chord_notes,
                    "note_names": note_names,
                    "chord_type": chord_type,
                    "root_note": root_note,
                    "error": f"Audio: {audio_result.get('error', 'Unknown')}, MIDI: {midi_result.get('error', 'Unknown')}",
                    "message": f"Failed to generate audio or MIDI for {root_note} {chord_type} chord"
                }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "An error occurred while processing the request"
        })

@app.route('/download_midi')
def download_midi():
    """Download the generated MIDI file"""
    try:
        temp_dir = tempfile.gettempdir()
        midi_path = os.path.join(temp_dir, "chord_output.mid")
        
        if os.path.exists(midi_path):
            return send_file(midi_path, as_attachment=True, download_name="chord_output.mid")
        else:
            return jsonify({"error": "MIDI file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
