# Chords - Piano Playback with FluidSynth

A Jupyter notebook that demonstrates playing musical chords using FluidSynth with a piano SoundFont.

## Features

- Plays an A major triad (A4, C#5, E5) using FluidSynth
- Uses a high-quality piano SoundFont for realistic sound
- Demonstrates MIDI note generation and audio playback
- Compatible with macOS (CoreAudio), Linux (ALSA), and Windows (DSound)

## Requirements

- Python 3.x
- conda environment "hhl" (or equivalent)
- FluidSynth library
- Jupyter Notebook

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd chords
```

2. Install required packages in your conda environment:
```bash
conda activate hhl
pip install pyfluidsynth mido python-rtmidi
```

3. Run the notebook:
```bash
jupyter notebook chords.ipynb
```

## Usage

The notebook will:
1. Load the piano SoundFont
2. Play an A major triad for 2.5 seconds
3. Clean up resources

## Files

- `chords.ipynb` - Main notebook with chord playback code
- `piano.sf2` - Piano SoundFont file
- `UprightPianoKW-small-SF2-20190703/` - Additional piano samples and SFZ files

## Troubleshooting

- **FluidSynth library error**: Make sure you have the system FluidSynth library installed
- **Audio not playing**: Check your audio settings and ensure the correct audio driver is selected
- **File not found**: Ensure the `piano.sf2` file is in the same directory as the notebook

## License

This project uses the CC0 licensed piano samples from the UprightPianoKW collection.
