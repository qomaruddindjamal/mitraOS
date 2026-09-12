import paramiko
import base64
import os

s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect('172.23.101.33', 22, 'root', 'admin123', timeout=5)

def get_file(remote_path, local_path):
    stdin, stdout, stderr = s.exec_command(f'base64 -w 0 "{remote_path}"')
    b64 = stdout.read().decode().strip()
    if b64:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'wb') as f:
            f.write(base64.b64decode(b64))
        return True
    return False

# 1. Download /root/.jwmrc
get_file('/root/.jwmrc', r'C:\mitraOS\rootfs\root\.jwmrc')
get_file('/root/.jwmrc', r'C:\mitraOS\rootfs\etc\jwm\system.jwmrc')
print('[+] Downloaded .jwmrc')

# 2. List /usr/share/mitraos
stdin, stdout, stderr = s.exec_command('ls -1 /usr/share/mitraos')
for item in stdout.read().decode().splitlines():
    item = item.strip()
    if item.endswith('.png') or item.endswith('.jpg'):
        get_file(f'/usr/share/mitraos/{item}', rf'C:\mitraOS\rootfs\usr\share\mitraos\{item}')
        if item.startswith('btn_'):
            get_file(f'/usr/share/mitraos/{item}', rf'C:\mitraOS\assets\ui\{item}')
        print(f'  [+] Asset: {item}')

# 3. List /usr/bin/mitra* and /usr/bin/workstation
stdin, stdout, stderr = s.exec_command('ls -1 /usr/bin/mitra* /usr/bin/workstation 2>/dev/null')
for line in stdout.read().decode().splitlines():
    p = line.strip()
    if p:
        b = os.path.basename(p)
        # Check if regular file (dereference symlink if needed)
        stdin2, stdout2, stderr2 = s.exec_command(f'test -f "{p}" && echo REG')
        if 'REG' in stdout2.read().decode():
            get_file(p, rf'C:\mitraOS\core\bin\{b}')
            get_file(p, rf'C:\mitraOS\rootfs\usr\bin\{b}')
            print(f'  [+] Script: {b}')

# 4. Check /etc/X11 and xinitrc
get_file('/etc/X11/xinit/xinitrc', r'C:\mitraOS\rootfs\etc\X11\xinit\xinitrc')
get_file('/etc/X11/xorg.conf', r'C:\mitraOS\rootfs\etc\X11\xorg.conf')

s.close()
print('[+] All real code and assets successfully extracted from VHDX!')
