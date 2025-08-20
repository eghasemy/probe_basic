#!/usr/bin/env python3
"""
Probe Basic Support Bundle Generator
Standalone script for creating support bundles outside the GUI
"""

import os
import sys
import time
import subprocess
import tempfile
import zipfile
import argparse
from datetime import datetime
from pathlib import Path

def collect_system_info(bundle_dir):
    """Collect system information"""
    print("Collecting system information...")
    info_file = bundle_dir / "system_info.txt"
    
    with open(info_file, 'w') as f:
        f.write(f"Probe Basic Support Bundle\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write("=" * 50 + "\n\n")
        
        # Python and system information
        f.write("SYSTEM INFORMATION:\n")
        f.write(f"Platform: {sys.platform}\n")
        f.write(f"Python Version: {sys.version}\n")
        f.write(f"Script Path: {os.path.abspath(__file__)}\n\n")
        
        # System commands
        commands = [
            ("Kernel", ["uname", "-a"]),
            ("Distribution", ["lsb_release", "-a"]),
            ("Memory", ["free", "-h"]),
            ("Disk Space", ["df", "-h"]),
            ("CPU Info", ["lscpu"]),
            ("USB Devices", ["lsusb"]),
            ("PCI Devices", ["lspci"]),
        ]
        
        for name, cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    f.write(f"{name}:\n{result.stdout}\n")
                else:
                    f.write(f"{name}: Command failed (exit code {result.returncode})\n")
                    if result.stderr:
                        f.write(f"Error: {result.stderr}\n")
            except subprocess.TimeoutExpired:
                f.write(f"{name}: Command timed out\n")
            except FileNotFoundError:
                f.write(f"{name}: Command not found\n")
            except Exception as e:
                f.write(f"{name}: Error - {e}\n")
            f.write("\n")

def collect_linuxcnc_config(bundle_dir):
    """Collect LinuxCNC configuration files"""
    print("Collecting LinuxCNC configuration...")
    
    # Try to find INI file
    ini_file = os.getenv('INI_FILE_NAME')
    if not ini_file:
        # Look for common INI locations
        common_paths = [
            "~/linuxcnc/configs/sim/probe_basic.ini",
            "/usr/share/linuxcnc/configs/sim/probe_basic.ini",
            "./probe_basic.ini",
        ]
        for path in common_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                ini_file = expanded_path
                break
    
    if ini_file and os.path.exists(ini_file):
        print(f"Found INI file: {ini_file}")
        
        # Copy INI file
        dest_ini = bundle_dir / "machine.ini"
        try:
            with open(ini_file, 'r') as src, open(dest_ini, 'w') as dst:
                dst.write(src.read())
        except Exception as e:
            print(f"Warning: Could not copy INI file: {e}")
        
        # Find related files
        config_dir = Path(ini_file).parent
        print(f"Searching config directory: {config_dir}")
        
        # Copy HAL files
        for hal_file in config_dir.glob("*.hal"):
            try:
                dest_path = bundle_dir / hal_file.name
                with open(hal_file, 'r') as src, open(dest_path, 'w') as dst:
                    dst.write(src.read())
                print(f"Copied: {hal_file.name}")
            except Exception as e:
                print(f"Warning: Could not copy {hal_file}: {e}")
        
        # Copy other config files
        for ext in ['*.ngc', '*.py', '*.yml', '*.yaml', '*.xml']:
            for config_file in config_dir.glob(ext):
                try:
                    dest_path = bundle_dir / config_file.name
                    with open(config_file, 'r') as src, open(dest_path, 'w') as dst:
                        dst.write(src.read())
                    print(f"Copied: {config_file.name}")
                except Exception as e:
                    print(f"Warning: Could not copy {config_file}: {e}")
    else:
        print("Warning: No LinuxCNC INI file found")
        error_file = bundle_dir / "config_error.txt"
        with open(error_file, 'w') as f:
            f.write("LinuxCNC configuration not found\n")
            f.write(f"INI_FILE_NAME environment variable: {os.getenv('INI_FILE_NAME', 'Not set')}\n")

def collect_hal_info(bundle_dir):
    """Collect HAL information"""
    print("Collecting HAL information...")
    hal_file = bundle_dir / "hal_info.txt"
    
    with open(hal_file, 'w') as f:
        f.write("HAL INFORMATION:\n")
        f.write("=" * 30 + "\n\n")
        
        # HAL commands
        commands = [
            ("Components", ["halcmd", "show", "comp"]),
            ("Pins", ["halcmd", "show", "pin"]),
            ("Signals", ["halcmd", "show", "sig"]),
            ("Parameters", ["halcmd", "show", "param"]),
            ("Threads", ["halcmd", "show", "thread"]),
            ("Functions", ["halcmd", "show", "funct"]),
        ]
        
        hal_running = False
        for name, cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    f.write(f"{name}:\n{result.stdout}\n\n")
                    hal_running = True
                else:
                    f.write(f"{name}: Command failed\n")
                    if result.stderr:
                        f.write(f"Error: {result.stderr}\n")
            except subprocess.TimeoutExpired:
                f.write(f"{name}: Command timed out\n")
            except FileNotFoundError:
                f.write(f"{name}: halcmd not found (LinuxCNC not installed?)\n")
                break
            except Exception as e:
                f.write(f"{name}: Error - {e}\n")
        
        if not hal_running:
            f.write("\nNote: HAL may not be running or LinuxCNC may not be installed\n")

def collect_logs(bundle_dir):
    """Collect relevant log files"""
    print("Collecting log files...")
    log_dir = bundle_dir / "logs"
    log_dir.mkdir()
    
    # Common log locations
    log_files = [
        "/var/log/linuxcnc.log",
        "/tmp/linuxcnc.log",
        "~/linuxcnc_debug.txt",
        "~/linuxcnc.log",
        "/var/log/dmesg",
        "/var/log/syslog",
        "/var/log/kern.log",
        "/var/log/Xorg.0.log",
    ]
    
    for log_path in log_files:
        expanded_path = os.path.expanduser(log_path)
        if os.path.exists(expanded_path):
            try:
                log_name = os.path.basename(expanded_path)
                dest_path = log_dir / log_name
                
                # Copy last 2000 lines for large log files
                with open(expanded_path, 'r') as src:
                    lines = src.readlines()
                    # Take last 2000 lines or all if less
                    lines_to_copy = lines[-2000:] if len(lines) > 2000 else lines
                    
                with open(dest_path, 'w') as dst:
                    dst.writelines(lines_to_copy)
                    
                print(f"Copied log: {log_name} ({len(lines_to_copy)} lines)")
                
            except Exception as e:
                print(f"Warning: Could not copy {log_path}: {e}")

def collect_probe_basic_info(bundle_dir):
    """Collect Probe Basic specific information"""
    print("Collecting Probe Basic information...")
    pb_file = bundle_dir / "probe_basic_info.txt"
    
    with open(pb_file, 'w') as f:
        f.write("PROBE BASIC INFORMATION:\n")
        f.write("=" * 30 + "\n\n")
        
        # Python path and modules
        f.write("Python Path:\n")
        for path in sys.path:
            f.write(f"  {path}\n")
        f.write("\n")
        
        # Try to find Probe Basic installation
        try:
            import probe_basic
            f.write(f"Probe Basic module found: {probe_basic.__file__}\n")
            if hasattr(probe_basic, '__version__'):
                f.write(f"Version: {probe_basic.__version__}\n")
        except ImportError:
            f.write("Probe Basic module not found in Python path\n")
        
        f.write("\n")
        
        # Environment variables
        f.write("Relevant Environment Variables:\n")
        env_vars = [
            'INI_FILE_NAME', 'LINUXCNC_HOME', 'EMC2_HOME', 'PYTHONPATH',
            'QT_PLUGIN_PATH', 'DISPLAY', 'USER', 'HOME'
        ]
        for var in env_vars:
            value = os.getenv(var, 'Not set')
            f.write(f"  {var}: {value}\n")

def create_bundle(output_path):
    """Create support bundle"""
    print(f"Creating support bundle: {output_path}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        bundle_dir = Path(temp_dir) / "probe_basic_support"
        bundle_dir.mkdir()
        
        # Collect all information
        collect_system_info(bundle_dir)
        collect_linuxcnc_config(bundle_dir)
        collect_hal_info(bundle_dir)
        collect_logs(bundle_dir)
        collect_probe_basic_info(bundle_dir)
        
        # Create ZIP archive
        print("Creating ZIP archive...")
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in bundle_dir.rglob('*'):
                if file_path.is_file():
                    arc_path = file_path.relative_to(bundle_dir)
                    zipf.write(file_path, arc_path)
                    
        print(f"Support bundle created: {output_path}")
        
        # Show bundle contents
        with zipfile.ZipFile(output_path, 'r') as zipf:
            file_count = len(zipf.filelist)
            total_size = sum(info.file_size for info in zipf.filelist)
            print(f"Bundle contains {file_count} files, {total_size:,} bytes uncompressed")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Generate Probe Basic support bundle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Create bundle with timestamp
  %(prog)s -o my_support.zip        # Specify output file
  %(prog)s --verbose                # Show detailed output
        """
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output ZIP file path (default: probe_basic_support_TIMESTAMP.zip)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show verbose output'
    )
    
    args = parser.parse_args()
    
    # Set output path
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"probe_basic_support_{timestamp}.zip"
    
    # Ensure .zip extension
    if not output_path.endswith('.zip'):
        output_path += '.zip'
    
    try:
        start_time = time.time()
        create_bundle(output_path)
        elapsed = time.time() - start_time
        
        print(f"\nSuccess! Support bundle created in {elapsed:.1f} seconds")
        print(f"File: {os.path.abspath(output_path)}")
        print(f"Size: {os.path.getsize(output_path):,} bytes")
        
        print("\nThis support bundle can be sent to technical support for assistance.")
        print("It contains system information, configuration files, and recent logs.")
        
    except Exception as e:
        print(f"Error creating support bundle: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())