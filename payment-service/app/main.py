from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Payment Service",
    description="API para gerenciamento de pagamentos (Mock/Stub)",
    version="1.0.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums e Models
class PaymentStatus(str, Enum):
    PENDING = "PENDENTE"
    PAID = "PAGO"
    CANCELLED = "CANCELADO"

class PaymentCreate(BaseModel):
    payment_code: str
    amount: float

class Payment(BaseModel):
    id: str
    payment_code: str
    amount: float
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

# Armazenamento em memória (para demonstração)
payments_db: List[Payment] = []

# Health check
@app.get("/health")
async def health_check():
    """Verifica a saúde do serviço."""
    return {"status": "healthy", "service": "payment-service"}

# Endpoints de pagamentos
@app.get("/payments", response_model=List[Payment])
async def list_payments():
    """Lista todos os pagamentos."""
    return payments_db

@app.post("/payments", response_model=Payment)
async def create_payment(payment_data: PaymentCreate):
    """Cria um novo pagamento."""
    payment = Payment(
        id=str(uuid.uuid4()),
        payment_code=payment_data.payment_code,
        amount=payment_data.amount,
        status=PaymentStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    payments_db.append(payment)
    return payment

@app.get("/payments/{payment_id}", response_model=Payment)
async def get_payment(payment_id: str):
    """Obtém um pagamento por ID."""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return payment

@app.patch("/payments/{payment_id}/mark-as-pending", response_model=Payment)
async def mark_payment_as_pending(payment_id: str):
    """Marca pagamento como pendente."""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    payment.status = PaymentStatus.PENDING
    payment.updated_at = datetime.utcnow()
    return payment

@app.patch("/payments/{payment_id}/mark-as-paid", response_model=Payment)
async def mark_payment_as_paid(payment_id: str):
    """Marca pagamento como pago."""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    payment.status = PaymentStatus.PAID
    payment.updated_at = datetime.utcnow()
    return payment

@app.patch("/payments/{payment_id}/mark-as-cancelled", response_model=Payment)
async def mark_payment_as_cancelled(payment_id: str):
    """Marca pagamento como cancelado."""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    payment.status = PaymentStatus.CANCELLED
    payment.updated_at = datetime.utcnow()
    return payment

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004) 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Payment Service",
    description="API para gerenciamento de pagamentos (Mock/Stub)",
    version="1.0.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums e Models
class PaymentStatus(str, Enum):
    PENDING = "PENDENTE"
    PAID = "PAGO"
    CANCELLED = "CANCELADO"

class PaymentCreate(BaseModel):
    payment_code: str
    amount: float

class Payment(BaseModel):
    id: str
    payment_code: str
    amount: float
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

# Armazenamento em memória (para demonstração)
payments_db: List[Payment] = []

# Health check
@app.get("/health")
async def health_check():
    """Verifica a saúde do serviço."""
    return {"status": "healthy", "service": "payment-service"}

# Endpoints de pagamentos
@app.get("/payments", response_model=List[Payment])
async def list_payments():
    """Lista todos os pagamentos."""
    return payments_db

@app.post("/payments", response_model=Payment)
async def create_payment(payment_data: PaymentCreate):
    """Cria um novo pagamento."""
    payment = Payment(
        id=str(uuid.uuid4()),
        payment_code=payment_data.payment_code,
        amount=payment_data.amount,
        status=PaymentStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    payments_db.append(payment)
    return payment

@app.get("/payments/{payment_id}", response_model=Payment)
async def get_payment(payment_id: str):
    """Obtém um pagamento por ID."""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return payment

@app.patch("/payments/{payment_id}/mark-as-pending", response_model=Payment)
async def mark_payment_as_pending(payment_id: str):
    """Marca pagamento como pendente."""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    payment.status = PaymentStatus.PENDING
    payment.updated_at = datetime.utcnow()
    return payment

@app.patch("/payments/{payment_id}/mark-as-paid", response_model=Payment)
async def mark_payment_as_paid(payment_id: str):
    """Marca pagamento como pago."""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    payment.status = PaymentStatus.PAID
    payment.updated_at = datetime.utcnow()
    return payment

@app.patch("/payments/{payment_id}/mark-as-cancelled", response_model=Payment)
async def mark_payment_as_cancelled(payment_id: str):
    """Marca pagamento como cancelado."""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    payment.status = PaymentStatus.CANCELLED
    payment.updated_at = datetime.utcnow()
    return payment

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004) 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Payment Service",
    description="API para gerenciamento de pagamentos (Mock/Stub)",
    version="1.0.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums e Models
