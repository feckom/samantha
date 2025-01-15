import concurrent.futures
import asyncio
from ollama import chat, ChatResponse
from kokoro_onnx import Kokoro
import simpleaudio as sa
import nltk
import json
import configparser
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Load configuration
config = configparser.ConfigParser()
config.read('samantha.cfg')

# Load Kokoro TTS model
kokoro = Kokoro(config['Settings']['tts_model'], config['Settings']['voices_file'])

class ConversationManager:
    def __init__(self):
        self.past_conversations = []

    def add_conversation(self, user_input, ai_response):
        self.past_conversations.append((user_input, ai_response))

    def get_past_conversations(self):
        return self.past_conversations

# Initialize conversation manager
conversation_manager = ConversationManager()

async def query_ollama_async(prompt, past_conversations=None):
    try:
        context = ""
        if past_conversations:
            context += "Past Conversations:\n" + "\n".join(
                f"- User: {conv[0]}\n- Samantha: {conv[1]}" for conv in past_conversations
            )

        # Form the full prompt without adding any greeting.
        full_prompt = (
            f"{config['Prompts']['system_prompt']}\n"
            f"Here is some context:\n{context}\n"
            f"{config['Prompts']['user_prompt'].format(user_input=prompt)}"
        )

        # Get response from the model
        response: ChatResponse = chat(
            model=config['Settings']['ollama_model'],
            messages=[{'role': 'user', 'content': full_prompt}]
        )
        return response.message.content
    except Exception as e:
        print(f"Error generating response from Ollama: {e}")
        return "Sorry, I couldn't generate a response."

def async_cached_text_to_speech(text, voice=None, lang=None):
    try:
        samples, sample_rate = kokoro.create(
            text,
            voice=voice or config['Settings']['default_voice'],
            lang=lang or config['Settings']['default_language'],
            speed=float(config['Settings']['tts_speed'])
        )
        samples = (samples * 32767).astype("int16")
        return samples, sample_rate
    except Exception as e:
        print(f"Error in text-to-speech conversion: {e}")
        return None, None

async def play_audio(samples, sample_rate):
    try:
        audio = sa.play_buffer(samples, 1, 2, sample_rate)
        audio.wait_done()
    except Exception as e:
        print(f"Error playing audio: {e}")

async def main():
    user_name = "User"  # Hardcoded for simplicity
    user_color = getattr(Fore, config['Colors']['user_color'].upper())
    samantha_color = getattr(Fore, config['Colors']['samantha_color'].upper())

    print(f"{samantha_color}Samantha is ready to chat! Type your questions below. (Type 'exit' to quit).{Style.RESET_ALL}")

    # Start a thread pool to handle concurrent execution
    with concurrent.futures.ThreadPoolExecutor() as executor:
        while True:
            user_input = input(f"\n{user_name}: ")

            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye! I’ll be here whenever you need me.")
                break

            print("Thinking...")

            # Execute the query asynchronously
            response = await query_ollama_async(user_input, past_conversations=conversation_manager.get_past_conversations())

            # Store the conversation in memory
            conversation_manager.add_conversation(user_input, response)

            # Split the response into sentences and process them concurrently
            sentences = nltk.sent_tokenize(response)

            # Create audio samples for each sentence concurrently
            audio_futures = []
            for sentence in sentences:
                audio_future = executor.submit(async_cached_text_to_speech, sentence)
                audio_futures.append(audio_future)

            # Play audio and print the response
            for i, sentence in enumerate(sentences):
                print(f"{samantha_color}{sentence}{Style.RESET_ALL}")
                samples, sample_rate = await asyncio.to_thread(audio_futures[i].result)

                if samples is not None:
                    await play_audio(samples, sample_rate)

if __name__ == "__main__":
    asyncio.run(main())
