# -*- coding: utf-8 -*-

import re
import json
import time
import logging
import requests

from functools import partialmethod
from chat import Chat
from config import API_TIMEOUT, RETRY_TIMEOUT, RETRY_CODES


logging.basicConfig(level=logging.DEBUG, format='[%(levelname)5s] %(message)s',)

API_URL = "https://api.telegram.org"

class Bot:

	_running = False
	_offset = 0

	def __init__(self, weather_map, api_token, api_timeout=API_TIMEOUT, name=None):
		self.token = api_token
		self.weather_map = weather_map
		self.api_timeout = api_timeout
		self._commands = []
		self.name = name

	def run(self):
		logging.debug('Running')
		self._running = True
		try:
			while self._running:
				updates = self.api_call(
					'getUpdates',
					offset=self._offset + 1,
					timeout=self.api_timeout
				)
				self._process_updates(updates)
		except KeyboardInterrupt:
			self.stop()
		logging.debug('Exiting')


	def api_call(self, method, **params):
		print(params)
		logging.debug('bot api call')
		url = "{0}/bot{1}/{2}".format(API_URL, self.token, method)
		response = requests.post(url, data=params)

		if response.status_code == 200:
			return response.json()
		elif response.status_code in RETRY_CODES:
			time.sleep(RETRY_TIMEOUT)
			return self.api_call(method, **params)
		else:
			if response.headers['content-type'] == 'application/json':
				err_msg = response.json()["description"]
			else:
				err_msg = response.text
			raise RuntimeError(err_msg)

	def send_message(self, chat_id, text, **options):
		logging.debug('send message')
		return self._send_message(chat_id=chat_id, text=text, **options)

	def send_photo(self, chat_id, photo, **options):
		logging.debug('send photo')
		return self._send_photo(chat_id=chat_id, photo=photo, **options)

	_send_message = partialmethod(api_call, "sendMessage")
	_send_photo = partialmethod(api_call, "sendPhoto")

	def stop(self):
		logging.debug('stop')
		self._running = False

	def _process_updates(self, updates):
		logging.debug('process update')
		if not updates["ok"]:
			return

		for update in updates["result"]:
			self._offset = max(self._offset, update["update_id"])

			if "message" in update:
				self._process_message(update["message"])

	def _process_message(self, message):
		logging.debug('process message')
		chat = Chat.from_message(self, message)

		if "text" not in message:
			if chat.has_location():
				message["text"] = '/location'
			else:
				return

		for patterns, handler in self._commands:
			m = re.search(patterns, message["text"], re.I)
			if m:
				return handler(chat, m)

	def command(self, regexp):
		def wrap(fn):
			self._commands.append((regexp, fn))
			return fn
		return wrap
