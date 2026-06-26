import subprocess
import time
import socket
import os

class MainframeCore:
    def __init__(self, mode="headless", host="telehack.com"):
        self.mode = mode.lower()
        self.host = host
        self.process = None       # headless ws3270 subprocess
        self.headed_proc = None   # headed wc3270 subprocess
        self.sock = None
        self.port = 4000
        self.demo_mode = False  # Live session — not a mock/demo run
        
        if self.mode == "headless":
            self.exe_path = r"C:\Program Files\wc3270\ws3270.exe"
        else:
            self.exe_path = r"C:\Program Files\wc3270\wc3270.exe"

    def start_session(self):
        print(f"[ENGINE] Starting {self.mode.upper()} session for {self.host}...")
        os.system("taskkill /F /IM wc3270.exe /T >nul 2>&1")
        os.system("taskkill /F /IM ws3270.exe /T >nul 2>&1")
        time.sleep(1)

        if self.mode == "headless":
            self.process = subprocess.Popen(
                [self.exe_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, bufsize=1
            )
            time.sleep(1)
            self.send_command(f"Connect({self.host})")
            time.sleep(2)
        else:
            # Launch wc3270 in a new CMD window via "start".
            # We apply STARTF_USESHOWWINDOW to the cmd.exe call so that it
            # receives a proper foreground activation context, which it then
            # passes through to wc3270 via "start" — bringing the window to
            # the front automatically without requiring a manual click.
            si = subprocess.STARTUPINFO()
            si.dwFlags = subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 1  # SW_SHOWNORMAL: activate and show in foreground
            self.headed_proc = subprocess.Popen(
                ["cmd.exe", "/c", "start", "Mainframe Session", self.exe_path, "-scriptport", str(self.port), self.host],
                startupinfo=si
            )
            time.sleep(2)

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(2.0)

            for _ in range(5):
                try:
                    self.sock.connect(("127.0.0.1", self.port))
                    break
                except Exception:
                    time.sleep(1)

            try:
                self.sock.recv(1024)
            except socket.timeout:
                pass

        print("[ENGINE] Waiting for remote server to boot (up to 15 seconds)...")
        # Actively poll for the [Press <Enter>] activation screen and dismiss it.
        # A single Enter() sent once after connect is unreliable — the scriptport
        # may not be ready to process it yet. This loop retries every second until
        # wc3270's startup screen is dismissed and the telehack prompt appears.
        for _ in range(20):
            time.sleep(1)
            screen = self.read_screen()
            lines = [ln.strip() for ln in screen.split('\n') if ln.strip()]
            if "." in lines:
                print("[ENGINE] Telehack prompt detected. Session active.")
                return  # prompt visible — no need for wait_for_prompt below
            if any("Press <Enter>" in ln or "[wc3270]" in ln for ln in lines) or not lines:
                # wc3270 activation screen still showing — send Enter to dismiss it
                self.send_command('Enter()')
        self.wait_for_prompt(timeout=5)  # final safety net

    def wait_for_prompt(self, timeout=15, stop_on_pagination=False) -> bool:
        """
        Robust prompt detection. If the screen is too long, it can either stop 
        to let the script extract Page 1, or type 'q' to abort the pagination entirely.
        """
        for _ in range(timeout):
            screen = self.read_screen()
            lines = [line.strip() for line in screen.split('\n') if line.strip()]
            
            if "." in lines:
                return True
                
            # THE FIX: Smart Pagination Handling
            # Distinguish between wc3270's own [Press <Enter>] startup activation
            # screen (send just Enter) vs telehack's pager (send q to quit pager).
            if any("Press <Enter>" in line for line in lines):
                if stop_on_pagination:
                    return True  # Stop so caller can scrape Page 1
                # Check if this is a pager (telehack content visible) or bare activation
                has_content = any(
                    line not in (".", "[wc3270]") and "Press <Enter>" not in line
                    for line in lines
                )
                if has_content:
                    print("[ENGINE] Pager detected. Sending q to escape...")
                    self.send_command('String("q")')
                self.send_command('Enter()')
                time.sleep(1.5)
                continue

            time.sleep(1)
            
        return False

    def send_command(self, cmd: str) -> str:
        output_lines = []
        if self.mode == "headless":
            if not self.process: raise Exception("Headless process not running.")
            self.process.stdin.write(cmd + "\n")
            self.process.stdin.flush()
            while True:
                line = self.process.stdout.readline().strip()
                if not line or line == "ok" or line.startswith("error"): break
                if line.startswith("data:"): output_lines.append(line[6:]) 
        else:
            if not self.sock: raise Exception("Socket not connected.")
            self.sock.sendall(f"{cmd}\n".encode('ascii'))
            time.sleep(0.2)
            response = ""
            while True:
                try:
                    chunk = self.sock.recv(4096).decode('ascii', errors='ignore')
                    response += chunk
                    if "ok\n" in response or "error\n" in response or not chunk: break
                except socket.timeout: break
                except ConnectionError: break
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith("data:"): output_lines.append(line[6:])

        return "\n".join(output_lines)

    def read_screen(self) -> str:
        return self.send_command("Ascii()")

    def wait_for_screen_change(self, previous_screen: str, timeout: int = 30) -> str:
        """
        Polls until the screen buffer changes from `previous_screen` AND then
        stabilizes (no further changes for 2 consecutive reads ~1 second apart),
        which means the host has finished sending its full response.

        Returns the final stable screen content directly — callers must NOT call
        read_screen() again afterwards, because the wc3270 24-row terminal may
        have already scrolled by the time a second Ascii() call arrives.

        Why this is needed in headed mode (wc3270 scriptport):
          send_command('Enter()') returns 'ok' the instant wc3270 registers the
          keypress — it does NOT block until telehack responds. So calling
          read_screen() immediately after Enter() always captures the old buffer.
          This method correctly waits for the remote host to finish responding.
        """
        changed = False
        last_screen = previous_screen
        stable_screen = ""      # stores the last captured stable content
        stable_count = 0
        # 4 consecutive polls × 0.5s = 2 seconds of stability required.
        # This prevents premature triggering between 1-second ping packet intervals:
        # each inter-packet gap is ~0.9s, so stable_count can reach at most 1
        # before the next packet resets it. Only true post-command stability
        # (summary + prompt, no more output) produces a 2s+ stable window.
        STABLE_READS_NEEDED = 4

        # Each loop iteration: 0.5s sleep + ~0.3s read_screen = ~0.8s per tick
        for _ in range(timeout * 2):
            time.sleep(0.5)
            current = self.read_screen()

            if not changed:
                if current.strip() != previous_screen.strip():
                    changed = True   # host has started responding

            if changed:
                if current.strip() == last_screen.strip():
                    stable_count += 1
                    stable_screen = current
                    if stable_count >= STABLE_READS_NEEDED:
                        return stable_screen  # screen settled — return it directly
                else:
                    stable_count = 0          # still receiving data, reset counter
                    stable_screen = current   # keep updating to latest content

            last_screen = current

        # Timed out — return whatever stable content we last captured
        return stable_screen if stable_screen else previous_screen

    def terminate_session(self):
        # Enter() dismisses the post-session [Press <Enter>] prompt that
        # wc3270 shows when the telehack connection has ended.
        self.send_command('Enter()')
        time.sleep(0.5)
        # Disconnect() cleanly closes the telehack 3270 session.
        self.send_command('Disconnect()')
        time.sleep(0.5)
        # Quit() tells wc3270 to close its window via the scriptport.
        self.send_command('Quit()')
        if self.sock:
            self.sock.close()
        # Terminate via saved process handle (faster and cleaner than taskkill).
        # taskkill is kept as final fallback for any orphaned processes.
        if self.headed_proc:
            try:
                self.headed_proc.terminate()
            except Exception:
                pass
        time.sleep(0.5)
        os.system("taskkill /F /IM wc3270.exe /T >nul 2>&1")
        print("[ENGINE] Session terminated.")