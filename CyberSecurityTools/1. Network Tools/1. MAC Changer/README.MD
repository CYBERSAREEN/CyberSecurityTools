
# MAC Address Changer Pro

A powerful, command-line based MAC address manipulation tool built with Python that allows you to change, reset, and monitor MAC addresses on network interfaces.

## 🚀 Features

- **MAC Address Modification**: Change MAC addresses to any valid format
- **Automatic Backup**: Stores original MAC addresses for easy restoration
- **Interface Management**: View available network interfaces
- **Reset Functionality**: Restore original MAC addresses with one command
- **Validation System**: Ensures MAC address format compliance
- **Non-Destructive**: Safe operations with proper error handling

## 📋 Requirements

- Python 3.x
- Linux operating system
- Root/administrator privileges
- `ip` command available (standard on most Linux distributions)

## 🛠 Installation

```bash
# Clone or download the script
git clone <repository-url>
cd mac-changer

# Make the script executable
chmod +x mac_changer.py

# Run directly with Python
python3 mac_changer.py -h
```

## 📖 Code Explanation

### Class Structure: `MACChanger`

The tool is built around a main class that handles all MAC address operations.

#### Initialization

```python
def __init__(self):
    self.storage_file = "original_mac.txt"  # File to store original MACs
    self.current_interface = None           # Track current interface
```

#### Banner Display

```python
def print_banner(self):
    # Displays the ASCII art banner using raw string to handle special characters
    # This creates a professional-looking header for the tool
```

#### Interface Discovery

```python
def get_available_interfaces(self):
    # Uses 'ip link show' command to list all network interfaces
    # Parses output to extract interface names, excluding loopback (lo)
    # Returns list of available interfaces like ['eth0', 'wlan0']
```

#### MAC Address Retrieval

```python
def get_current_mac(self, interface):
    # Runs 'ip link show [interface]' to get interface details
    # Parses output for 'link/ether' line to extract MAC address
    # Returns MAC address string or None if not found
```

#### MAC Format Validation

```python
def validate_mac_format(self, mac):
    # Checks if MAC address follows xx:xx:xx:xx:xx:xx format
    # Validates: length=17, 6 colon-separated parts, each part is 2 hex digits
    # Returns True for valid MAC, False for invalid
```

#### Storage System

```python
def store_original_mac(self, interface, mac):
    # Stores original MAC addresses in text file
    # Uses dictionary to handle multiple interfaces
    # Format: "interface:mac_address" per line
```

#### MAC Change Operations

```python
def change_mac_address(self, interface, new_mac):
    # 1. Stores original MAC for backup
    # 2. Brings interface down using 'ip link set interface down'
    # 3. Changes MAC with 'ip link set interface address new_mac'
    # 4. Brings interface back up
    # 5. Verifies the change was successful
```

#### Reset Functionality

```python
def reset_mac_address(self, interface):
    # 1. Retrieves original MAC from storage file
    # 2. Brings interface down
    # 3. Restores original MAC address
    # 4. Brings interface back up
    # 5. Verifies restoration was successful
```

## 🎯 Usage Examples

### View Available Interfaces

```bash
sudo python3 mac_changer.py -a
# or
sudo python3 mac_changer.py --available
```

**Output:**

```
[+] Available Interfaces:
    - eth0
    - wlan0
```

### Show Current MAC Address

```bash
sudo python3 mac_changer.py -i eth0 -s
# or
sudo python3 mac_changer.py --interface eth0 --show
```

**Output:**

```
[+] Current MAC address for eth0: 08:00:27:12:34:56
[+] Original MAC address for eth0: 08:00:27:12:34:56
[+] Currently using original MAC address
```

### Change MAC Address

```bash
sudo python3 mac_changer.py -i eth0 -m 00:11:22:33:44:55
# or
sudo python3 mac_changer.py --interface eth0 --setmac 00:11:22:33:44:55
```

**Output:**

```
[*] Current MAC: 08:00:27:12:34:56
[+] Original MAC stored for eth0
[*] Changing MAC address to: 00:11:22:33:44:55
[*] Bringing eth0 down...
[*] Setting new MAC address...
[*] Bringing eth0 up...
[+] Successfully changed MAC address to 00:11:22:33:44:55
```

