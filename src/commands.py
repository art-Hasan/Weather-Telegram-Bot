# -*- coding: utf-8 -*-

import os
import json
import requests

from bot import Bot
from weather import WeatherMap

weather_map = WeatherMap(os.environ['API_WEATHERMAP'])
bot = Bot(weather_map, os.environ['API_TOKEN'])

@bot.command(r'/start')
def start(chat, match):
	if match.group(0) != None:
		return chat.send_text()

@bot.command(r'/location')
def location(chat, match):
	if match.group(0) != None:
		reply_markup = {
			"keyboard": [
				[{
					"text": "Отправить местоположение",
					"request_location": True
				}],
				["Сегодня","На 3 дня"]
			],
			"one_time_keyboard": False,
			"resize_keyboard": True,
		}
		return chat.keyboard_markup(reply_markup)


@bot.command(r'Сегодня')
def weather_today(chat, match):
	if match.group(0) != None and chat.has_location():

		location = chat.get_location()
		response = bot.weather_map.api_call(location, 'weather')
		processed_resp = bot.weather_map.process_response(response)

		html = "<strong>{}, {}</strong>\n\n".format(processed_resp.get("city"), processed_resp.get("country"))
		html += "<i>Описание - </i>{}\n".format(processed_resp.get("description"))
		html += "<i>Температура - </i>{} C°\n".format(processed_resp.get("temp"))
		html += "<i>Скорость ветра - </i>{} м/с\n".format(processed_resp.get("wind"))
		html += "<i>Влажность - </i>{} %".format(processed_resp.get("humidity"))

		# icon_url = processed_resp.get("icon")
		# f = open('image.png', 'w')
		# f.write(unicode(requests.get(icon_url).content, "ISO-8859-1"))
		# f.close()

		# with open('image.png', mode="r") as f:
		# 	chat.send_image(f, caption='icon from weathermap')
		return chat.reply(html, parse_mode="HTML")
		# return chat.send_image(processed_resp.get("icon"), caption='some caption')
	else:
		return chat.send_text('Отправьте свое местоположение')


@bot.command(r'На 3 дня')
def forecast(chat, match):
	if match.group(0) != None and chat.has_location():
		location = chat.get_location()
		response = bot.weather_map.api_call(location, 'forecast')
		return chat.send_text(json.dumps(response))
	else:
		return chat.send_text('Отправьте свое местоположение')

@bot.command(r'/stop')
def stop(chat, match):
	isMatch = match.group(0)
	if isMatch:
		return bot.stop()
