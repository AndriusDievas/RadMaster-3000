from pathlib import Path
start = 0
stop = 1
startProgressBar = 0
portsReady = 0                                                                 # Port set function has finished writing to ports.txt
LEDstart = 1                                                                     # Status indicator variable. If GM stopped - set to 1 and reset indicators
CPSout = 0
value = 0
exit = 0
CPSthreshold = 8
extsTART = 0

T = 5
CF = 0.1041


elapsedTime = 0

data_folder = Path("data/")                                                    # path to main data storage
config_folder = Path("config/")
report_path = "data/GM-report.txt"                                             # path to report data storage
data_path = "data/GM-data.txt"                                                 # path to counts data storage

CPSthreadStart = 0

module_list = []

connections = {}

det1 = {}
det2 = {}
counts = {}
CPS1 = {}
CPS2 = {}
uSv1 = {}
uSv2 = {}
aCPS = {}
auSv = {}

det1_CPSlist = [] 
det2_CPSlist = [] 
det1_uSvlist = []
det2_uSvlist = []

# coef = {}

# def coef_read():
#     # Read the coefficients from the file
#     with open(config_folder/'coef.txt', 'r') as f:
#         lines = f.readlines()
        
        
#         for i in range(1, len(lines), 3):
#             module = f"module-{i//3+1}"
#             if lines[i].startswith('Detector'):
#                 coef1 = float(lines[i].split('=')[1].strip())
#             else:
#                 coef1 = 1.0
#             if lines[i+1].startswith('Detector'):
#                 coef2 = float(lines[i+1].split('=')[1].strip())
#             else:
#                 coef2 = 1.0
#             coef[module] = (coef1, coef2)
#             print(f"{module} Coefficients: {coef1}, {coef2}")
            
# coef_read()

# print(coef)
