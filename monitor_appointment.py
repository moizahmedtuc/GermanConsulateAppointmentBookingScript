import requests
import base64
from bs4 import BeautifulSoup
import time
import telegram
import asyncio

# Telegram bot token and chat ID
BOT_TOKEN = '8170088016:AAEYWvDPdpUWeLRh56f8_53nNielfmXKZyQ'
CHAT_ID = '5591971533'

# TrueCaptcha credentials
TRUECAPTCHA_USER_ID = 'speedymoiz'
TRUECAPTCHA_API_KEY = '	HQecFgFPgTTsJNKZK0nL'

# URLs
CAPTCHA_URL = 'https://service2.diplo.de/rktermin/extern/appointment_showMonth.do?locationCode=kara&realmId=772&categoryId=1417'
APPOINTMENT_URL = 'https://service2.diplo.de/rktermin/extern/appointment_showMonth.do'

# Telegram bot setup
bot = telegram.Bot(token=BOT_TOKEN)


# def solve_captcha():
#     # Fetch CAPTCHA image
#     response = requests.get(CAPTCHA_URL)
#     soup = BeautifulSoup(response.content, 'html.parser')
#
#     captcha_img_url = soup.find('img', {'id': 'captchaImage'}).get('src')
#     captcha_img_response = requests.get(captcha_img_url)
#
#     # Send CAPTCHA to TrueCaptcha
#     truecaptcha_payload = {
#         "userid": TRUECAPTCHA_USER_ID,
#         "apikey": TRUECAPTCHA_API_KEY,
#         "data": captcha_img_response.content,
#     }
#     truecaptcha_response = requests.post('https://api.apitruecaptcha.com/solve', json=truecaptcha_payload)
#     captcha_text = truecaptcha_response.json()['result']
#     return captcha_text

def solve_captcha(image_path):
    """Solve CAPTCHA using TrueCaptcha."""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('ascii')
        url = 'https://api.apitruecaptcha.com/one/gettext'
        data = {
            'userid': TRUECAPTCHA_USER_ID,
            'apikey': TRUECAPTCHA_API_KEY,
            'data': encoded_string,
        }
        response = requests.post(url, json=data)
        result = response.json()
        if 'result' in result:
            return result['result']
        else:
            raise Exception(f"Captcha solving failed: {result}")


def fetch_captcha_image(session):
    """Fetch CAPTCHA image and save locally."""
    response = session.get(CAPTCHA_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    captcha_img_tag = soup.find('img', {'id': 'captchaImage'})
    if not captcha_img_tag:
        return None  # No CAPTCHA present on the page

    captcha_img_url = captcha_img_tag.get('src')
    captcha_img_response = session.get(captcha_img_url)

    with open("captcha.jpg", "wb") as f:
        f.write(captcha_img_response.content)
    return "captcha.jpg"


def check_appointment_page(session):
    """Solve CAPTCHA, submit it, and fetch the appointment page."""
    while True:
        # Fetch CAPTCHA image
        captcha_image_path = fetch_captcha_image(session)
        if not captcha_image_path:
            break  # No CAPTCHA to solve; continue to the next step

        # Solve CAPTCHA using TrueCaptcha
        captcha_text = solve_captcha(captcha_image_path)
        print(f"Captcha solved: {captcha_text}")

        # Submit CAPTCHA and move to the appointment page
        payload = {'captchaText': captcha_text}
        response = session.post(CAPTCHA_URL, data=payload)
        if "captchaImage" not in response.text:
            break  # Successfully bypassed CAPTCHA

    soup = BeautifulSoup(response.content, 'html.parser')
    page_content = soup.get_text()
    return page_content

async def notify_via_telegram(message):
    """Send notification to Telegram."""
    await bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    print("Monitoring appointment page...")
    session = requests.Session()  # Persistent session to handle cookies
    previous_content = ""

    while True:
        try:
            # Check the appointment page
            current_content = check_appointment_page(session)
            if current_content != previous_content:
                print("Change detected! Notifying...")
                asyncio.run(notify_via_telegram("Appointment page has changed! Check the website."))
                previous_content = current_content
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(5)  # Wait 5 seconds before the next check


if __name__ == "__main__":
    main()