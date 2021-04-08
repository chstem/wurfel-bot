import os
import random
import re

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.ext import MessageHandler, Filters

TOKEN = os.environ['WURFEL_TG_TOKEN']
DICE_FILE = os.getenv('WURFEL_FILES', 'dices.yaml')

with open(DICE_FILE) as f:
    dices = load(f, Loader=Loader)

re_triggers = re.compile('|'.join(dices['triggers']), re.I)
parse_mode = ParseMode.MARKDOWN if dices['markdown'] else None


def throw(dices):

    # randomly select values
    results = [random.choice(values) for values in dices['dices']]

    # resolve annotations
    while True:
        lengths = [len(i) if isinstance(i, dict) else 0 for i in results]
        try:
            i = lengths.index(1)
        except ValueError:
            raise ValueError('No single key found. Check your yaml file.')
        key = list(results[i].keys())[0]
        results = [i.get(key, i) if isinstance(i, dict) else i for i in results]

    return dices['separator'].join(map(str, results))


def throw_command(update: Update, context: CallbackContext) -> None:
    text = throw(dices)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=parse_mode)


def throw_trigger(update, context):
    #if TRIGGER_RE.search(update.message.text):
    if re_triggers.search(update.message.text):
        text = throw(dices)
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=parse_mode)


updater = Updater(TOKEN)
fname = os.path.basename(DICE_FILE)
command_name = fname[:fname.rindex('.')],
updater.dispatcher.add_handler(CommandHandler(command_name, throw_command))

message_handler = MessageHandler(Filters.text & (~Filters.command), throw_trigger)
updater.dispatcher.add_handler(message_handler)


if __name__ == '__main__':
    updater.start_polling()
    updater.idle()
