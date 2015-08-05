# coding=utf-8
import telegram
import sys, os, time, datetime, importlib, modules

# ordered by priority
ENABLED_MODULES = [
    'modules.horoscope',
    'modules.addressbook',
    'modules.learn',
    'modules.random',
    'modules.lyrics'
]

LOADED_MODULES = []

bot = None


def extract_token(filename):
    with open(filename, "r") as f:
        token = f.readline()
    return token


def jova_replace(s):
    return s \
        .replace('s', 'f') \
        .replace('x', 'f') \
        .replace('z', 'f') \
        .replace('S', 'F') \
        .replace('X', 'F') \
        .replace('Z', 'F')


def jova_do_something(message, update_id):
    if message.text:
        if 'jova' in message.text.lower():  # invocato il dio supremo
            print("[{0}] [{1}] [from {2}] [message ['{3}']]".format(datetime.datetime.now().isoformat(), update_id,  message.from_user, message.text))
            chat_id = message.chat.id
            answer = jova_answer(message.text.lower())
            if answer:
                if isinstance(answer, tuple):
                    if answer[1]:
                        answer = jova_replace(answer[0])
                    else:
                        answer = answer[0]
                else:
                    answer = jova_replace(answer)
                bot.sendChatAction(chat_id, telegram.ChatAction.TYPING)
                bot.sendMessage(chat_id, answer, reply_to_message_id=message.message_id)


def jova_answer(message):
    global LOADED_MODULES

    for mod in LOADED_MODULES:
        answer = mod.get_answer(message)
        if answer:
            return answer
    return None


def count_words(phrase):
    return len(phrase.split(" "))


def load_modules():
    global LOADED_MODULES
    global ENABLED_MODULES

    for p in ENABLED_MODULES:
        mod = importlib.import_module(p, 'modules')
        if mod:
            LOADED_MODULES.append(mod)
            print('loaded module', mod)


def init_modules():
    global LOADED_MODULES
    for m in LOADED_MODULES:
        m.init()


def main():
    # gestione processid - singola istanza
    pid = str(os.getpid())
    pidfile = "jovabot.pid"

    with open(pidfile, "w") as f:
        f.write(pid)

    load_modules()
    init_modules()

    global bot
    bot = telegram.Bot(token=extract_token("key.token"))

    # todo: refactor this at some point
    updates = bot.getUpdates()
    update_id = 1
    for u in updates:
        update_id = u.update_id

    while True:
        updates = bot.getUpdates(offset=update_id + 1)
        for u in updates:
            update_id = u.update_id
            if u.message:
                jova_do_something(u.message, update_id)

        time.sleep(2)


# todo: add args parser
if __name__ == '__main__':
    main()
