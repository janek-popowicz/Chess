import tkinter as tk
from tkinter import ttk
import json
from language import global_translations

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"volume": 0.5, "resolution": "1260x960", "icons": "classic", "highlight_enemy": 0, "nerd_view": 0}

def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)


def main():
    config = load_config()

    root = tk.Tk()
    root.title("Settings")

    # Głośność
    tk.Label(root, text=global_translations.get('volume')).grid(row=0, column=0, padx=10, pady=10)
    volume = tk.IntVar(value=config["volume"])
    tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, variable=volume).grid(row=0, column=1, padx=10, pady=10)

    # Rozdzielczość
    tk.Label(root, text=global_translations.get('resolution')).grid(row=1, column=0, padx=10, pady=10)
    resolution = tk.StringVar(value=config["resolution"])
    ttk.Combobox(root, textvariable=resolution, values=["1260x960", "1300x1000", "1660x1360", "2364x2064"]).grid(row=1, column=1, padx=10, pady=10)

    # Ikony figur
    tk.Label(root, text=global_translations.get('pieces_icons')).grid(row=2, column=0, padx=10, pady=10)
    icons = tk.StringVar(value=config["icons"])
    ttk.Combobox(root, textvariable=icons, values=["classic", "modern", "classic_2", "military_symbols", "military", "detailed", "gold", "custom"]).grid(row=2, column=1, padx=10, pady=10)

    # Podświetlenie figur przeciwnika
    highlight_enemy = tk.BooleanVar(value=config["highlight_enemy"])
    tk.Checkbutton(root, variable=highlight_enemy, text=global_translations.get('highlight_enemy'),onvalue=1,offvalue=0).grid(row=3, column=1, padx=10, pady=10)
    
    nerd_view = tk.BooleanVar(value=config["nerd_view"])
    tk.Checkbutton(root, variable=nerd_view, text=global_translations.get('nerd_view'),onvalue=1,offvalue=0).grid(row=4, column=1, padx=10, pady=10)

    # Zapisz i Zastosuj
    def save_and_apply():
        config["volume"] = volume.get()
        config["resolution"] = resolution.get()
        config["icons"] = icons.get()
        config["highlight_enemy"] = highlight_enemy.get()
        config["nerd_view"] = nerd_view.get()
        save_config(config)
        root.destroy()
        return

    tk.Button(root, text=global_translations.get('save_and_apply'), command=save_and_apply).grid(row=7, column=0, columnspan=2, padx=10, pady=10)

    root.mainloop()
    