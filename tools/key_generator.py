"""
Gerador SIMPLES de Chaves para BaixaFy Desktop
USO EXCLUSIVO DO DESENVOLVEDOR
"""

import secrets
import string

def generate_license_key():
    """Gera chave de 20 dígitos aleatória"""
    # Usar apenas letras maiúsculas e números (sem confusos: 0, O, 1, I)
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    key = ''.join(secrets.choice(chars) for _ in range(20))
    formatted_key = '-'.join(key[i:i+4] for i in range(0, 20, 4))
    return key, formatted_key

def generate_batch_keys(count=10):
    """Gera lote de chaves"""
    keys = []
    for i in range(count):
        key, formatted_key = generate_license_key()
        keys.append({'key': key, 'formatted': formatted_key})
    return keys

def main():
    print("🔑 Gerador de Chaves BaixaFy Desktop")
    print("="*50)
    
    while True:
        print("\n1. Gerar chave única")
        print("2. Gerar 10 chaves")
        print("3. Gerar 50 chaves")
        print("4. Sair")
        
        choice = input("\nEscolha (1-4): ").strip()
        
        if choice == '1':
            key, formatted = generate_license_key()
            print(f"\n✅ Chave gerada:")
            print(f"   Para cliente: {formatted}")
            print(f"   Para código: '{key}',")
            
        elif choice == '2':
            keys = generate_batch_keys(10)
            print(f"\n✅ 10 chaves geradas:")
            print("\nPara enviar aos clientes:")
            for i, k in enumerate(keys, 1):
                print(f"{i:2d}. {k['formatted']}")
            
            print(f"\nPara adicionar no código (license_manager.py):")
            print("_VALID_KEYS = [")
            for k in keys:
                print(f"    '{k['key']}',")
            print("]")
            
        elif choice == '3':
            keys = generate_batch_keys(50)
            
            # Salvar em arquivo
            with open('chaves_geradas.txt', 'w') as f:
                f.write("CHAVES PARA CLIENTES:\n")
                f.write("="*50 + "\n")
                for i, k in enumerate(keys, 1):
                    f.write(f"{i:2d}. {k['formatted']}\n")
                
                f.write(f"\nPARA CÓDIGO (license_manager.py):\n")
                f.write("="*50 + "\n")
                f.write("_VALID_KEYS = [\n")
                for k in keys:
                    f.write(f"    '{k['key']}',\n")
                f.write("]\n")
            
            print(f"✅ 50 chaves salvas em 'chaves_geradas.txt'")
            
        elif choice == '4':
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    main()