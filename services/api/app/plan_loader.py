import os
from .config import DATA_DIR, ALLOWED_PROGRAMM

def load_plan(programm):
    if programm not in ALLOWED_PROGRAMM:
        raise ValueError(f"Invalid programm {programm}")
    
    programm_md_path = os.path.join(DATA_DIR, "md", programm + ".md")
    print(f"Ищем план {programm_md_path}")
    if os.path.exists(programm_md_path):
        with open(programm_md_path, 'r', encoding='utf-8') as f:
            plan = f.read()
    else:
        plan = None

    return plan