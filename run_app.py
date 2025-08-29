#!/usr/bin/env python3
"""
Simple script to run the Flask chord generator app
"""

import os
import sys

def check_dependencies():
    """Check if required files exist"""
    required_files = [
        "piano.sf2",
        "app.py",
        "templates/index.html"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all files are in the current directory.")
        return False
    
    return True

def main():
    """Main function to run the app"""
    print("🎵 Chord Generator Flask App")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ All required files found!")
    print("🚀 Starting Flask app...")
    print("\n📱 Open your browser and go to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the app")
    print("-" * 40)
    
    try:
        # Import and run the app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install Flask: pip install flask")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
