import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, String, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# ==========================================
# 1. DATABASE & FASTAPI SETUP
# ==========================================
DATABASE_URL = "sqlite:///dimensies.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

# TABEL 1: Groepen (Slaat de unieke codes op)
class GroepTabel(Base):
    __tablename__ = "groepen"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    groeps_naam: Mapped[str] = mapped_column(String(100), nullable=False)
    unieke_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

# TABEL 2: Scores (Gekoppeld aan een groep via een ForeignKey)
class ScoreTabel(Base):
    __tablename__ = "scores"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    groeps_code: Mapped[str] = mapped_column(String(50), nullable=False)  # Link naar de groep
    naam: Mapped[str] = mapped_column(String(100), nullable=False)  # unique=True is weg zodat meerdere groepen d1 kunnen opslaan
    score: Mapped[int] = mapped_column(default=0)
    poging: Mapped[int] = mapped_column(default=1)
Base.metadata.create_all(engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2. PYDANTIC MODELS (Voor de frontend)
# ==========================================
class GroepAanmakenData(BaseModel):
    groeps_naam: str




class EnqueteData(BaseModel):
    groeps_code: str  # De frontend MOET de ingevulde groepscode meesturen
    poging: int # front end toevoegen
    v1_d1: Optional[int] = None; v2_d1: Optional[int] = None; v3_d1: Optional[int] = None; v4_d1: Optional[int] = None; v5_d1: Optional[int] = None
    v1_d2: Optional[int] = None; v2_d2: Optional[int] = None; v3_d2: Optional[int] = None; v4_d2: Optional[int] = None; v5_d2: Optional[int] = None
    v1_d3: Optional[int] = None; v2_d3: Optional[int] = None; v3_d3: Optional[int] = None; v4_d3: Optional[int] = None; v5_d3: Optional[int] = None
    v1_d4: Optional[int] = None; v2_d4: Optional[int] = None; v3_d4: Optional[int] = None; v4_d4: Optional[int] = None; v5_d4: Optional[int] = None
    v1_d5: Optional[int] = None; v2_d5: Optional[int] = None; v3_d5: Optional[int] = None; v4_d5: Optional[int] = None; v5_d5: Optional[int] = None
    v1_d6: Optional[int] = None; v2_d6: Optional[int] = None; v3_d6: Optional[int] = None; v4_d6: Optional[int] = None; v5_d6: Optional[int] = None
    v1_d7: Optional[int] = None; v2_d7: Optional[int] = None; v3_d7: Optional[int] = None; v4_d7: Optional[int] = None; v5_d7: Optional[int] = None
    v1_d8: Optional[int] = None; v2_d8: Optional[int] = None; v3_d8: Optional[int] = None; v4_d8: Optional[int] = None; v5_d8: Optional[int] = None
    v1_d9: Optional[int] = None; v2_d9: Optional[int] = None; v3_d9: Optional[int] = None; v4_d9: Optional[int] = None; v5_d9: Optional[int] = None
    v1_d10: Optional[int] = None; v2_d10: Optional[int] = None; v3_d10: Optional[int] = None; v4_d10: Optional[int] = None; v5_d10: Optional[int] = None


# ==========================================
# 3. API ENDPOINTS (ROUTES)
# ==========================================

# 1. ROUTE: Nieuwe groep aanmaken en code genereren
@app.post("/groep-aanmaken")
def maak_groep_aan(data: GroepAanmakenData):
    # Genereert een korte unieke code van 8 tekens, bijv. 'B1C3D5E7'
    gegenereerde_code = str(uuid.uuid4())[:8].upper()
    
    with SessionLocal() as session:
        nieuwe_groep = GroepTabel(
            groeps_naam=data.groeps_naam,
            unieke_code=gegenereerde_code
        )
        session.add(nieuwe_groep)
        session.commit()
        
    return {
        "status": "success",
        "groeps_naam": data.groeps_naam,
        "unieke_code": gegenereerde_code
    }
  
# 2. ROUTE: Scores berekenen en opslaan voor een SPECIFIEKE groep
@app.post("/opslaan")
def bereken_en_sla_op(data: EnqueteData):
    
    with SessionLocal() as session:
        # Controleer eerst of de meegestuurde groepscode wel echt bestaat
        groep_bestaat = session.scalar(select(GroepTabel).where(GroepTabel.unieke_code == data.groeps_code))
        if not groep_bestaat:
            raise HTTPException(status_code=404, detail="Ingevoerde groepscode is ongeldig!")

        # Jouw rekenlogica
        d1 = (data.v1_d1 or 1) + (data.v2_d1 or 1) + (data.v3_d1 or 1) + (data.v4_d1 or 1) + (data.v5_d1 or 1)
        d2 = (data.v1_d2 or 1) + (data.v2_d2 or 1) + (data.v3_d2 or 1) + (data.v4_d2 or 1) + (data.v5_d2 or 1)
        d3 = (data.v1_d3 or 1) + (data.v2_d3 or 1) + (data.v3_d3 or 1) + (data.v4_d3 or 1) + (data.v5_d3 or 1)
        d4 = (data.v1_d4 or 1) + (data.v2_d4 or 1) + (data.v3_d4 or 1) + (data.v4_d4 or 1) + (data.v5_d4 or 1)
        d5 = (data.v1_d5 or 1) + (data.v2_d5 or 1) + (data.v3_d5 or 1) + (data.v4_d5 or 1) + (data.v5_d5 or 1)
        d6 = (data.v1_d6 or 1) + (data.v2_d6 or 1) + (data.v3_d6 or 1) + (data.v4_d6 or 1) + (data.v5_d6 or 1)
        d7 = (data.v1_d7 or 1) + (data.v2_d7 or 1) + (data.v3_d7 or 1) + (data.v4_d7 or 1) + (data.v5_d7 or 1)
        d8 = (data.v1_d8 or 1) + (data.v2_d8 or 1) + (data.v3_d8 or 1) + (data.v4_d8 or 1) + (data.v5_d8 or 1)
        d9 = (data.v1_d9 or 1) + (data.v2_d9 or 1) + (data.v3_d9 or 1) + (data.v4_d9 or 1) + (data.v5_d9 or 1)
        d10 = (data.v1_d10 or 1) + (data.v2_d10 or 1) + (data.v3_d10 or 1) + (data.v4_d10 or 1) + (data.v5_d10 or 1)

        dimensions = [d1 + d2 + d3 + d4 + d5 + d6 + d7 + d8 + d9 + d10]

        alles_om_op_te_slaan = {
            "dimensie_1": d1, "dimensie_2": d2, "dimensie_3": d3, "dimensie_4": d4, "dimensie_5": d5,
            "dimensie_6": d6, "dimensie_7": d7, "dimensie_8": d8, "dimensie_9": d9, "dimensie_10": d10,
            "totale_score": dimensions[0]
        }

        # Opslaan: We zoeken nu op combinaties van groeps_code EN de naam van de score
        for naam_score, waarde in alles_om_op_te_slaan.items():
            resultaat = session.scalar(
                select(ScoreTabel).where(
                    ScoreTabel.groeps_code == data.groeps_code,
                    ScoreTabel.poging == data.poging, 
                    ScoreTabel.naam == naam_score
                )
            )
            
            if not resultaat:
                resultaat = ScoreTabel(groeps_code=data.groeps_code, poging=data.poging, naam=naam_score)
                session.add(resultaat)
                
            resultaat.score = waarde
            
        session.commit()

    return {"status": "success", "bericht": f"Scores succesvol verwerkt voor groepscode {data.groeps_code}!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)

# http://localhost:8000/docs
