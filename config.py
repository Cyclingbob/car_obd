import os
dir_path = os.path.dirname(os.path.realpath(__file__))

program_file = os.path.join(dir_path, "program.py")
debug_mode = False
online_version = "https://raw.githubusercontent.com/Cyclingbob/car_obd/main/version.txt"
online_file = "https://raw.githubusercontent.com/Cyclingbob/car_obd/main/program.py"
metrics_file = os.path.join(dir_path, "metrics.txt")
version_file = os.path.join(dir_path, "version.txt")

button1 = 17
button2 = 27

night_mode = (128, 128, 128)
day_mode = (255, 255, 255)