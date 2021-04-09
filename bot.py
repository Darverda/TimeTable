import requests
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import config
import os
import main

PORT = int(os.environ.get('PORT', 5000))


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hello. I'm a bot that will help you to get the schedule.")

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, I didn't understand that command.")

def get_timetable_on_week(update, context):
    timetable = main.get_on_week(session)
    context.bot.send_message(chat_id=update.effective_chat.id, text=timetable)

def get_timetable_by_date(update, context):
    date = context.args[0]
    timetable = main.get_by_date(session, date)
    context.bot.send_message(chat_id=update.effective_chat.id, text=timetable)

def get_timetable_today(update, context):
    pass

def get_timetable_tomorrow(update, context):
    pass


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def add_handlers(dispatcher):
    start_handler = CommandHandler('start', start)
    timetable_handler = CommandHandler('timetable', get_timetable_on_week)
    by_date_timetable_handler = CommandHandler('ondate', get_timetable_by_date)
    today_timetable_handler = CommandHandler('today', get_timetable_today)
    tomorrow_timetable_handler = CommandHandler('tomorrow', get_timetable_tomorrow)
    unknown_handler = MessageHandler(Filters.command, unknown)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(timetable_handler)
    dispatcher.add_handler(by_date_timetable_handler)
    dispatcher.add_handler(today_timetable_handler)
    dispatcher.add_handler(tomorrow_timetable_handler)
    dispatcher.add_handler(unknown_handler)
    dispatcher.add_error_handler(error)


if __name__ == '__main__':
    session = requests.session()
    main.login(session)

    updater = Updater(token=config.TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    add_handlers(dispatcher)

    # updater.start_webhook(listen="0.0.0.0",
    #                       port=int(PORT),
    #                       url_path=config.TELEGRAM_TOKEN)
    # updater.bot.setWebhook('https://timetable106.herokuapp.com/' + config.TELEGRAM_TOKEN)
    updater.start_polling()

    updater.idle()