import os
import openai
import telebot
import requests
from io import BytesIO
from PIL import Image
from threading import Thread
import time as t
from gtts import gTTS
import speech_recognition as sr

openai.api_key = os.getenv("OPENAI_API_KEY")
telegramAPI = os.getenv("telegramKey")

bot = telebot.TeleBot(telegramAPI)

ai = 'Aiva'
human = 'Human'

start_sequence = f"\n{ai}:"
restart_sequence = f"\n{human}: "

init_prompt = f"The following is a conversation with a helpful AI chatbot named {ai} and a human named {human}. The chatbot is helpful, creative, clever, and very friendly."

prompt = init_prompt
remember = ""

# Model
maxTokens = 1024

audioMode = True

time = 0

def getResponse(prompt):
    global maxTokens, human, ai
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.9,
        max_tokens=maxTokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[f" {human}:", f" {ai}:"]
    )["choices"][0]['text']

    audio = None
    if audioMode:
        output = gTTS(text = response, lang = 'en', slow = False)
        audio = BytesIO()
        output.write_to_fp(audio)
        audio.seek(0)

        r = sr.Recognizer()
        r.adjust_for_ambient_noise(audio, duration=0.2)
        MyText = r.recognize_google(audio)
        MyText = MyText.lower()
        print(MyText)

    return response, audio

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,f'Chat id: {message.chat.id}')
    bot.send_message(message.chat.id,'Hello, I am Paco. I am a chatbot created by Davide Berweger. How can I help you today?')

@bot.message_handler(commands=['help'])
def start(message):
    text = '1. /history\n2. /model\n3. /remember\n4. /forget\n5. /fakePerson\n6. /fakeCat\n7. /fakeArt\n8. /fakeHorse\n9. /fakeCity'
    bot.send_message(message.chat.id,text)

@bot.message_handler(commands=['history'])
def history(message):
    global prompt
    print('Getting history...')
    bot.send_message(message.chat.id,prompt)

@bot.message_handler(commands=['forget'])
def forget(message):
    global prompt,time
    time = 0
    print('Forgetting...')
    prompt = init_prompt
    bot.send_message(message.chat.id,'I got amnesia... I forgot all of my memories...')

@bot.message_handler(commands=['audio'])
def audio(message):
    global audioMode
    audioMode = not audioMode
    bot.send_message(message.chat.id,f'Audio mode: {audioMode}')

@bot.message_handler(commands=['remember'])
def forget(message):
    global remember,prompt
    print('Remembering...')
    remember = message.text[9:]
    bot.send_message(message.chat.id,'Remembering...')
    bot.send_message(message.chat.id, f'I remember that: {remember}')
    prompt = f'{remember}\n\n{prompt}'

@bot.message_handler(commands=['fakePerson'])
def fakePerson(message):
    print('faking image...')
    url = 'https://thispersondoesnotexist.com/image'
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.send_photo(message.chat.id, img)

@bot.message_handler(commands=['fakeCat'])
def fakeCat(message):
    print('faking cat...')
    url = 'https://thiscatdoesnotexist.com/'
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.send_photo(message.chat.id, img)

@bot.message_handler(commands=['fakeArt'])
def fakeArt(message):
    print('faking art...')
    url = 'https://thisartworkdoesnotexist.com/'
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.send_photo(message.chat.id, img)

@bot.message_handler(commands=['fakeHorse'])
def fakeHorse(message):
    print('faking horse...')
    url = 'https://thishorsedoesnotexist.com/'
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.send_photo(message.chat.id, img)

@bot.message_handler(commands=['fakeCity'])
def fakeCity(message):
    print('faking city...')
    url = 'http://thiscitydoesnotexist.com/static/images/mgdwrstjqskiqxwg.jpg'
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.send_photo(message.chat.id, img)

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    global prompt, time, audioMode, human, ai
    time = 300
    
    if message.text[0] != '.' and '/' not in message.text:
        prompt += f'{human}: {message.text}\n{ai}: '
        response, audio = getResponse(prompt)
        response = response.replace("\n","")
        prompt += f'{response}\n'
        if audioMode:
            bot.send_audio(message.chat.id, audio)
        else:
            bot.send_message(message.chat.id,response)
            
        print(f'message: {message.text}, response: {response}')

class myClass(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        global time, prompt
        while True:
            if time == 0:
                time = -1
                print('Forgetting the conversation...')
                prompt = init_prompt
                t.sleep(60)
            elif time > 0:
                time -= 1

            t.sleep(1)

myClass()

bot.infinity_polling()