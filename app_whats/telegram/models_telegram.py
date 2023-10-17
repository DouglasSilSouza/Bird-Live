def modelos_telegram(modelo):
    modelos_msg = [
        {'nome': 'hello world',
         'modelo': {
            "text": "hello_world",
            }
        },
        {'nome': 'inicio',
         'modelo': {
            "text": "Olá tudo bem? esse é um text de modelo\nPodemos iniciar o atendimento agora?",
            }
        },
    ]
    for models in modelos_msg:
        if modelo == models.get('nome'):
            return models.get('modelo').get('text')