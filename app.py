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

@app.route('/play_12bar_blues', methods=['POST'])
def play_12bar_blues():
    """Play a 12-bar blues progression in the chosen key"""
    try:
        data = request.get_json()
        root_note = data.get('root_note', 'C')
        duration = float(data.get('duration', 1.0))  # Shorter duration for progression
        velocity = int(data.get('velocity', 96))
        
        # 12-bar blues progression pattern
        # I = root major, IV = 4th major, V = 5th major
        blues_progression = [
            (root_note, "major"),      # Bar 1-4: I chord
            (root_note, "major"),      # Bar 2
            (root_note, "major"),      # Bar 3
            (root_note, "major"),      # Bar 4
            (get_4th_note(root_note), "major"),      # Bar 5-6: IV chord
            (get_4th_note(root_note), "major"),      # Bar 6
            (root_note, "major"),      # Bar 7-8: I chord
            (root_note, "major"),      # Bar 8
            (get_5th_note(root_note), "major"),      # Bar 9: V chord
            (get_4th_note(root_note), "major"),      # Bar 10: IV chord
            (root_note, "major"),      # Bar 11-12: I chord
            (root_note, "major")       # Bar 12
        ]
        
        progression_info = []
        all_notes = []
        
        # Play each chord in the progression
        for i, (note, chord_type) in enumerate(blues_progression, 1):
            chord_notes = get_chord_notes(chord_type, note)
            note_names = [get_note_name(note) for note in chord_notes]
            
            progression_info.append({
                "bar": i,
                "chord": f"{note} {chord_type}",
                "notes": note_names,
                "midi_notes": chord_notes
            })
            
            # Play the chord
            audio_result = generate_chord_audio(chord_notes, duration, velocity)
            if audio_result["success"]:
                all_notes.extend(chord_notes)
            else:
                # If audio fails, just collect the notes for MIDI
                all_notes.extend(chord_notes)
        
        # Create MIDI file for the entire progression
        midi_result = create_midi_file(all_notes, duration * 12, velocity)
        
        if midi_result["success"]:
            result = {
                "success": True,
                "progression": progression_info,
                "root_note": root_note,
                "method": "midi",
                "file_path": midi_result["file_path"],
                "message": f"Successfully played 12-bar blues in {root_note} key! Created MIDI file for download."
            }
        else:
            result = {
                "success": False,
                "progression": progression_info,
                "root_note": root_note,
                "error": midi_result.get("error", "Unknown"),
                "message": f"Failed to create MIDI file for 12-bar blues in {root_note} key"
            }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "An error occurred while processing the 12-bar blues request"
        })

def get_4th_note(root_note):
    """Get the 4th note (perfect 4th) from the root note"""
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    root_index = notes.index(root_note)
    fourth_index = (root_index + 5) % 12  # Perfect 4th is 5 semitones up
    return notes[fourth_index]

def get_5th_note(root_note):
    """Get the 5th note (perfect 5th) from the root note"""
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    root_index = notes.index(root_note)
    fifth_index = (root_index + 7) % 12  # Perfect 5th is 7 semitones up
    return notes[fifth_index]

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
