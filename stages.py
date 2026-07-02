STAGES = [
    #{"id": "stage1", "name": "Micro Peripherals Testing", "command": " ./BRNKL-Black-Test/invoke stage1"},
    {"id": "1", "name": "Stage 1: Micro Peripherals Testing", "command": "export PATH=$PATH:/home/pi/.local/bin && cd BRNKL-Black-Test && /home/pi/.local/bin/invoke stage1"},
    {"id": "2", "name": "Stage 2: CM4 Testing", "command": "pwd"},
    {"id": "3", "name": "Stage 3: Flash Balena and Lock", "command": "echo './BRNKL-Black-Test/invoke stage3'"},
]