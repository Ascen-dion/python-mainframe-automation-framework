import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
import shutil

class XMLAuditLogger:
    def __init__(self, tc_id):
        self.tc_id = tc_id
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.log_dirs = {
            "new": os.path.join(self.base_dir, "ExecutionEngine", "AuditLogs", "01_New_Request"),
            "exec": os.path.join(self.base_dir, "ExecutionEngine", "AuditLogs", "02_Executing"),
            "comp": os.path.join(self.base_dir, "ExecutionEngine", "AuditLogs", "03_Completed")
        }
        
        # Ensure folders exist
        for path in self.log_dirs.values():
            os.makedirs(path, exist_ok=True)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"{tc_id}_Audit_{timestamp}.xml"
        self.current_path = os.path.join(self.log_dirs["new"], self.filename)
        
        # Initialize XML structure
        self.root = ET.Element("AuditLog")
        ET.SubElement(self.root, "TestCaseID").text = self.tc_id
        ET.SubElement(self.root, "StartTime").text = str(datetime.now())
        self.steps_node = ET.SubElement(self.root, "ExecutionSteps")
        
        self._save_xml()

    def update_status(self, new_status):
        """Moves the XML file to the corresponding lifecycle folder."""
        if new_status == "executing":
            new_path = os.path.join(self.log_dirs["exec"], self.filename)
        elif new_status == "completed":
            new_path = os.path.join(self.log_dirs["comp"], self.filename)
        else:
            return

        if os.path.exists(self.current_path):
            shutil.move(self.current_path, new_path)
            self.current_path = new_path

    def log_step(self, action, details, status="INFO"):
        """Appends a new XML node for the execution step."""
        step = ET.SubElement(self.steps_node, "Step")
        ET.SubElement(step, "Timestamp").text = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        ET.SubElement(step, "Action").text = action
        ET.SubElement(step, "Status").text = status
        ET.SubElement(step, "Details").text = str(details)
        self._save_xml()
        print(f"[{self.tc_id}] [{action}] {details}")

    def _save_xml(self):
        """Writes beautifully formatted XML to the active file."""
        xml_str = ET.tostring(self.root, 'utf-8')
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="    ")
        # minidom adds extra blank lines, we filter them out
        clean_xml = os.linesep.join([s for s in pretty_xml.splitlines() if s.strip()])
        with open(self.current_path, "w") as f:
            f.write(clean_xml)