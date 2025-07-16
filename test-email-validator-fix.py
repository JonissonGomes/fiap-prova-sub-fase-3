#!/usr/bin/env python3
"""
Script para testar se o email-validator está funcionando corretamente
em todos os serviços que usam EmailStr.
"""

import sys
import traceback

def test_email_validator():
    """Testa se o email-validator está instalado e funcionando"""
    try:
        import email_validator
        print(f"✅ email-validator instalado - versão: {email_validator.__version__}")
        return True
    except ImportError as e:
        print(f"❌ email-validator não está instalado: {e}")
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
        
        # Testa com um email inválido
        try:
            invalid_data = {"email": "invalid-email"}
            TestModel(**invalid_data)
            print("❌ Validação de email inválido deveria falhar")
            return False
        except Exception:
            print("✅ Validação de email inválido funcionando corretamente")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar Pydantic EmailStr: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Erro ao testar Pydantic EmailStr: {e}")
        traceback.print_exc()
        return False

def test_auth_service_models():
    """Testa os modelos do auth-service"""
    try:
        sys.path.insert(0, 'auth-service')
        from app.domain.user import UserBase, UserCreate, LoginRequest
        
        # Testa UserBase
        user_data = {
            "email": "test@example.com",
            "name": "Test User"
        }
        user = UserBase(**user_data)
        print(f"✅ UserBase funcionando: {user.email}")
        
        # Testa UserCreate
        create_data = {
            "email": "create@example.com",
            "name": "Create User",
            "password": "password123"
        }
        user_create = UserCreate(**create_data)
        print(f"✅ UserCreate funcionando: {user_create.email}")
        
        # Testa LoginRequest
        login_data = {
            "email": "login@example.com",
            "password": "password123"
        }
        login_request = LoginRequest(**login_data)
        print(f"✅ LoginRequest funcionando: {login_request.email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar modelos do auth-service: {e}")
        traceback.print_exc()
        return False

def test_customer_service_models():
    """Testa os modelos do customer-service"""
    try:
        sys.path.insert(0, 'customer-service')
        from app.domain.customer import CustomerBase, CustomerCreate, CustomerUpdate
        
        # Testa CustomerBase
        customer_data = {
            "email": "customer@example.com",
            "name": "Test Customer",
            "phone": "11999999999",
            "cpf": "12345678901"
        }
        customer = CustomerBase(**customer_data)
        print(f"✅ CustomerBase funcionando: {customer.email}")
        
        # Testa CustomerCreate
        customer_create = CustomerCreate(**customer_data)
        print(f"✅ CustomerCreate funcionando: {customer_create.email}")
        
        # Testa CustomerUpdate
        update_data = {
            "email": "updated@example.com",
            "name": "Updated Customer"
        }
        customer_update = CustomerUpdate(**update_data)
        print(f"✅ CustomerUpdate funcionando: {customer_update.email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar modelos do customer-service: {e}")
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    print("🔍 Testando email-validator em todos os serviços...\n")
    
    # Testa dependências básicas
    print("1. Testando dependências básicas:")
    email_validator_ok = test_email_validator()
    pydantic_ok = test_pydantic_email()
    
    if not email_validator_ok or not pydantic_ok:
        print("\n❌ Dependências básicas falharam. Instale com:")
        print("pip install email-validator==2.1.0")
        print("pip install 'pydantic[email]==2.5.0'")
        return False
    
    print("\n2. Testando modelos do auth-service:")
    auth_ok = test_auth_service_models()
    
    print("\n3. Testando modelos do customer-service:")
    customer_ok = test_customer_service_models()
    
    # Resultado final
    print("\n" + "="*50)
    if email_validator_ok and pydantic_ok and auth_ok and customer_ok:
        print("✅ Todos os testes passaram! email-validator está funcionando corretamente.")
        return True
    else:
        print("❌ Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 