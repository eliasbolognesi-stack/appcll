from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ================= PRODUTO =================
class ProdutoBase(BaseModel):
    nome: str
    preco: float
    quantidade: int


class ProdutoCreate(ProdutoBase):
    pass


class Produto(ProdutoBase):
    id: int
    data_cadastro: datetime

    class Config:
        from_attributes = True


# ================= CLIENTE =================
class ClienteBase(BaseModel):
    nome: str
    telefone: Optional[str]
    limite_fiado: float


class ClienteCreate(ClienteBase):
    pass


class Cliente(ClienteBase):
    id: int
    debito: float
    data_cadastro: datetime

    class Config:
        from_attributes = True


# ================= ITEM VENDA =================
class ItemVendaBase(BaseModel):
    produto_id: int
    quantidade: int
    preco_unitario: float


class ItemVendaCreate(ItemVendaBase):
    pass


class ItemVenda(ItemVendaBase):
    id: int
    venda_id: int

    class Config:
        from_attributes = True


# ================= VENDA =================
class VendaBase(BaseModel):
    cliente_id: Optional[int]
    total: float


class VendaCreate(VendaBase):
    itens: List[ItemVendaCreate]


class Venda(VendaBase):
    id: int
    data: datetime
    itens: List[ItemVenda]

    class Config:
        from_attributes = True


# ================= PAGAMENTO =================
class PagamentoCreate(BaseModel):
    cliente_id: int
    valor: float