### Reset to Original MAC

```bash
sudo python3 mac_changer.py -i eth0 -r
# or
sudo python3 mac_changer.py --interface eth0 --reset
```

**Output:**

```
[*] Resetting eth0 to original MAC: 08:00:27:12:34:56
[*] Bringing eth0 down...
[*] Restoring original MAC address...
[*] Bringing eth0 up...
[+] Successfully restored original MAC address: 08:00:27:12:34:56
```

## 🔧 Command Line Arguments

| Argument        | Short  | Description                                 |
| --------------- | ------ | ------------------------------------------- |
| `--available` | `-a` | Show all available network interfaces       |
| `--interface` | `-i` | Specify network interface to work with      |
| `--setmac`    | `-m` | Set new MAC address (requires -i)           |
| `--reset`     | `-r` | Reset to original MAC address (requires -i) |
| `--show`      | `-s` | Show current MAC address (requires -i)      |
| `--help`      | `-h` | Show help message and examples              |

## ⚠️ Important Notes

### Root Privileges

**Always run with sudo:** MAC address changes require root privileges. Without sudo, the tool will fail to modify interfaces.

```bash
# Correct
sudo python3 mac_changer.py -i eth0 -m 00:11:22:33:44:55

# Incorrect (will fail)
python3 mac_changer.py -i eth0 -m 00:11:22:33:44:55
```

### MAC Address Format

- Must be exactly 17 characters long
- Format: `xx:xx:xx:xx:xx:xx`
- Each `xx` must be a valid hexadecimal pair (00-FF)
- Example valid MAC: `00:1A:2B:3C:4D:5E`

### Storage File

The tool creates `original_mac.txt` to store original MAC addresses. Do not delete this file if you want to reset interfaces later.

## 🛡️ Error Handling

The tool includes comprehensive error handling:

- **Invalid MAC Format**: Validates input before attempting changes
- **Interface Verification**: Checks if specified interface exists
- **Command Execution**: Monitors success of system commands
- **File Operations**: Handles storage file read/write errors
- **Permission Checks**: Requires root privileges for modifications

## 🔍 Troubleshooting

### Common Issues

1. **"Interface not found"**

   - Use `-a` flag to see available interfaces
   - Check interface name spelling
2. **"MAC format unsupported"**

   - Ensure format is `xx:xx:xx:xx:xx:xx`
   - Use lowercase letters for hex digits
3. **"No original MAC address found"**

   - Original MAC wasn't stored (first time use)
   - Storage file was deleted or corrupted
4. **Operation fails**

   - Ensure you're using `sudo`
   - Check if interface is currently in use

### Manual Verification

You can manually verify MAC addresses:

```bash
ip link show eth0
# Look for "link/ether" followed by MAC address
```

## 📁 File Structure

```
mac_changer.py          # Main script
original_mac.txt        # Auto-generated storage file
README.md              # This documentation
```

## 🎨 Technical Details

### System Commands Used

- `ip link show` - Interface discovery and MAC reading
- `ip link set [interface] down` - Disable interface
- `ip link set [interface] address [mac]` - Change MAC address
- `ip link set [interface] up` - Enable interface

### Storage Format

The `original_mac.txt` file uses simple text format:

```
eth0:08:00:27:12:34:56
wlan0:02:42:ac:11:00:02
```

### Return Codes

- **Success**: Returns `True` and displays `[+]` messages
- **Failure**: Returns `False` and displays `[-]` error messages

## 🤝 Contributing

Feel free to contribute by:

- Reporting bugs
- Suggesting new features
- Improving documentation
- Submitting pull requests

## ⚖️ Legal Disclaimer

This tool is intended for:

- Educational purposes
- Network testing in controlled environments
- Legitimate security research

**Always ensure you have proper authorization** before changing MAC addresses on any network. Unauthorized MAC address spoofing may violate laws or network policies.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Note**: This tool works best on Linux systems. Windows and macOS may require different system commands and approaches.
