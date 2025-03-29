import os
import time
import random
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager


# Katalog docelowy dla pobranych plików
download_dir = os.path.expanduser("~/Downloads")

# Konfiguracja Firefoksa
options = Options()
service = Service(GeckoDriverManager().install())
# options.add_argument("--headless")  # Uruchamianie bez GUI (możesz usunąć, jeśli chcesz widzieć, co się dzieje)
driver = webdriver.Firefox(service=service, options=options)

def download_games(num_games):
    url = f"https://www.chess.com/library/collections/openings-by-name-tWVhQu4a?itemsPerPage=25"
    driver.get(url)
    time.sleep(random.uniform(3, 6))

    num_pages = (num_games // 25) + (1 if num_games % 25 else 0)
    print(f"📥 Pobieranie {num_games} openingów ({num_pages} stron)...")

    for page in range(1, num_pages + 1):
        print(f"➡️ Strona {page}/{num_pages}")
        
        try:
            # Usunięcie bannera
            try:
                close_banner = driver.find_element(By.CLASS_NAME, "ready-to-play-banner-content")
                driver.execute_script("arguments[0].remove();", close_banner)
                print("✅ Usunięto banner.")
            except:
                pass
            
            time.sleep(random.uniform(1, 3))
            
            # Zaznaczenie wszystkich partii
            try:
                checkbox = driver.find_element(By.ID, "selectAll")
                driver.execute_script("arguments[0].click();", checkbox)
                print("✅ Zaznaczono wszystkie partie.")
            except:
                print("⚠️ Nie znaleziono przycisku zaznaczenia.")
                continue
            
            time.sleep(random.uniform(1, 3))
            
            # Kliknięcie pobrania
            try:
                download_button = driver.find_element(By.CSS_SELECTOR, '[data-cy="download-btn"]')
                driver.execute_script("arguments[0].click();", download_button)
                print("✅ Kliknięto przycisk pobierania.")
            except:
                print("⚠️ Nie znaleziono przycisku pobierania.")
                continue
            
            time.sleep(random.uniform(2, 5))
            
            # Przejście do następnej strony
            try:
                next_page = driver.find_element(By.CLASS_NAME, "chevron-right")
                next_page.click()
                print("➡️ Przejście do następnej strony.")
            except:
                print("⚠️ Nie znaleziono przycisku przejścia.")
                break
            
            time.sleep(random.uniform(4, 8))
        except Exception as e:
            print(f"❌ Błąd na stronie {page}: {e}")
            break
    player = "openings"
    merge_pgn_files(player)

def merge_pgn_files(player):
    merged_file = os.path.join(download_dir, f"{player}.pgn")
    pgn_files = sorted([f for f in os.listdir(download_dir) if f.endswith(".pgn")])
    
    if not pgn_files:
        print(f"⚠️ Brak plików do scalania dla {player}!")
        return
    
    print(f"🔄 Scalanie {len(pgn_files)} plików PGN dla {player}...")
    
    with open(merged_file, "w", encoding="utf-8") as outfile:
        for pgn_file in pgn_files:
            with open(os.path.join(download_dir, pgn_file), "r", encoding="utf-8") as infile:
                outfile.write(infile.read() + "\n\n")
            os.remove(os.path.join(download_dir, pgn_file))
    
    print(f"✅ Pobrano i scalono {player} do {merged_file}")

# Pobieranie partii dla wszystkich arcymistrzów
download_games(2014)

driver.quit()
print("🎉 Pobieranie zakończone!")
