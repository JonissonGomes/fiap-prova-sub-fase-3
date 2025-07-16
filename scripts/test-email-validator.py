#!/usr/bin/env python3

"""
Script para testar se o email-validator está instalado corretamente
"""

import sys

def test_email_validator():
    """Testa se o email-validator está instalado e funcionando"""
    try:
        import email_validator
        print("✅ email-validator importado com sucesso!")
        print(f"   Versão: {email_validator.__version__}")
        
        # Testa validação básica
        from email_validator import validate_email, EmailNotValidError
        
        # Testa com um email válido
        email = "test@example.com"
        validated = validate_email(email)
        print(f"✅ Validação de email funcionando: {validated.email}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar email-validator: {e}")
        print("💡 Execute: pip install email-validator")
        return False
        
    except Exception as e:
        print(f"❌ Erro ao testar email-validator: {e}")
        return False

def test_pydantic_email():
    """Testa se o Pydantic consegue usar email-validator"""
    try:
        from pydantic import BaseModel, EmailStr
        
        class TestModel(BaseModel):
            email: EmailStr
        
        # Testa com um email válido
        test_data = {"email": "test@example.com"}
        model = TestModel(**test_data)
        print(f"✅ Pydantic EmailStr funcionando: {model.email}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar Pydantic EmailStr: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Erro ao testar Pydantic EmailStr: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testando email-validator...")
    print("=" * 50)
    
    success = True
    
    # Testa email-validator
    if not test_email_validator():
        success = False
    
    print()
    
    # Testa Pydantic EmailStr
    if not test_pydantic_email():
        success = False
    
    print()
    print("=" * 50)
    
    if success:
        print("✅ Todos os testes passaram!")
        sys.exit(0)
    else:
        print("❌ Alguns testes falharam!")
        sys.exit(1) 