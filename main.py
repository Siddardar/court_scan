import warnings
from operator import index
import requests
from bs4 import BeautifulSoup
from auth import USERNAME, PASSWORD, PIN
import base64
import rsa
import info
import time as wait
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re as reSearch


def warn(*args, **kwargs):
    pass


warnings.warn = warn


class CourtBooking(object):
    def __init__(self):
        self.client = requests.Session()
        # Ensures that requests mimic browser so that access does not get denied
        self.custom_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }

        chrome_options = Options()
        chrome_options.headless = True
        # chrome_options.add_argument(
        #   'user-data-dir=C:\\Users\\srsan\\AppData\\Local\\Google\\Chrome\\User Data')
        # chrome_options.add_argument('profile-directory=Profile 1')
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(
            'chromedriver.exe', options=chrome_options)

    def login(self):
        r = self.client.get(
            'https://members.myactivesg.com/auth', headers=self.custom_headers)
        soup = BeautifulSoup(r.content, 'lxml')

        public_key_text = soup.find('input', {'name': 'rsapublickey'})['value']

        # Base64 encoding(rsa encrption(changing password str to bytes, chaging the rsa key found on website to a rsa PublicKey object))
        ec_password = base64.b64encode(rsa.encrypt(str.encode(
            PASSWORD), rsa.PublicKey.load_pkcs1_openssl_pem(public_key_text)))

        # Additional token needed by website for security
        csrf_token = soup.find('input', {'name': '_csrf'})['value']

        data_dict = {
            'email': USERNAME,
            'ecpassword': ec_password,
            '_csrf': csrf_token,
        }

        login_r = self.client.post(
            'https://members.myactivesg.com/auth/signin', headers=self.custom_headers, data=data_dict)

        if login_r.url == 'https://members.myactivesg.com/profile':
            print('Login Success')
            global cookies
            cookies = self.client.cookies

        else:
            print('Login Failed. Check login details and try again')
            self.driver.close()
            exit()

    def sel_login(self):
        self.driver.get('https://members.myactivesg.com/auth/signin')
        for c in cookies:
            self.driver.add_cookie({
                'name': c.name,
                'value': c.value
            })

        self.driver.refresh()
        print('Selenium logged in')

    def delay(self):
        current_datetime = datetime.datetime.now()

        if current_datetime.hour > 6:
            search_datetime = datetime.datetime(
                current_datetime.year, current_datetime.month, current_datetime.day+1, 7, 00, 00)
        else:
            search_datetime = datetime.datetime(
                current_datetime.year, current_datetime.month, current_datetime.day, 7, 00, 00)

        delay_wait = search_datetime - current_datetime

        print(f'Waiting for {int(delay_wait.seconds/60)} minutes')
        wait.sleep(delay_wait.seconds)
        wait.sleep(5)

    def slots(self, soup, id):
        available_courts = []
        courts_want = []

        for court in soup.find_all('div', class_='subvenue-slot'):
            for slots in court.find_all('div', class_='col-xs-4 col-sm-2 chkbox-grid'):
                avail = slots.find('input').get('value')
                if avail != None and avail[0] == 'C':
                    available_courts.append(avail)
        try:
            if len(info.search_id) > info.search_id.index(id):
                next_loc = f'\nNext location: {info.search_list[info.search_id.index(id)+1]}. Press "n" to search here\n'
        except:
            next_loc = '\n'+'\033[91m' + \
                'Last location in search location\n'+'\033[91m'

        if available_courts != [] and info.pre_selection != ['n']:
            timings_found = []
            for time in info.pre_selection:
                time_search = time + ':00:00'
                for c in available_courts:
                    if time_search in c:
                        courts_want.append(c)
                        timings_found.append(time)
                        print(f'Court found at {time}00hrs')
                        break

            if len(courts_want) == len(info.pre_selection):
                return courts_want

            elif timings_found != info.pre_selection:
                timing_unavailable = [
                    t for t in info.pre_selection if t not in timings_found]
                for t in timing_unavailable:
                    print(f'Court not found at {t}00hrs')
                print("Choose from courts shown below")

        elif available_courts != []:
            timings_found = []
            pass

        elif available_courts == []:
            print(f'No courts available\n{next_loc}')
            return courts_want

        if info.pre_selection == ['n'] or timing_unavailable != []:
            count = 1
            for avail_court in available_courts:
                court_info = avail_court.split(";")
                court_no = court_info[0]
                time_start = court_info[-2]
                time_end = court_info[-1]
                time = [time_start, time_end]

                print(f'{count:02}: {court_no}, {time}')
                count += 1

            print(next_loc)
            manual_selection = list(
                input(f'Select Court to book (Max {2 - len(timings_found)}): ').split(","))

            if manual_selection == ['n']:
                courts_want = []
                return courts_want
            elif manual_selection == ['exit']:
                self.driver.close()
                exit

            for s in manual_selection:
                index = int(s) - 1
                courts_want.append(available_courts[index])

            return courts_want

    def morning(self):

        booking_url = 'https://members.myactivesg.com/facilities/'
        self.driver.get(booking_url)
        wait.sleep(1)

        html_source = self.driver.page_source
        soup = BeautifulSoup(html_source, 'lxml')

        token_all = str(soup.find('iframe', attrs={'title': 'reCAPTCHA'}))

        url = reSearch.search(
            "(?P<url>https?://[^\s]+)", token_all).group("url")
        index_start = int(url.find('v=')) + 2
        index_end = int(url.find('&amp;size=invisible'))

        token = url[index_start:index_end]
        print(f'Token found: {token}')

        if info.delay == 'y':
            self.delay()

        try:
            self.driver.get(
                f'https://members.myactivesg.com/facilities/solve_captcha?token={token}')
            wait.sleep(0.5)

            WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[title^='reCAPTCHA']")))
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="recaptcha-anchor-label"]'))).click()
            self.driver.switch_to.parent_frame()
            wait.sleep(0.5)
            submit_button = self.driver.find_element_by_xpath(
                '//*[@id="main"]/div[3]/div/article/section[2]/section/div[1]/form/div[2]/button')
            submit_button.click()
            wait.sleep(0.5)
        except:
            print('Captcha not needed')

        court_url = 'https://members.myactivesg.com/facilities/quick-booking'

        for id in info.search_id:
            print(
                f'Searching for courts at {info.search_list[info.search_id.index(id)]} on {info.booking_date.strftime("%B %d, %Y")}')
            cookies = self.driver.get_cookies()
            # print(cookies)

            for cookie in cookies:
                self.client.cookies.set(cookie['name'], cookie['value'])

            data = {
                'activity_filter': '18',
                'venue_filter': f'{id}',
                'date_filter': f'{info.booking_date.strftime("%a, %#d %b %Y")}'
            }
            court_res = self.client.post(
                court_url, data=data, headers=self.custom_headers)

            self.driver.execute_script(
                f"""
            
                xhr.open("POST", {court_url}, true);
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.send(JSON.stringify({data}));
                
            """)

            soup = BeautifulSoup(court_res.content, 'lxml')

            courts_want = self.slots(soup, id)

            if courts_want != []:
                break

        if len(courts_want) == 0:
            # self.driver.close()
            return

        self.driver.get(court_url)
        for court in courts_want:
            print(f'Booking {court[:8]} at {court[-17:-15]}00hrs')
            court_number = court[7]
            if 'School' in info.search_list[info.search_id.index(id)]:
                court_time = str(int(court[-8:-6])-9)
            else:
                court_time = str(int(court[-8:-6])-7)
            button = self.driver.find_element_by_xpath(
                f'//*[@id="formTimeslots"]/div[1]/div[{court_number}]/div/div[{court_time}]')
            button.click()
            wait.sleep(0.5)

        if info.test != 'y':
            cart = self.driver.find_element_by_id('addtocartbtn')
            cart.click()
            wait.sleep(1)

            self.driver.get('https://members.myactivesg.com/cart')
            print('Added to cart')

    def available_dates(self):

        search_list = info.search_list
        search_id = info.search_id
        timestamp = info.booking_timestamp

        for id in search_id:
            print(
                f'Searching for courts at {search_list[search_id.index(id)]} on {info.booking_date.strftime("%B %d, %Y")}')

            court_url = f'https://members.myactivesg.com/facilities/view/activity/18/venue/{id}?time_from={timestamp}'
            court_res = self.client.get(court_url, headers=self.custom_headers)

            soup = BeautifulSoup(court_res.content, 'lxml')

            courts_want = self.slots(soup, id)

            if courts_want != []:
                break

        try:
            self.driver.get(court_url)
            for court in courts_want:
                print(f'Booking {court[:8]} at {court[-17:-15]}00hrs')
                court_number = court[7]
                if 'School' in search_list[search_id.index(id)]:
                    court_time = str(int(court[-8:-6])-9)
                else:
                    court_time = str(int(court[-8:-6])-7)
                button = self.driver.find_element_by_xpath(
                    f'//*[@id="formTimeslots"]/div[1]/div[{court_number}]/div/div[{court_time}]')
                button.click()
                wait.sleep(0.5)

            if info.test != 'y':
                cart = self.driver.find_element_by_id('addtocartbtn')
                cart.click()
                wait.sleep(1)

                self.driver.get('https://members.myactivesg.com/cart')
                print('Added to cart')
        except:
            return

    def checkout_cart(self):
        return


if __name__ == '__main__':
    booking = CourtBooking()
    booking.login()
    booking.sel_login()
    if info.morning == 'y':
        booking.morning()
    else:
        booking.available_dates()
