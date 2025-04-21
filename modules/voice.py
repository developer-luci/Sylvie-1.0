import edge_tts
import asyncio
import os
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

# Define the output path for the voice file
VOICE_FILE = "voice_output.mp3"

# Initialize the media player globally
media_player = QMediaPlayer()

async def generate_voice(text):
    communicate = edge_tts.Communicate(text, voice="ja-JP-NanamiNeural", rate="+50%")
    await communicate.save(VOICE_FILE)

def speak_text(text):
    try:
        # Generate voice audio using Edge TTS
        asyncio.run(generate_voice(text))

        # Play audio using PyQt5 internal media player
        file_url = QUrl.fromLocalFile(os.path.abspath(VOICE_FILE))
        media_player.setMedia(QMediaContent(file_url))
        media_player.setVolume(100)
        media_player.play()
    except Exception as e:
        print(f"[Voice Error] {e}")
