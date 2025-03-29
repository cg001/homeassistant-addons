import os
import paramiko

host = os.getenv("SFTP_HOST")
port = int(os.getenv("SFTP_PORT", 22))
username = os.getenv("SFTP_USER")
password = os.getenv("SFTP_PASS")

print(f"🔌 Verbindung zu {host}:{port} wird getestet...")

try:
    client = paramiko.Transport((host, port))
    client.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(client)
    print("✅ SFTP-Verbindung erfolgreich hergestellt.")
    sftp.close()
    client.close()
except Exception as e:
    print("❌ Verbindung fehlgeschlagen:", str(e))
