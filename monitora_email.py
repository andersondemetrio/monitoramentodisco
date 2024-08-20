import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time
import logging
import psutil


logging.basicConfig(level=logging.DEBUG)

# Configurações de e-mail
from_email = "rrpriceservicos@gmail.com"
from_password = "wqnu fmtq ofxp awpt"
to_email = ["anderson.debhora@gmail.com"]
subject = "Alerta: Uso de Disco Acima do Limite - E:\\Databases"

# Diretório para monitorar
disk_path = "E:\\Databases"

# Tamanho total do disco em GB
disk_total_gb = 10.0

# Limite de uso do disco em porcentagem
alert_threshold_percent = 10.0

# Intervalo de verificação em segundos
check_interval = 60  # 60 segundos

# Função para enviar e-mail
def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ", ".join(to_email)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(from_email, from_password)
            smtp.sendmail(from_email, to_email, msg.as_string())
            logging.debug(f"Email enviado com sucesso para {to_email}")
            print(f"Email enviado com sucesso para {to_email}")
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"Erro de autenticação SMTP: {e}")
    except Exception as e:
        logging.error(f"Erro durante o envio de e-mail: {e}")

# Função para verificar o uso do disco
def check_disk_usage(disk, total_gb, threshold_percent):
    usage = psutil.disk_usage(disk)
    used_gb = usage.used / (1024 ** 3)  # Convertendo bytes para GB
    used_percent = (used_gb / total_gb) * 100
    return used_percent >= threshold_percent, used_percent

# Loop de monitoramento contínuo
while True:
    exceeds_threshold, used_percent = check_disk_usage(disk_path, disk_total_gb, alert_threshold_percent)
    if exceeds_threshold:
        logging.debug(f"O uso do disco {disk_path} atingiu {used_percent:.2f}% ({used_percent * disk_total_gb / 100:.2f} GB usados).")
        
        # Cria o corpo do e-mail
        body = f"""
        <html>
        <style>
        h1. {{"color": "red"}}
        p. {{"color": "black"}}

        </style>

            <body>
                <h1>Alerta de Uso de Disco</h1>
                <p>O uso do disco <b>{disk_path}</b> atingiu <b>{used_percent:.2f}%</b> ({used_percent * disk_total_gb / 100:.2f} GB usados).</p>
                <p>Por favor, verifique o espaço disponível.</p>
            </body>
        </html>
        """
        
        # Envia o e-mail
        send_email(subject, body)
    else:
        logging.debug(f"Tudo certo. Uso do disco {disk_path} está em {used_percent:.2f}%.")

    # Aguarda antes da próxima verificação
    time.sleep(check_interval)