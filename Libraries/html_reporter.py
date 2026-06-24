import os
from datetime import datetime

def generate_reports(batch_results, batch_start_time):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # NEW: Strictly Separated Folder Structure
    cons_rep_path = os.path.join(base_dir, "ExecutionEngine", "Reports", "Consolidated")
    ind_rep_path = os.path.join(base_dir, "ExecutionEngine", "Reports", "Individual")
    
    os.makedirs(cons_rep_path, exist_ok=True)
    os.makedirs(ind_rep_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # NEW: Premium Enterprise CSS
    shared_css = """
    <style>
        :root { --primary: #0A2240; --secondary: #1F4E79; --pass: #10B981; --fail: #EF4444; --bg: #F3F4F6; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; background-color: var(--bg); color: #111827; }
        .navbar { background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%); color: white; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .navbar h2 { margin: 0; font-size: 22px; font-weight: 600; letter-spacing: 0.5px; }
        .container { padding: 30px; max-width: 1400px; margin: auto; }
        .card { background: white; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); padding: 25px; margin-bottom: 25px; border: 1px solid #E5E7EB; }
        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .info-item { padding: 15px; background: #F9FAFB; border-left: 4px solid var(--secondary); border-radius: 6px; }
        .info-item strong { display: block; font-size: 12px; color: #6B7280; text-transform: uppercase; margin-bottom: 4px; }
        .info-item span { font-size: 16px; font-weight: 500; color: #111827; }
        table { width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 15px; border-radius: 8px; overflow: hidden; border: 1px solid #E5E7EB; }
        th, td { border-bottom: 1px solid #E5E7EB; padding: 14px 16px; text-align: left; }
        th { background-color: #F9FAFB; color: #374151; font-weight: 600; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }
        td { font-size: 14px; }
        .badge { padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; color: white; display: inline-block; }
        .pass { background-color: var(--pass); }
        .fail { background-color: var(--fail); }
        .accordion { background-color: white; color: #111827; cursor: pointer; padding: 20px; width: 100%; border: 1px solid #E5E7EB; border-radius: 8px; text-align: left; outline: none; font-size: 15px; transition: 0.2s; display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .accordion:hover { background-color: #F9FAFB; border-color: #D1D5DB; }
        .panel { padding: 0 20px; background-color: white; display: none; border: 1px solid #E5E7EB; border-top: none; margin-bottom: 20px; border-radius: 0 0 8px 8px; }
        .summary-card { display: flex; gap: 24px; margin-bottom: 30px; }
        .stat-box { flex: 1; padding: 24px; text-align: center; border-radius: 10px; color: white; font-weight: 600; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .stat-total { background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%); }
        .stat-pass { background: linear-gradient(135deg, #059669 0%, #10B981 100%); }
        .stat-fail { background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%); }
        .payload-box { background: #1E293B; color: #10B981; padding: 20px; border-radius: 8px; font-family: 'Consolas', monospace; font-size: 14px; white-space: pre-wrap; line-height: 1.5; overflow-x: auto; border: 1px solid #0F172A; }
        a.view-link { color: var(--secondary); text-decoration: none; font-size: 13px; font-weight: 600; padding: 6px 12px; border: 1px solid var(--secondary); border-radius: 4px; transition: 0.2s; }
        a.view-link:hover { background-color: var(--secondary); color: white; }
    </style>
    <script>
        function togglePanel(id) {
            var panel = document.getElementById('panel-' + id);
            if (panel.style.display === "block") { panel.style.display = "none"; } 
            else { panel.style.display = "block"; }
        }
    </script>
    """

    html_execution_body = ""
    total = len(batch_results)
    passed = sum(1 for r in batch_results if r['status'].upper() == "PASSED")
    failed = total - passed

    for res in batch_results:
        test_id = res['tc_id']
        status_class = "pass" if res['status'].upper() == "PASSED" else "fail"
        ind_file_name = f"{test_id}_{timestamp}.html"
        ind_report_file = os.path.join(ind_rep_path, ind_file_name)
        
        # --- Individual HTML ---
        i_rep = f"<!DOCTYPE html><html><head><title>{test_id} - Report</title>{shared_css}</head><body>"
        i_rep += f"<div class='navbar'><h2>Jarvis Execution Detail</h2><span>{batch_start_time.strftime('%Y-%m-%d %H:%M:%S')}</span></div>"
        i_rep += "<div class='container'><div class='card'><h3>Execution Summary</h3><div class='info-grid'>"
        i_rep += f"<div class='info-item'><strong>Test ID</strong><span>{test_id}</span></div>"
        i_rep += f"<div class='info-item'><strong>Description</strong><span>{res['description']}</span></div>"
        i_rep += f"<div class='info-item'><strong>Target System</strong><span>{res['airport']}</span></div>"
        i_rep += f"<div class='info-item'><strong>Duration</strong><span>{res['duration']}s</span></div>"
        i_rep += f"<div class='info-item'><strong>Environment</strong><span>Mainframe SIT</span></div>"
        i_rep += f"<div class='info-item'><strong>Status</strong><span class='badge {status_class}'>{res['status']}</span></div>"
        i_rep += "</div></div>"
        
        i_rep += "<div class='card'><h3>Extracted Screen Payload</h3>"
        i_rep += f"<div class='payload-box'>{res['forecast']}</div>"
        i_rep += "</div></div></body></html>"
        
        with open(ind_report_file, "w") as f:
            f.write(i_rep)

        # --- Consolidated HTML Body ---
        # Note the relative path pointing UP one directory to get from Consolidated -> Individual
        rel_path = f"../Individual/{ind_file_name}"
        html_execution_body += f"<button class='accordion' onclick=\"togglePanel('{test_id}')\">"
        html_execution_body += f"<div style='display:flex; align-items:center; gap:20px;'>"
        html_execution_body += f"<span style='width: 80px;'><strong>{test_id}</strong></span>"
        html_execution_body += f"<span style='width: 250px; color: #4B5563;'>{res['description']}</span>"
        html_execution_body += f"<span style='width: 100px;'>Target: {res['airport']}</span>"
        html_execution_body += f"<span style='width: 80px;'>{res['duration']}s</span>"
        html_execution_body += f"<a href='{rel_path}' target='_blank' class='view-link'>View Detail Report</a></div>"
        html_execution_body += f"<div><span class='badge {status_class}'>{res['status']}</span></div></button>"
        
        html_execution_body += f"<div id='panel-{test_id}' class='panel'><table>"
        html_execution_body += "<tr><th style='width:20%;'>Data Field</th><th>Captured Value</th></tr>"
        html_execution_body += f"<tr><td>Raw Mainframe Output</td><td><div class='payload-box' style='padding:10px;'>{res['forecast']}</div></td></tr>"
        html_execution_body += "</table><br></div>"

    # --- Finalize Dashboard ---
    cons_report_file = os.path.join(cons_rep_path, f"Execution_Dashboard_{timestamp}.html")
    c_rep = f"<!DOCTYPE html><html><head><title>Jarvis Automation Dashboard</title>{shared_css}</head><body>"
    c_rep += f"<div class='navbar'><h2>Jarvis Consolidated Dashboard</h2><span>Batch Run: {batch_start_time.strftime('%Y-%m-%d %H:%M:%S')}</span></div>"
    c_rep += "<div class='container'><div class='summary-card'>"
    c_rep += f"<div class='stat-box stat-total'><span style='font-size: 14px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;'>Total Scripts</span><br><span style='font-size: 36px; line-height: 1.2;'>{total}</span></div>"
    c_rep += f"<div class='stat-box stat-pass'><span style='font-size: 14px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;'>Total Passed</span><br><span style='font-size: 36px; line-height: 1.2;'>{passed}</span></div>"
    c_rep += f"<div class='stat-box stat-fail'><span style='font-size: 14px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;'>Total Failed</span><br><span style='font-size: 36px; line-height: 1.2;'>{failed}</span></div>"
    c_rep += "</div><h3 style='color: #111827; margin-bottom: 15px;'>Execution Details</h3>"
    c_rep += html_execution_body
    c_rep += "</div></body></html>"

    with open(cons_report_file, "w") as f:
        f.write(c_rep)
        
    print(f"\n[SYSTEM] Reports Generated!")
    print(f" Dashboard: {cons_report_file}")