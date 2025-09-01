import os
import random

import requests


def generate_verification_code(length=6):
    """Генерация случайного шестизначного числа для отправки в SMS"""
    return "".join([random.choice("0123456789") for i in range(length)])


def send_sms(phone_number, text):
    """Отправка SMS lk регистрации"""
    api_id = os.getenv("API_KEY_SMS")
    params = {"api_id": api_id, "to": phone_number, "text": text, "json": 1}  # Ответ в формате JSON
    response = requests.post("https://sms.ru/sms/send", data=params)
    return response.json()
