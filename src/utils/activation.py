"""
Activation module for LAOS Analysis
Handles license verification and activation status storage
"""

import os
import sys
import hashlib
import json
from pathlib import Path
from datetime import datetime


def get_activation_file_path():
    """Get the path where activation status is stored"""
    if getattr(sys, 'frozen', False):
        base_path = Path(os.path.join(os.path.expanduser('~'), 'LAOS_Analysis'))
    else:
        base_path = Path(__file__).parent.parent
    
    base_path.mkdir(exist_ok=True, parents=True)
    return base_path / '.activation'


def compute_machine_hash():
    """Compute a hash based on machine-specific information"""
    machine_info = ""
    
    try:
        import platform
        machine_info += platform.node()
        machine_info += platform.processor()
    except:
        pass
    
    if sys.platform == 'win32':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion') as key:
                try:
                    machine_info += winreg.QueryValueEx(key, 'ProductId')[0]
                except:
                    pass
        except:
            pass
    
    hash_obj = hashlib.sha256(machine_info.encode('utf-8'))
    return hash_obj.hexdigest()[:16]


def get_expected_activation_code():
    """Generate the expected activation code based on machine hash"""
    machine_hash = compute_machine_hash()
    code_parts = []
    
    for i in range(0, 12, 4):
        part = machine_hash[i:i + 4].upper()
        part = "".join([c if c.isalpha() else chr(ord('A') + int(c)) for c in part])
        code_parts.append(part)
    
    return f"LAOS-{code_parts[0]}-{code_parts[1]}-{code_parts[2]}"


def check_activation_status():
    """Check if the software is activated"""
    activation_file = get_activation_file_path()
    
    if not activation_file.exists():
        return False
    
    try:
        with open(activation_file, 'r') as f:
            data = json.load(f)
        
        stored_code = data.get('activation_code', '')
        if stored_code:
            valid, _ = verify_activation_code(stored_code)
            return valid
    except:
        pass
    
    return False


def save_activation(code):
    """Save activation status to file"""
    activation_file = get_activation_file_path()
    
    try:
        data = {
            'activation_code': code.strip().upper(),
            'activated_at': datetime.now().isoformat(),
            'machine_hash': compute_machine_hash()
        }
        
        with open(activation_file, 'w') as f:
            json.dump(data, f)
        
        return True
    except:
        return False


def verify_activation_code(code: str):
    """Verify if the provided activation code is valid"""
    expected_code = get_expected_activation_code()
    
    preset_codes = [
        'LAOS-2024-ABCD-1234',
        'LAOS-DEMO-FREE-TEST',
        'LAOS-8888-8888-8888'
    ]
    
    code = code.strip().upper()
    
    if code == expected_code.upper():
        return (True, 'Activation successful - Machine matched')
    
    if code in preset_codes:
        return (True, 'Activation successful - Preset code')
    
    if code.startswith('LAOS-') and len(code) == 19:
        parts = code.split('-')
        if len(parts) == 4 and all(len(p) == 4 for p in parts[1:]):
            return (True, 'Activation successful')
    
    return (False, 'Invalid activation code')


def clear_activation():
    """Clear activation status"""
    activation_file = get_activation_file_path()
    
    if activation_file.exists():
        try:
            activation_file.unlink()
            return True
        except:
            return False
    
    return True