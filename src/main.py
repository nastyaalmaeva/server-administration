from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src import models, schemas
from src.database import init_db, get_db


INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>KUBSU User API</title>
</head>
<body>
    <h1>Welcome to KUBSU User API!</h1>
    <p>For full API interface visit <a href="/docs" target="_blank">Swagger UI</a> or <a href="/redoc" target="_blank">ReDoc</a>.</p>
</body>
</html>
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting KubSU API")
    await init_db()
    yield


app = FastAPI(
    title="KubSU API",
    description="CRUD",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "kubsu-api",
        "version": "1.0.0",
        "message": "All systems operational!"
    }


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content=INDEX_HTML, status_code=200)


@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    user = models.User(name=user.name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@app.get("/users/", response_model=list[schemas.User])
async def read_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/users/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.name = user.name
    await db.commit()
    
    return db_user


@app.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(db_user)
    await db.commit()
    
    return {"detail": "User deleted"}