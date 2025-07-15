from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.domain.sale import Sale
from app.ports.sale_repository import SaleRepository
from datetime import datetime

class MongoDBSaleRepository(SaleRepository):
    """Implementação do repositório de vendas usando MongoDB."""

    def __init__(self, client: AsyncIOMotorClient, db_name: str = "sales_db", collection_name: str = "sales"):
        self.client = client
        self.db = client[db_name]
        self.collection = self.db[collection_name]

    async def save(self, sale: Sale) -> Sale:
        """Salva uma venda."""
        try:
            sale_dict = sale.to_dict()
            result = await self.collection.insert_one(sale_dict)
            sale_dict["_id"] = result.inserted_id
            return Sale.from_dict(sale_dict)
        except Exception as e:
            raise ValueError(f"Erro ao salvar venda: {str(e)}")

    async def find_by_id(self, sale_id: str) -> Optional[Sale]:
        """Busca uma venda pelo ID."""
        try:
            sale = await self.collection.find_one({"_id": ObjectId(sale_id)})
            if sale:
                return Sale.from_dict(sale)
            return None
        except Exception as e:
            raise ValueError(f"Erro ao buscar venda: {str(e)}")

    async def find_by_vehicle_id(self, vehicle_id: str) -> Optional[Sale]:
        """Busca uma venda pelo ID do veículo."""
        try:
            sale = await self.collection.find_one({"vehicle_id": vehicle_id})
            if sale:
                return Sale.from_dict(sale)
            return None
        except Exception as e:
            raise ValueError(f"Erro ao buscar venda por ID do veículo: {str(e)}")

    async def find_by_payment_code(self, payment_code: str) -> Optional[Sale]:
        """Busca uma venda pelo código de pagamento."""
        try:
            sale = await self.collection.find_one({"payment_code": payment_code})
            if sale:
                return Sale.from_dict(sale)
            return None
        except Exception as e:
            raise ValueError(f"Erro ao buscar venda por código de pagamento: {str(e)}")

    async def find_all(self) -> List[Sale]:
        """Lista todas as vendas."""
        try:
            sales = []
            async for sale in self.collection.find():
                sales.append(Sale.from_dict(sale))
            return sales
        except Exception as e:
            raise ValueError(f"Erro ao listar vendas: {str(e)}")

    async def find_by_status(self, status: str) -> List[Sale]:
        """Lista vendas por status."""
        try:
            sales = []
            async for sale in self.collection.find({"payment_status": status}):
                sales.append(Sale.from_dict(sale))
            return sales
        except Exception as e:
            raise ValueError(f"Erro ao listar vendas por status: {str(e)}")

    async def update(self, sale: Sale) -> Optional[Sale]:
        """Atualiza uma venda."""
        try:
            sale_dict = sale.to_dict()
            result = await self.collection.update_one(
                {"_id": ObjectId(sale.id)},
                {"$set": sale_dict}
            )
            if result.modified_count > 0:
                return Sale.from_dict(sale_dict)
            return None
        except Exception as e:
            raise ValueError(f"Erro ao atualizar venda: {str(e)}")

    async def delete(self, sale_id: str) -> bool:
        """Remove uma venda."""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(sale_id)})
            return result.deleted_count > 0
        except Exception as e:
            raise ValueError(f"Erro ao remover venda: {str(e)}") 