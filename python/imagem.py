
import base64
import os.path
import io

from PIL import Image, ImageOps
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from unidecode import unidecode


def gravar_imagem(nome, conteudo, caminho="", transformar='livro'):
    nome = unidecode(secure_filename(nome.title().replace(" ", "")))
    
    imagem, formato, formato_gravar = processar_imagem(conteudo, transformar)

    if imagem is None:
        return ""

    tamanho_bytes = retornar_tamanho_bytes(imagem, formato)

    if tamanho_bytes > 2:
        print("São permitidas a gravação de imagens de até 2MB")
        return ""

    os.makedirs(caminho, exist_ok=True)
    caminho = os.path.join(caminho, nome + '.' + formato_gravar)

    print(caminho, imagem.size, tamanho_bytes)
    imagem.save(caminho, optimize=True, compress_level=9)

    return caminho


def processar_imagem(conteudo, transformar='livro'):
    if conteudo is None:
        return None, ""

    if isinstance(conteudo, Image.Image):
        imagem = conteudo
    elif isinstance(conteudo, FileStorage):
        imagem = Image.open(conteudo)
    else:
        if conteudo.strip() == "" or "," not in conteudo:
            return None, ""

        header, encoded = conteudo.split(",", 1)
        imagem = Image.open(io.BytesIO(base64.b64decode(encoded)))

    formato = imagem.format.lower()
    formato_gravar = "jpg"

    if transformar == "livro":
        imagem = transformar_formato(imagem)
        imagem = redimensionar(imagem)
    elif transformar == "perfil":
        imagem = transformar_formato(imagem)
        imagem = redimensionar(imagem, novo_tamanho=(500, 500))
        #formato_gravar = formato
    elif transformar == "perfil_capa":
        imagem = transformar_formato(imagem)

    if formato == "png" and formato_gravar != "jpg" and formato_gravar != "jpeg":
        imagem = imagem.quantize(colors=128)

    return imagem, formato, formato_gravar


def transformar_formato(imagem):
    if imagem.format.lower() == "png":
        imagem = imagem.convert("RGB")
    return imagem


def redimensionar(imagem, novo_tamanho=(500, 600)):
    img_redmin = imagem.copy()
    img_redmin.thumbnail(novo_tamanho, Image.LANCZOS)

    return img_redmin


def retornar_tamanho_bytes(imagem, formato):
    buffer = io.BytesIO()
    imagem.save(buffer, format=formato)
    return buffer.tell() / (1024 * 1024)


def imagem_to_base64(imagem, formato):
    buffered = io.BytesIO()
    imagem.save(buffered, format=formato)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

