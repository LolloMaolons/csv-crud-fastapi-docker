from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI()
CSV_FILE = "data.csv"
COLUMNS = ["id", "nome", "cognome", "codice_fiscale"]

# Crea il CSV se non esiste
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=COLUMNS).to_csv(CSV_FILE, index=False)

class Item(BaseModel):
    id: int
    nome: str
    cognome: str
    codice_fiscale: str

def read_csv():
    try:
        if not os.path.exists(CSV_FILE):
            return pd.DataFrame(columns=COLUMNS)
        df = pd.read_csv(CSV_FILE, dtype=str)
        if df.empty:
            return pd.DataFrame(columns=COLUMNS)
        return df
    except Exception as e:
        print("ERRORE LETTURA CSV:", e)
        return pd.DataFrame(columns=COLUMNS)

def write_csv(df):
    try:
        df.to_csv(CSV_FILE, index=False)
    except Exception as e:
        print("ERRORE SCRITTURA CSV:", e)

@app.get("/items/count")
def count_items():
    try:
        df = read_csv()
        return {"count": len(df)}
    except Exception as e:
        print("ERRORE COUNT_ITEMS:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/items/", response_model=Item)
def create_item(item: Item):
    try:
        df = read_csv()
        if "id" in df and not df["id"].empty and str(item.id) in df["id"].values:
            raise HTTPException(status_code=400, detail="ID already exists")
        new_row = pd.DataFrame([item.dict()])
        df = pd.concat([df, new_row], ignore_index=True)
        write_csv(df)
        return item
    except Exception as e:
        print("ERRORE CREATE_ITEM:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/items/", response_model=list[Item])
def get_items():
    try:
        df = read_csv()
        df["id"] = pd.to_numeric(df["id"], errors='coerce').fillna(0).astype(int)
        return df.to_dict(orient="records")
    except Exception as e:
        print("ERRORE GET_ITEMS:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/items/{id}", response_model=Item)
def get_item(id: int):
    try:
        df = read_csv()
        df["id"] = pd.to_numeric(df["id"], errors='coerce').fillna(0).astype(int)
        row = df[df["id"] == id]
        if row.empty:
            raise HTTPException(status_code=404, detail="Item not found")
        return row.iloc[0].to_dict()
    except Exception as e:
        print("ERRORE GET_ITEM:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/items/{id}", response_model=Item)
def update_item(id: int, item: Item):
    try:
        df = read_csv()
        df["id"] = pd.to_numeric(df["id"], errors='coerce').fillna(0).astype(int)
        idx = df[df["id"] == id].index
        if idx.empty:
            raise HTTPException(status_code=404, detail="Item not found")
        df.loc[idx[0]] = [item.id, item.nome, item.cognome, item.codice_fiscale]
        write_csv(df)
        return item
    except Exception as e:
        print("ERRORE UPDATE_ITEM:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/items/{id}")
def delete_item(id: int):
    try:
        df = read_csv()
        df["id"] = pd.to_numeric(df["id"], errors='coerce').fillna(0).astype(int)
        idx = df[df["id"] == id].index
        if idx.empty:
            raise HTTPException(status_code=404, detail="Item not found")
        df = df.drop(idx)
        write_csv(df)
        return {"message": "Item deleted successfully"}
    except Exception as e:
        print("ERRORE DELETE_ITEM:", e)
        raise HTTPException(status_code=500, detail=str(e))

