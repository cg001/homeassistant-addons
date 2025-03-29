import os
import paramiko

print("🧪 TEST: Skript wurde erfolgreich ausgeführt")

host = os.getenv("SFTP_HOST")
port = int(os.getenv("SFTP_PORT", 22))
username = os.getenv("SFTP_USER")
password = os.getenv("SFTP_PASS")
directory = os.getenv("SFTP_DIR")

print(f"🔌 Verbindung zu {host}:{port} wird getestet...")

try:
    client = paramiko.Transport((host, port))
    client.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(client)
    print("✅ SFTP-Verbindung erfolgreich hergestellt.")

    print(f"📁 Wechsel in Verzeichnis: {directory}")
    sftp.chdir(directory)

    print("📂 XML-Dateien im Zielverzeichnis:")
    for f in sftp.listdir_attr("."):
        if f.filename.lower().endswith(".xml"):
            print(f" - {f.filename} ({f.st_size} Bytes)")

    sftp.close()
    client.close()
except Exception as e:
    print("❌ Fehler beim Zugriff:", str(e))
