import tkinter as tk
from tkinter import ttk
import json
from language import global_translations

CONFIG_FILE = "config.json"

def load_config():
    """
    Ładuje konfigurację z pliku `config.json`.

    Returns:
        dict: Słownik z ustawieniami konfiguracji.
    """
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        # Domyślne ustawienia w przypadku braku pliku konfiguracyjnego
        return {
            "volume": 0.5,
            "resolution": "1260x960",
            "icons": "classic",
            "highlight_enemy": 0,
            "nerd_view": 0
        }

def save_config(config):
    """
    Zapisuje konfigurację do pliku `config.json`.

    Args:
        config (dict): Słownik z ustawieniami konfiguracji.
    """
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)

def main():
    """
    Główna funkcja wyświetlająca okno ustawień gry.
    """
    # Załadowanie aktualnej konfiguracji
    config = load_config()

    # Inicjalizacja okna głównego
    root = tk.Tk()
    root.title(global_translations.get("settings"))

    # Ustawienie głośności
    tk.Label(root, text=global_translations.get('volume')).grid(row=0, column=0, padx=10, pady=10)
    volume = tk.IntVar(value=config["volume"])
    tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, variable=volume).grid(row=0, column=1, padx=10, pady=10)

    # Ustawienie rozdzielczości
    tk.Label(root, text=global_translations.get('resolution')).grid(row=1, column=0, padx=10, pady=10)
    resolution = tk.StringVar(value=config["resolution"])
    ttk.Combobox(
        root,
        textvariable=resolution,
        values=["1260x960", "1300x1000", "1660x1360", "2364x2064"]
    ).grid(row=1, column=1, padx=10, pady=10)

    # Wybór ikon figur
    tk.Label(root, text=global_translations.get('pieces_icons')).grid(row=2, column=0, padx=10, pady=10)
    icons = tk.StringVar(value=config["icons"])
    ttk.Combobox(
        root,
        textvariable=icons,
        values=["classic", "modern", "classic_2", "military_symbols", "military", "detailed", "gold", "custom"]
    ).grid(row=2, column=1, padx=10, pady=10)

    # Opcja podświetlenia figur przeciwnika
    highlight_enemy = tk.BooleanVar(value=config["highlight_enemy"])
    tk.Checkbutton(
        root,
        variable=highlight_enemy,
        text=global_translations.get('highlight_enemy'),
        onvalue=1,
        offvalue=0
    ).grid(row=3, column=1, padx=10, pady=10)

    # Opcja trybu nerd_view
    nerd_view = tk.BooleanVar(value=config["nerd_view"])
    tk.Checkbutton(
        root,
        variable=nerd_view,
        text=global_translations.get('nerd_view'),
        onvalue=1,
        offvalue=0
    ).grid(row=4, column=1, padx=10, pady=10)

    # Funkcja zapisu i zastosowania ustawień
    def save_and_apply():
        """
        Zapisuje zmienione ustawienia do pliku i zamyka okno ustawień.
        """
        config["volume"] = volume.get()
        config["resolution"] = resolution.get()
        config["icons"] = icons.get()
        config["highlight_enemy"] = highlight_enemy.get()
        config["nerd_view"] = nerd_view.get()
        save_config(config)
        root.destroy()

    # Przycisk "Zapisz i Zastosuj"
    tk.Button(
        root,
        text=global_translations.get('save_and_apply'),
        command=save_and_apply
    ).grid(row=7, column=0, columnspan=2, padx=10, pady=10)

    # Uruchomienie pętli głównej
    root.mainloop()
