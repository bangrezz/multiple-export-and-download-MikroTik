"""
[NOTE] :
- Skrip ini bisa digunakan
- Skrip ini sukses untuk login ke beberapa device mikrotik, ekspor file log, kemudian download ke laptop
[WARN] : Namun dikarenakan algoritma regexp mencari filenya, skrip ini mendownload file yang mirip dengan nama file yang baru digenerate
[NEXT] : Solusinya untuk download file yang akurat, bisa menggunakan fitur "tool fetch mikrotik"
"""


import paramiko
import ipaddress
import socket
import sys
import os
import datetime
import time
import re

os.system('')

def login_mikrotik(ip, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=username, password=password, timeout=20)
        print("\033[32m" + f"[+] Berhasil login ke {ip}" + "\033[0m")

        # Get the current date and time
        now = datetime.datetime.now()
        #date_time = now.strftime("%Y-%m-%d-%H-%M-%S")
        date_time = now.strftime("%Y%m%d-%H%M%S")

        # Define the log filename
        log_filename = f"{ip}-{date_time}.log"

        # Export the log file
        command = f"/log print file={log_filename}"
        stdin, stdout, stderr = ssh.exec_command(command)
        print(f"[*] Eksekusi perintah '{command}' di {ip}:")
        print(stdout.read().decode())

        time.sleep(5)  # wait for 5 seconds

        # Buat objek SFTP
        sftp = ssh.open_sftp()

        # Pola regexp untuk mencocokkan nama file
        pattern = rf"\b{ip}-\d{{8}}-\d{{6}}\.log\.txt\b"

        # Mendapatkan daftar semua file di direktori root
        files = sftp.listdir('/')

        # Mencari file yang cocok dengan pola
        for file in files:
            if re.match(pattern, file):
                # Lokasi file di komputer lokal (direktori tempat skrip dijalankan)
                local_file = os.path.join(os.getcwd(), file)

                # Mendownload file
                sftp.get('/' + file, local_file)

        # Menutup koneksi
        sftp.close()

    except socket.timeout:
        print("\033[31m" + f"[!] Target {ip} tidak ada: Connection timed out." + "\033[0m")
        print("[*] Coba lagi menggunakan network atau IP address yang berbeda")
        sys.exit(1)
    except paramiko.AuthenticationException:
        print(f"[!] Gagal login ke {ip} authentication failed")
    except Exception as e:
        print(f"[*] Gagal login ke {ip}: {e}")
    finally:
        ssh.close()

def main():
    username = 'admin'
    password = ''
    ip_range_input = input("""
        [*] Masukkan range IP dengan format dibawah
             |
             v
        192.168.1.0/24
            atau
        192.168.1.1-192.168.1.100 (tanpa spasi diantara '-')


        : """)

    if '-' in ip_range_input:
        start_ip, end_ip = ip_range_input.split('-')
        start_ip = ipaddress.IPv4Address(start_ip)
        end_ip = ipaddress.IPv4Address(end_ip)

        for ip_int in range(int(start_ip), int(end_ip) + 1):
            ip = ipaddress.IPv4Address(ip_int)
            login_mikrotik(str(ip), username, password)
    else:
        ip_range = ipaddress.ip_network(ip_range_input)
        for ip in ip_range.hosts():
            login_mikrotik(str(ip), username, password)

if __name__ == "__main__":
    main()
