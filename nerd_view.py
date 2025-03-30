import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from datetime import datetime, timedelta

class NormalStatsWindow:
    def __init__(self, master, data_queue, moves_queue):
        self.master = master
        self.data_queue = data_queue
        self.moves_queue = moves_queue
        self.evaluations = []
        self.move_counts = []
        self.timestamps = []
        self.move_times = []
        self.move_number = 0
        
        # Konfiguracja okna
        self.master.title("Chess Analytics Dashboard")
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Konfiguracja wykresów z użyciem GridSpec
        self.figure = Figure(figsize=(12, 10), dpi=100)
        self.grid = self.figure.add_gridspec(3, 1, height_ratios=[2, 1,1], hspace=0.6)
        
        # Wykres ewaluacji
        self.ax_eval = self.figure.add_subplot(self.grid[0])
        self.ax_eval.tick_params(labelbottom=False)  # Ukryj etykiety osi X na górnym wykresie
        
        # Wykres liczby ruchów
        self.ax_moves = self.figure.add_subplot(self.grid[1], sharex=self.ax_eval)
        self.ax_moves_time = self.figure.add_subplot(self.grid[2])
        self.ax_moves_time.set_title("Czas wykonania ruchów")
        self.ax_moves_time.set_xlabel("Numer ruchu")
        self.ax_moves_time.set_ylabel("Czas (s)")
        self.ax_moves_time.grid(True, alpha=0.3)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.update_data()

    def update_data(self):
        while not self.data_queue.empty():
            # Odbierz dane w formacie (timestamp, evaluation, move_count)
            timestamp, evaluation, move_count = self.data_queue.get()
            dt = datetime.fromtimestamp(timestamp)
            
            self.timestamps.append(dt)
            self.evaluations.append(evaluation)
            self.move_counts.append(move_count)
        while not self.moves_queue.empty():
            move_time = self.moves_queue.get()
            self.move_number += 1
            self.move_times.append((self.move_number, move_time))
        self.update_plots()
        self.master.after(100, self.update_data)


    def update_plots(self):
        # Czyszczenie obu wykresów
        self.ax_eval.clear()
        self.ax_moves.clear()
        
        if self.timestamps:
            # Oblicz czas, który upłynął od pierwszego timestampu
            start_time = self.timestamps[0]
            elapsed_seconds = [(ts - start_time).total_seconds() for ts in self.timestamps]
            
            # Wykres ewaluacji
            self.ax_eval.plot(elapsed_seconds, self.evaluations, 
                            'b-', label="Przewaga białych", linewidth=1.5)
            self.ax_eval.plot(elapsed_seconds, [-x for x in self.evaluations], 
                            'r--', label="Przewaga czarnych", alpha=0.7)
            self.ax_eval.axhline(0, color='gray', linestyle=':', linewidth=1)
            self.ax_eval.set_title("Analiza pozycji w czasie rzeczywistym")
            self.ax_eval.set_ylabel("Przewaga (w pionkach)")
            self.ax_eval.legend(loc='upper left')
            self.ax_eval.grid(True, alpha=0.3)
            
            # Wykres liczby ruchów
            self.ax_moves.plot(elapsed_seconds, self.move_counts, 
                             'g-', label="Dostępne ruchy", linewidth=1.5)
            self.ax_moves.set_title("Liczba możliwych ruchów")
            self.ax_moves.set_xlabel("Czas gry (MM:SS)")
            self.ax_moves.set_ylabel("Liczba ruchów")
            self.ax_moves.legend(loc='upper left')
            self.ax_moves.grid(True, alpha=0.3)
            
            # Formatowanie osi X jako MM:SS
            def format_func(x, pos):
                minutes = int(x // 60)
                seconds = int(x % 60)
                return f"{minutes:02d}:{seconds:02d}"
            
            self.ax_eval.xaxis.set_major_formatter(ticker.FuncFormatter(format_func))
            
            # Automatyczne skalowanie osi X z marginesem
            padding = 10  # sekundy
            if len(elapsed_seconds) > 0:
                min_x = max(0, elapsed_seconds[0] - padding)
                max_x = elapsed_seconds[-1] + padding
                self.ax_eval.set_xlim(min_x, max_x)
            
            self.canvas.draw()
        if self.move_times:
            moves = [x[0] for x in self.move_times]
            times = [x[1] for x in self.move_times]
            
            self.ax_moves_time.clear()
            self.ax_moves_time.bar(moves, times, color='purple', alpha=0.7)
            self.ax_moves_time.set_title("Czas wykonania ruchów")
            self.ax_moves_time.set_xlabel("Numer ruchu")
            self.ax_moves_time.set_ylabel("Czas (s)")
            self.ax_moves_time.grid(True, alpha=0.3)
            
            # Automatyczne skalowanie
            self.ax_moves_time.relim()
            self.ax_moves_time.autoscale_view()
            
            # Etykiety co 5 ruchów
            if len(moves) > 10:
                self.ax_moves_time.xaxis.set_major_locator(ticker.MultipleLocator(5))



class NetworkStatsWindow:
    def __init__(self, master, ping_queue, your_ip_address, other_ip_adress, is_server=False):
        self.master = master
        self.ping_queue = ping_queue
        self.your_ip_address = your_ip_address
        self.other_ip_adress = other_ip_adress
        self.is_server = is_server
        self.start_time = datetime.now()
        
        # Inicjalizacja danych
        self.ping_data = []
        self.timestamps = []
        
        # Konfiguracja GUI
        self._setup_gui()
        self.update_data()

    def _setup_gui(self):
        """Konfiguruje interfejs graficzny"""
        self.master.title("Network Monitor")
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Tworzenie wykresów
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.grid = self.figure.add_gridspec(2, 1, height_ratios=[2, 1])
        
        # Górny wykres - ping
        self.ax_ping = self.figure.add_subplot(self.grid[0])
        self.ax_ping.set_title("Ping History")
        self.ax_ping.grid(True, alpha=0.3)
        
        # Dolny panel informacyjny
        self.ax_info = self.figure.add_subplot(self.grid[1])
        self.ax_info.axis('off')
        
        # Dodaj statyczne informacje
        self._update_info_panel()
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _update_info_panel(self):
        """Aktualizuje panel ze statycznymi informacjami"""
        role = "SERVER" if self.is_server else "CLIENT"
        text = (
            f"IP: {self.your_ip_address}\n"
            f"Host: {self.other_ip_adress}\n"
            f"Role: {role}\n"
            f"Uptime: {datetime.now() - self.start_time}"
        )
        
        self.ax_info.clear()
        self.ax_info.text(
            0.05, 0.7,
            text,
            fontsize=10,
            family='monospace',
            verticalalignment='top'
        )

    def update_data(self):
        """Pobiera nowe dane z kolejki i aktualizuje wykres"""
        while not self.ping_queue.empty():
            ping_time = self.ping_queue.get()
            self.ping_data.append(ping_time)
            self.timestamps.append(datetime.now())
            
            # Ogranicz historię do 60 ostatnich próbek
            if len(self.ping_data) > 60:
                self.ping_data.pop(0)
                self.timestamps.pop(0)
        
        self._redraw_plots()
        self.master.after(1000, self.update_data)

    def _redraw_plots(self):
        """Przerysowuje wszystkie elementy wizualne"""
        # Wykres pingu
        self.ax_ping.clear()
        if self.ping_data and self.timestamps:
            # Oblicz czas, który upłynął od startu
            elapsed_seconds = [(ts - self.start_time).total_seconds() for ts in self.timestamps]
            self.ax_ping.plot(elapsed_seconds, self.ping_data, 'g-', label="Ping (ms)")
            
            # Formatowanie osi X jako MM:SS
            def format_func(x, pos):
                minutes = int(x // 60)
                seconds = int(x % 60)
                return f"{minutes:02d}:{seconds:02d}"
            
            self.ax_ping.xaxis.set_major_formatter(ticker.FuncFormatter(format_func))
            self.ax_ping.set_xlabel("Czas (MM:SS)")
            self.ax_ping.legend()
            self.ax_ping.grid(True, alpha=0.3)
            
            # Automatyczne skalowanie osi X z marginesem
            if len(elapsed_seconds) > 0:
                padding = 10  # sekundy
                min_x = max(0, elapsed_seconds[0] - padding)
                max_x = elapsed_seconds[-1] + padding
                self.ax_ping.set_xlim(min_x, max_x)
        
        # Panel informacyjny
        self._update_info_panel()
        self.canvas.draw()
    def _format_time(self, x, pos):
        """Formatuje znaczniki czasu na osi X"""
        dt = x if isinstance(x, datetime) else datetime.fromtimestamp(x)
        return dt.strftime('%H:%M:%S') if dt else ""
    
class AlgorithmInfoWindow:
    def __init__(self, master, moves_list, algorithm_name, search_depth, additional_info="", best_move=None):
        self.master = master
        self.moves_list = moves_list
        self.algorithm_name = algorithm_name
        self.search_depth = search_depth
        self.additional_info = additional_info
        self.best_move = best_move

        # Konfiguracja okna
        self.master.title("Engine Configuration Info")
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Nagłówki
        self._create_info_section("Dostępne ruchy z bazy:", row=0)
        self._create_info_section("Konfiguracja algorytmu:", row=2)
        self._create_info_section("Dodatkowe informacje:", row=4)
        self._create_info_section("Najlepszy ruch:", row=6)

        # Pole dla ruchów
        self.moves_text = tk.Listbox(self.frame, height=15, width=25)
        self.moves_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        self._update_moves()

        # Pole dla informacji o algorytmie
        algo_frame = tk.Frame(self.frame)
        algo_frame.grid(row=3, column=0, sticky="w", padx=5)
        
        self.algorithm_var = tk.StringVar(value=self.algorithm_name)
        self.depth_var = tk.StringVar(value=f"Głębokość: {self.search_depth}")
        
        tk.Label(algo_frame, textvariable=self.algorithm_var).pack(anchor="w")
        tk.Label(algo_frame, textvariable=self.depth_var).pack(anchor="w")

        # Pole dodatkowych informacji
        self.info_var = tk.StringVar(value=self.additional_info)
        info_label = tk.Label(self.frame, textvariable=self.info_var, 
                            justify="left", wraplength=300)
        info_label.grid(row=5, column=0, sticky="w", padx=5, pady=2)

        # Best move display frame
        self.best_move_frame = tk.Frame(self.frame)
        self.best_move_frame.grid(row=7, column=0, sticky="w", padx=5, pady=2)
        
        self.best_move_var = tk.StringVar(value=self._format_best_move(best_move))
        self.best_move_label = tk.Label(
            self.best_move_frame, 
            textvariable=self.best_move_var,
            font=('Courier', 12),
            fg='green'
        )
        self.best_move_label.pack(anchor="w")

        # Scrollbar dla listy ruchów
        scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.moves_text.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.moves_text.configure(yscrollcommand=scrollbar.set)

        # Konfiguracja grid
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

    def _create_info_section(self, title, row):
        lbl = tk.Label(self.frame, text=title, font=('Arial', 10, 'bold'))
        lbl.grid(row=row, column=0, sticky="w", padx=5, pady=(10,2))

    def _update_moves(self):
        self.moves_text.delete(0, tk.END)
        for move in self.moves_list:
            self.moves_text.insert(tk.END, move)

    def update_moves(self, new_moves):
        self.moves_list = new_moves
        self._update_moves()

    def update_algorithm(self, new_algorithm):
        self.algorithm_name = new_algorithm
        self.algorithm_var.set(new_algorithm)

    def update_additional_info(self, new_info):
        self.additional_info = new_info
        self.info_var.set(new_info)

    def update_depth(self, new_depth):
        self.search_depth = new_depth
        self.depth_var.set(f"Głębokość: {new_depth}")

    def _format_best_move(self, move):
        """Format best move for display"""
        if not move:
            return "Brak ruchu"
        if isinstance(move, (list, tuple)) and len(move) >= 4:
            letters = 'hgfedcba'
            numbers = '12345678'
            from_pos = f"{letters[move[1]]}{numbers[move[0]]}"
            to_pos = f"{letters[move[3]]}{numbers[move[2]]}"
            return f"Z: {from_pos} → Na: {to_pos}"
        return str(move)

    def update_best_move(self, new_move):
        """Update the displayed best move"""
        self.best_move = new_move
        self.best_move_var.set(self._format_best_move(new_move))