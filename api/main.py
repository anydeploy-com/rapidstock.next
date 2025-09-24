from fastapi import FastAPI, Depends, HTTPException, Response
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, event
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
import meilisearch
from pydantic import BaseModel
from typing import Optional, List
import os
import logging
import time
from sqlalchemy.exc import IntegrityError

app = FastAPI(title="RapidStock API", description="FastAPI backend for RapidStock", version="1.0.0")

# Logger setup for Meilisearch sync
logger = logging.getLogger("meili_sync")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(asctime)s [MeiliSync] %(message)s", "%H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

DATABASE_URL = "sqlite:///../data/sqlite/rapidstock.db"
MEILI_URL = os.getenv("MEILI_URL", "http://127.0.0.1:7700")
MEILI_API_KEY = os.getenv("MEILI_API_KEY", "qRT4skbJgqeeTdsw8oABvC0AF9qcl10cz-1VTYEu_Hs")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Enable WAL mode and related performance/consistency PRAGMAs for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL;")  # Improves concurrency
        cursor.execute("PRAGMA synchronous=NORMAL;")  # Safe enough with WAL, faster than FULL
        cursor.execute("PRAGMA foreign_keys=ON;")  # Ensure FK constraints are enforced
    finally:
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=True)
Base = declarative_base()


# SQLAlchemy Models
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"))
    attributes = relationship("Attribute", back_populates="product", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    products = relationship("Product", backref="category")

class Attribute(Base):
    __tablename__ = "attributes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    value = Column(String)
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="attributes")

Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class AttributeCreate(BaseModel):
    name: str
    value: str

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: int
    attributes: Optional[List[AttributeCreate]] = []

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class AttributeOut(AttributeCreate):
    id: int
    class Config:
        from_attributes = True

class ProductOut(ProductCreate):
    id: int
    attributes: List[AttributeOut] = []
    class Config:
        from_attributes = True

class CategoryOut(CategoryCreate):
    id: int
    class Config:
        from_attributes = True

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Meilisearch client
meili_client = meilisearch.Client(MEILI_URL, MEILI_API_KEY)
PRODUCT_INDEX = "products"
CATEGORY_INDEX = "categories"
ATTRIBUTE_INDEX = "attributes"


@app.on_event("startup")
def on_startup():
    logger.info("Starting FastAPI application startup sequence")
    start_total = time.perf_counter()
    # Ensure Meilisearch indexes exist
    created_indexes = []
    try:
        for idx in [PRODUCT_INDEX, CATEGORY_INDEX, ATTRIBUTE_INDEX]:
            t_idx = time.perf_counter()
            try:
                meili_client.get_index(idx)
                logger.info(f"Index '{idx}' exists (checked in {(time.perf_counter()-t_idx)*1000:.1f} ms)")
            except meilisearch.errors.MeilisearchApiError:
                meili_client.create_index(idx, {"primaryKey": "id"})
                created_indexes.append(idx)
                logger.info(f"Created missing index '{idx}' in {(time.perf_counter()-t_idx)*1000:.1f} ms")
    except Exception as e:
        logger.error(f"[Startup Error] Could not connect to Meilisearch at {MEILI_URL}: {e}")
        logger.warning("Continuing startup without Meilisearch sync. Search endpoints may be unavailable.")
        logger.info(f"Startup complete in {(time.perf_counter()-start_total)*1000:.1f} ms (skipped Meilisearch sync)")
        return

    # Sync all DB data to Meilisearch
    db = SessionLocal()
    try:
        logger.info("Beginning full SQLite -> Meilisearch resync")
        t_sync_start = time.perf_counter()
        # Products
        t = time.perf_counter()
        products = db.query(Product).all()
        product_docs = [
            {"id": p.id, "name": p.name, "description": p.description, "category_id": p.category_id}
            for p in products
        ]
        meili_client.index(PRODUCT_INDEX).delete_all_documents()
        if product_docs:
            meili_client.index(PRODUCT_INDEX).add_documents(product_docs)
        logger.info(f"Synced {len(product_docs)} products in {(time.perf_counter()-t)*1000:.1f} ms")

        # Categories
        t = time.perf_counter()
        categories = db.query(Category).all()
        category_docs = [
            {"id": c.id, "name": c.name, "description": c.description}
            for c in categories
        ]
        meili_client.index(CATEGORY_INDEX).delete_all_documents()
        if category_docs:
            meili_client.index(CATEGORY_INDEX).add_documents(category_docs)
        logger.info(f"Synced {len(category_docs)} categories in {(time.perf_counter()-t)*1000:.1f} ms")

        # Attributes
        t = time.perf_counter()
        attributes = db.query(Attribute).all()
        attribute_docs = [
            {"id": a.id, "name": a.name, "value": a.value, "product_id": a.product_id}
            for a in attributes
        ]
        meili_client.index(ATTRIBUTE_INDEX).delete_all_documents()
        if attribute_docs:
            meili_client.index(ATTRIBUTE_INDEX).add_documents(attribute_docs)
        logger.info(f"Synced {len(attribute_docs)} attributes in {(time.perf_counter()-t)*1000:.1f} ms")

        total_time = (time.perf_counter() - t_sync_start) * 1000
        created_str = ", created indexes: " + ", ".join(created_indexes) if created_indexes else ""
        logger.info(
            f"Completed Meilisearch resync in {total_time:.1f} ms (products={len(product_docs)}, categories={len(category_docs)}, attributes={len(attribute_docs)}){created_str}"
        )
    finally:
        db.close()
    logger.info(f"Startup complete in {(time.perf_counter()-start_total)*1000:.1f} ms")

