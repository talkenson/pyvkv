mainMenu = {
    'one_time': True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "payload": "{\"act\":\"sendAll\"}",
                "label": "Просмотреть все сообщения"
                },
            "color": "primary"
        }],
        [{
            "action": {
                "type": "text",
                "payload": "{\"act\":\"checkNew\"}",
                "label": "Проверить на наличие новых"
                },
            "color": "positive"
        }],
        [{
            "action": {
                "type": "text",
                "payload": "{\"act\":\"exit\"}",
                "label": "Выключить бота"
                },
            "color": "negative"
        }]
        ]
    }
exit = {
    'one_time': True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "payload": "{\"act\":\"exit\"}",
                "label": "Выключить бота"
                },
            "color": "primary"
        }]
        ]
    }
