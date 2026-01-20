import sys
import os
import time
import json
import logging
import re
import random
import requests
from typing import Optional, Dict, Any
from datetime import datetime

# Üçüncü taraf kütüphaneler
from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Colorama'yı başlat
# Windows terminalleri için UTF-8 kodlamasını zorla (UnicodeEncodeError hatasını önlemek için)
sys.stdout.reconfigure(encoding='utf-8')
init(autoreset=True)

# Gürültülü Selenium loglarını engelle
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Farklı cihaz kimliklerinden oluşan havuz (Tespit edilmeyi zorlaştırır)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
]

def clear_console():
    """Konsolu temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

class InstagramSeleniumBot:
    """
    Instagram profil bilgilerini çekmek için Selenium tabanlı bot.
    Görünmez olması için headless (arkaplan) modda çalışır.
    """
    def __init__(self):
        self.driver = None
        self._setup_driver()

    def _setup_driver(self):
        """Chrome sürücüsünü headless modda başlatır."""
        print(f"{Fore.BLUE}⚙️  Arkaplan sistemi hazırlanıyor (Selenium)...{Style.RESET_ALL}")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # Modern headless mod
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--log-level=3")  # Gereksiz logları kapat
        
        # Anti-tespit önlemi: Rastgele User-Agent seç
        user_agent = random.choice(USER_AGENTS)
        chrome_options.add_argument(f"user-agent={user_agent}")
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        try:
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=chrome_options
            )
        except Exception as e:
            print(f"{Fore.RED}⛔ Sürücü başlatılamadı: {e}{Style.RESET_ALL}")
            sys.exit(1)

    def scrape_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Kullanıcı profiline gider ve Meta etiketleri ile DOM üzerinden verileri çeker.
        """
        if not self.driver:
            return None

        url = f"https://www.instagram.com/{username}/"
        try:
            self.driver.get(url)
            # Meta etiketlerinin yüklenmesi için bekle
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "meta"))
            )

            # 404/Bulunamadı kontrolü
            page_title = self.driver.title
            if "Page Not Found" in page_title or "Bulunamadı" in page_title:
                return None

            data = {
                "username": username,
                "full_name": "N/A",
                "followers": "0",
                "following": "0",
                "posts": "0",
                "is_verified": False,
                "is_private": False,
                "biography": "",
                "external_url": None,
                "profile_image_url": None,
                "scraped_at": datetime.now().isoformat()
            }

            # JS'nin meta etiketlerini doldurması için kısa bir süre bekle
            time.sleep(3) 
            
            # 1. Sayısal Verileri og:description'dan Çek (Dilden bağımsız yaklaşım)
            try:
                og_desc_element = self.driver.find_elements(By.XPATH, '//meta[@property="og:description"]')
                if og_desc_element:
                    og_desc = og_desc_element[0].get_attribute("content")
                    # Örnek: "699M Takipçi, 180 Takip, 8,305 Gönderi - ..."
                    stats_part = og_desc.split(' - ')[0]
                    
                    # Regex ile sayı ve etiketi bul: {sayı} {etiket}
                    patterns = re.findall(r'([\d\.,\s]+[KMB]?)[\s]+([^\d,]+)', stats_part)
                    
                    for value, label in patterns:
                        label = label.lower().strip()
                        value = value.strip()
                        
                        if any(x in label for x in ['takipçi', 'follower']):
                            data['followers'] = value
                        elif any(x in label for x in ['takip', 'following']) and 'takipçi' not in label:
                            data['following'] = value
                        elif any(x in label for x in ['gönderi', 'post']):
                            data['posts'] = value
                
                    # Regex başarısız olursa virgülle ayırmayı dene
                    if data['followers'] == "0" and ',' in stats_part:
                        parts = stats_part.split(',')
                        if len(parts) >= 3:
                            data['followers'] = parts[0].strip().split(' ')[0]
                            data['following'] = parts[1].strip().split(' ')[0]
                            data['posts'] = parts[2].strip().split(' ')[0]
            except Exception:
                pass 

            # 2. Tam Adı og:title'dan Çek
            try:
                og_title_element = self.driver.find_elements(By.XPATH, '//meta[@property="og:title"]')
                if og_title_element:
                    og_title = og_title_element[0].get_attribute("content")
                    # Format: "Name (@username) • Instagram..."
                    if "(@"+username+")" in og_title:
                        data['full_name'] = og_title.split('(@')[0].strip()
                    elif "•" in og_title:
                        data['full_name'] = og_title.split('•')[0].strip()
            except:
                pass

            # 3. Doğrulanmış Hesap Kontrolü
            try:
                page_source = self.driver.page_source
                if "Verified" in page_source or "Doğrulanmış" in page_source or 'aria-label="Verified"' in page_source:
                    data['is_verified'] = True
            except:
                pass

            # 4. Gizli Hesap Kontrolü
            try:
                page_text = self.driver.page_source.lower()
                if "this account is private" in page_text or "bu hesap gizli" in page_text:
                    data['is_private'] = True
            except:
                pass

            # 5. Biyografi Çekme (Meta veya Script üzerinden)
            try:
                scripts = self.driver.find_elements(By.XPATH, "//script[@type='application/ld+json']")
                for script in scripts:
                    try:
                        jc = json.loads(script.get_attribute("innerHTML"))
                        if jc.get('@type') == 'Person':
                            if 'description' in jc: data['biography'] = jc['description']
                            if 'name' in jc and data['full_name'] == "N/A": data['full_name'] = jc['name']
                    except: continue
            except:
                pass

            # 6. Profil Resmi URL'si
            try:
                img_element = self.driver.find_element(By.XPATH, '//meta[@property="og:image"]')
                if img_element:
                    data['profile_image_url'] = img_element.get_attribute("content")
            except:
                pass

            return data

        except Exception:
            return None

    def close(self):
        """Sürücüyü kapatır."""
        if self.driver:
            self.driver.quit()

    def download_profile_image(self, url: str, username: str):
        """Profil resmini HD olarak indirir ve kaydeder."""
        if not url: return None
        try:
            filename = f"pp_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return filename
        except Exception:
            return None
        return None

