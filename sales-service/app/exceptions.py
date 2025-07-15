from fastapi import HTTPException, status

class SaleNotFoundError(HTTPException):
    """Exceção lançada quando uma venda não é encontrada."""
    def __init__(self, sale_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venda com ID {sale_id} não encontrada"
        ) 

class InvalidSaleDataError(Exception):
    def __init__(self, message="Dados inválidos para a venda"):
        super().__init__(message)

class DuplicatePaymentCodeError(Exception):
    def __init__(self, message="Código de pagamento duplicado"):
        super().__init__(message)

class InvalidPaymentStatusError(Exception):
    def __init__(self, message="Status de pagamento inválido"):
        super().__init__(message)