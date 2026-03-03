import subprocess
import argparse

class MACChanger:
    def __init__(self):
        self.storage_file = "original_mac.txt"
        self.current_interface = None
        
    def print_banner(self):
        banner = r"""
╔═════════════════════════════════════╗
║  ███╗   ███╗ █████╗  ██████╗        ║
║  ████╗ ████║██╔══██╗██╔════╝        ║
║  ██╔████╔██║███████║██║             ║
║  ██║╚██╔╝██║██╔══██║██║             ║
║  ██║ ╚═╝ ██║██║  ██║╚██████╗        ║
║  ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝        ║
║                                     ║
║        Address  Changer  Pro        ║
╚═════════════════════════════════════╝
        """
        print(banner)
    
    def get_available_interfaces(self):
        """Get list of available network interfaces"""
        try:
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            interfaces = []
            current_interface = None
            
            for line in result.stdout.split('\n'):
                if ':' in line and not line.strip().startswith(' '):
                    # Extract interface name (e.g., "1: lo:" -> "lo")
                    parts = line.split(':')
                    if len(parts) >= 2:
                        interface = parts[1].strip()
                        if interface and interface not in ['lo']:
                            interfaces.append(interface)
            return interfaces
        except Exception as e:
            print(f"Error getting interfaces: {e}")
            return []
    
    def show_available_interfaces(self):
        """Display available interfaces"""
        interfaces = self.get_available_interfaces()
        print("\n[+] Available Interfaces:")
        for interface in interfaces:
            print(f"    - {interface}")
        print()
    
    def get_current_mac(self, interface):
        """Get current MAC address of an interface"""
        try:
            result = subprocess.run(['ip', 'link', 'show', interface], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'link/ether' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'link/ether':
                            if i + 1 < len(parts):
                                return parts[i + 1]
            return None
        except Exception as e:
            print(f"Error getting MAC: {e}")
            return None
    
    def validate_mac_format(self, mac):
        """Validate MAC address format"""
        if len(mac) != 17:
            return False
        parts = mac.split(':')
        if len(parts) != 6:
            return False
        for part in parts:
            if len(part) != 2:
                return False
            try:
                int(part, 16)
            except:
                return False
        return True
    
    def store_original_mac(self, interface, mac):
        """Store original MAC address in file"""
        try:
            # Read existing content
            existing_data = {}
            try:
                with open(self.storage_file, 'r') as f:
                    for line in f:
                        if ':' in line:
                            stored_interface, stored_mac = line.strip().split(':', 1)
                            existing_data[stored_interface] = stored_mac
            except FileNotFoundError:
                pass
            
            # Update with new interface
            existing_data[interface] = mac
            
            # Write back to file
            with open(self.storage_file, 'w') as f:
                for stored_interface, stored_mac in existing_data.items():
                    f.write(f"{stored_interface}:{stored_mac}\n")
            return True
        except Exception as e:
            print(f"Error storing MAC: {e}")
            return False
    
    def get_original_mac(self, interface):
        """Retrieve original MAC address from file"""
        try:
            with open(self.storage_file, 'r') as f:
                for line in f:
                    if line.strip() and ':' in line:
                        parts = line.strip().split(':', 1)
                        if len(parts) == 2 and parts[0] == interface:
                            return parts[1]
            return None
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error reading stored MAC: {e}")
            return None
    
    def change_mac_address(self, interface, new_mac):
        """Change MAC address of specified interface"""
        try:
            # Get and store original MAC
            original_mac = self.get_current_mac(interface)
            if original_mac:
                print(f"[*] Current MAC: {original_mac}")
                if self.store_original_mac(interface, original_mac):
                    print(f"[+] Original MAC stored for {interface}")
                else:
                    print("[-] Failed to store original MAC")
            
            print(f"[*] Changing MAC address to: {new_mac}")
            
            # Bring interface down
            print(f"[*] Bringing {interface} down...")
            down_result = subprocess.run(['ip', 'link', 'set', interface, 'down'], 
                                       capture_output=True, text=True)
            if down_result.returncode != 0:
                print(f"[-] Failed to bring interface down: {down_result.stderr}")
                return False
            
            # Change MAC address
            print(f"[*] Setting new MAC address...")
            mac_result = subprocess.run(['ip', 'link', 'set', interface, 'address', new_mac], 
                                      capture_output=True, text=True)
            if mac_result.returncode != 0:
                print(f"[-] Failed to set MAC address: {mac_result.stderr}")
                # Try to bring interface back up
                subprocess.run(['ip', 'link', 'set', interface, 'up'], capture_output=True)
                return False
            
            # Bring interface up
            print(f"[*] Bringing {interface} up...")
            up_result = subprocess.run(['ip', 'link', 'set', interface, 'up'], 
                                     capture_output=True, text=True)
            if up_result.returncode != 0:
                print(f"[-] Failed to bring interface up: {up_result.stderr}")
                return False
            
            # Wait a moment for interface to stabilize
            import time
            time.sleep(2)
            
            # Verify change
            current_mac = self.get_current_mac(interface)
            if current_mac and current_mac.lower() == new_mac.lower():
                print(f"[+] Successfully changed MAC address to {new_mac}")
                return True
            else:
                print(f"[-] MAC address was not changed. Current: {current_mac}, Expected: {new_mac}")
                return False
                
        except Exception as e:
            print(f"[-] Error changing MAC address: {e}")
            return False
    
    def reset_mac_address(self, interface):
        """Reset MAC address to original"""
        original_mac = self.get_original_mac(interface)
        if not original_mac:
            print(f"[-] No original MAC address found for {interface}")
            print(f"[*] Check {self.storage_file} for stored MAC addresses")
            return False
        
        print(f"[*] Resetting {interface} to original MAC: {original_mac}")
        
        try:
            # Bring interface down
            print(f"[*] Bringing {interface} down...")
            down_result = subprocess.run(['ip', 'link', 'set', interface, 'down'], 
                                       capture_output=True, text=True)
            if down_result.returncode != 0:
                print(f"[-] Failed to bring interface down: {down_result.stderr}")
                return False
            
            # Reset to original MAC
            print(f"[*] Restoring original MAC address...")
            mac_result = subprocess.run(['ip', 'link', 'set', interface, 'address', original_mac], 
                                      capture_output=True, text=True)
            if mac_result.returncode != 0:
                print(f"[-] Failed to restore MAC address: {mac_result.stderr}")
                # Try to bring interface back up
                subprocess.run(['ip', 'link', 'set', interface, 'up'], capture_output=True)
                return False
            
            # Bring interface up
            print(f"[*] Bringing {interface} up...")
            up_result = subprocess.run(['ip', 'link', 'set', interface, 'up'], 
                                     capture_output=True, text=True)
            if up_result.returncode != 0:
                print(f"[-] Failed to bring interface up: {up_result.stderr}")
                return False
            
            # Wait a moment for interface to stabilize
            import time
            time.sleep(2)
            
            # Verify reset
            current_mac = self.get_current_mac(interface)
            if current_mac and current_mac.lower() == original_mac.lower():
                print(f"[+] Successfully restored original MAC address: {original_mac}")
                return True
            else:
                print(f"[-] MAC address was not restored. Current: {current_mac}, Expected: {original_mac}")
                return False
                
        except Exception as e:
            print(f"[-] Error resetting MAC address: {e}")
            return False
    
    def show_current_mac(self, interface):
        """Show current MAC address of interface"""
        current_mac = self.get_current_mac(interface)
        if current_mac:
            print(f"[+] Current MAC address for {interface}: {current_mac}")
            
            # Show original MAC if available
            original_mac = self.get_original_mac(interface)
            if original_mac:
                print(f"[+] Original MAC address for {interface}: {original_mac}")
                if current_mac.lower() == original_mac.lower():
                    print("[+] Currently using original MAC address")
                else:
                    print("[!] Currently using modified MAC address")
        else:
            print(f"[-] Could not retrieve MAC address for {interface}")
    
    def run(self):
        """Main method to run the tool"""
        self.print_banner()
        
        parser = argparse.ArgumentParser(description='MAC Address Changer Tool')
        parser.add_argument('-a', '--available', action='store_true', 
                          help='Show available interfaces')
        parser.add_argument('-i', '--interface', type=str, 
                          help='Network interface to modify')
        parser.add_argument('-m', '--setmac', type=str, 
                          help='New MAC address (format: xx:xx:xx:xx:xx:xx)')
        parser.add_argument('-r', '--reset', action='store_true', 
                          help='Reset to original MAC address')
        parser.add_argument('-s', '--show', action='store_true', 
                          help='Show current MAC address')
        
        args = parser.parse_args()
        
        # Show available interfaces
        if args.available:
            self.show_available_interfaces()
            return
        
        # Show current MAC address
        if args.show:
            if not args.interface:
                print("[-] Please specify an interface using -i")
                return
            
            interfaces = self.get_available_interfaces()
            if args.interface not in interfaces:
                print(f"[-] Interface {args.interface} not found")
                self.show_available_interfaces()
                return
                
            self.show_current_mac(args.interface)
            return
        
        # Reset MAC address
        if args.reset:
            if not args.interface:
                print("[-] Please specify an interface using -i")
                return
            
            interfaces = self.get_available_interfaces()
            if args.interface not in interfaces:
                print(f"[-] Interface {args.interface} not found")
                self.show_available_interfaces()
                return
                
            self.reset_mac_address(args.interface)
            return
        
        # Change MAC address
        if args.interface and args.setmac:
            if not self.validate_mac_format(args.setmac):
                print("[-] MAC format unsupported. Use format: xx:xx:xx:xx:xx:xx")
                return
            
            # Verify interface exists
            interfaces = self.get_available_interfaces()
            if args.interface not in interfaces:
                print(f"[-] Interface {args.interface} not found")
                self.show_available_interfaces()
                return
            
            self.change_mac_address(args.interface, args.setmac)
            return
        
        # If no valid arguments provided, show help
        if not any(vars(args).values()):
            parser.print_help()
            print("\nExamples:")
            print("  sudo python3 mac_changer.py -a")
            print("  sudo python3 mac_changer.py -i eth0 -s")
            print("  sudo python3 mac_changer.py -i eth0 -m 00:11:22:33:44:55")
            print("  sudo python3 mac_changer.py -i eth0 -r")
            print("\nNote: Requires root privileges for MAC changing operations")

def main():
    try:
        changer = MACChanger()
        changer.run()
    except KeyboardInterrupt:
        print("\n[!] Tool interrupted by user")
    except Exception as e:
        print(f"[-] An error occurred: {e}")

if __name__ == "__main__":
    main()