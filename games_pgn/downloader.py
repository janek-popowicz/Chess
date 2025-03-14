import time
import random
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager


options = Options()
options.add_argument("--headless")  # Uruchamianie bez GUI (możesz usunąć, jeśli chcesz widzieć, co się dzieje)
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)

# Strona z partiami Kasparova
url = "https://www.chess.com/pl/games/bobby-fischer"
driver.get(url)
time.sleep(random.uniform(2, 4))  # Czekamy na załadowanie strony

all_games_pgn = []
page_count = 1

while page_count < 48:
    try:
        print(f"📄 Przetwarzanie strony {page_count}...")

        # **1. Zamknięcie bannera (jeśli istnieje)**
        try:
            close_banner = driver.find_element(By.CLASS_NAME, "ready-to-play-banner-content")
            driver.execute_script("arguments[0].remove();", close_banner)
            print("✅ Usunięto banner.")
        except:
            print("ℹ️ Brak bannera.")

        time.sleep(random.uniform(0.5, 1.5))

        # **2. Kliknięcie checkboxa "Wybierz wszystkie"**
        try:
            select_all_checkbox = driver.find_element(By.ID, "master-games-check-all")
            driver.execute_script("arguments[0].click();", select_all_checkbox)
            print("✅ Zaznaczono wszystkie partie.")
        except:
            print("⚠️ Nie znaleziono przycisku zaznaczenia.")
            continue

        time.sleep(random.uniform(0.5, 1.5))

        # **3. Kliknięcie przycisku pobierania**
        try:
            download_button = driver.find_element(By.CLASS_NAME, "master-games-download-icon")
            driver.execute_script("arguments[0].click();", download_button)
            print("✅ Kliknięto przycisk pobierania.")
        except:
            print("⚠️ Nie znaleziono przycisku pobierania.")
            continue

        time.sleep(random.uniform(1, 2))

        # **4. Pobranie PGN z kodu strony**
        pgn_elements = driver.find_elements(By.CLASS_NAME, "archive-games-download-games")
        for element in pgn_elements:
            all_games_pgn.append(element.text)

        time.sleep(random.uniform(0.5, 1.5))

        # **5. Przejście do następnej strony**
        try:
            next_page = driver.find_element(By.CLASS_NAME, "chevron-right")
            next_page.click()
            print("➡️ Przejście do następnej strony.")
            page_count += 1
        except:
            print("⚠️ Nie znaleziono przycisku przejścia.")

        time.sleep(random.uniform(2, 4))  # Opóźnienie przed kolejną stroną

    except Exception as e:
        print(f"❌ Błąd: {e}")
        break

# **Zapisanie do pliku PGN**
with open("kasparov_games.pgn", "w", encoding="utf-8") as f:
    f.write("\n\n".join(all_games_pgn))

print(f"🎉 Pobrano {len(all_games_pgn)} partii i zapisano do ktośtam_games.pgn")
driver.quit()
