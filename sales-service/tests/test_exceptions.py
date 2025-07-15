import pytest
from app.exceptions import (
    SaleNotFoundError,
    InvalidSaleDataError,
    DuplicatePaymentCodeError,
    InvalidPaymentStatusError
)

def test_sale_not_found_error():
    error = SaleNotFoundError("Venda não encontrada")
    assert str(error) == "Venda não encontrada"
    assert isinstance(error, Exception)

def test_invalid_sale_data_error():
    error = InvalidSaleDataError("Dados inválidos")
    assert str(error) == "Dados inválidos"
    assert isinstance(error, Exception)

def test_duplicate_payment_code_error():
    error = DuplicatePaymentCodeError("Código de pagamento duplicado")
    assert str(error) == "Código de pagamento duplicado"
    assert isinstance(error, Exception)

def test_invalid_payment_status_error():
    error = InvalidPaymentStatusError("Status de pagamento inválido")
    assert str(error) == "Status de pagamento inválido"
    assert isinstance(error, Exception)

def test_exception_hierarchy():
    assert issubclass(SaleNotFoundError, Exception)
    assert issubclass(InvalidSaleDataError, Exception)
    assert issubclass(DuplicatePaymentCodeError, Exception)
    assert issubclass(InvalidPaymentStatusError, Exception)

def test_exception_with_custom_message():
    custom_message = "Erro personalizado"
    error = SaleNotFoundError(custom_message)
    assert str(error) == custom_message

def test_exception_with_empty_message():
    error = SaleNotFoundError("")
    assert str(error) == ""

def test_exception_with_none_message():
    error = SaleNotFoundError(None)
    assert str(error) == "None"

def test_exception_with_non_string_message():
    error = SaleNotFoundError(123)
    assert str(error) == "123"