# Global DB IntegrityError handler
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc: IntegrityError):
    # Provide a cleaner message instead of 500
    detail = "Database integrity error"
    if "FOREIGN KEY constraint failed" in str(exc.orig):
        detail = "Referenced resource does not exist (foreign key constraint failed)."
    return Response(status_code=400, content=f"{detail}")

@app.post("/products/", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    # Validate category exists
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail=f"Category id {product.category_id} does not exist")
    db_product = Product(name=product.name, description=product.description, category_id=product.category_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    # Add attributes
    new_attribute_docs = []
    for attr in product.attributes:
        db_attr = Attribute(name=attr.name, value=attr.value, product_id=db_product.id)
        db.add(db_attr)
        db.flush()  # get id before commit
        new_attribute_docs.append({"id": db_attr.id, "name": db_attr.name, "value": db_attr.value, "product_id": db_attr.product_id})
    db.commit()
    db.refresh(db_product)
    # Index in Meilisearch (product + any new attributes)
    try:
        meili_client.index(PRODUCT_INDEX).add_documents([
            {"id": db_product.id, "name": db_product.name, "description": db_product.description, "category_id": db_product.category_id}
        ])
        if new_attribute_docs:
            meili_client.index(ATTRIBUTE_INDEX).add_documents(new_attribute_docs)
    except Exception as e:
        logger.warning(f"Meilisearch indexing failed for product {db_product.id}: {e}")
    return db_product

# New: list all products
@app.get("/products/", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

# New: retrieve single product
@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# New: delete product (and its attributes) + remove from Meilisearch
@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Collect related attribute IDs before deletion
    attribute_ids = [a.id for a in product.attributes]

    # Delete attributes then product
    db.query(Attribute).filter(Attribute.product_id == product_id).delete(synchronize_session=False)
    db.delete(product)
    db.commit()

    # Update Meilisearch indexes (ignore errors so deletion succeeds regardless)
    try:
        meili_client.index(PRODUCT_INDEX).delete_document(product_id)
    except Exception as e:
        logger.warning(f"Failed to delete product {product_id} from Meilisearch: {e}")
    if attribute_ids:
        try:
            meili_client.index(ATTRIBUTE_INDEX).delete_documents(attribute_ids)
        except Exception as e:
            logger.warning(f"Failed to delete {len(attribute_ids)} attribute docs from Meilisearch: {e}")

    return Response(status_code=204)

@app.post("/categories/", response_model=CategoryOut)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    # Index in Meilisearch
    meili_client.index(CATEGORY_INDEX).add_documents([
        {"id": db_category.id, "name": db_category.name, "description": db_category.description}
    ])
    return db_category

@app.post("/attributes/", response_model=AttributeOut)
def create_attribute(attribute: AttributeCreate, product_id: int, db: Session = Depends(get_db)):
    db_attr = Attribute(name=attribute.name, value=attribute.value, product_id=product_id)
    db.add(db_attr)
    db.commit()
    db.refresh(db_attr)
    # Index in Meilisearch
    meili_client.index(ATTRIBUTE_INDEX).add_documents([
        {"id": db_attr.id, "name": db_attr.name, "value": db_attr.value, "product_id": db_attr.product_id}
    ])
    return db_attr

@app.get("/search/products/")
def search_products(q: str):
    results = meili_client.index(PRODUCT_INDEX).search(q)
    return results["hits"]

@app.get("/search/categories/")
def search_categories(q: str):
    results = meili_client.index(CATEGORY_INDEX).search(q)
    return results["hits"]

@app.get("/search/attributes/")
def search_attributes(q: str):
    results = meili_client.index(ATTRIBUTE_INDEX).search(q)
    return results["hits"]

@app.get("/")
def read_root():
    return {"message": "Welcome to RapidStock API"}

@app.get("/health")
def health_check():
    try:
        ms_health = meili_client.health()
        meili_status = ms_health.get("status", "unknown")
    except Exception:
        meili_status = "unavailable"
    overall = "healthy" if meili_status == "available" else "degraded"
    return {"status": overall, "meilisearch": meili_status}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}