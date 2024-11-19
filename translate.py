import asyncio
import os
from decode_audio import decode_tts_output
import json
import sys
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(file_dir)
import aiohttp
import dotenv
from base64 import decodebytes
dotenv.load_dotenv()
translations_file = os.path.join(file_dir, "translations.txt")

"""
README
Translates text from Vietnamese to English using Google Translate for Anki. These are helper functions that
will be used the main python file. 
"""

def find_translation(file_path, viet_word):
    with open(file_path, 'r', encoding='utf-8', errors="ignore") as file:
        for line in file:
            try:
                word, translation = line.strip().split(',', 1)
                if word == viet_word:
                    return translation
            except Exception as e:
                pass
    return None

async def translate_text(input):
    print(os.listdir(file_dir))
    input = input.strip().lower()
    find_trans = find_translation(translations_file, input)
    if(find_trans):
        print("translation in file already")
        return {"data": {"translations": [{"translatedText": find_trans}]}}
    url = "https://translation.googleapis.com/language/translate/v2?key=" + os.getenv("API")
    headers = {"Content-Type": "application/json"}
    
    # Fetch API key from environment variables
    api_key = os.getenv("API")
    #print(api_key)
    if not api_key:
        #print("API key not found")
        return

    query = {
        "q": input,
        "target": "en",
        "format": "text",
        "source": "vi",
        "model": "base",
    }
    
    # Asynchronous request using aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=query, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                english = result["data"]["translations"]
                english = [translation["translatedText"] for translation in english]
                english = ", ".join(english)
                with open(translations_file, "a") as file:
                    file.write(f"{input}, {english}\n")
                print(result)
                return result
            else:
                print(f"Error: {response.status}")
                print(await response.text())
                return None

async def tts(input):
    api_key = os.getenv("API")
    if not api_key:
        print("API key not found")
        return
    url = "https://texttospeech.googleapis.com/v1/text:synthesize?key=" + os.getenv("API")
    headers = {"Content-Type": "application/json"}
    query = {
        "input": {"text": input},
        "voice": {
            "languageCode": "vi",
            "ssmlGender": "MALE",
        },
        "audioConfig": {
            "audioEncoding": "MP3",
        },
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=query, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                result = result["audioContent"]
                input_file_txt = os.path.join(os.getcwd(), "audio", f"{input}.txt")
                output_file_mp3 = os.path.join(os.getcwd(), "audio", f"{input}.mp3")
                with open(output_file_mp3, "wb") as new_file:
                    new_file.write(decodebytes(result.encode('utf-8')))
            else:
                print(f"Error: {response.status}")
                print(await response.text())

# Run the async function
