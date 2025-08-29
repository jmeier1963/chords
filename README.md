# Chords - Interactive Music Theory Web Application

A Flask web application that generates and plays musical chords, scales, and progressions using FluidSynth with AI-powered music analysis.

## Features

### 🎵 Core Functionality

- **Chord Generation & Playback**: Input any chord (e.g., "C major", "F#m7") and hear it played
- **12-Bar Blues Progression**: Play complete blues progressions in any key
- **Scale Playback**: AI-suggested scales for improvisation over chords, played note-by-note
- **MIDI File Generation**: Download MIDI files for further editing

### 🤖 AI-Powered Features

- **Song Analysis**: Input a song title and get the chord progression with AI analysis
- **Scale Suggestions**: OpenAI-powered recommendations for scales that fit over any chord
- **Music Theory Integration**: Intelligent chord and scale relationships

### 🎹 Technical Features

- **High-Quality Audio**: Uses FluidSynth with piano SoundFont for realistic sound
- **Cross-Platform**: Compatible with macOS (CoreAudio), Linux (ALSA), and Windows (DSound)
- **Real-Time Playback**: Instant audio generation and playback
- **Responsive Web Interface**: Modern, intuitive UI for all music functions

## Requirements

- Python 3.8+
- conda environment "hhl" (or equivalent)
- FluidSynth system library
- OpenAI API key (for AI features)
- Modern web browser

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/jmeier1963/chords.git
cd chords
```

### 2. Install System Dependencies

**macOS:**

```bash
brew install fluid-synth
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install fluidsynth
```

**Windows:**

Download FluidSynth from the official website or use a package manager like Chocolatey.

### 3. Set Up Python Environment

```bash
conda activate hhl
pip install -r requirements.txt
```

### 4. Configure OpenAI API (Optional)

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_api_key_here
```

### 5. Ensure SoundFont File

Make sure `piano.sf2` is in the project root directory.

## Usage

### Starting the Application

```bash
python app.py
```

Or use the convenience script:

```bash
python run_app.py
```

The application will be available at `http://localhost:5000`

### Web Interface Features

#### 🎵 Play Chord

1. Enter a chord (e.g., "C major", "F#m", "Bb7")
2. Click "🎵 Play Chord"
3. Hear the chord and see suggested scales for improvisation
4. Click "🎹 Play Scale" to hear any suggested scale

#### 🎸 12-Bar Blues

1. Select a root note (e.g., "C", "F", "G")
2. Click "Play 12-Bar Blues Progression"
3. Hear the complete blues progression

#### 🤖 AI Song Analysis

1. Enter a song title (e.g., "Hotel California", "Wonderwall")
2. Click "Analyze Song & Play Chords"
3. Get AI-generated chord progression and play it

## Project Structure

```
chords/
├── app.py                 # Main Flask application
├── run_app.py            # Convenience script to run the app
├── requirements.txt      # Python dependencies
├── piano.sf2            # Piano SoundFont file
├── .env                 # Environment variables (create this)
├── templates/
│   └── index.html       # Web interface
├── chords.ipynb         # Original Jupyter notebook
└── README.md            # This file
```

## API Endpoints

- `GET /` - Main web interface
- `POST /generate_chord` - Generate and play a chord
- `POST /play_12bar_blues` - Play 12-bar blues progression
- `POST /analyze_song` - AI-powered song analysis
- `POST /play_scale` - Play a scale note-by-note
- `GET /download_midi` - Download generated MIDI file

## Dependencies

### Core Dependencies

- `flask>=2.0.0` - Web framework
- `pyfluidsynth` - Audio synthesis
- `mido` - MIDI file handling
- `python-rtmidi` - MIDI interface

### AI Features

- `openai>=1.0.0` - OpenAI API client
- `python-dotenv>=0.19.0` - Environment variable management

### Development

- `jupyter` - Jupyter notebook support
- `notebook` - Jupyter notebook interface
- `numpy` - Numerical operations
- `ipykernel` - Jupyter kernel

## Troubleshooting

### Common Issues

**"Couldn't find the FluidSynth library"**

- Install the system FluidSynth library (see Installation section)
- Ensure the library is in your system PATH

**Audio not playing**

- Check your audio settings and volume
- Verify the correct audio driver is selected
- Ensure `piano.sf2` is in the project root

**OpenAI API errors**

- Verify your API key in the `.env` file
- Check your OpenAI account status and credits
- Ensure the API key has the correct permissions

**Scale playback issues**

- The application now uses static MIDI mapping for reliable ascending scales
- All scales play in strict ascending order with proper octave progression

### Debug Mode

Enable debug logging by checking the browser console for detailed information about requests and responses.

## Testing & Code Structure

### Running Tests

Test individual endpoints using curl:

```bash
# Test chord generation
curl -X POST http://localhost:5000/generate_chord \
  -H "Content-Type: application/json" \
  -d '{"chord":"C major","duration":1.0,"velocity":80}'

# Test scale playback
curl -X POST http://localhost:5000/play_scale \
  -H "Content-Type: application/json" \
  -d '{"scale_notes":["C","D","E","F","G","A","B"],"duration":0.6,"velocity":80}'
```

### Code Structure

- **Audio Generation**: `generate_chord_audio()`, `play_scale_notes()`
- **Music Theory**: `get_chord_notes()`, `get_4th_note()`, `get_5th_note()`
- **AI Integration**: `analyze_song_with_openai()`, `analyze_scales_for_chord()`
- **Web Routes**: Chord generation, blues progression, song analysis, scale playback

## Recent Updates

### Scale Playback Improvements (Latest)

- **Static MIDI Mapping**: Replaced complex calculations with reliable three-octave mapping
- **Ascending Order**: All scales now play in strict ascending order
- **Octave Progression**: Natural progression through octaves without calculation errors
- **Enhanced Reliability**: Consistent playback for all scale types

### Previous Features

- **AI Song Analysis**: GPT-4o-mini powered chord progression analysis
- **Scale Suggestions**: Intelligent scale recommendations for improvisation
- **12-Bar Blues**: Complete blues progression playback
- **MIDI Generation**: Downloadable MIDI files for further editing

## License

This project uses the CC0 licensed piano samples from the UprightPianoKW collection.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the browser console for error messages
3. Verify all dependencies are properly installed
4. Ensure the FluidSynth system library is available
