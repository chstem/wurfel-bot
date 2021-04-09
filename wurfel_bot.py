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
DICE_FILES = os.getenv('WURFEL_FILES', 'dices.yaml,pets.yaml')


class DICE:

    def __init__(self, dice_file):

        with open(dice_file) as f:
            dices = load(f, Loader=Loader)

        self.re_triggers = re.compile('|'.join(dices['triggers']), re.I)
        self.parse_mode = ParseMode.MARKDOWN if dices['markdown'] else None
        self.dices = dices['dices']
        self.separator = dices['separator']
        self.basename = os.path.basename(dice_file)
        self.basename = self.basename[:self.basename.rindex('.')]

    def throw(self):

        # randomly select values
        results = [random.choice(values) for values in self.dices]

        # resolve annotations
        while True:
            lengths = [len(i) if isinstance(i, dict) else 0 for i in results]
            if not any(lengths):
                break
            try:
                i = lengths.index(1)
            except ValueError:
                raise ValueError('No single key found. Check your yaml file.')
            key = list(results[i].keys())[0]
            results = [i.get(key, i) if isinstance(i, dict) else i for i in results]

        return self.separator.join(map(str, results))

    def command(self, update: Update, context: CallbackContext) -> None:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=self.throw(), parse_mode=self.parse_mode)

    def trigger(self, message_text):
        if self.re_triggers.search(message_text):
            return self.throw()
        return None


dices = [DICE(fname) for fname in DICE_FILES.split(',')]

def triggers(update, context):
    random.shuffle(dices)
    for dice in dices:
        text = dice.trigger(update.message.text)
        if text:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text, parse_mode=dice.parse_mode)
            break


updater = Updater(TOKEN)
updater.dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), triggers))
for dice in dices:
    updater.dispatcher.add_handler(CommandHandler(dice.basename, dice.command))


if __name__ == '__main__':
    updater.start_polling()
    updater.idle()
