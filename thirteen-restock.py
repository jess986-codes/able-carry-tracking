import requests
import logging
from bs4 import BeautifulSoup
# from selenium import webdriver
import smtplib
from email.mime.text import MIMEText
import constants


# FUNCTIONS
def request_page(url):

    try:
        page = requests.get(url)
        if (page.status_code == 200):
            logging.info('Successfully loaded site')
            html = BeautifulSoup(page.content, "html.parser")
            return html

        else:
            logging.error('Unable to load site')
            exit()
    except:
        logging.error('Encountered issue with loading site')
        exit()

def check_stock(html, colour, url):
    selected_colour = html.find(class_='swatch__label--color').find(class_='swatch__value').text.lower()
    is_colour = colour in selected_colour

    warehouse_picker_html = html.find(class_='swatch-wrapper swatch-wrapper-product-daily-13l').find(class_='swatch__item active')
    is_world = warehouse_picker_html.find(title='WORLD')

    if (is_colour and is_world):
        is_btn_enabled = html.find(id='AddToCart-product-daily-13l', class_='disabled') == None

        # extra measure
        add_btn_txt = html.find(id='AddToCartText-product-daily-13l').text.lower()
        isRestocked = constants.RESTOCKED_TEXT in add_btn_txt

        if (is_btn_enabled or isRestocked):
            send_success_email(colour, url)
        else:
            logging.info(f"{colour} is not in stock yet")
    else:
        send_error_email(colour, url)

def send_email(subject, body):
    sender = "sending.ved@gmail.com"
    recipients = ["notification.ved@gmail.com", "jess986.sendit@proton.me"]
    password = "{password}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")

def send_success_email(product, url):
    logging.info(f"{product} is back in stock. Proceeding to send email notification.")
    subject = f"{product} is in stock!!".upper()
    body = f"{product} is finally in stock!! Here's the link: {url}"
    send_email(subject, body)

def send_error_email(product, url):
    logging.error('Wrong link, need to check link again')
    subject = f"The link for {product} is wrong".upper()
    body = f"The link for {product} is wrong. Check this link: {url}"
    send_email(subject, body)

# SCRIPT
def main():
    url_map = {
        constants.BLACK : constants.THIRTEEN_BLACK_URL,
        constants.OLIVE : constants.THIRTEEN_OLIVE_URL,
        constants.RED : constants.THIRTEEN_RED_URL
    }

    for key in url_map:
        page_html = request_page(url_map[key])
        if (page_html != None):
            check_stock(page_html, key, url_map[key])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(message)s')
    main()
