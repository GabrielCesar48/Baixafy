"""
Sistema de Licenciamento Seguro para BaixaFy Desktop
Validação de chaves criptografadas com proteção anti-reverse engineering
"""

import os
import json
import base64
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from pathlib import Path
import platform
import subprocess
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecureLicenseManager:
    """
    Gerenciador seguro de licenças com criptografia avançada
    """
    
    # Chave mestra (ALTERE ESTA CHAVE PARA SEU PROJETO!)
    _MASTER_KEY = b"BaixaFy2024SecureKeyMaster!@#$%"
    
    # Chaves válidas criptografadas (você adiciona aqui as chaves que gera)
    _ENCRYPTED_KEYS_DB = """
    gAAAAABjKqB8X9vQ2K5L7M8N9O0P1Q2R3S4T5U6V7W8X9Y0Z1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q8R9S0T
    gAAAAABjKqB9Y8wR3L6M9N0O1P2Q3R4S5T6U7V8W9X0Y1Z2A3B4C5D6E7F8G9H0I1J2K3L4M5N6O7P8Q9R0S1T2U
    gAAAAABjKqC0Z9xS4M7N0O1P2Q3R4S5T6U7V8W9X0Y1Z2A3B4C5D6E7F8G9H0I1J2K3L4M5N6O7P8Q9R0S1T2U3V
    BQC4-P8PJ-NEZ2-HD9B-HZH5
    """
    
    def __init__(self):
        self.hardware_id = self._generate_hardware_id()
        self.cipher_suite = self._get_cipher_suite()
        self.valid_keys = self._decrypt_keys_db()
        
    def _generate_hardware_id(self):
        """
        Gera ID único e consistente baseado no hardware
        (Mesmo ID sempre na mesma máquina)
        """
        try:
            # Informações do sistema
            system_info = []
            
            # Nome da máquina
            system_info.append(platform.node())
            
            # Processador
            system_info.append(platform.processor())
            
            # Sistema operacional
            system_info.append(f"{platform.system()}-{platform.release()}")
            
            # MAC Address (mais estável)
            try:
                import uuid
                mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                               for elements in range(0,2*6,2)][::-1])
                system_info.append(mac)
            except:
                system_info.append("no-mac")
            
            # Volume serial do Windows (se disponível)
            if platform.system() == "Windows":
                try:
                    result = subprocess.run(['vol', 'C:'], capture_output=True, text=True)
                    if result.returncode == 0 and 'Serial Number' in result.stdout:
                        serial = result.stdout.split('Serial Number is ')[1].strip()
                        system_info.append(serial)
                except:
                    pass
            
            # Gerar hash consistente
            combined = '|'.join(system_info)
            hardware_id = hashlib.sha256(combined.encode()).hexdigest()[:16]
            
            return hardware_id.upper()
            
        except Exception:
            # Fallback para ID genérico (menos seguro)
            fallback = f"{platform.system()}-{platform.node()}"
            return hashlib.md5(fallback.encode()).hexdigest()[:16].upper()
    
    def _get_cipher_suite(self):
        """
        Cria suite de criptografia baseada na chave mestra
        """
        # Derivar chave da chave mestra + hardware ID
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._MASTER_KEY[:16],  # Usar parte da chave mestra como salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self._MASTER_KEY + self.hardware_id.encode()))
        return Fernet(key)
    
    def _decrypt_keys_db(self):
        """
        Descriptografa base de chaves válidas
        """
        try:
            valid_keys = []
            
            for encrypted_key in self._ENCRYPTED_KEYS_DB.strip().split('\n'):
                encrypted_key = encrypted_key.strip()
                if encrypted_key:
                    try:
                        # Descriptografar chave
                        decrypted = self.cipher_suite.decrypt(encrypted_key.encode())
                        key_data = json.loads(decrypted.decode())
                        valid_keys.append(key_data)
                    except:
                        continue  # Ignorar chaves inválidas
            
            return valid_keys
            
        except Exception:
            # Se falhar, retornar lista vazia (modo demo apenas)
            return []
    
    def validate_license_key(self, license_key):
        """
        Valida chave de licença fornecida pelo usuário
        
        Args:
            license_key (str): Chave de 20 dígitos fornecida pelo usuário
            
        Returns:
            dict: Resultado da validação com informações da licença
        """
        # Limpar e formatar chave
        clean_key = license_key.replace('-', '').replace(' ', '').upper()
        
        # Validar formato
        if len(clean_key) != 20 or not clean_key.isalnum():
            return {
                'valid': False,
                'error': 'Formato de chave inválido. Use 20 dígitos alfanuméricos.'
            }
        
        # Procurar chave na base de dados
        for key_data in self.valid_keys:
            if key_data['key'] == clean_key:
                # Verificar se não expirou
                if 'expiry' in key_data:
                    expiry_date = datetime.fromisoformat(key_data['expiry'])
                    if datetime.now() > expiry_date:
                        return {
                            'valid': False,
                            'error': 'Esta chave de licença expirou.'
                        }
                
                # Verificar limite de ativações (se especificado)
                if 'max_activations' in key_data:
                    # Aqui você implementaria controle de ativações
                    # Por simplicidade, vamos assumir que está OK
                    pass
                
                # Chave válida!
                return {
                    'valid': True,
                    'key': clean_key,
                    'days': key_data.get('days', 30),
                    'type': key_data.get('type', 'premium'),
                    'features': key_data.get('features', ['unlimited_downloads']),
                    'hardware_id': self.hardware_id
                }
        
        # Chave não encontrada
        return {
            'valid': False,
            'error': 'Chave de licença inválida ou não encontrada.'
        }
    
    def create_license_file(self, validation_result):
        """
        Cria arquivo de licença local criptografado
        """
        if not validation_result['valid']:
            return False
        
        try:
            # Dados da licença
            license_data = {
                'key': validation_result['key'],
                'activation_date': datetime.now().isoformat(),
                'expiry_date': (datetime.now() + timedelta(days=validation_result['days'])).isoformat(),
                'hardware_id': self.hardware_id,
                'type': validation_result['type'],
                'features': validation_result['features'],
                'checksum': self._generate_license_checksum(validation_result)
            }
            
            # Criptografar dados
            encrypted_data = self.cipher_suite.encrypt(json.dumps(license_data).encode())
            
            # Salvar arquivo de licença
            license_file = Path.home() / '.baixafy' / 'license.dat'
            license_file.parent.mkdir(exist_ok=True)
            
            with open(license_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Criar arquivo secundário (backup)
            backup_file = license_file.parent / 'lic.bak'
            with open(backup_file, 'wb') as f:
                f.write(encrypted_data)
            
            return True
            
        except Exception as e:
            return False
    
    def check_existing_license(self):
        """
        Verifica se existe licença válida no sistema
        
        Returns:
            dict: Status da licença atual
        """
        license_file = Path.home() / '.baixafy' / 'license.dat'
        backup_file = Path.home() / '.baixafy' / 'lic.bak'
        
        # Tentar arquivo principal primeiro
        for file_path in [license_file, backup_file]:
            if file_path.exists():
                try:
                    with open(file_path, 'rb') as f:
                        encrypted_data = f.read()
                    
                    # Descriptografar
                    decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                    license_data = json.loads(decrypted_data.decode())
                    
                    # Validar hardware ID
                    if license_data.get('hardware_id') != self.hardware_id:
                        continue  # Licença de outra máquina
                    
                    # Verificar expiração
                    expiry_date = datetime.fromisoformat(license_data['expiry_date'])
                    if datetime.now() > expiry_date:
                        return {
                            'status': 'expired',
                            'message': 'Licença expirada',
                            'expiry_date': expiry_date
                        }
                    
                    # Validar checksum
                    expected_checksum = self._generate_license_checksum({
                        'key': license_data['key'],
                        'type': license_data['type'],
                        'features': license_data['features']
                    })
                    
                    if license_data.get('checksum') != expected_checksum:
                        continue  # Licença corrompida
                    
                    # Licença válida
                    days_remaining = (expiry_date - datetime.now()).days
                    
                    return {
                        'status': 'active',
                        'message': 'Licença ativa',
                        'days_remaining': max(0, days_remaining),
                        'expiry_date': expiry_date,
                        'type': license_data['type'],
                        'features': license_data['features']
                    }
                    
                except Exception:
                    continue  # Tentar próximo arquivo
        
        # Nenhuma licença válida encontrada
        return {
            'status': 'trial',
            'message': 'Modo trial (10 downloads)',
            'downloads_remaining': 10
        }
    
    def _generate_license_checksum(self, validation_result):
        """
        Gera checksum para validar integridade da licença
        """
        data_to_hash = (
            validation_result['key'] + 
            self.hardware_id + 
            validation_result.get('type', 'premium') +
            str(validation_result.get('features', []))
        )
        
        return hmac.new(
            self._MASTER_KEY,
            data_to_hash.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
    
    def reset_trial(self):
        """
        Reseta trial (apenas para debug - REMOVER EM PRODUÇÃO)
        """
        license_file = Path.home() / '.baixafy' / 'license.dat'
        backup_file = Path.home() / '.baixafy' / 'lic.bak'
        
        for file_path in [license_file, backup_file]:
            if file_path.exists():
                file_path.unlink()
        
        return True


# Instância global do gerenciador
license_manager = SecureLicenseManager()


def get_license_status():
    """
    Função helper para obter status da licença
    """
    return license_manager.check_existing_license()


def validate_license(license_key):
    """
    Função helper para validar licença
    """
    result = license_manager.validate_license_key(license_key)
    
    if result['valid']:
        # Criar arquivo de licença
        if license_manager.create_license_file(result):
            return result
        else:
            return {
                'valid': False,
                'error': 'Erro ao ativar licença. Tente novamente.'
            }
    
    return result