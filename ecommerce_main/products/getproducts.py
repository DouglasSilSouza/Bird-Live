import requests

class GetProducts:
    def __init__(self, parameter= None) -> None:
        self.url = 'https://fakestoreapi.com/products'
        self.parameter = parameter
        self.session = requests.session()
    
    def get_products(self):
        if self.parameter:
            self.url = f"{self.url}/{self.parameter}"

        response = self.session.get(self.url)
        return response.json()