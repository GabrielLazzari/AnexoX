import base64
import io
from os.path import isfile
import re
import sqlite3
import threading
from time import sleep

import pandas as pd
from PIL import Image
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from python.modelos.livro import *
from python.imagem import processar_imagem, imagem_to_base64


class Driver(webdriver.Chrome):
    def __init__(self, url="", options=None, mostrar_browser=False, tempo_espera=10):
        self.erro = False
        self.ocupado = False
        self.tempo_espera = tempo_espera
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


drivers = []
def retornar_driver_livre():
    global drivers

    if len(drivers) == 0:
        drivers.append(Driver("https://www.amazon.com.br/Livros", mostrar_browser=True))
        return drivers[0]

    tentativa = 0
    while tentativa != 3:
        for d in drivers:
            if not d.ocupado:
                return d

        if len(drivers) < 10:
            drivers.append(Driver("https://www.amazon.com.br/Livros"))
            return drivers[0]

        sleep(1)
        tentativa += 1

    print('ok')
    return None


def finalizar_crawler_drivers():
    for driver in drivers:
        print('fechando...', driver)
        driver.fechar()


def procurar_livros_internet(pesquisa):
    driver = retornar_driver_livre()

    if driver is None or driver.erro:
        return []

    driver.ocupado = True

    el = driver.find_element(By.NAME, "field-keywords")

    el.clear()
    el.send_keys(pesquisa + Keys.ENTER)

    livros = []

    for pos, item_link in enumerate(driver.find_elements(By.XPATH, "//*[@data-component-type='s-search-result']")):
        if len(livros) > 4:
            break

        driver.implicitly_wait(driver.tempo_espera)

        link = item_link.find_element(By.XPATH, ".//*[@data-cy='title-recipe']//a").get_attribute("href").strip()
        if link.startswith("https://www.amazon.com.br/gp/video") or '/gp/video' in link:
            continue

        driver.execute_script("window.open('', '_blank');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(link)

        livro = Livro()
        livro.site_link = "Amazon"
        livro.link = link

        driver.implicitly_wait(0)

        if len(titulo := driver.find_elements(By.ID, "productTitle")) > 0:
            livro.titulo = titulo[0].get_attribute("innerText").strip()
        else:
            continue

        if len(preco := driver.find_elements(By.XPATH, '//*[@id="tmm-grid-swatch-PAPERBACK"]//*[@class="slot-price"]')) > 0:
            livro.preco = preco[0].get_attribute("innerText").replace("R$", "").strip()
        elif len(preco := driver.find_elements(By.XPATH, '//*[@id="tmm-grid-swatch-OTHER"]//*[@class="slot-price"]')) > 0:
            livro.preco = preco[0].get_attribute("innerText").replace("R$", "").strip()

        if len(descricao := driver.find_elements(By.XPATH, '//*[@id="bookDescription_feature_div"]//*[contains(@class, "a-expander-content")]')) > 0:
            teste = descricao[0].get_attribute("innerHTML")
            livro.descricao = descricao[0].get_attribute("innerText").strip()

        if len(img := driver.find_elements(By.XPATH, './/*[@id="imgTagWrapperId"]//img')) > 0:
            livro.img = img[0].get_attribute("src").strip()

            response_img = requests.get(livro.img)
            if response_img.status_code == 200:
                livro.img_obj, formato = processar_imagem(Image.open(io.BytesIO(response_img.content)))
                livro.img = f"data:image/{formato};base64,{imagem_to_base64(livro.img_obj, formato)}"

        if len(qtd_paginas := driver.find_elements(By.ID, "rpi-attribute-book_details-fiona_pages")) > 0:
            if len(children := qtd_paginas[0].find_elements(By.XPATH, './*')) > 2:
                livro.qtd_paginas = ''.join(re.findall(r"\d+", children[2].get_attribute("textContent"))).strip()

        if len(nome_editora := driver.find_elements(By.ID, "rpi-attribute-book_details-publisher")) > 0:
            if len(children := nome_editora[0].find_elements(By.XPATH, './*')) > 2:
                livro.editora = retornar_usuario(children[2].get_attribute("textContent").strip(), tipo=TipoUsuario.Editora)

        if len(isbn := driver.find_elements(By.ID, "rpi-attribute-book_details-isbn13")) > 0:
            if len(children := isbn[0].find_elements(By.XPATH, './*')) > 2:
                livro.isbn = children[2].get_attribute("textContent").strip()

        encontrou_autor_com_img = False
        if len(area_autor := driver.find_elements(By.ID, "followTheAuthor_feature_div")) > 0:
            area_autor = area_autor[0]
            livro.autor = Usuario()
            livro.autor.tipo = TipoUsuario.Autor

            if len(nome_autor := area_autor.find_elements(By.XPATH, './/*[contains(@class,"_follow-the-author-card_style_authorNameColumn")]//span//span')) > 0:
                livro.autor.nome = nome_autor[0].get_attribute("innerText").strip()

            if len(img_autor := area_autor.find_elements(By.TAG_NAME, 'img')) > 0:
                livro.autor.img = img_autor[0].get_attribute("src")

                response_img = requests.get(livro.autor.img)
                if response_img.status_code == 200:
                    livro.autor.img_obj, formato = processar_imagem(Image.open(io.BytesIO(response_img.content)))
                    livro.autor.img = f"data:image/{formato};base64,{imagem_to_base64(livro.autor.img_obj, formato)}"

            if livro.autor.nome != "":
                encontrou_autor_com_img = True

        if not encontrou_autor_com_img and len(area_autor := driver.find_elements(By.XPATH, '//*[@id="bylineInfo"]//*[contains(@class, "author")]//a')) > 0:
            livro.autor = Usuario()
            livro.autor.tipo = TipoUsuario.Autor
            livro.autor.nome = area_autor[0].get_attribute("innerText").strip()


        livros.append(livro)

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    driver.implicitly_wait(driver.tempo_espera)
    driver.ocupado = False

    return livros


#   procurar_livros_internet("quatro vidas de um cachorro")
finalizar_crawler_drivers()
