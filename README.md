# 🚀 Jarvis-Replica: Python Mainframe Automation Framework

**Enterprise Mainframe Automation | Zero-Dependency | Native Memory-Scraping**

A proof-of-concept workspace demonstrating the modernization of legacy mainframe test automation (formerly OpenText UFT/Jarvis). This framework completely bypasses the need for Playwright, UFT licenses, or brittle OCR by directly interacting with the terminal's memory buffer via native OS subprocess pipes and `ws3270`.

---

## 🏗️ Framework Capabilities

| Feature | Description |
|---|---|
| **Hybrid Execution Engine** | Seamlessly toggle between silent `subprocess` CI/CD runs (Headless) and visual TCP socket-driven debugging (Headed). |
| **Relational Test Data** | Ingests complex, multi-sheet Excel data driven by a Master RunManager, mirroring UFT's object-linking logic. |
| **XML Lifecycle Auditing** | State-machine file logging that tracks execution traces through `New_Request`, `Executing`, and `Completed` directories. |
| **Enterprise HTML Dashboards** | Auto-generated, dual-layer Extent-style reports with CSS badging, accordion payload visibility, and individual deep-linking. |
| **JSON Object Repository** | Total separation of UI coordinates from business logic. Update a 24x80 coordinate in the JSON without touching Python code. |

---

## 📁 Architecture Overview

```text
BOA_Python_Mainframe_Framework/
│
├── docs/                        ← Architecture DDR & flow diagrams
│   └── Mainframe_Architecture_Guide.md
│
├── Drivers/
│   └── enterprise_driver.py     ← Master pipeline orchestrator class
│
├── ExecutionEngine/
│   ├── AuditLogs/               ← XML State-Machine Logs
│   │   ├── 01_New_Request/
│   │   ├── 02_Executing/
│   │   └── 03_Completed/
│   ├── Reports/
│   │   ├── Consolidated/        ← Macro Batch Dashboards
│   │   └── Individual/          ← Micro Test Case Reports
│   └── run_batch.py             ← 🎯 MAIN ENTRY POINT (Toggle modes here)
│
├── Libraries/
│   ├── audit_logger.py          ← XML Trace generation & File movement
│   ├── excel_utils.py           ← Relational cross-sheet Data Parser
│   ├── html_reporter.py         ← Extent-style UI generation
│   ├── mainframe_core.py        ← The Hybrid Subprocess/Socket Engine
│   └── mainframe_utils.py       ← Screen text coordinate extractor
│
├── ObjectRepository/
│   └── mainframe_or.json        ← 24x80 Grid mapping definitions
│
├── TestData/
│   └── batch_input.xlsx         ← Master (RunManager) & Component Data Sheets
│
└── TestFlows/
    └── weather_lookup_flow.py   ← Sample multi-screen business logic
```

---

## ⚙️ Environment Setup & Prerequisites

### Python Requirements

- Python 3.8+ (64-bit recommended)

### Mainframe Emulator

You must have the open-source wc3270 suite installed at the default Windows directory:

- `C:\Program Files\wc3270\wc3270.exe` (For Headed mode)
- `C:\Program Files\wc3270\ws3270.exe` (For Headless mode)

### Python Dependencies

```powershell
python -m pip install openpyxl
```

---

## 🚀 Execution Guide

### 1. Configure Test Data

Ensure `TestData/batch_input.xlsx` is configured correctly:

- Must contain a `RunManager` sheet with `TC_ID` and `RunFlag (Y/N)`.
- Component sheets (e.g., `LoginData`, `WeatherData`) must link their rows to the Master sheet via the exact `TC_ID` string.

### 2. Set Execution Mode

Open `ExecutionEngine/run_batch.py` and set your desired mode in the constants block:

```python
# "headless" = Silent CI/CD runs (Bypasses Firewalls via OS Pipes)
# "headed"   = Visual Debugging (Pops GUI via self-healing Sockets)
EXECUTION_MODE = "headed"
```

### 3. Run the Pipeline

Ensure your Excel file is closed (to prevent COM locks), open your terminal, navigate to the framework root, and run:

```bash
python ExecutionEngine/run_batch.py
```

### 4. Review Artifacts

#### Audit Trail

Check:

```text
ExecutionEngine/AuditLogs/03_Completed/
```

for the XML trace files detailing the exact state transitions.

#### Execution UI

Navigate to:

```text
ExecutionEngine/Reports/Consolidated/
```

and open the latest:

```text
Execution_Dashboard_*.html
```

in your browser to view interactive run metrics and extracted screen payloads.

---

## 📌 Notes

- Headless mode is recommended for CI/CD pipelines.
- Headed mode is recommended for debugging and local development.
- Keep the Object Repository (`mainframe_or.json`) updated when screen coordinates change.
- The framework maintains full separation between business logic, test data, and UI coordinate mapping.

---

**Engineered for Bank of America QE Modernization Initiatives**
