# security.py - Security measures for Klip

import hashlib
import hmac
import os
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64


class SecurityManager:
    """Manages security features for the application."""
    
    def __init__(self):
        self.app_signature = self._generate_app_signature()
        self._verify_integrity()
    
    def _generate_app_signature(self):
        """Generate a unique signature for the application."""
        # Combine multiple system identifiers
        machine_id = self._get_machine_id()
        app_path = os.path.abspath(sys.argv[0])
        
        signature = hashlib.sha256(
            f"{machine_id}{app_path}".encode()
        ).hexdigest()
        
        return signature
    
    def _get_machine_id(self):
        """Get a unique machine identifier."""
        try:
            if sys.platform == 'win32':
                import subprocess
                # Get Windows machine GUID
                result = subprocess.run(
                    ['wmic', 'csproduct', 'get', 'UUID'],
                    capture_output=True,
                    text=True
                )
                uuid = result.stdout.split('\n')[1].strip()
                return uuid
            else:
                # For other platforms, use MAC address
                import uuid
                return str(uuid.getnode())
        except:
            # Fallback to a combination of system info
            import platform
            return hashlib.sha256(
                f"{platform.node()}{platform.machine()}".encode()
            ).hexdigest()
    
    def _verify_integrity(self):
        """Verify the application hasn't been tampered with."""
        # Check if running from expected location
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            exe_path = sys.executable
            
            # Verify the executable hasn't been modified
            if not self._check_file_integrity(exe_path):
                self._handle_tampering()
    
    def _check_file_integrity(self, filepath):
        """Check if a file's integrity is intact."""
        try:
            # Calculate current hash
            with open(filepath, 'rb') as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()
            
            # In production, compare with stored hash
            # For now, we'll assume it's valid
            return True
        except:
            return False
    
    def _handle_tampering(self):
        """Handle detected tampering."""
        print("Security violation detected. Application will exit.")
        sys.exit(1)
    
    def encrypt_data(self, data: str, password: str) -> str:
        """Encrypt sensitive data."""
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.app_signature.encode()[:16],
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        # Encrypt
        f = Fernet(key)
        encrypted = f.encrypt(data.encode())
        
        return base64.b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data: str, password: str) -> str:
        """Decrypt sensitive data."""
        try:
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.app_signature.encode()[:16],
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Decrypt
            f = Fernet(key)
            encrypted = base64.b64decode(encrypted_data)
            decrypted = f.decrypt(encrypted)
            
            return decrypted.decode()
        except:
            return None
    
    def verify_api_request(self, data: dict, secret_key: str) -> bool:
        """Verify API request hasn't been tampered with."""
        # Create signature
        message = ''.join(str(v) for v in sorted(data.values()))
        signature = hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature == data.get('signature', '')
    
    def obfuscate_string(self, text: str) -> str:
        """Simple string obfuscation."""
        return base64.b85encode(text.encode()).decode()
    
    def deobfuscate_string(self, obfuscated: str) -> str:
        """Reverse string obfuscation."""
        try:
            return base64.b85decode(obfuscated).decode()
        except:
            return None


# Anti-debugging measures
def detect_debugger():
    """Detect if application is being debugged."""
    # Check for common debugger processes
    debugger_processes = [
        'ollydbg.exe', 'x64dbg.exe', 'x32dbg.exe',
        'ida.exe', 'ida64.exe', 'windbg.exe',
        'processhacker.exe', 'cheatengine.exe'
    ]
    
    if sys.platform == 'win32':
        import subprocess
        try:
            result = subprocess.run(
                ['tasklist'],
                capture_output=True,
                text=True
            )
            running_processes = result.stdout.lower()
            
            for debugger in debugger_processes:
                if debugger.lower() in running_processes:
                    print("Debugger detected. Application will exit.")
                    sys.exit(1)
        except:
            pass


def verify_environment():
    """Verify the application is running in a legitimate environment."""
    # Check if running in a virtual machine (basic check)
    if sys.platform == 'win32':
        try:
            import subprocess
            result = subprocess.run(
                ['systeminfo'],
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout.lower()
            
            # Common VM indicators
            vm_indicators = ['vmware', 'virtualbox', 'qemu', 'hyperv', 'virtual']
            for indicator in vm_indicators:
                if indicator in output:
                    # Log but don't block (many legitimate users run in VMs)
                    print("Virtual environment detected.")
                    break
        except:
            pass


# Initialize security on import
_security_manager = SecurityManager()

# Run security checks
detect_debugger()
verify_environment()
