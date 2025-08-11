# Local QR Scan Server

This project provides a minimal Flask application for simulating QR-code scans on a local network. A phone scans a QR code that points to your laptop. The server logs limited request data and immediately redirects the phone to your chosen educational website.

## Overview

* `app.py` – Flask server with three routes:
  * `GET /` status page.
  * `GET /scan` logs data then redirects.
  * `GET /dashboard` PIN-protected scan dashboard.
* `generate_qr.py` – Creates a QR code pointing to `/scan` on your LAN IP.
* Data is kept only in memory and cleared on server restart.

## Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Server

```bash
python app.py
```

At startup the server prints:

* The dashboard PIN (6 digits) – required to view `/dashboard`.
* The listening address (default `0.0.0.0:5000`).

Open `http://<laptop-ip>:5000/` in a browser to see the status page.

### Dashboard

Visit `http://<laptop-ip>:5000/dashboard?pin=PIN` or open `/dashboard`, enter the PIN and view the log table. The table lists scans in reverse chronological order.

### Generate the QR Code

```bash
python generate_qr.py
```

The script prints the full URL and saves a `qr_scan.png` file. Make sure both the phone and the laptop are on the same Wi-Fi network. If the laptop's IP changes, regenerate the QR code.

### Testing with a Phone

1. Ensure the server is running and the phone is on the same network.
2. Open the QR image on your laptop and scan it with the phone.
3. The phone is redirected to the educational website (default `https://www.karunya.edu/`).
4. Refresh the dashboard to see the new entry.

## Environment Variables

* `EDU_REDIRECT_URL` – override the redirect target.
* `DASHBOARD_PIN` – set a fixed dashboard PIN.
* `PORT` – change the listening port (affects QR generation too).

## Notes

* Only anonymized IP, hashed User-Agent (short prefix), language, referrer, and timestamp are logged.
* All data stays in memory; restarting the server clears the history.
* The server binds to `0.0.0.0` so devices on the LAN can access it. Check firewall settings if the phone cannot connect.
