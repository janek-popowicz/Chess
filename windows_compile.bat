del /S /Q build launcher.spec

pyinstaller -F ^
  --add-data "normal_games;normal_games" ^
  --add-data "algorithms;algorithms" ^
  --add-data "custom_board_game;custom_board_game" ^
  --add-data "engine;engine" ^
  --add-data "grandmaster;grandmaster" ^
  --add-data "multiplayer;multiplayer" ^
  --add-data "interface;interface" ^
  --hidden-import=tkinter ^
  --hidden-import=tkinter.filedialog ^
  --hidden-import=numpy ^
  --hidden-import=matplotlib ^
  --hidden-import=time ^
  --hidden-import=random ^
  --hidden-import=pygame ^
  --hidden-import=tkinter.ttk ^
  --hidden-import=matplotlib.figure.Figure ^
  --hidden-import=matplotlib.backends.backend_tkagg.FigureCanvasTkAgg ^
  --hidden-import=matplotlib.backends.backend_tkagg ^
  --hidden-import=matplotlib.dates ^
  --hidden-import=matplotlib.ticker ^
  --hidden-import=datetime.datetime ^
  --hidden-import=datetime.timedelta ^
  launcher.py
