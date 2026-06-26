def execute_weather_flow(mf_engine, row_data, logger):
    login_data = row_data.get("LoginData", {})
    username = login_data.get("Username", "GUEST")
    weather_data = row_data.get("WeatherData", {})
    airport_code = weather_data.get("AirportCode", "LAX")
    
    logger.log_step("LOGIN", f"Simulating Authentication for User: {username}")
    logger.log_step("NAVIGATE", "Verifying main terminal prompt.")
    
    if not mf_engine.wait_for_prompt(timeout=2):
        mf_engine.send_command('Enter()')
        if not mf_engine.wait_for_prompt(timeout=3):
            logger.log_step("ERROR", "System stuck. Cannot find main menu.")
            return {"status": "Failed", "forecast": "Not at main menu"}

    logger.log_step("INPUT", f"Entering weather command for: {airport_code}")
    # Snapshot BEFORE the command so wait_for_screen_change can detect host response.
    # In headed mode, Enter() is NOT synchronous — it returns immediately when the
    # keypress is registered, not when telehack responds. Without the snapshot,
    # read_screen() captures the previous test's content every time.
    pre_screen = mf_engine.read_screen()
    mf_engine.send_command(f'String("weather {airport_code}")')
    mf_engine.send_command('Enter()')
    
    logger.log_step("READ", "Waiting for server to process...")
    # wait_for_screen_change returns the stable screen it captured internally.
    # We use it directly — calling read_screen() again afterwards risks reading
    # a different state because the 24-row terminal may have scrolled by then.
    weather_screen = mf_engine.wait_for_screen_change(pre_screen, timeout=15)
    
    lines = weather_screen.split('\n')

    # Extract only lines AFTER the last occurrence of this command's echo.
    # The 24-row wc3270 buffer accumulates history from all previous tests;
    # anchoring on the echo ensures we capture only this test's response.
    anchor = f"weather {airport_code}"
    last_anchor_idx = max(
        (i for i, ln in enumerate(lines) if anchor in ln),
        default=-1
    )
    if last_anchor_idx >= 0:
        result_lines = [ln.strip() for ln in lines[last_anchor_idx + 1:]
                        if ln.strip() and ln.strip() != "."]
        extracted_forecast = "\n".join(result_lines) if result_lines else "Null/Blank Screen Data Captured."
    else:
        # Fallback: no echo found — take last 6 non-empty lines
        clean_lines = [ln.strip() for ln in lines if ln.strip() and ln.strip() != "."]
        extracted_forecast = "\n".join(clean_lines[-6:]) if clean_lines else "Null/Blank Screen Data Captured."
        
    logger.log_step("EXTRACT", "Screen payload captured successfully.")
    
    logger.log_step("NAVIGATE", "Ensuring clean menu state...")
    if not mf_engine.wait_for_prompt(timeout=1):
        mf_engine.send_command('String("q")')
        mf_engine.send_command('Enter()')
        mf_engine.wait_for_prompt(timeout=3)
    
    return {
        "status": "Passed" if "Null" not in extracted_forecast else "Failed",
        "forecast": extracted_forecast
    }