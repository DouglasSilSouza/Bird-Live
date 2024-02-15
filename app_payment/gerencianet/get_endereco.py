import requests

def endereco(cep):
    url = f'https://brasilapi.com.br/api/cep/v2/{cep}'
    session = requests.Session()

    response = session.get(url)
    return response.json()