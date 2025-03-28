import json
import threading


def load_config():
    with open("config.json", "r") as file:
        return json.load(file)


class TranslationSingleton:
    _instance = None
    _lock = threading.Lock()

    def __init__(self, language='en'):
        if TranslationSingleton._instance is not None:
            raise Exception("This is a Singleton class. Use get_instance() to get the instance.")
        self.language = language
        self.translations = {}  # Przechowywanie tłumaczeń
        self._load_translations()

    def _load_translations(self):
        """
        Wczytuje plik JSON z tłumaczeniami dla zadanego języka.
        """
        try:
            with open(f"interface/translations/{self.language}.json", "r", encoding="utf-8") as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            print(f"Błąd: Plik z tłumaczeniami dla języka {self.language} nie istnieje.")
        except json.JSONDecodeError:
            print("Błąd: Plik tłumaczeń jest niepoprawny.")

    @staticmethod
    def get_instance(language='en'):
        """
        Zwraca instancję Singletona dla zadanego języka (jeśli jeszcze nie załadowana).
        """
        with TranslationSingleton._lock:
            if TranslationSingleton._instance is None:
                TranslationSingleton._instance = TranslationSingleton(language)
        return TranslationSingleton._instance

    def get(self, key):
        """
        Zwraca tłumaczenie dla zadanego klucza.
        """
        return self.translations.get(key, key)


# Tworzymy globalną instancję Singletona
config = load_config()
global_translations = TranslationSingleton.get_instance(config["language"])

def language_selection_screen(screen):
    """
    Wyświetla ekran wyboru języka i zapisuje wybór do config.json.
    
    Args:
        screen (pygame.Surface): Powierzchnia ekranu pygame.
    """
    import pygame
    
    # Colors and fonts
    BACKGROUND = (32, 32, 32)
    TEXT_COLOR = (255, 255, 255)
    GOLD = (255, 215, 0)
    BUTTON_COLOR = (60, 60, 60)
    BUTTON_HOVER = (80, 80, 80)
    
    title_font = pygame.font.Font(None, 48)
    button_font = pygame.font.Font(None, 36)
    
    # Language options
    languages = [
        {"code": "pl", "name": "Polski", "flag": "interface/flags/pl.png"},
        {"code": "en", "name": "English", "flag": "interface/flags/en.png"}
    ]
    
    # Load flag images
    for lang in languages:
        try:
            flag = pygame.image.load(lang["flag"])
            lang["flag_surface"] = pygame.transform.scale(flag, (60, 40))
        except:
            lang["flag_surface"] = None
    
    # Create buttons
    button_height = 80
    button_width = 300
    spacing = 40
    start_y = screen.get_height() // 2 - (len(languages) * (button_height + spacing)) // 2
    
    buttons = []
    for i, lang in enumerate(languages):
        rect = pygame.Rect(
            screen.get_width() // 2 - button_width // 2,
            start_y + i * (button_height + spacing),
            button_width,
            button_height
        )
        buttons.append((rect, lang))
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        screen.fill(BACKGROUND)
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw title
        title = title_font.render("Select Language / Wybierz Język", True, GOLD)
        title_rect = title.get_rect(center=(screen.get_width() // 2, start_y - 80))
        screen.blit(title, title_rect)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button, lang in buttons:
                    if button.collidepoint(mouse_pos):
                        # Save to config and reload translations
                        config = load_config()
                        config["language"] = lang["code"]
                        with open("config.json", "w") as f:
                            json.dump(config, f, indent=4)
                        
                        # Update global translations
                        global global_translations
                        global_translations = TranslationSingleton.get_instance(lang["code"])
                        return
        
        # Draw buttons
        for button, lang in buttons:
            # Button background
            color = BUTTON_HOVER if button.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, color, button)
            pygame.draw.rect(screen, GOLD, button, 2)
            
            # Draw flag if available
            if lang["flag_surface"]:
                flag_pos = (button.x + 20, button.centery - 20)
                screen.blit(lang["flag_surface"], flag_pos)
            
            # Draw language name
            text = button_font.render(lang["name"], True, TEXT_COLOR)
            text_rect = text.get_rect(
                midleft=(button.x + 100, button.centery)
            )
            screen.blit(text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
