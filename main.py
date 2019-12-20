from telegram.ext import Updater
from telegram.ext import RegexHandler, CommandHandler
import logging
from config import HELP_Message, coinquery, topx, TOKEN
from config import NamevId, cryptoHero_re
from ut import coinmarketcap, chart, getprice

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
updater = Updater(token=TOKEN)

dispatcher = updater.dispatcher


def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=HELP_Message)


def btcquery(bot, update, groups):
    """币价查询"""
    c = coinmarketcap()
    msg = update.message.text
    msg = msg.strip()
    if len(msg.split()) == 2:
        b, t = msg.split()
        if t.startswith("1"):
            fname = chart(t, b=b)
            with open(fname, "rb") as f:
                bot.send_photo(chat_id=update.message.chat_id, photo=f, timeout=30)
        else:
            text = c.getCoinmarketcap(b, all=True)
            bot.send_message(chat_id=update.message.chat_id, text=text)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=c.getCoinmarketcap(msg))


def Topx(bot, update, groups):
    c = coinmarketcap()
    top = groups[0]
    text = c.getTopCoinmarketcap(top)
    bot.send_message(chat_id=update.message.chat_id, text=text)


def CryptoHero(bot, update, groups):
    msg = update.message.text
    msg = msg.strip()
    itemid = NamevId[msg]
    price = getprice(itemid)
    if price:
        text = "{}的价格为{} ETH".format(msg, price / 1e18)
        bot.send_message(chat_id=update.message.chat_id, text=text)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


# /help
dispatcher.add_handler(CommandHandler("help", help))

# top排行榜
topx_handler = RegexHandler(topx, callback=Topx, pass_groups=True)
dispatcher.add_handler(topx_handler)

# 币价查询
btc_handler = RegexHandler(coinquery, callback=btcquery, pass_groups=True)
dispatcher.add_handler(btc_handler)

# cryptoHero_handler = RegexHandler(cryptoHero_re, callback=CryptoHero, pass_groups=True)
# dispatcher.add_handler(cryptoHero_handler)

dispatcher.add_error_handler(error)

updater.start_polling()
updater.idle()
