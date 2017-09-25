# -*- coding: utf-8 -*-

import json
import logging

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)5s] %(message)s',)

class Chat:

	_location = None

	def __init__(self, bot, chat_id, chat_type, src_message):
		self.id = chat_id
		self.bot = bot
		self.chat_type = chat_type
		self.message = src_message

		if "location" in src_message:
			Chat._location = src_message["location"]

	def send_text(self, text, **options):
		logging.debug('chat send text')
		return self.bot.send_message(self.id, text, **options)

	def send_image(self, photo, **options):
		logging.debug('chat send image')
		return self.bot.send_photo(self.id, photo, **options)

	def keyboard_markup(self, reply_markup):
		self.reply(u'Используйте клавиатуру для управления', reply_markup)

	def reply(self, text, markup=None, parse_mode=None):
		if markup is None:
			return self.send_text(
				text,
				disable_web_page_preview='true',
				parse_mode=parse_mode
			)
		else:
			return self.send_text(
					text,
					disable_web_page_preview='true',
					reply_markup=json.dumps(markup),
					parse_mode=parse_mode
				)

	def get_location(self):
		logging.debug('chat get location')
		return Chat._location

	def has_location(self):
		logging.debug('has location')
		return Chat._location != None

	@staticmethod
	def from_message(bot, message):
		logging.debug('chat from message')
		chat = message["chat"]
		return Chat(bot, chat["id"], chat["type"], message)

	def __str__(self):
		return "location -- [{}]".format(self._location)

	
