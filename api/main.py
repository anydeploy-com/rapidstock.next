from fastapi import FastAPI, Response
from sqlalchemy.exc import IntegrityError
from contextlib import asynccontextmanager
import time
from config import APP_TITLE, APP_DESCRIPTION, APP_VERSION
from database import engine, SessionLocal, Base
from routes import products_router, categories_router, attributes_router, search_router
from services.meili import meili_service, logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting FastAPI application startup sequence")
    start_total = time.perf_counter()

    try:
        # Ensure Meilisearch indexes exist
        created_indexes = meili_service.ensure_indexes_exist()

        # Sync all DB data to Meilisearch
        db = SessionLocal()
        try:
            product_count, category_count, attribute_count, sync_time = meili_service.sync_all_data(db)

            created_str = ", created indexes: " + ", ".join(created_indexes) if created_indexes else ""
            logger.info(
                f"Completed Meilisearch resync in {sync_time:.1f} ms (products={product_count}, categories={category_count}, attributes={attribute_count}){created_str}"
            )
        finally:
            db.close()

    except Exception as e:
        logger.error(f"[Startup Error] Could not connect to Meilisearch: {e}")
        logger.warning("Continuing startup without Meilisearch sync. Search endpoints may be unavailable.")
        logger.info(f"Startup complete in {(time.perf_counter()-start_total)*1000:.1f} ms (skipped Meilisearch sync)")
        yield
        return

    logger.info(f"Startup complete in {(time.perf_counter()-start_total)*1000:.1f} ms")
    yield
    # Shutdown (if needed)

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan
)

# Create all tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(products_router)
app.include_router(categories_router)
app.include_router(attributes_router)
app.include_router(search_router)

# Global DB IntegrityError handler
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc: IntegrityError):
    # Provide a cleaner message instead of 500
    detail = "Database integrity error"
    if "FOREIGN KEY constraint failed" in str(exc.orig):
        detail = "Referenced resource does not exist (foreign key constraint failed)."
    return Response(status_code=400, content=f"{detail}")

@app.get("/")
def read_root():
    return {"message": "Welcome to RapidStock API"}

@app.get("/health")
def health_check():
    meili_status = meili_service.health_check()
    overall = "healthy" if meili_status == "available" else "degraded"
    return {"status": overall, "meilisearch": meili_status}