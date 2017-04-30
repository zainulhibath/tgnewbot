#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import json
import logging
import os
import subprocess

import time

import sys

from telegram import ChatAction
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('bot.ini')

updater = Updater(token=config['KEYS']['bot_api'])
path = config['PATH']['path']
sudo_users = json.loads(config['ADMIN']['sudo'])
dispatcher = updater.dispatcher

def build(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Building")
        os.chdir(path)
        build_command = ['./scripts/bacon.sh']
        subprocess.call(build_command)
        if os.path.exists("/tmp/IllusionKernel-bacon.zip"):
        	bot.sendMessage(chat_id=update.message.chat_id,
        					text="Build done, use /upload if you want zip")
        else:
        	bot.sendMessage(chat_id=update.message.chat_id,
        					text="RIP, Build failed LMAO")
    else:
        sendNotAuthorizedMessage(bot, update)

def upload(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id,
                            action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Uploading to the chat")
        filename = "/tmp/IllusionKernel-bacon.zip"
        bot.sendDocument(
            document=open(filename, "rb"),
            chat_id=update.message.chat_id)
    else:
        sendNotAuthorizedMessage(bot,update)

def restart(bot, update):
    if isAuthorized(update):
         bot.sendMessage(update.message.chat_id, "Bot is restarting...")
         time.sleep(0.2)
         os.execl(sys.executable, sys.executable, *sys.argv)
    else:
         sendNotAuthorizedMessage()

def leave(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
        bot.sendMessage(update.message.chat_id, "Goodbye!")
        bot.leaveChat(update.message.chat_id)
    else:
        sendNotAuthorizedMessage(bot, update)

def sendNotAuthorizedMessage(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                        action=ChatAction.TYPING)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="You aren't authorized for this lulz @" + update.message.from_user.username)

def help(bot, update):
    bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
    bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id,
        text="I've sent you help via PM @" + update.message.from_user.username + ".")
    bot.sendMessage(update.message.from_user.id,
        text="Here is some help for you.\n/build,\n/upload,\n/restart,\n/leave, and\n/help for this menu.")


def isAuthorized(update):
    return update.message.from_user.id in sudo_users

def pull(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
        bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text="Fetching remote repo")
        subprocess.call(['git', 'fetch', 'origin', 'master', '--force'])
        bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text="Resetting to latest commit")
        subprocess.call(['git', 'reset', '--hard', 'origin/master'])
        restart(bot, update)
    else:
        sendNotAuthorizedMessage(bot, update)

def push(bot, update):
    if isAuthorized(update):
        subprocess.call(['git', 'push', 'origin', 'master', '--force'])
        bot.sendMessage(update.message.chat_id, text="K pushed")
    else:
        sendNotAuthorizedMessage(bot, update)

def trigger_characters(bot, update):
    try:
        msg=str(update.message.text).lower()
        if msg[0]=='!':
            mod_command=msg.replace("!", "")
            eval(mod_command)(bot, update)
        elif msg[0]=='#':
            mod_command=msg.replace("#", "")
            eval(mod_command)(bot, update)
    except UnicodeEncodeError:
        pass

buildHandler = CommandHandler('build', build)
uploadHandler = CommandHandler('upload', upload)
restartHandler = CommandHandler('restart', restart)
leaveHandler = CommandHandler('leave', leave)
helpHandler = CommandHandler('help', help)
idHandler = CommandHandler('id', id)
pullHandler = CommandHandler('pull', pull)
pushHandler = CommandHandler('push', push)

dispatcher.add_handler(buildHandler)
dispatcher.add_handler(uploadHandler)
dispatcher.add_handler(restartHandler)
dispatcher.add_handler(leaveHandler)
dispatcher.add_handler(helpHandler)
dispatcher.add_handler(idHandler)
dispatcher.add_handler(pullHandler)
dispatcher.add_handler(pushHandler)

dispatcher.add_handler(MessageHandler(Filters.text, trigger_characters))

updater.start_polling()
updater.idle()