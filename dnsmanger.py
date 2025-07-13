import subprocess
import ctypes
import sys
from prettytable import PrettyTable


def is_admin():
    """Check if the script is run with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_active_interface():
    """
    Detect the most appropriate active network interface.
    Prioritize Wi-Fi, then Ethernet.
    """
    result = subprocess.run('netsh interface show interface',
                            capture_output=True, text=True, shell=True)
    print("\n[Network Interfaces]")
    print(result.stdout)
    interfaces = result.stdout.splitlines()
    candidates = []

    for line in interfaces:
        if "Connected" in line:
            parts = line.strip().split()
            name = " ".join(parts[3:])  # Interface name may contain spaces
            candidates.append(name)

    # Prioritize Wi-Fi
    for iface in candidates:
        if "Wi-Fi" in iface:
            return iface
    # Then Ethernet
    for iface in candidates:
        if "Ethernet" in iface:
            return iface

    # Otherwise return the first connected interface found
    return candidates[0] if candidates else None


def force_clear_dns(interface):
    """Fully clear all DNS settings and flush DNS cache"""
    try:
        subprocess.run(f'netsh interface ipv4 set dnsservers name="{interface}" source=dhcp register=none',
                       shell=True, check=True)
        subprocess.run(f'netsh interface ipv6 set dnsservers name="{interface}" source=dhcp register=none',
                       shell=True, check=True)
        subprocess.run('ipconfig /flushdns', shell=True, check=True)
        print(f"\n✅ All DNS settings completely cleared for interface '{interface}'.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to clear DNS settings: {e}")


def set_dns(interface, primary, secondary=None):
    """Set custom DNS servers on the specified interface"""
    try:
        force_clear_dns(interface)
        subprocess.run(f'netsh interface ipv4 set dns name="{interface}" static {primary} primary',
                       shell=True, check=True)
        if secondary:
            subprocess.run(f'netsh interface ipv4 add dns name="{interface}" {secondary} index=2',
                           shell=True, check=True)
        print("\n✅ DNS configured successfully:")
        print(f"Primary DNS: {primary}")
        if secondary:
            print(f"Secondary DNS: {secondary}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to set DNS: {e}")


def show_dns_menu():
    """Display predefined DNS server list"""
    DNS_SERVERS = [
        {"name": "Cloudflare", "primary": "1.1.1.1", "secondary": "1.0.0.1"},
        {"name": "Google", "primary": "8.8.8.8", "secondary": "8.8.4.4"},
        {"name": "Quad9", "primary": "9.9.9.9", "secondary": "149.112.112.112"},
        {"name": "OpenDNS", "primary": "208.67.222.222", "secondary": "208.67.220.220"},
        {"name": "DNS.WATCH", "primary": "84.200.69.80", "secondary": "84.200.70.40"},
        {"name": "Comodo", "primary": "8.26.56.26", "secondary": "8.20.247.20"},
        {"name": "Verisign", "primary": "64.6.64.6", "secondary": "64.6.65.6"},
        {"name": "CleanBrowsing", "primary": "185.228.168.9", "secondary": "185.228.169.9"},
        {"name": "Alternate DNS", "primary": "76.76.19.19", "secondary": "76.223.122.150"},
        {"name": "AdGuard", "primary": "94.140.14.14", "secondary": "94.140.15.15"},
        {"name": "Shecan", "primary": "178.22.122.100", "secondary": "185.51.200.2"},
        {"name": "Electro", "primary": "78.157.42.100", "secondary": "78.157.42.101"},
        {"name": "Radar Game", "primary": "10.202.10.10", "secondary": "10.202.10.11"},
        {"name": "403.online", "primary": "10.202.10.202", "secondary": "10.202.10.102"},
        {"name": "Asiatech", "primary": "194.104.158.48", "secondary": "194.104.158.78"},
        {"name": "Bogzar", "primary": "185.55.226.26", "secondary": "185.55.225.25"},
    ]

    table = PrettyTable()
    table.field_names = ["#", "Name", "Primary DNS", "Secondary DNS"]
    for i, server in enumerate(DNS_SERVERS, start=1):
        table.add_row([i, server["name"], server["primary"], server["secondary"]])

    print("\n📋 Available DNS Servers:")
    print(table)
    return DNS_SERVERS


def show_current_dns(interface):
    """Show current DNS settings of the interface"""
    print(f"\n🔍 Current DNS settings for interface '{interface}':")
    subprocess.run(f'netsh interface ipv4 show dns name="{interface}"', shell=True)


def main():
    if not is_admin():
        print("⚠ Please run this script as Administrator!")
        input("Press Enter to exit...")
        sys.exit(1)

    while True:
        print("\n" + "=" * 50)
        print(" DNS Manager ".center(50, "="))
        print("=" * 50)
        print("1. Show current DNS settings")
        print("2. Set custom DNS")
        print("3. Select from predefined DNS list")
        print("4. Clear all DNS settings")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        interface = get_active_interface()
        if not interface:
            print("\n⚠ No active network interface found!")
            input("\nPress Enter to continue...")
            continue

        print(f"\n🔌 Active interface detected: {interface}")

        if choice == "1":
            show_current_dns(interface)
        elif choice == "2":
            primary = input("Enter Primary DNS: ").strip()
            secondary = input("Enter Secondary DNS (optional): ").strip() or None
            set_dns(interface, primary, secondary)
        elif choice == "3":
            servers = show_dns_menu()
            try:
                selection = int(input("\nSelect DNS server by number: "))
                if 1 <= selection <= len(servers):
                    server = servers[selection - 1]
                    set_dns(interface, server["primary"], server["secondary"])
                else:
                    print("⚠ Invalid selection.")
            except ValueError:
                print("⚠ Please enter a valid number.")
        elif choice == "4":
            force_clear_dns(interface)
        elif choice == "5":
            print("👋 Exiting DNS Manager...")
            sys.exit(0)
        else:
            print("⚠ Invalid choice.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        from prettytable import PrettyTable
    except ImportError:
        print("\n⚠ Please install prettytable first:")
        print("pip install prettytable")
        sys.exit(1)

    main()
