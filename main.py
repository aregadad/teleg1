import time
from inspect import cleandoc

import requests
import telegram
from environs import Env


def main():
    env = Env()
    env.read_env()
    devman_token = env('DEVMAN_TOKEN')
    telegram_bot_token = env('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = env('TELEGRAM_CHAT_ID')

    bot = telegram.Bot(token=telegram_bot_token)

    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': f'Token {devman_token}'}
    params = {}

    while True:
        try:
            print('\nЗапрос отправлен. Ждем ответ от сервера')
            feedback_response = requests.get(
                url, params=params, headers=headers, timeout=120)
            feedback_response.raise_for_status()
            feedback_payload = feedback_response.json()
            if feedback_payload['status'] == 'found':
                params['timestamp'] = feedback_payload['last_attempt_timestamp']
                if feedback_payload['new_attempts'][0]['is_negative']:
                    message = f'''
                    У вас проверили работу: {feedback_payload['new_attempts'][0]['lesson_title']}.
                    К сожалению в работе нашлись ошибки.
                    Ссылка: {feedback_payload['new_attempts'][0]['lesson_url']}
                    '''
                else:
                    message = f'''
                    У вас проверили работу: {feedback_payload['new_attempts'][0]['lesson_title']}.
                    Преподавателю всё понравилось. Можно приступать к следующему уроку!
                    Ссылка: {feedback_payload['new_attempts'][0]['lesson_url']}
                    '''
                print('Ответ получен')
                bot.send_message(chat_id=telegram_chat_id,
                                 text=cleandoc(message))
                print('Сообщение в телеграм отправлено')
            elif feedback_payload['status'] == 'timeout':
                params['timestamp'] = feedback_payload['timestamp_to_request']
                print('Нет ответа от сервера.')
        except requests.ReadTimeout:
            print('Нет ответа от сервера.')
        except requests.ConnectionError:
            print('Проблемы с подключением. Переподключаемся.')
            time.sleep(10)


if __name__ == '__main__':
    main()
