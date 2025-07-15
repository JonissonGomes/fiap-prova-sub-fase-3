from abc import ABC, abstractmethod
from typing import List, Optional
from ..domain.sale import Sale
from ..schemas.sale_schema import SaleCreate, SaleUpdate, SaleResponse

class SaleRepository(ABC):
    """Interface para o repositório de vendas."""
    
    @abstractmethod
    async def save(self, sale: SaleCreate) -> SaleResponse:
        """Salva uma nova venda."""
        pass

    @abstractmethod
    async def find_by_id(self, sale_id: str) -> Optional[SaleResponse]:
        """Busca uma venda pelo ID."""
        pass

    @abstractmethod
    async def find_by_vehicle_id(self, vehicle_id: str) -> Optional[SaleResponse]:
        """Busca uma venda pelo ID do veículo."""
        pass

    @abstractmethod
    async def find_by_payment_code(self, payment_code: str) -> Optional[SaleResponse]:
        """Busca uma venda pelo código de pagamento."""
        pass

    @abstractmethod
    async def find_all(self) -> List[SaleResponse]:
        """Lista todas as vendas."""
        pass

    @abstractmethod
    async def find_by_status(self, status: str) -> List[SaleResponse]:
        """Lista vendas por status."""
        pass

    @abstractmethod
    async def update(self, sale_id: str, sale_update: SaleUpdate) -> SaleResponse:
        """Atualiza uma venda existente."""
        pass

    @abstractmethod
    async def delete(self, sale_id: str) -> None:
        """Remove uma venda."""
        pass 