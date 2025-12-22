from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from sqlalchemy import func
from datetime import datetime
from database import Base, engine, SessionLocal
from models import User, Struk, Produk
from app.pipeline.receipt_pipeline import run_pipeline

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

app = FastAPI(title="Carbon Scanner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

class UserAuth(BaseModel):
    username: str
    password: str

@app.post("/register")
def register(payload: UserAuth, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username sudah dipakai")

    user = User(
        username=payload.username,
        password_hash=pwd_context.hash(payload.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"msg": "User terdaftar", "user_id": user.id}

@app.post("/login")
def login(payload: UserAuth, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()

    if not user or not pwd_context.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Username/password salah")

    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id 
    }

@app.post("/predict-carbon/{user_id}")
async def predict_carbon(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        result = run_pipeline(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    struk = Struk(user_id=user_id, total_emisi=0)
    db.add(struk)
    db.commit()
    db.refresh(struk)

    detected_products = []

    for item in result.get("detected_products", []):
        nama = item.get("produk")
        if not nama:
            continue

        produk = Produk(
            struk_id=struk.id,
            nama=nama,
            kategori=item.get("kategori", "unknown"),
            berat_kg=0,
            karbon=0,
            karbon_factor=item.get("karbon_kg_per_kg", 0),
            confidence=item.get("confidence", 0),
        )

        db.add(produk)

        detected_products.append({
            "produk": nama,
            "kategori": item.get("kategori"),
            "karbon_kg_per_kg": item.get("karbon_kg_per_kg"),
            "confidence": item.get("confidence"),
        })

    db.commit()

    return {
        "struk_id": struk.id,
        "raw_text": result.get("raw_text", ""),
        "detected_products": detected_products
    }


@app.post("/calculate-carbon/{struk_id}")
def calculate_carbon(struk_id: int, payload: dict, db: Session = Depends(get_db)):
    struk = db.query(Struk).filter(Struk.id == struk_id).first()
    if not struk:
        raise HTTPException(status_code=404, detail="Struk tidak ditemukan")

    detail = []
    total = 0

    for item in payload["items"]:
        produk = db.query(Produk).filter(
            Produk.struk_id == struk_id,
            Produk.nama == item["produk"]
        ).first()

        if not produk:
            continue

        berat = item["berat_kg"]
        karbon = round(berat * produk.karbon_factor, 3)

        produk.berat_kg = berat
        produk.karbon = karbon
        total += karbon

        detail.append({
            "produk": produk.nama,
            "berat_kg": berat,
            "karbon": karbon
        })

    struk.total_emisi = round(total, 3)
    db.commit()

    return {
        "detail": detail,
        "total_karbon": struk.total_emisi
    }

@app.get("/riwayat/{user_id}")
def get_riwayat_user(user_id: int, db: Session = Depends(get_db)):
    struks = (
        db.query(Struk)
        .filter(Struk.user_id == user_id)
        .order_by(Struk.id.desc())
        .all()
    )

    return [
        {
            "struk_id": s.id,
            "total_emisi": s.total_emisi
        }
        for s in struks
    ]


@app.get("/riwayat/detail/{struk_id}")
def get_detail_riwayat(struk_id: int, db: Session = Depends(get_db)):
    struk = db.query(Struk).filter(Struk.id == struk_id).first()
    if not struk:
        raise HTTPException(status_code=404, detail="Struk tidak ditemukan")

    return {
        "struk_id": struk.id,
        "total_emisi": struk.total_emisi,
        "produk": [
            {
                "nama": p.nama,
                "kategori": p.kategori,
                "berat_kg": p.berat_kg,
                "karbon": p.karbon,
                "confidence": p.confidence
            }
            for p in struk.produk
        ]
    }



@app.get("/dashboard/{user_id}")
def dashboard(user_id: int, db: Session = Depends(get_db)):
    now = datetime.now()

    total_bulan_ini = (
        db.query(func.sum(Struk.total_emisi))
        .filter(
            Struk.user_id == user_id,
            func.month(Struk.created_at) == now.month,
            func.year(Struk.created_at) == now.year,
        )
        .scalar()
        or 0
    )

    monthly = (
        db.query(
            func.month(Struk.created_at).label("month"),
            func.sum(Struk.total_emisi).label("total"),
        )
        .filter(Struk.user_id == user_id)
        .group_by(func.month(Struk.created_at))
        .order_by(func.month(Struk.created_at))
        .all()
    )

    monthly_data = [
        {
            "month": int(m.month),
            "emisi": float(m.total),
        }
        for m in monthly
    ]

    category = (
        db.query(
            Produk.kategori,
            func.sum(Produk.karbon).label("total"),
        )
        .join(Struk, Produk.struk_id == Struk.id)
        .filter(Struk.user_id == user_id)
        .group_by(Produk.kategori)
        .all()
    )

    category_data = [
        {
            "name": c.kategori,
            "value": float(c.total),
        }
        for c in category
    ]

    return {
        "total_bulan_ini": round(total_bulan_ini, 3),
        "monthly": monthly_data,
        "category": category_data,
    }
