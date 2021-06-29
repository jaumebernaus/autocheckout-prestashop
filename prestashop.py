### LOGGING
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(funcName)s:%(levelname)s:%(message)s')

#guarde en un fitxer els logs
file_handler = logging.FileHandler('bot_neobyte.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

#mostra els logs INFO en consola
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


### LIBRARIES
import requests
from bs4 import BeautifulSoup
import time
import json


###CODE
class neobyteBot:
    def __init__(self, cookie, product_id, qty, monitor = 10):
        self.cookie = cookie
        self.id = product_id
        self.qty = qty

        self.monitor = monitor

        self.token = self.getToken()
        self.addToCart()

        #self.createArchive("")

        self.purchase()

    def getToken(self):
        #busque el token d'usuari que es troba en la pagina principal i el retorne
        self.headers = {
            "authority": "www.botiga.prestashop",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "sec-ch-ua-mobile": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-language": "es-ES,es;q=0.9",
            "cookie": self.cookie
        }
        logger.info('Requesting main page')
        response = requests.get('https://www.botiga.prestashop/', headers=self.headers)
        logger.info(f'Response {response.status_code}')

        logger.debug(f'Response data: {response.text}')

        soup = BeautifulSoup(response.text, 'lxml')

        scripts = soup.findAll('script', {'type': 'text/javascript'})

        for script in scripts:
            s = str(script)
            if 'static_token' in s:
                token = s.split("static_token='")[1].split("'")[0]
                logger.info(f'Extracted token: {token}')
                return token

        logger.warning('Failed to find token')
        exit()

    def addToCart(self):
        #afegeix el item al cart i treu els items que hi sobren
        url = "https://www.botiga.prestashop/"

        querystring = {"rand":str(int(time.time() * 1000))}

        payload = f"controller=cart&add=1&ajax=true&qty={self.qty}&id_product={self.id}&token={self.token}"
        headers = {
            "authority": "www.botiga.prestashop",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "x-requested-with": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?1",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.botiga.prestashop",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.botiga.prestashop/",
            "accept-language": "es-ES,es;q=0.9",
            "cookie": self.cookie
        }

        logger.info('Adding to cart')
        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        logger.info(f'Response {response.status_code}')

        logger.debug(f'Response data: {response.text}')

        data = json.loads(response.text)

        self.final_cart = data

        if data['hasError']:
            logger.warning('Not in stock')
            time.sleep(self.monitor)

            logger.info('Retrying...')
            self.addToCart()

        else:
            for elem in data['products']:
                if elem['id'] == self.id and elem['quantity'] > self.qty:
                    #si hi ha més quantitat del item que volem cridem reduceQty()
                    self.final_cart = self.reduceQty(elem['quantity'] - self.qty)
                if elem['id'] != self.id:
                    #si hi ha més items dels que volem cridem removeFromCart()
                    self.final_cart = self.removeFromCart(elem['id'])

    def removeFromCart(self, id):
        #elimine items del cart
        url = "https://www.botiga.prestashop/"

        querystring = {"rand":str(int(time.time() * 1000))}

        payload = f"controller=cart&delete=1&id_product={id}&token={self.token}&ajax=true"
        headers = {
            "cookie": self.cookie,
            "authority": "www.botiga.prestashop",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "x-requested-with": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?1",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.botiga.prestashop",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.botiga.prestashop",
            "accept-language": "es-ES,es;q=0.9"
        }
        logger.info(f'Removing {id} from cart')
        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        logger.info(f'Response {response.status_code}')

        return json.loads(response.text)

    def reduceQty(self, amount):
        url = "https://www.botiga.prestashop/"

        querystring = {"rand":str(int(time.time() * 1000))}

        payload = f"controller=cart&ajax=true&add=true&getproductprice=true&summary=true&id_product={self.id}&ipa=0&op=down&qty={amount}&token={self.token}&allow_refresh=1"
        headers = {
            "cookie": self.cookie,
            "authority": "www.botiga.prestashop",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "x-requested-with": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?1",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.botiga.prestashop",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.botiga.prestashop",
            "accept-language": "es-ES,es;q=0.9"
        }
        logger.info(f'Removing {amount} x {self.id} from cart')
        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        logger.info(f'Response {response.status_code}')

        return json.loads(response.text)

    def purchase(self):
        #inicie el proces de compra
        url = "https://www.botiga.prestashop/pedido-rapido"

        querystring = {"rand":str(int(time.time() * 1000))}

        payload = f"ajax=true&method=updateTOSStatusAndGetPayments&checked=1&token={self.token}"
        headers = {
            "cookie": self.cookie,
            "authority": "www.botiga.prestashop",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "x-requested-with": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?1",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.botiga.prestashop",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.botiga.prestashop/pedido-rapido",
            "accept-language": "es-ES,es;q=0.9"
        }
        logger.info(f'Checking out')
        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        logger.info(f'Response {response.status_code}')

        data = json.loads(response.text)

        html = data['HOOK_PAYMENT']

        self.createArchive(html)



    def createArchive(self, html_text):
        #crea un archiu amb un boto que ens porta a la pasarel·la de pagament
        products = self.final_cart['products']
        total = self.final_cart['total'].replace('€','')


        resum = ""
        for elem in products:
            if elem['quantity'] == 1:
                resum += f"<p> {elem['quantity']} ud de {elem['name']}</p>"
            else:
                resum += f"<p> {elem['quantity']} uds de {elem['name']}</p>"
        html_text = resum + f"<h3>Total: {total}</h3>" + html_text


        html_text = html_text.replace('</form>','<input type="submit" value="Pagar"> </form>')
        html_text = html_text.replace('<div class="row"', '<div class="row" style="visibility: hidden;"')

        print(html_text)

















if __name__ == "__main__":
    cookies = ##COOKIES##
    b = neobyteBot(cookies, 6314, 2)
