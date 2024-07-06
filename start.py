import os
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def log(log_text):
    log_text = str(time.strftime("%Y.%m.%d %H:%M:%S")) + " ➾ " + log_text
    print(log_text)
    log_file = open("log.txt", "a", encoding='utf-8')
    log_file.write(log_text + "\n")
    log_file.close()

def trendyol_yorum_cek(url):
    if os.path.exists("yorumlar.txt"):
        os.remove("yorumlar.txt")

    chrome_options = Options()
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    time.sleep(9) 

    try:
        total_comments = 0
        last_height = driver.execute_script("return document.body.scrollHeight")
        time.sleep(5)
        kac_yorum_var = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/div/div/div[1]/div/div[2]/div[2]/div[3]/div').text
        kac_yorum_var = kac_yorum_var.replace(" Yorum", "")
        log('Toplam ' + kac_yorum_var + ' yorum var.')
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5) 

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

            html_content = driver.page_source
            soup = BeautifulSoup(html_content, "html.parser")
            comments = soup.find_all("p")

            exclude_patterns = [
                r"Acele et! Son \d+ günde \d+[\+\.,]? adet ürün satıldı!!",
                r"\d+B kişinin sepetinde, tükenmeden al!",
                r"Popüler ürün! Son \d+ saatte \d+B kişi görüntüledi!",
                r"Sevilen ürün! \d+B kişi favoriledi!",
                r"Sepetinizde Ürün Bulunmamaktadır.",
                r"10.000’lerce yeni ürünü ve sezon trendlerini büyük indirimlerle yakalamak için,"
            ]

            def is_excluded(text):
                for pattern in exclude_patterns:
                    if re.search(pattern, text):
                        return True
                return False

            with open("yorumlar.txt", "a", encoding='utf-8') as dosya:
                for comment in comments:
                    if not any(comment.has_attr(attr) for attr in ["class", "div", "span", "id"]):
                        if not is_excluded(comment.text):
                            dosya.write(comment.text + "\n")
                            print(comment.text)
                            total_comments += 1

    except Exception as e:
        log('Hata: ' + str(e))
    finally:
        log(f'Toplam {total_comments} yorum toplandı.')
        log('Program sonlandı')
        driver.quit()


urun_url = input("Trendyol ürününün yorumlar sayfasının linkini giriniz: ")
if '?' in urun_url:
    urun_url = urun_url[:urun_url.index('?')]  
urun_url += "/yorumlar"
trendyol_yorum_cek(urun_url)