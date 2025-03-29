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
        
        # Formatowanie osi czasu
        self.ax_moves.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
        self.figure.autofmt_xdate()

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
            # Wykres ewaluacji
            self.ax_eval.plot(self.timestamps, self.evaluations, 
                            'b-', label="Przewaga białych", linewidth=1.5)
            self.ax_eval.plot(self.timestamps, [-x for x in self.evaluations], 
                            'r--', label="Przewaga czarnych", alpha=0.7)
            self.ax_eval.axhline(0, color='gray', linestyle=':', linewidth=1)
            self.ax_eval.set_title("Analiza pozycji w czasie rzeczywistym")
            self.ax_eval.set_ylabel("Przewaga (w pionkach)")
            self.ax_eval.legend(loc='upper left')
            self.ax_eval.grid(True, alpha=0.3)
            
            # Wykres liczby ruchów
            self.ax_moves.plot(self.timestamps, self.move_counts, 
                             'g-', label="Dostępne ruchy", linewidth=1.5)
            self.ax_moves.set_title("Liczba możliwych ruchów")
            self.ax_moves.set_xlabel("Czas gry (MM:SS)")
            self.ax_moves.set_ylabel("Liczba ruchów")
            self.ax_moves.legend(loc='upper left')
            self.ax_moves.grid(True, alpha=0.3)
            
            # Automatyczne skalowanie osi X
            self.ax_eval.relim()
            self.ax_eval.autoscale_view(scalex=True)
            self.ax_moves.relim()
            self.ax_moves.autoscale_view(scalex=True)
            
            # Marginesy dla lepszej widoczności
            padding = timedelta(seconds=10)
            if len(self.timestamps) > 1:
                self.ax_eval.set_xlim(
                    self.timestamps[0] - padding, 
                    self.timestamps[-1] + padding
                )
            
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
    def __init__(self, master, ping_queue, ip_address, hostname, is_server=False):
        self.master = master
        self.ping_queue = ping_queue
        self.ip_address = ip_address
        self.hostname = hostname
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
            f"IP: {self.ip_address}\n"
            f"Host: {self.hostname}\n"
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
        if self.ping_data:
            self.ax_ping.plot(self.timestamps, self.ping_data, 'g-', label="Ping (ms)")
            self.ax_ping.xaxis.set_major_formatter(ticker.FuncFormatter(self._format_time))
            self.ax_ping.legend()
            self.ax_ping.grid(True, alpha=0.3)
        
        # Panel informacyjny
        self._update_info_panel()
        self.canvas.draw()

    def _format_time(self, x, pos):
        """Formatuje znaczniki czasu na osi X"""
        dt = x if isinstance(x, datetime) else datetime.fromtimestamp(x)
        return dt.strftime('%H:%M:%S') if dt else ""