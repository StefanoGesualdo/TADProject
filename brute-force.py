import csv
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


URL = "https://valid-exmarc.seiconsulting.it/app/exma?c=600000"


def leggi_credenziale(csv_path, riga=0):
    """
    CSV atteso:
    user;password
    mario.rossi;Password123
    """

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        righe = list(reader)

    if not righe:
        raise ValueError("Il CSV è vuoto.")

    if riga < 0 or riga >= len(righe):
        raise ValueError(f"Riga {riga} non presente nel CSV.")

    user = righe[riga].get("user")
    password = righe[riga].get("password")

    if not user or not password:
        raise ValueError("Il CSV deve contenere le colonne: user;password")

    return user, password


def login_singolo(user, password, headless=False):
    options = webdriver.ChromeOptions()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        driver.get(URL)

        wait = WebDriverWait(driver, 15)

        campo_user = wait.until(
            EC.presence_of_element_located((By.ID, "txMatricola"))
        )
        campo_password = wait.until(
            EC.presence_of_element_located((By.ID, "txPsw"))
        )
        pulsante_login = wait.until(
            EC.element_to_be_clickable((By.ID, "btnLogin"))
        )

        campo_user.clear()
        campo_user.send_keys(user)

        campo_password.clear()
        campo_password.send_keys(password)

        pulsante_login.click()

        # Qui aspettiamo un eventuale cambio pagina o messaggio
        wait.until(lambda d: d.current_url != URL or d.find_elements(By.ID, "lblMsg"))

        if driver.current_url != URL:
            return True
        else:
            return False

        #print("Login inviato.")
        #print("URL attuale:", driver.current_url)

        #messaggi = driver.find_elements(By.ID, "lblMsg")
        #if messaggi and messaggi[0].text.strip():
        #    print("Messaggio pagina:", messaggi[0].text.strip())

    finally:
     #   input("Premi INVIO per chiudere il browser...")
       driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Percorso file CSV con user;password")
    #parser.add_argument("--riga", type=int, default=0, help="Riga da usare, partendo da 0")
    parser.add_argument("--headless", action="store_true", help="Esegui senza finestra browser")

    args = parser.parse_args()

    with open("credenziali.csv", "r", encoding="utf-8") as file:
        numero_righe = sum(1 for riga in file) - 1 # meno l'intestazione
   
    for i in range(0, numero_righe):
        #user, password = leggi_credenziale(args.csv, args.riga)
        user, password = leggi_credenziale(args.csv, i)
        if login_singolo(user, password, args.headless):
            print("credenziali trovate")
            print("user", user)
            print("password", password)
            break