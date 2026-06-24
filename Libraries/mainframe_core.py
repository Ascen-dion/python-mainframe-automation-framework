import subprocess
import time
import socket

class MainframeCore:
    def __init__(self, mode="headless", host="telehack.com"):
        self.mode = mode.lower()
        self.host = host
        self.process = None
        self.sock = None
        self.port = 4000
        
        # Determine the correct execution engine based on mode
        if self.mode == "headless":
            self.exe_path = r"C:\Program Files\wc3270\ws3270.exe"
        else:
            self.exe_path = r"C:\Program Files\wc3270\wc3270.exe"

    def start_session(self):
        """Launches the emulator and connects to the host."""
        print(f"[ENGINE] Starting {self.mode.upper()} session for {self.host}...")
        
        if self.mode == "headless":
            # Native subprocess piping for silent CI/CD runs
            self.process = subprocess.Popen(
                [self.exe_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            time.sleep(1)
        else:
            # Launch the visual UI with the automation port open (NO internal pipes!)
            cmd = [self.exe_path, "-scriptport", str(self.port)]
            self.process = subprocess.Popen(cmd)
            time.sleep(2) # Give the GUI time to render
            
            # Connect Python to the GUI via our proven socket method
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(2.0)
            self.sock.connect(("127.0.0.1", self.port))
            
            # Clear any initial background connection noise
            try:
                self.sock.recv(1024)
            except socket.timeout:
                pass

        # Send the initial connection command to the mainframe server
        self.send_command(f"Connect({self.host})")
        time.sleep(2)

    def send_command(self, cmd: str) -> str:
        """Injects commands via Pipes (Headless) or Sockets (Headed)."""
        output_lines = []
        
        if self.mode == "headless":
            if not self.process:
                raise Exception("Headless process not running.")
                
            self.process.stdin.write(cmd + "\n")
            self.process.stdin.flush()
            
            while True:
                line = self.process.stdout.readline().strip()
                if not line or line == "ok" or line.startswith("error"):
                    break
                if line.startswith("data:"):
                    output_lines.append(line[6:]) # Strip the "data: " prefix
                    
        else:
            if not self.sock:
                raise Exception("Socket not connected for headed mode.")
                
            self.sock.sendall(f"{cmd}\n".encode('ascii'))
            time.sleep(0.2)
            
            response = ""
            response = ""
            while True:
                try:
                    chunk = self.sock.recv(4096).decode('ascii', errors='ignore')
                    response += chunk
                    if "ok\n" in response or "error\n" in response or not chunk:
                        break
                except socket.timeout:
                    break
                except ConnectionError:
                    # The emulator closed the port instantly (Expected behavior when sending 'Quit()')
                    break
                    
            # Parse the socket response to perfectly match the headless formatting
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith("data:"):
                    output_lines.append(line[6:])

        return "\n".join(output_lines)

    def read_screen(self) -> str:
        """Captures the current 24x80 text buffer."""
        return self.send_command("Ascii()")

    def terminate_session(self):
        """Safely shuts down the emulator process and network ports."""
        self.send_command("Quit()")
        if self.sock:
            self.sock.close()
        print("[ENGINE] Session terminated.")