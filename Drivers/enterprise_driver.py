import sys
import os
import time
from datetime import datetime

# Ensure the root framework directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Libraries.mainframe_core import MainframeCore
from Libraries.audit_logger import XMLAuditLogger
from Libraries.html_reporter import generate_reports
from Libraries.excel_utils import get_test_data
from TestFlows.weather_lookup_flow import execute_weather_flow

class EnterpriseDriver:
    def __init__(self, mode="headless", start_time=None):
        self.execution_mode = mode
        self.start_time = start_time
        self.engine = MainframeCore(mode=self.execution_mode, host="telehack.com")
        self.batch_results = []

    def run_pipeline(self):
        try:
            print("[SYSTEM] Loading relational Test Data from Excel...")
            test_cases = get_test_data()
            
            self.engine.start_session()
            
            for index, row_data in enumerate(test_cases):
                # Start individual test timer
                tc_start = time.time()
                
                # Extract relational data correctly
                tc_id = row_data.get("TC_ID", f"TC_UNKNOWN_{index}")
                description = row_data.get("Description", "No Description")
                target_airport = row_data.get("WeatherData", {}).get("AirportCode", "N/A")
                
                logger = XMLAuditLogger(tc_id)
                logger.log_step("SYSTEM", f"Executing: {description}")
                logger.update_status("executing")
                
                result = execute_weather_flow(self.engine, row_data, logger)
                
                # Calculate Duration
                tc_duration = round(time.time() - tc_start, 2)
                
                # Pass clean, extracted data to the HTML reporter
                self.batch_results.append({
                    "tc_id": tc_id,
                    "description": description,
                    "airport": target_airport,
                    "duration": tc_duration,
                    "status": result.get("status", "Failed"),
                    "forecast": result.get("forecast", "No data captured")
                })
                
                logger.log_step("FLOW_END", f"Status: {result.get('status')} | Duration: {tc_duration}s")
                logger.update_status("completed")
                print("-" * 50)
                
            if self.batch_results:
                generate_reports(self.batch_results, self.start_time)
                
        except Exception as e:
            print(f"\n[FATAL ERROR] {e}")
        finally:
            self.engine.terminate_session()