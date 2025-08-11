import os
import socket
import qrcode

PORT = int(os.environ.get("PORT", "5000"))


def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def main():
    ip = get_lan_ip()
    url = f"http://{ip}:{PORT}/scan"
    img = qrcode.make(url)
    filename = "qr_scan.png"
    img.save(filename)
    print(url)
    print(f"Saved QR to {filename}")


if __name__ == "__main__":
    main()
