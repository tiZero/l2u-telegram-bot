import logging
import ypsu
import os

from uuid import uuid4

from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update
)

from telegram.ext import (
    Updater,
    InlineQueryHandler,
    CommandHandler, MessageHandler,
    Filters,
    CallbackContext
)


example1 = '\\forall x \\in \\bbR we have that x^2 \\pm 1 \\neq 0'
example2 = 'The map \\rho : G \\to \\frakg \\otimes \\Gamma is injective'
example3 = 'The obstruction is \\itw_1(M) \\in \\itH^1(M, \\bbZ_2)'

usage123 = 'Usage examples:\n\n`> ' + \
            example1 + '\n> `' + ypsu.convert(example1) + '\n\n`> ' + \
            example2 + '\n> `' + ypsu.convert(example2) + '\n\n`> ' + \
            example3 + '\n> `' + ypsu.convert(example3)


def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_markdown('You can use this chat to see how LaTeX ' + \
        'is rendered or to copy-paste the output.\n\n' + usage123
    )


def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_markdown(usage123 + \
        '\n\nFor more, please visit the [wiki page](https://github.com/' + \
        'ypsu/latex-to-unicode/wiki) of the original project on GitHub.'
    )


def convert(update: Update, _: CallbackContext) -> None:
    answer = ypsu.convert(update.message.text)
    if not answer:
        return
    update.message.reply_text(answer)


def inlinequery(update: Update, _: CallbackContext) -> None:
    result = ypsu.convert(update.inline_query.query)
    if not result:
        return
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Convert to Unicode",
            input_message_content=InputTextMessageContent(result),
            description=result
        )
    ]

    update.inline_query.answer(results)


if __name__ == "__main__":

    NAME = os.environ['NAME']
    TOKEN = os.environ['TOKEN']

    # Port is given by Heroku
    PORT = os.environ.get('PORT')

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the Updater
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    # Add handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help_command))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, convert))

    dp.add_handler(InlineQueryHandler(inlinequery))

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN,
                          webhook_url=f"https://{NAME}.herokuapp.com/{TOKEN}")
    updater.idle()
