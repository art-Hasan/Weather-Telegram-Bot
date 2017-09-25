# -*- coding: utf-8 -*-

import logging
import requests

from config import API_TIMEOUT, RETRY_CODES, RETRY_TIMEOUT

API_WEATHERMAP_URL = "http://api.openweathermap.org/data/2.5"
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)5s] %(message)s',)

class WeatherMap:
	def __init__(self, api_token):
		self.token = api_token

	def api_call(self, location, method, **params):
		url = '{0}/{1}'.format(API_WEATHERMAP_URL, method)
		logging.debug('weather map api call')
		lat = location["latitude"]
		lon = location["longitude"]
		payload = {
			'lat': lat,
			'lon': lon,
			'lang': 'ru',
			'units': 'metric',
			'appid': self.token
		}
		response = requests.post(url, params=payload)

		if response.status_code == 200:
			return response.json()
		elif response.status_code in RETRY_CODES:
			time.sleep(RETRY_TIMEOUT)
			return self.api_call(location, method, **params)
		else:
			if response.headers['content-type'] == 'application/json':
				err_msg = response.json()["description"]
			else:
				err_msg = response.text
			raise RuntimeError(err_msg)

	def process_response(self, response):
		city = response.get("name")
		country = response.get("sys")["country"]
		weather = response.get("weather")
		description = weather[0].get("description")
		temp = response.get("main")["temp"]
		wind = response.get("wind")["speed"]
		humidity = response.get("main")["humidity"]
		icon_id = weather[0].get("icon")
		#url = "http://openweathermap.org/img/w/{0}.png".format(icon_id)
		# icon = requests.get(url)

		response = {
			'country' : country,
			'city' : city,
			'description' : description,
			'temp' : temp,
			'wind' : wind,
			'humidity' : humidity,
			'icon' : url
		}

		return response