class DisplayManager:
    """Ekran çıktılarını yöneten sınıf."""
    @staticmethod
    def show_header():
        clear_console()
        print(f"│ {Fore.CYAN}{'OTOMATİK ARKA PLAN SİSTEMİ':^58} {Fore.YELLOW}")
        print(f"├{'─'*60}┤")
        print(f"│ {Fore.WHITE}Sistem: {Fore.GREEN}SELENIUM HEADLESS{'':>32} {Fore.YELLOW}")
        print(f"│ {Fore.WHITE}Durum: {Fore.GREEN}AKTİF{'':>41} {Fore.YELLOW}")
        print(f"└{'─'*60}┘{Style.RESET_ALL}\n")

    @staticmethod
    def show_profile(data: Dict[str, Any]):
        print(f"\n{Fore.YELLOW}{'_'*60}")
        print(f"|{Fore.CYAN}{' INSTAGRAM PROFİL RAPORU ':^58} {Fore.YELLOW}|")
        print(f"|{'_'*60}|")

        DisplayManager._row("Kullanıcı", data['username'], Fore.CYAN)
        DisplayManager._row("İsim", data['full_name'], Fore.WHITE)
        
        print(f"{Fore.YELLOW}╟{'─'*60}╢")
        DisplayManager._row("Takipçi", data['followers'], Fore.LIGHTGREEN_EX)
        DisplayManager._row("Takip", data['following'], Fore.LIGHTGREEN_EX)
        DisplayManager._row("Gönderi", data['posts'], Fore.LIGHTGREEN_EX)
        
        print(f"{Fore.YELLOW}╟{'─'*60}╢")
        DisplayManager._row("Doğrulanmış", '✅ Evet' if data['is_verified'] else '❌ Hayır', Fore.WHITE)
        DisplayManager._row("Gizli Hesap", '🔒 Evet' if data['is_private'] else '🔓 Hayır', Fore.WHITE)

        if 'profile_image_url' in data and data['profile_image_url']:
             DisplayManager._row("Profil Resmi", "Bulundu (HD)", Fore.CYAN)

        if data['biography']:
            bio = data['biography'].replace('\n', ' ')
            DisplayManager._row("Biyo", bio[:50] + '...' if len(bio) > 50 else bio)
            
        print(f"{Fore.YELLOW}╚{'═'*60}╝\n")

    @staticmethod
    def _row(label, value, color=Fore.WHITE):
        print(f"{Fore.YELLOW}│ {Fore.GREEN}{label:<20}{Fore.YELLOW}: {color}{str(value):>33} {Fore.YELLOW}│")

def main():
    DisplayManager.show_header()
    
    bot = InstagramSeleniumBot()
    
    while True:
        try:
            username = input(f"\n{Fore.CYAN}🔍 Kullanıcı adı girin (Çıkış: q): {Style.RESET_ALL}").strip()
            
            if username.lower() == 'q':
                break
                
            if not username:
                continue

            print(f"{Fore.BLUE}⌛ Veriler çekiliyor (Arka plan)...{Style.RESET_ALL}")
            
            data = bot.scrape_profile(username)
            
            if data:
                DisplayManager.show_profile(data)
                
                # Kayıt seçeneği
                if input(f"{Fore.MAGENTA}💾 Bilgileri ve resmi kaydet? (e/h): {Style.RESET_ALL}").lower() == 'e':
                    # JSON Kaydet
                    filename = f"selenium_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    print(f"{Fore.GREEN}✅ Veri Kaydedildi: {filename}")

                    # Resmi Kaydet
                    if 'profile_image_url' in data and data['profile_image_url']:
                        print(f"{Fore.BLUE}⌛ Profil resmi indiriliyor...{Style.RESET_ALL}")
                        saved_img = bot.download_profile_image(data['profile_image_url'], username)
                        if saved_img:
                             print(f"{Fore.GREEN}✅ Resim Kaydedildi: {saved_img}{Style.RESET_ALL}")
                        else:
                             print(f"{Fore.RED}❌ Resim indirilemedi.{Style.RESET_ALL}")

            else:
                print(f"{Fore.RED}❌ Kullanıcı bulunamadı veya erişim hatası!{Style.RESET_ALL}")

        except KeyboardInterrupt:
            break
    
    print(f"\n{Fore.YELLOW}Sistem kapatılıyor...{Style.RESET_ALL}")
    bot.close()

if __name__ == "__main__":
    main()
