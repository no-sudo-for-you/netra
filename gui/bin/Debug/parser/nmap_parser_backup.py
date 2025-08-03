#!/usr/bin/env python3
"""
RedBlue Labs Nmap Parser - Clean Version Without Risk Assessment
"""

import re
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import argparse

class SimpleNmapParser:
    """Simple nmap parser for GUI integration"""
    
    def __init__(self):
        self.assets = []
    
    def process_scan_files(self, file_paths: List[str]) -> Dict:
        """Process multiple scan files and return network breakdown"""
        print(f"Processing {len(file_paths)} files...")
        
        all_assets = {}  # Use dict to merge duplicate IPs
        
        for file_path in file_paths:
            print(f"Processing: {file_path}")
            file_assets = self._parse_single_file(file_path)
            
            # Merge assets (same IP from different scans)
            for asset in file_assets:
                ip = asset['ip_address']
                if ip in all_assets:
                    # Merge port data
                    existing_ports = {f"{p['port']}/{p['protocol']}" for p in all_assets[ip]['ports']}
                    for port in asset['ports']:
                        port_key = f"{port['port']}/{port['protocol']}"
                        if port_key not in existing_ports:
                            all_assets[ip]['ports'].append(port)
                    
                    # Update other fields if better info available
                    if asset.get('hostname') and not all_assets[ip].get('hostname'):
                        all_assets[ip]['hostname'] = asset['hostname']
                    if asset.get('os_match') and not all_assets[ip].get('os_match'):
                        all_assets[ip]['os_match'] = asset['os_match']
                        all_assets[ip]['os_accuracy'] = asset.get('os_accuracy', 0)
                    if asset.get('mac_address') and not all_assets[ip].get('mac_address'):
                        all_assets[ip]['mac_address'] = asset['mac_address']
                        all_assets[ip]['vendor'] = asset.get('vendor', '')
                else:
                    all_assets[ip] = asset
        
        self.assets = list(all_assets.values())
        
        # Add basic stats (NO RISK CALCULATION)
        for asset in self.assets:
            asset['open_port_count'] = len([p for p in asset['ports'] if p['state'] == 'open'])
            asset['open_services'] = ', '.join(set([p['service'] for p in asset['ports'] if p['state'] == 'open' and p['service']]))
        
        return self._generate_breakdown()
    
    def _parse_single_file(self, file_path: str) -> List[Dict]:
        """Parse a single nmap file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
        
        # Split by "Nmap scan report for" to get individual hosts
        host_sections = re.split(r'Nmap scan report for ', content)
        
        assets = []
        for section in host_sections[1:]:  # Skip first section (header)
            if section.strip():
                asset = self._parse_host_section(section)
                if asset:
                    assets.append(asset)
        
        return assets
    
    def _parse_host_section(self, section: str) -> Optional[Dict]:
        """Parse a single host section"""
        lines = section.strip().split('\n')
        if not lines:
            return None
        
        # Extract IP from first line
        first_line = lines[0]
        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', first_line)
        if not ip_match:
            return None
        
        asset = {
            'ip_address': ip_match.group(1),
            'hostname': '',
            'mac_address': '',
            'vendor': '',
            'os_match': '',
            'os_accuracy': 0,
            'status': 'unknown',
            'ports': []
        }
        
        # Extract hostname if in parentheses
        hostname_match = re.search(r'\(([^)]+)\)', first_line)
        if hostname_match:
            asset['hostname'] = hostname_match.group(1)
        
        # Process all lines
        for line in lines:
            line = line.strip()
            
            # Host status
            if 'Host is up' in line:
                asset['status'] = 'up'
            elif 'Host is down' in line:
                asset['status'] = 'down'
                return asset
            
            # MAC Address
            if line.startswith('MAC Address:'):
                mac_match = re.search(r'MAC Address: ([A-Fa-f0-9:]{17})', line)
                if mac_match:
                    asset['mac_address'] = mac_match.group(1)
                    vendor_match = re.search(r'\((.+)\)', line)
                    if vendor_match:
                        asset['vendor'] = vendor_match.group(1)
            
            # OS Detection
            if 'OS details:' in line:
                os_match = re.search(r'OS details: (.+)', line)
                if os_match:
                    asset['os_match'] = os_match.group(1)
                    asset['os_accuracy'] = 95
            elif 'Running:' in line and not asset['os_match']:
                os_match = re.search(r'Running: (.+)', line)
                if os_match:
                    asset['os_match'] = os_match.group(1)
                    asset['os_accuracy'] = 80
            
            # Ports
            port_match = re.match(r'(\d+)/(tcp|udp)\s+(open|closed|filtered)(?:\s+(.+))?', line)
            if port_match:
                port_num = int(port_match.group(1))
                protocol = port_match.group(2)
                state = port_match.group(3)
                service_info = port_match.group(4) or ''
                
                service_parts = service_info.split() if service_info else []
                service_name = service_parts[0] if service_parts else ''
                
                # Extract version info
                product = ''
                version = ''
                if service_info:
                    # Common patterns
                    ssh_match = re.search(r'ssh\s+OpenSSH\s+([\d.p]+)', service_info)
                    if ssh_match:
                        product = 'OpenSSH'
                        version = ssh_match.group(1)
                    
                    http_match = re.search(r'http\s+Apache httpd\s+([\d.]+)', service_info)
                    if http_match:
                        product = 'Apache httpd'
                        version = http_match.group(1)
                    
                    if not version:
                        version_match = re.search(r'(\d+\.\d+[\d.]*)', service_info)
                        if version_match:
                            version = version_match.group(1)
                
                asset['ports'].append({
                    'port': port_num,
                    'protocol': protocol,
                    'state': state,
                    'service': service_name,
                    'product': product,
                    'version': version,
                    'extra_info': service_info
                })
        
        return asset if asset['status'] == 'up' or asset['ports'] else None
    
    def _generate_breakdown(self) -> Dict:
        """Generate network breakdown"""
        if not self.assets:
            return {"error": "No assets found"}
        
        # Calculate summary stats
        active_devices = len([a for a in self.assets if a['status'] == 'up'])
        total_open_ports = sum(a['open_port_count'] for a in self.assets)
        
        # Top services
        service_counts = {}
        for asset in self.assets:
            for port in asset['ports']:
                if port['state'] == 'open' and port['service']:
                    service_counts[port['service']] = service_counts.get(port['service'], 0) + 1
        
        top_services = [{'service': k, 'count': v} for k, v in sorted(service_counts.items(), key=lambda x: x[1], reverse=True)][:10]
        
        # Vendor breakdown
        vendor_counts = {}
        devices_without_vendor = 0
        
        for asset in self.assets:
            vendor = asset['vendor']
            if vendor and vendor.strip():
                vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1
            else:
                # Count devices with no vendor info
                devices_without_vendor += 1
                vendor_counts['No Vendor Info'] = vendor_counts.get('No Vendor Info', 0) + 1
        
        vendors_found = [{'vendor': k, 'count': v} for k, v in sorted(vendor_counts.items(), key=lambda x: x[1], reverse=True)]
        
        # OS breakdown  
        os_counts = {}
        for asset in self.assets:
            os_name = asset['os_match'] or 'Unknown'
            if 'linux' in os_name.lower():
                os_name = 'Linux'
            elif 'windows' in os_name.lower():
                os_name = 'Windows'
            elif 'android' in os_name.lower():
                os_name = 'Android'
            
            os_counts[os_name] = os_counts.get(os_name, 0) + 1
        
        os_distribution = [{'os': k, 'count': v} for k, v in sorted(os_counts.items(), key=lambda x: x[1], reverse=True)]
        
        return {
            'summary': {
                'total_devices': len(self.assets),
                'active_devices': active_devices,
                'total_open_ports': total_open_ports
            },
            'assets': self.assets,
            'top_services': top_services,
            'vendors_found': vendors_found,
            'os_distribution': os_distribution
        }
    
    def export_for_llm(self, output_file: str = None) -> str:
        """Export data for LLM analysis"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"network_scan_{timestamp}.json"
        
        export_data = {
            'scan_metadata': {
                'export_time': datetime.now().isoformat(),
                'total_assets': len(self.assets)
            },
            'network_summary': {
                'total_devices': len(self.assets),
                'active_devices': len([a for a in self.assets if a['status'] == 'up']),
                'total_open_ports': sum(a['open_port_count'] for a in self.assets)
            },
            'assets': self.assets
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"Data exported for LLM: {output_file}")
        return output_file

