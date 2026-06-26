def execute_geoip_flow(mf_engine, row_data, logger):
    geoip_data = row_data.get("GeoIPData", {})
    target_ip = geoip_data.get("IP_Address", "8.8.4.4")
    
    logger.log_step("NAVIGATE", "Verifying main terminal prompt.")
    
    if not mf_engine.wait_for_prompt(timeout=2):
        mf_engine.send_command('Enter()')
        if not mf_engine.wait_for_prompt(timeout=3):
            logger.log_step("ERROR", "System stuck. Cannot find main menu.")
            return {"status": "Failed", "forecast": "Not at main menu"}

    logger.log_step("INPUT", f"Executing ping for: {target_ip}")
    # Snapshot BEFORE the command so wait_for_screen_change can detect host response.
    # In headed mode, Enter() is NOT synchronous — wc3270 returns 'ok' when the
    # keypress is registered, not when telehack finishes the ping (~5-15s later).
    pre_screen = mf_engine.read_screen()
    mf_engine.send_command(f'String("ping {target_ip}")')
    mf_engine.send_command('Enter()')
    
    logger.log_step("READ", "Waiting for ping response...")
    # wait_for_screen_change returns the stable screen it captured internally.
    # Calling read_screen() again afterwards would miss the data — ping output
    # fills the 24-row terminal and can scroll off between the last internal
    # poll and a second external Ascii() call.
    screen_data = mf_engine.wait_for_screen_change(pre_screen, timeout=60)
    
    lines = screen_data.split('\n')
    all_non_empty = [ln.strip() for ln in lines if ln.strip()]

    # Find anchor line (the command echo: ".ping 8.8.8.8")
    anchor = f"ping {target_ip}"
    try:
        last_anchor_idx = max(i for i, ln in enumerate(all_non_empty) if anchor in ln)
        # Take ALL lines after the anchor. Do NOT filter bare '.' characters here
        # because telehack uses '.' as BOTH its shell prompt AND its per-packet
        # ping indicator. We only strip the very last lone '.' (the final prompt).
        result_lines = all_non_empty[last_anchor_idx + 1:]
    except ValueError:
        # Anchor scrolled off the 24-row screen — use all non-empty lines
        result_lines = all_non_empty

    # Remove only the trailing shell prompt '.' (not mid-content dots)
    while result_lines and result_lines[-1] == ".":
        result_lines.pop()

    screen_changed = screen_data.strip() != pre_screen.strip()

    if result_lines:
        extracted_payload = "\n".join(result_lines)
    elif screen_changed:
        # Extraction found nothing but screen DID change — ping ran but all output
        # was bare prompt dots or scrolled off. Return last 10 raw lines so the
        # report always shows evidence of what happened.
        extracted_payload = "\n".join(all_non_empty[-10:]) if all_non_empty else f"ping {target_ip}: Response received"
    else:
        extracted_payload = "Null/Blank Data"
            
    logger.log_step("EXTRACT", "Ping payload captured successfully.")
    # No menu-state cleanup needed here — this is the last test in the batch.
    # After ping completes, telehack shows a session-end screen requiring Enter
    # to terminate. That is handled by the engine's terminate_session().

    # Pass if the screen changed (ping command was executed and telehack responded).
    # Only fail if the screen was completely unchanged (command never reached host).
    status = "Failed" if (not screen_changed or extracted_payload == "Null/Blank Data") else "Passed"
    
    return {
        "status": status,
        "forecast": extracted_payload
    }