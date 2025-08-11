import os
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template_string, session
import hashlib
import secrets
from ipaddress import ip_address, IPv4Address, IPv6Address

app = Flask(__name__)
app.secret_key = os.urandom(24)

# In-memory log storage
scan_events = []

# Environment configuration
REDIRECT_URL = os.environ.get("EDU_REDIRECT_URL", "https://www.karunya.edu/")
DASHBOARD_PIN = os.environ.get("DASHBOARD_PIN")
if DASHBOARD_PIN is None:
    DASHBOARD_PIN = f"{secrets.randbelow(10**6):06d}"
    print(f"[INFO] Generated dashboard PIN: {DASHBOARD_PIN}")
else:
    print("[INFO] Using dashboard PIN from env")


# Helper functions
def anonymize_ip(ip: str) -> str:
    try:
        parsed = ip_address(ip)
        if isinstance(parsed, IPv4Address):
            parts = ip.split('.')
            parts[-1] = '0'
            return '.'.join(parts)
        elif isinstance(parsed, IPv6Address):
            hextets = ip.split(':')
            return ':'.join(hextets[:4]) + '::'
    except ValueError:
        pass
    return 'unknown'


def short_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:10]


def get_client_ip() -> str:
    xfwd = request.headers.get('X-Forwarded-For', request.remote_addr)
    # X-Forwarded-For may contain multiple IPs
    if xfwd:
        ip = xfwd.split(',')[0].strip()
    else:
        ip = request.remote_addr or '0.0.0.0'
    return ip


@app.after_request
def apply_security_headers(resp):
    resp.headers['Content-Security-Policy'] = "default-src 'self'"
    resp.headers['Referrer-Policy'] = 'no-referrer'
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    return resp


@app.route('/')
def index():
    return '<h1>QR Scan Server Running</h1><p>Scan the QR code or visit /scan.</p>'


@app.route('/scan')
def scan():
    ip = anonymize_ip(get_client_ip())
    ua = request.headers.get('User-Agent', '')
    ua_hash = short_hash(ua)
    ua_snippet = ua[:120]
    lang = request.headers.get('Accept-Language', '')
    ref = request.referrer or ''
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    scan_events.append({
        'timestamp': timestamp,
        'ip': ip,
        'ua_hash': ua_hash,
        'ua_snippet': ua_snippet,
        'lang': lang,
        'ref': ref,
    })

    return redirect(REDIRECT_URL, code=302)


DASHBOARD_TEMPLATE = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 4px; font-size: 14px; }
        th { background: #eee; }
    </style>
</head>
<body>
<h1>Scan Dashboard</h1>
<p>Total scans: {{ events|length }}</p>
<table>
    <tr><th>Timestamp</th><th>IP</th><th>UA Hash</th><th>UA Snippet</th><th>Language</th><th>Referrer</th></tr>
    {% for e in events %}
    <tr>
        <td>{{ e.timestamp }}</td>
        <td>{{ e.ip }}</td>
        <td>{{ e.ua_hash }}</td>
        <td>{{ e.ua_snippet }}</td>
        <td>{{ e.lang }}</td>
        <td>{{ e.ref }}</td>
    </tr>
    {% endfor %}
</table>
</body>
</html>
"""


LOGIN_TEMPLATE = """
<!doctype html>
<html><body>
<h1>Dashboard Login</h1>
<form method="post">
    <input type="password" name="pin" placeholder="PIN" autofocus />
    <button type="submit">Enter</button>
</form>
</body></html>
"""


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if session.get('auth'):
        events = list(reversed(scan_events))
        return render_template_string(DASHBOARD_TEMPLATE, events=events)

    pin = request.values.get('pin')
    if request.method == 'POST' and pin == DASHBOARD_PIN:
        session['auth'] = True
        return redirect(url_for('dashboard'))
    elif request.args.get('pin') == DASHBOARD_PIN:
        session['auth'] = True
        return redirect(url_for('dashboard'))
    else:
        return render_template_string(LOGIN_TEMPLATE)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '5000'))
    print(f"[INFO] Server listening on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
