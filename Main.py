import requests
import json
from datetime import datetime
import os
import sys
from typing import Optional, Dict, Any
from colorama import Fore, Style, init

# Renkli terminal çıktılarını başlat
init(autoreset=True)

class InstagramAPI:
    """
    Instagram profil bilgilerini çekmek için API tabanlı sınıf.
    Kısıtlı erişim sunabilir (Hızlı ama her zaman çalışmayabilir).
    """
    def __init__(self, username: str):
        self.username = username
        self.api_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'X-IG-App-ID': '936619743392459',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Origin': 'https://www.instagram.com',
            'Referer': f'https://www.instagram.com/{username}/',
            'DNT': '1'
        }
        self.profile_data: Optional[Dict[str, Any]] = None

    def fetch_profile_info(self) -> bool:
        """API üzerinden profil verilerini çeker."""
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=15)
            if response.status_code == 404:
                self._error_message("Kullanıcı bulunamadı!")
                return False

            response.raise_for_status()
            self.profile_data = response.json()

            if "data" in self.profile_data and "user" in self.profile_data["data"]:
                return True

            self._error_message("Geçersiz yanıt alındı")
            return False

        except requests.exceptions.RequestException as e:
            self._error_message(f"API Hatası: {str(e)}")
            return False
        except json.JSONDecodeError:
            self._error_message("Geçersiz JSON yanıtı alındı")
            return False

    def display_info(self) -> None:
        """Bilgileri konsol üzerinde şık bir formatta görüntüler."""
        if not self.profile_data:
            self._error_message("Profil verisi alınamadı!")
            return

        user = self.profile_data["data"]["user"]
        clear_console()

        print(f"\n{Fore.YELLOW}{'_'*60}")
        print(f"|{Fore.CYAN}{'INSTAGRAM PROFİL ANALİZİ':^58} {Fore.YELLOW}|")
        print(f"|{'_'*60}|")

        self._info_line("Kullanıcı", user['username'], Fore.CYAN)
        self._info_line("Tam Ad", user['full_name'], Fore.CYAN)

        print(f"{Fore.YELLOW}╟{'─'*60}╢")
        self._info_line("Takipçi", f"{user['edge_followed_by']['count']:,}", Fore.LIGHTGREEN_EX)
        self._info_line("Takip", f"{user['edge_follow']['count']:,}", Fore.LIGHTGREEN_EX)
        self._info_line("Gönderi", f"{user['edge_owner_to_timeline_media']['count']:,}", Fore.LIGHTGREEN_EX)

        print(f"{Fore.YELLOW}╟{'─'*60}╢")
        self._info_line("Doğrulanmış", '✅ Evet' if user['is_verified'] else '❌ Hayır')
        self._info_line("Gizli", '✅ Evet' if user['is_private'] else '❌ Hayır')

        if user['biography']:
            bio = user['biography'].replace('\n', ' ')
            self._info_line("Biyografi", bio[:40] + '...' if len(bio) > 40 else bio)

        print(f"{Fore.YELLOW}╚{'═'*60}╝\n")
        self._print_header("Ek Bilgiler")

        if user.get('business_email'):
            self._info_line("İş E-postası", user['business_email'])

        if user.get('external_url'):
            self._info_line("Harici Link", user['external_url'])

        self.save_to_json(user)

    def save_to_json(self, data: Dict[str, Any]) -> None:
        """Verileri JSON dosyası olarak kaydeder."""
        choice = input(f"{Fore.YELLOW}📂 Profil bilgilerini kaydetmek ister misiniz? (e/h): {Style.RESET_ALL}").lower()
        if choice == 'e':
            filename = f"instagram_{self.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"\n{Fore.GREEN}✅ Profil bilgileri '{filename}' olarak kaydedildi.{Style.RESET_ALL}")
            except IOError as e:
                self._error_message(f"Dosya yazma hatası: {str(e)}")

    def _error_message(self, message: str) -> None:
        """Hata mesajı yazdırır."""
        print(f"\n{Fore.RED}⛔ {message}{Style.RESET_ALL}")

    def _print_header(self, title: str) -> None:
        """Başlık yazdırır."""
        print(f"\n{Fore.MAGENTA}┌{'─'*58}┐")
        print(f"│ {Fore.CYAN}{title.upper():^56} {Fore.MAGENTA}│")
        print(f"└{'─'*58}┘{Style.RESET_ALL}")

    def _info_line(self, label: str, value: Any, color: str = Fore.WHITE) -> None:
        """Tablonun bir satırını yazdırır."""
        print(f"{Fore.YELLOW}│ {Fore.GREEN}{label:<25}{Fore.YELLOW}: {color}{value:>28} {Fore.YELLOW}│")

def clear_console():
    """Konsolu temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_main_menu() -> None:
    """Ana menüyü gösterir."""
    clear_console()
    print(f"│ {Fore.CYAN}{'INSTAGRAM PROFİL SORGU':^58} {Fore.YELLOW}")
    print(f"├{'─'*60}┤")
    print(f"│ {Fore.WHITE}Geliştirici: {Fore.CYAN}@Memati8383{'':>30} {Fore.YELLOW}")
    print(f"│ {Fore.WHITE}github: {Fore.CYAN}https://github.com/Memati8383/{'':>35} {Fore.YELLOW}")
    print(f"└{'─'*60}┘{Style.RESET_ALL}")

def main():
    show_main_menu()

    while True:
        username = input(f"\n{Fore.CYAN}🔍 Instagram kullanıcı adı (Çıkmak için 'q'): {Style.RESET_ALL}").strip()

        if username.lower() == 'q':
            print(f"\n{Fore.YELLOW}👋 Çıkış yapılıyor...{Style.RESET_ALL}")
            sys.exit(0)

        if not username:
            print(f"{Fore.RED}⚠ Lütfen geçerli bir kullanıcı adı girin!{Style.RESET_ALL}")
            continue

        print(f"\n{Fore.BLUE}⌛ Profil bilgileri alınıyor...{Style.RESET_ALL}")
        insta = InstagramAPI(username)

        if insta.fetch_profile_info():
            insta.display_info()
        else:
            print(f"{Fore.RED}⛔ Kullanıcı bulunamadı veya profili gizli!{Style.RESET_ALL}")

        again = input(f"\n{Fore.YELLOW}🔄 Başka bir kullanıcı sorgulamak ister misiniz? (e/h): {Style.RESET_ALL}").lower()
        if again != 'e':
            print(f"\n{Fore.YELLOW}👋 Program sonlandırıldı.{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}⏹ Program kullanıcı tarafından durduruldu.{Style.RESET_ALL}")
        sys.exit(1)
