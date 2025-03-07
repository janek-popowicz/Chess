import tkinter as tk
from tkinter import ttk
import json
import subprocess

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"volume": 0.5, "resolution": "1260x960"}

def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)

def apply_settings(volume, resolution):
    print(f"Zastosowano ustawienia: Głośność={volume}, Rozdzielczość={resolution}")

def main():
    config = load_config()

    root = tk.Tk()
    root.title("Ustawienia")

    # Głośność
    tk.Label(root, text="Głośność").grid(row=0, column=0, padx=10, pady=10)
    volume = tk.IntVar(value=config["volume"])
    tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, variable=volume).grid(row=0, column=1, padx=10, pady=10)

    # Rozdzielczość
    tk.Label(root, text="Rozdzielczość").grid(row=1, column=0, padx=10, pady=10)
    resolution = tk.StringVar(value=config["resolution"])
    ttk.Combobox(root, textvariable=resolution, values=["1260x960", "1300x1000", "1660x1360", "2364x2064"]).grid(row=1, column=1, padx=10, pady=10)

    # Zapisz i Zastosuj
    def save_and_apply():
        config["volume"] = volume.get()
        config["resolution"] = resolution.get()
        save_config(config)
        apply_settings(config["volume"], config["resolution"])
        root.destroy()
        subprocess.Popen(["python3", "launcher.py"])

    tk.Button(root, text="Zapisz i Zastosuj", command=save_and_apply).grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()