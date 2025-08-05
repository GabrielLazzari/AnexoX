
import base64
import os.path
import io

from PIL import Image, ImageOps
from werkzeug.utils import secure_filename
from unidecode import unidecode


def gravar_imagem(nome, conteudo, caminho="", livro=True):
    nome = unidecode(secure_filename(nome.title().replace(" ", "")))

    imagem, formato = processar_imagem(conteudo, livro)

    if imagem is None:
        return ""

    tamanho_bytes = retornar_tamanho_bytes(imagem, formato)

    if tamanho_bytes > 2:
        print("São permitidas a gravação de imagens de até 2MB")
        return ""

    os.makedirs(caminho, exist_ok=True)
    caminho = os.path.join(caminho, nome + '.' + formato)

    print(caminho, imagem.size, tamanho_bytes)
    imagem.save(caminho)

    return caminho


def processar_imagem(conteudo, transformar=True):
    if conteudo is None:
        return None, ""

    if isinstance(conteudo, Image.Image):
        imagem = conteudo
    else:
        if conteudo.strip() == "" or "," not in conteudo:
            return None, ""

        header, encoded = conteudo.split(",", 1)
        imagem = Image.open(io.BytesIO(base64.b64decode(encoded)))

    formato = imagem.format.lower()

    if transformar:
        imagem = transformar_formato(imagem)
        imagem = redimensionar(imagem)

    return imagem, formato


def transformar_formato(imagem):
    if imagem.format.lower() == "png":
        return imagem.convert("RGB")
    return imagem


def redimensionar(imagem, novo_tamanho=(500, 600)):
    img_redmin = imagem.copy()
    img_redmin.thumbnail(novo_tamanho, Image.LANCZOS)

    return img_redmin


def retornar_tamanho_bytes(imagem, formato):
    buffer = io.BytesIO()
    imagem.save(buffer, format=formato)
    return buffer.tell() / (1024 * 1024)
