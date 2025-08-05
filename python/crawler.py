import base64
import io
from os.path import isfile
import re
import sqlite3
import threading

import pandas as pd
from PIL import Image
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from python.imagem import processar_imagem


class Driver(webdriver.Chrome):
    def __init__(self, url="", options=None, mostrar_browser=False, tempo_espera=10):
        self.erro = False
        if options is None:
            options = Options()
            if not mostrar_browser:
                options.add_argument("--headless")
            options.add_argument('--log-level=3')

        super().__init__(options=options)
        self.mostrar_browser = mostrar_browser
        self.url = url
        self.implicitly_wait(tempo_espera)
        try:
            self.get(url)
        except:
            print("\033[31mNão foi possível se conectar na url\033[m")
            self.fechar()
            self.erro = True

    def __enter__(self):
        # Ao executar with open, posso colocar qualquer coisa aqui que vai executar antes do codigo dentro do with open
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.fechar()

    def fechar(self):
        self.close()
        self.quit()


driver = None


def image_to_base64(image, formato):
    buffered = io.BytesIO()
    image.save(buffered, format=formato)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def procurar_livros_internet(pesquisa):
    global driver

    if driver is None:
        driver = Driver("https://www.amazon.com.br/Livros", mostrar_browser=True)

    if driver.erro:
        return []

    el = driver.find_element(By.NAME, "field-keywords")

    el.clear()
    el.send_keys(pesquisa + Keys.ENTER)
    el = driver.find_element(By.XPATH, "//*[@data-component-type='s-search-result']")

    el = el.find_element(By.CLASS_NAME, "s-product-image-container")

    livros = []

    for e in el.find_elements(By.TAG_NAME, "img"):
        link = e.get_attribute("src")
        print(link)

        response = requests.get(link)
        if response.status_code == 200:
            img, formato = processar_imagem(Image.open(io.BytesIO(response.content)))

            # img_tag = f'<img src="data:image/{formato};base64,{image_to_base64(img, formato)}" /> Autor teste'

            livros.append({
                "titulo": "",
                "titulo_pesquisado": pesquisa,
                "autor": "",
                "editora": "",
                "link": link,
                "descricao": "",
                "img": f"data:image/{formato};base64,{image_to_base64(img, formato)}"
            })

            # img.show()

    return livros


if driver is not None:
    print('f')
    driver.fechar()
