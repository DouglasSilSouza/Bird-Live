def modelos_whatsapp(modelo, nome="Usuário"):
    modelos_msg = [
        {'nome': 'hello world',
         'modelo': {
            "name": "hello_world",
            "language": {"code": "en_US"}
            }
        },
        {'nome': 'inicio',
         'modelo': {
            "name": "inicio",
            "language": {"code": "pt_BR"},
            "components": [
                {
                "type": "header",
                "parameters": [{
                    "type": "text",
                    "text": f"{nome}"
                    }]
                },
                {
                "type": "body",
                "parameters": [{
                    "type": "text",
                    "text": "DLS Empresa"
                }]
            }]
        }}
    ]
    for models in modelos_msg:
        if modelo == models.get('nome'):
            return models.get('modelo')