class PaymentStatus(str, Enum):
    PENDING = "PENDENTE"
    PAID = "PAGO"
    CANCELLED = "CANCELADO"

class PaymentCreate(BaseModel):
    payment_code: str
    amount: float

class Payment(BaseModel):
    id: str
    payment_code: str
    amount: float
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

# Armazenamento em memória (para demonstração)
payments_db: List[Payment] = []

# Health check
@app.get("/health")
async def health_check():
    """Verifica a saúde do serviço."""
    return {"status": "healthy", "service": "payment-service"}

# Endpoints de pagamentos
@app.get("/payments", response_model=List[Payment])
async def list_payments():
    """Lista todos os pagamentos."""
    return payments_db

@app.post("/payments", response_model=Payment)
async def create_payment(payment_data: PaymentCreate):
    """Cria um novo pagamento."""
    payment = Payment(
        id=str(uuid.uuid4()),
        payment_code=payment_data.payment_code,
        amount=payment_data.amount,
        status=PaymentStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    payments_db.append(payment)
    return payment

@app.get("/payments/{payment_id}", response_model=Payment)
async def get_payment(payment_id: str):
    """Obtém um pagamento por ID."""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return payment

@app.patch("/payments/{payment_id}/mark-as-pending", response_model=Payment)
async def mark_payment_as_pending(payment_id: str):
    """Marca pagamento como pendente."""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    payment.status = PaymentStatus.PENDING
    payment.updated_at = datetime.utcnow()
    return payment

@app.patch("/payments/{payment_id}/mark-as-paid", response_model=Payment)
async def mark_payment_as_paid(payment_id: str):
    """Marca pagamento como pago."""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    payment.status = PaymentStatus.PAID
    payment.updated_at = datetime.utcnow()
    return payment

@app.patch("/payments/{payment_id}/mark-as-cancelled", response_model=Payment)
async def mark_payment_as_cancelled(payment_id: str):
    """Marca pagamento como cancelado."""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    payment.status = PaymentStatus.CANCELLED
    payment.updated_at = datetime.utcnow()
    return payment

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004) 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Payment Service",
    description="API para gerenciamento de pagamentos (Mock/Stub)",
    version="1.0.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums e Models
class PaymentStatus(str, Enum):
    PENDING = "PENDENTE"
    PAID = "PAGO"
    CANCELLED = "CANCELADO"

class PaymentCreate(BaseModel):
    payment_code: str
    amount: float

class Payment(BaseModel):
    id: str
    payment_code: str
    amount: float
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

# Armazenamento em memória (para demonstração)
payments_db: List[Payment] = []

# Health check
@app.get("/health")
async def health_check():
    """Verifica a saúde do serviço."""
    return {"status": "healthy", "service": "payment-service"}

# Endpoints de pagamentos
@app.get("/payments", response_model=List[Payment])
async def list_payments():
    """Lista todos os pagamentos."""
    return payments_db

@app.post("/payments", response_model=Payment)
async def create_payment(payment_data: PaymentCreate):
    """Cria um novo pagamento."""
    payment = Payment(
        id=str(uuid.uuid4()),
        payment_code=payment_data.payment_code,
        amount=payment_data.amount,
        status=PaymentStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    payments_db.append(payment)
    return payment

@app.get("/payments/{payment_id}", response_model=Payment)
async def get_payment(payment_id: str):
    """Obtém um pagamento por ID."""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return payment

@app.patch("/payments/{payment_id}/mark-as-pending", response_model=Payment)
async def mark_payment_as_pending(payment_id: str):
    """Marca pagamento como pendente."""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    payment.status = PaymentStatus.PENDING
    payment.updated_at = datetime.utcnow()
    return payment

@app.patch("/payments/{payment_id}/mark-as-paid", response_model=Payment)
async def mark_payment_as_paid(payment_id: str):
    """Marca pagamento como pago."""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    payment.status = PaymentStatus.PAID
    payment.updated_at = datetime.utcnow()
    return payment

@app.patch("/payments/{payment_id}/mark-as-cancelled", response_model=Payment)
async def mark_payment_as_cancelled(payment_id: str):
    """Marca pagamento como cancelado."""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    payment.status = PaymentStatus.CANCELLED
    payment.updated_at = datetime.utcnow()
    return payment

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004) 