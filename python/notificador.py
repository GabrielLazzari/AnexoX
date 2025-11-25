
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl


configuracoes = None


def carregar_configuracoes():
    global configuracoes

    try:
        with open('config.config', 'r') as file:
            configuracoes = json.load(file)
    except Exception as e:
        print("Erro ao abir .config:", str(e))


def enviar_email(email, titulo, mensagem):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = titulo
        msg["From"] = configuracoes['email']
        msg["To"] = email
        msg.attach(MIMEText(mensagem, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(configuracoes['email'], configuracoes['senha'])
            server.sendmail(configuracoes['email'], email, msg.as_string())

    except Exception as e:
        print(e)


def enviar_email_recuperar_senha(email, nova_senha):
    carregar_configuracoes()
    
    enviar_email(email, "Alteração senha AcervoX", "Segue sua nova senha: <b>" + nova_senha + "</b>")

    print(configuracoes)
