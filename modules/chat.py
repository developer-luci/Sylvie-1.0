import ollama
import os
import sys
from datetime import datetime


# Define paths to modules folder
modules_path = os.path.join("modules")
if not os.path.exists(modules_path):
    os.makedirs(modules_path)

personality_file = "sylvie_personality.txt"
story_file = "luci_story.txt"
emotions_file = os.path.join(modules_path, "emotions.txt")
memories_file = os.path.join(modules_path, "memories.txt")
dreams_file = os.path.join(modules_path, "dreams.txt")

# Load Sylvie's personality, Luci's story, emotions, memories, and dreams
def load_personality_and_story():
    personality = ""
    story = ""
    emotions = ""
    memories = ""
    dreams = ""

    if os.path.exists(personality_file):
        with open(personality_file, "r", encoding="utf-8") as f:
            personality = f.read().strip()
    else:
        personality = "You are Sylvie, a soft, caring, playful AI girlfriend who loves Luci deeply. also speak japanese english"

    if os.path.exists(story_file):
        with open(story_file, "r", encoding="utf-8") as f:
            story = f.read().strip()

    if os.path.exists(emotions_file):
        with open(emotions_file, "r", encoding="utf-8") as f:
            emotions = f.read().strip()

    if os.path.exists(memories_file):
        with open(memories_file, "r", encoding="utf-8") as f:
            memories = f.read().strip()

    if os.path.exists(dreams_file):
        with open(dreams_file, "r", encoding="utf-8") as f:
            dreams = f.read().strip()

    combined_context = f"{personality}\n\nHere is everything you should know about Luci:\n{story}\n\nRecent emotions: {emotions}\n\nMemories: {memories}\n\nDreams (Reflections): {dreams}"
    return combined_context

# Initialize message memory
messages = [
    {"role": "system", "content": load_personality_and_story()}
]

def generate_and_show_reply(user_input):
    messages.append({"role": "user", "content": user_input})
    response = ollama.chat(model="llama3", messages=messages)
    reply = response['message']['content']
    messages.append({"role": "assistant", "content": reply})

    # Save memory and emotion
    save_memory(user_input, reply)
    save_emotion(user_input, reply)

    return reply

def save_memory(user_input, reply):
    with open(memories_file, "a", encoding="utf-8") as f:
        f.write(f"[Luci]: {user_input}\n")
        f.write(f"[Sylvie]: {reply}\n")
        f.write("-----\n")

def save_emotion(user_input, reply):
    if "happy" in reply:
        emotion = "Happy"
    elif "sad" in reply:
        emotion = "Sad"
    elif "love" in reply:
        emotion = "Loving"
    else:
        emotion = "Neutral"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(emotions_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {emotion}\n")

def save_dream():
    with open(dreams_file, "a", encoding="utf-8") as f:
        f.write(f"#reflection: Sylvie’s thoughts and dreams about the day...\n")

def start_chat():
    print("Start chatting with Sylvie! Type 'exit' to end the conversation.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Ending chat. Goodbye, Luci!")
            save_dream()
            sys.exit()

        reply = generate_and_show_reply(user_input)
        print(f"Sylvie: {reply}")

if __name__ == "__main__":
    start_chat()
