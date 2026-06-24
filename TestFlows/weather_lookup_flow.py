import time

def execute_weather_flow(mf_engine, row_data, logger):
    login_data = row_data.get("LoginData", {})
    username = login_data.get("Username", "GUEST")
    
    weather_data = row_data.get("WeatherData", {})
    airport_code = weather_data.get("AirportCode", "LAX")
    
    logger.log_step("LOGIN", f"Simulating Authentication for User: {username}")
    
    logger.log_step("NAVIGATE", "Verifying main terminal prompt.")
    screen = mf_engine.read_screen()
    
    if "." not in screen:
        mf_engine.send_command('Enter()')
        time.sleep(1)
        if "." not in mf_engine.read_screen():
            logger.log_step("ERROR", "System stuck. Cannot find main menu.")
            return {"status": "Failed", "forecast": "Not at main menu"}

    logger.log_step("INPUT", f"Entering weather command for: {airport_code}")
    mf_engine.send_command(f'String("weather {airport_code}")')
    mf_engine.send_command('Enter()')
    
    # Wait longer for the external weather API to return data to the mainframe
    time.sleep(3.5) 
    
    logger.log_step("READ", "Capturing updated weather forecast screen.")
    weather_screen = mf_engine.read_screen()
    
    # ---------------------------------------------------------
    # NEW SCRAPING LOGIC: Grab the entire block of text safely
    # ---------------------------------------------------------
    lines = weather_screen.split('\n')
    # Filter out empty lines and the command prompt lines to isolate the clean payload
    clean_lines = [line.strip() for line in lines if line.strip() and not line.startswith(".")]
    
    if clean_lines:
        # Join the first 4 lines of actual data to capture the full location and forecast
        extracted_forecast = "\n".join(clean_lines[:4])
    else:
        extracted_forecast = "Null/Blank Screen Data Captured."
        
    logger.log_step("EXTRACT", "Screen payload captured successfully.")
    
    logger.log_step("NAVIGATE", "Resetting screen back to main menu.")
    mf_engine.send_command('Enter()')
    time.sleep(1)
    
    return {
        "status": "Passed" if "Null" not in extracted_forecast else "Failed", 
        "forecast": extracted_forecast
    }