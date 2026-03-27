from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

# Importar models primeiro para registrar todas as classes
import models as db_models
from database import engine, get_db, mapper_registry
import schemas

# Configurar mappers
mapper_registry.configure()

# ✅ CRIA TABELAS
db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mercearia do João API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= PRODUTOS =================
@app.get("/api/produtos", response_model=List[schemas.Produto])
def get_produtos(db: Session = Depends(get_db)):
    return db.query(db_models.Produto).all()


@app.post("/api/produtos", response_model=schemas.Produto)
def create_produto(produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    db_produto = db_models.Produto(**produto.dict())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto


@app.get("/api/produtos/{produto_id}", response_model=schemas.Produto)
def get_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(db_models.Produto).filter(db_models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@app.put("/api/produtos/{produto_id}", response_model=schemas.Produto)
def update_produto(produto_id: int, produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    db_produto = db.query(db_models.Produto).filter(db_models.Produto.id == produto_id).first()
    if not db_produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    for key, value in produto.dict().items():
        setattr(db_produto, key, value)
    
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto


@app.delete("/api/produtos/{produto_id}")
def delete_produto(produto_id: int, db: Session = Depends(get_db)):
    db_produto = db.query(db_models.Produto).filter(db_models.Produto.id == produto_id).first()
    if not db_produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    db.delete(db_produto)
    db.commit()
    return {"message": "Produto deletado com sucesso"}


# ================= CLIENTES =================
@app.get("/api/clientes", response_model=List[schemas.Cliente])
def get_clientes(db: Session = Depends(get_db)):
    return db.query(db_models.Cliente).all()


@app.post("/api/clientes", response_model=schemas.Cliente)
def create_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = db_models.Cliente(**cliente.dict())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente


@app.get("/api/clientes/{cliente_id}", response_model=schemas.Cliente)
def get_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(db_models.Cliente).filter(db_models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente


@app.put("/api/clientes/{cliente_id}", response_model=schemas.Cliente)
def update_cliente(cliente_id: int, cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = db.query(db_models.Cliente).filter(db_models.Cliente.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    for key, value in cliente.dict().items():
        setattr(db_cliente, key, value)
    
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente


@app.delete("/api/clientes/{cliente_id}")
def delete_cliente(cliente_id: int, db: Session = Depends(get_db)):
    db_cliente = db.query(db_models.Cliente).filter(db_models.Cliente.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    db.delete(db_cliente)
    db.commit()
    return {"message": "Cliente deletado com sucesso"}


# ================= VENDAS =================
@app.get("/api/vendas", response_model=List[schemas.Venda])
def get_vendas(db: Session = Depends(get_db)):
    return db.query(db_models.Venda).all()


@app.post("/api/vendas", response_model=schemas.Venda)
def create_venda(venda: schemas.VendaCreate, db: Session = Depends(get_db)):
    # Criar venda
    db_venda = db_models.Venda(
        cliente_id=venda.cliente_id,
        total=venda.total
    )
    db.add(db_venda)
    db.flush()
    
    # Criar itens de venda
    for item in venda.itens:
        db_item = db_models.ItemVenda(
            venda_id=db_venda.id,
            produto_id=item.produto_id,
            quantidade=item.quantidade,
            preco_unitario=item.preco_unitario
        )
        db.add(db_item)
        
        # Atualizar estoque do produto
        produto = db.query(db_models.Produto).filter(db_models.Produto.id == item.produto_id).first()
        if produto:
            produto.quantidade -= item.quantidade
    
    # Atualizar débito do cliente se aplicável
    if venda.cliente_id:
        cliente = db.query(db_models.Cliente).filter(db_models.Cliente.id == venda.cliente_id).first()
        if cliente:
            cliente.debito += venda.total
    
    db.commit()
    db.refresh(db_venda)
    return db_venda


@app.get("/api/vendas/{venda_id}", response_model=schemas.Venda)
def get_venda(venda_id: int, db: Session = Depends(get_db)):
    venda = db.query(db_models.Venda).filter(db_models.Venda.id == venda_id).first()
    if not venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return venda


# ================= PAGAMENTOS =================
@app.post("/api/pagamentos")
def create_pagamento(pagamento: schemas.PagamentoCreate, db: Session = Depends(get_db)):
    cliente = db.query(db_models.Cliente).filter(db_models.Cliente.id == pagamento.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    if pagamento.valor > cliente.debito:
        raise HTTPException(status_code=400, detail="Valor maior que o débito")
    
    cliente.debito -= pagamento.valor
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    
    return {"message": "Pagamento recebido com sucesso", "debito_atual": cliente.debito}