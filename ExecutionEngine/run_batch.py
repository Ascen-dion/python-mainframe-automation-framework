import sys
import os
from datetime import datetime

# Ensure the root framework directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Drivers.enterprise_driver import EnterpriseDriver

if __name__ == "__main__":
    print("=========================================")
    print(" JARVIS-REPLICA MAINFRAME PIPELINE       ")
    print("=========================================\n")
    
    # ---------------------------------------------------------
    # TOGGLE EXECUTION MODE HERE
    # "headless" = Silent CI/CD mode (ws3270)
    # "headed"   = Visual Debugging mode (wc3270 UI)
    # ---------------------------------------------------------
    EXECUTION_MODE = "headed" 
    
    batch_start_time = datetime.now()
    
    # Initialize and run the pipeline
    pipeline = EnterpriseDriver(mode=EXECUTION_MODE, start_time=batch_start_time)
    pipeline.run_pipeline()