def print_network_breakdown(network_data):
    """Print network breakdown"""
    print(f"\n{'='*80}")
    print("NETWORK SCAN BREAKDOWN")
    print(f"{'='*80}")
    
    summary = network_data['summary']
    print(f"Total Devices: {summary['total_devices']}")
    print(f"Active Devices: {summary['active_devices']}")
    print(f"Total Open Ports: {summary['total_open_ports']}")
    
    print(f"\nTop Services:")
    for service in network_data['top_services'][:5]:
        print(f"  {service['service']}: {service['count']} devices")
    
    print(f"\nVendors Found:")
    total_vendor_devices = 0
    for vendor in network_data['vendors_found']:
        print(f"  {vendor['vendor']}: {vendor['count']} devices")
        total_vendor_devices += vendor['count']
    
    # Show the math - this should show missing devices
    devices_without_vendor = summary['total_devices'] - total_vendor_devices
    if devices_without_vendor > 0:
        print(f"  [Missing vendor info for {devices_without_vendor} devices]")
    
    print(f"\nTEST: This is a test message to see if changes work")
    
    print(f"\nAssets:")
    print(f"{'IP':<15} {'Hostname':<20} {'Vendor':<20} {'Ports':<8} {'Services'}")
    print("-" * 90)
    
    for asset in network_data['assets']:
        ip = asset['ip_address']
        hostname = (asset['hostname'] or 'N/A')[:19]
        vendor = (asset.get('vendor', '') or 'No Vendor')[:19]
        ports = str(asset['open_port_count'])
        services = (asset['open_services'] or 'None')[:25]
        
        print(f"{ip:<15} {hostname:<20} {vendor:<20} {ports:<8} {services}")
    
    print(f"\nTEST: End of asset list")

def main():
    parser = argparse.ArgumentParser(description='RedBlue Labs Nmap Parser')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Parse command for processing files
    parse_parser = subparsers.add_parser('parse', help='Parse scan files and show breakdown')
    parse_parser.add_argument('files', nargs='+', help='Scan files to process')
    parse_parser.add_argument('--export', help='Export to JSON file for LLM')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'parse':
        # Process files
        scanner = SimpleNmapParser()
        network_data = scanner.process_scan_files(args.files)
        
        if 'error' in network_data:
            print(f"Error: {network_data['error']}")
            return
        
        # Show breakdown
        print_network_breakdown(network_data)
        
        # Export if requested
        if args.export:
            scanner.export_for_llm(args.export)

if __name__ == "__main__":
    main()