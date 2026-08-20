import urllib.request
import zipfile
import io
import json

def test_all():
    print('=== 1. TESTING DYNAMIC ZIP DOWNLOAD FOR live_hacker_news_forge.zip ===')
    url = 'http://127.0.0.1:8740/api/download/live_hacker_news_forge.zip'
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as res:
        data = res.read()
        print('Downloaded ' + str(len(data)) + ' bytes')
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            print('Files inside ZIP:', zf.namelist()[:7])
            server_py = zf.read('server.py').decode('utf-8')
            print('Exact server.py content header inside ZIP:')
            print(server_py[:180])

    print('\n=== 2. TESTING DYNAMIC ZIP DOWNLOAD FOR crypto_portfolio_tracker.zip ===')
    url2 = 'http://127.0.0.1:8740/api/download/crypto_portfolio_tracker.zip'
    with urllib.request.urlopen(url2, timeout=5) as res:
        data2 = res.read()
        print('Downloaded ' + str(len(data2)) + ' bytes')
        with zipfile.ZipFile(io.BytesIO(data2)) as zf:
            print('Files inside ZIP:', zf.namelist()[:7])
            server_py2 = zf.read('server.py').decode('utf-8')
            print('Exact server.py content header inside ZIP:')
            print(server_py2[:180])

    print('\n=== 3. TESTING IDE INJECTION FOR EVERY SINGLE IDE ===')
    ides = ['antigravity', 'cursor', 'claude_desktop', 'claude_code', 'windsurf', 'z_code', 'opencode', 'codex']
    for ide in ides:
        inject_url = 'http://127.0.0.1:8740/api/ide/inject'
        payload = json.dumps({
            'ide': ide,
            'mcp_name': 'live_hacker_news_forge',
            'server_path': 'D:/Aditya/Forge/mcp/live_hacker_news_forge/server.py'
        }).encode('utf-8')
        req = urllib.request.Request(inject_url, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as res:
            resp_data = json.loads(res.read().decode())
            print('Inject ' + ide + ' -> OK: ' + str(resp_data.get('ok')) + ' | Path: ' + str(resp_data.get('config_path')))

if __name__ == '__main__':
    test_all()
