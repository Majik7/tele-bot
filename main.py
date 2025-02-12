import requests
import os
import telebot
from dotenv import load_dotenv
from telebot.types import BotCommand

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

commandlist = [
    telebot.types.BotCommand("start", "say hello to the bot :)"),
    telebot.types.BotCommand("catsays", "make a cat say something"),
    telebot.types.BotCommand("define", "define a word"),
]

bot.set_my_commands(commandlist)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "hello :D i am a new bot")

@bot.message_handler(commands=['angrycat'])
def catmood(message):
    bot.reply_to(message, "what is the cat's tag? - \n ")
    bot.register_next_step_handler(message, cattext)

def cattext(message):
    catsmood = message.text
    bot.reply_to(message, "ok now what is the cat saying?")
    bot.register_next_step_handler(message, catsays, catsmood)
    
def catsays(message, catsmood):
    args = message.text
    if not args:
        bot.reply_to(message, "give something to the cat to say >:(")
        return

    url = f"https://cataas.com/cat/{catsmood.replace(' ', '%20')}/says/{args.replace(' ', '%20')}"  # URL encode spaces
    res = requests.get(url)

    try:
        res.raise_for_status()
    except Exception as e:
        print(f'something went wrong :( - {e})')
        bot.reply_to(message, 'smth went wrong')
        return

    with open('cat.jpeg', 'wb') as f:
        f.write(res.content)

    with open('cat.jpeg', 'rb') as f:
        bot.send_photo(message.chat.id, f)

@bot.message_handler(commands=['define'])
def definestart(message):
    bot.reply_to(message, "what word do you want to define?")
    bot.register_next_step_handler(message, defineaword)
    
def defineaword(message):
    args = message.text.strip()
    if not args:
        bot.reply_to(message, "tell me a word to define bruh")
        return

    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{args}"
    res = requests.get(url)

    try:
        res.raise_for_status()
    except Exception as e:
        bot.reply_to(message, f'something went wrong - {e}')
        return
        
    data = res.json()

    definitions = []
    for entry in data:
        for meaning in entry.get("meanings", []):
            for definition in meaning.get("definitions", []):
                definitions.append(definition["definition"])
                if len(definitions) == 3:  # Limit to 3 definitions
                    break
            if len(definitions) == 3:
                break
        if len(definitions) == 3:
            break
            
    if not definitions:
        bot.reply_to(message, 'sorry no definitions were found :(')
        return
    
    responsetext = f"*Definitions :*\n" + "\n".join(f" - {d}" for d in definitions)

    bot.reply_to(message, responsetext, parse_mode = "Markdown")
    
bot.infinity_polling()
