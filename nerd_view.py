import tkinter as tk
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import matplotlib.ticker as ticker  # NEW
from datetime import datetime, timedelta
import threading

class StatsWindow:
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