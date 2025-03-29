import tkinter as tk
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import threading

class StatsWindow:
    def __init__(self, master, data_queue):
        self.master = master
        self.data_queue = data_queue
        self.timestamps = []
        self.evaluations = []
        self.start_time = time.time()

        # Konfiguracja okna
        self.master.title("Real-Time Evaluation")
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Konfiguracja wykresu
        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        # Formatowanie osi czasu
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
        self.figure.autofmt_xdate()

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.update_data()

    def update_data(self):
        while not self.data_queue.empty():
            # Odbierz krotkę (timestamp, evaluation)
            timestamp, evaluation = self.data_queue.get()
            self.timestamps.append(datetime.fromtimestamp(timestamp))
            self.evaluations.append(evaluation)

        self.update_plot()
        self.master.after(100, self.update_data)  # Szybsze aktualizacje

    def update_plot(self):
        self.ax.clear()
        if self.evaluations:
            # Główne linie wykresu
            self.ax.plot(self.timestamps, self.evaluations, 'b-', label="White Evaluation", linewidth=1.5)
            self.ax.plot(self.timestamps, [-x for x in self.evaluations], 'r--', label="Black Evaluation", alpha=0.7)
            
            # Linia zerowa
            self.ax.axhline(0, color='gray', linestyle=':')
            
            # Automatyczne skalowanie osi
            self.ax.relim()
            self.ax.autoscale_view(scalex=True, scaley=True)
            
            # Dynamiczne dostosowanie osi X
            if len(self.timestamps) > 1:
                # Oblicz 5% marginesu po prawej stronie
                total_span = (self.timestamps[-1] - self.timestamps[0]).total_seconds()
                right_margin = timedelta(seconds=total_span * 0.05)
                
                self.ax.set_xlim(
                    left=self.timestamps[0],
                    right=self.timestamps[-1] + right_margin
                )
            elif len(self.timestamps) == 1:
                # Dla jednego punktu ustaw 10-sekundowe okno
                self.ax.set_xlim(
                    left=self.timestamps[0] - timedelta(seconds=5),
                    right=self.timestamps[0] + timedelta(seconds=5)
                )

            # Pozostałe ustawienia
            self.ax.set_title("Real-Time Evaluation")
            self.ax.set_xlabel("Game Time (MM:SS)")
            self.ax.set_ylabel("Advantage (pawn units)")
            self.ax.legend(loc='upper left')
            self.ax.grid(True, alpha=0.3)
            
            self.canvas.draw()