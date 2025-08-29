from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI()
CSV_FILE = "data.csv"

class Item(BaseModel):
    id: int
    nome: str
    cognome: str
    codice_fiscale: str

def read_csv():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(columns=["id", "nome", "cognome", "codice_fiscale"])
    return pd.read_csv(CSV_FILE)

def write_csv(df):
    df.to_csv(CSV_FILE, index=False)

@app.post("/items/", response_model=Item)
def create_item(item: Item):
    df = read_csv()
    if item.id in df["id"].values:
        raise HTTPException(status_code=400, detail="ID already exists")
    new_row = pd.DataFrame([item.dict()])
    df = pd.concat([df, new_row], ignore_index=True)
    write_csv(df)
    return item

@app.get("/items/", response_model=list[Item])
def get_items():
    df = read_csv()
    return df.to_dict(orient="records")

@app.get("/items/{id}", response_model=Item)
def get_item(id: int):
    df = read_csv()
    row = df[df["id"] == id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Item not found")
    return row.iloc[0].to_dict()

@app.put("/items/{id}", response_model=Item)
def update_item(id: int, item: Item):
    df = read_csv()
    idx = df[df["id"] == id].index
    if idx.empty:
        raise HTTPException(status_code=404, detail="Item not found")
    df.loc[idx[0]] = [item.id, item.nome, item.cognome, item.codice_fiscale]
    write_csv(df)
    return item

@app.delete("/items/{id}")
def delete_item(id: int):
    df = read_csv()
    idx = df[df["id"] == id].index
    if idx.empty:
        raise HTTPException(status_code=404, detail="Item not found")
    df = df.drop(idx)
    write_csv(df)
    return {"message": "Item deleted successfully"}

@app.get("/items/count")
def count_items():
    df = read_csv()
    count = len(df)
    return {"count": count}