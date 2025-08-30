#!/usr/bin/env python3

# Read the original file
with open('app.py', 'r') as f:
    content = f.read()

# Define the new function
new_function = '''def generate_chord_table_with_openai(song_title):
    """Use OpenAI GPT-5 with Responses API to generate a complete chord sheet"""
    try:
        SYSTEM_INSTRUCTIONS = """You are a meticulous music engraver.
- Output ONLY the chord sheet for the requested song, in Markdown.
- Avoid melody/lyrics unless asked; focus on harmonic form.
- Prefer concise, standard chord symbols (C, Dm7, G7, Cmaj7, F#m7b5, etc.).
- Include: title, composer/unknown, key, tempo (BPM), time signature, form sections (A, B, bridge), and barlines.
- Use section headers and 4-bar line breaks. Show turnarounds/endings if typical.
- If the song is not in the public domain or is ambiguous, produce a tasteful ORIGINAL progression in the requested style that evokes the vibe without quoting protected material.
- Offer a transpose table by common instruments at the end (Concert, Bb, Eb).
"""

        PROMPT_TEMPLATE = """Create a chord sheet.

Title: {title}
Style: jazz standard
Preferred key: C major
Time signature: 4/4
Tempo (BPM): 120

Formatting requirements:
- Markdown
- Header block with metadata
- Form diagram (AABA, ABAC, etc.) if applicable
- Chords laid out in 4-bar groupings with barlines like: | Cmaj7  | Dm7  G7 | Cmaj7  | Cmaj7 |
- Include an optional intro and ending if stylistically appropriate
- Provide a 2–4 bar vamp if common for the style
- Add a simple transpose table (Concert, Bb, Eb) for the first 8 bars

If the title is likely a copyrighted song, invent an original progression in the same style and clearly mark it as 'Original progression in the style of jazz standard'.
"""

        user_prompt = PROMPT_TEMPLATE.format(title=song_title)
        
        client = openai.OpenAI()
        
        # Create the response using the Responses API
        resp = client.responses.create(
            model="gpt-5",
            instructions=SYSTEM_INSTRUCTIONS,
            input=user_prompt,
        )

        output = resp.output_text  # unified text accessor (handles tool/segment stitching)
        
        # Add timestamp to the output
        from datetime import datetime
        stamped_output = f"# {song_title}\\n\\n_Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}_\\n\\n" + output
        
        print(f"Raw GPT-5 response for '{song_title}': {stamped_output}")
        
        return {"success": True, "data": {"chord_sheet": stamped_output}}
            
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return {"success": False, "error": str(e)}'''

# Find the start and end of the old function
start_marker = 'def generate_chord_table_with_openai(song_title):'
end_marker = 'if __name__ == \'__main__\':'

start_pos = content.find(start_marker)
end_pos = content.find(end_marker)

if start_pos != -1 and end_pos != -1:
    # Replace the old function with the new one
    new_content = content[:start_pos] + new_function + '\\n\\n' + content[end_pos:]
    
    # Write the updated content back to the file
    with open('app.py', 'w') as f:
        f.write(new_content)
    
    print("Function replaced successfully!")
else:
    print("Could not find function markers")
