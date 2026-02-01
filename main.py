# main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

# carregar dados na memória (para o teste é suficiente)
df = pd.read_csv("data/consolidado_despesas_validado_final.csv", encoding="utf-8")

app = FastAPI(title="API Operadoras ANS - Teste Estágio")

# liberar CORS para o frontend Vue local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/operadoras")
def listar_operadoras(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    q: str | None = None,
):
    # agrupar por CNPJ + RazaoSocial + UF para ter uma linha por operadora/UF
    base = df[["CNPJ", "RazaoSocial", "UF"]].drop_duplicates()

    if q:
        q_lower = q.lower()
        base = base[
            base["RazaoSocial"].str.lower().str.contains(q_lower, na=False)
            | base["CNPJ"].astype(str).str.contains(q_lower)
        ]

    total = len(base)
    start = (page - 1) * limit
    end = start + limit
    pagina = base.iloc[start:end]

    data = pagina.to_dict(orient="records")
    return {
        "data": data,
        "total": total,
        "page": page,
        "limit": limit,
    }

@app.get("/api/operadoras/{cnpj}")
def detalhes_operadora(cnpj: str):
    parte = df[df["CNPJ"].astype(str) == cnpj]
    if parte.empty:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")

    # pegar algumas infos básicas da primeira linha
    linha = parte.iloc[0]
    return {
        "CNPJ": str(linha["CNPJ"]),
        "RazaoSocial": linha["RazaoSocial"],
        "Modalidade": linha.get("Modalidade"),
        "UF": linha.get("UF"),
    }

@app.get("/api/operadoras/{cnpj}/despesas")
def historico_despesas(cnpj: str):
    parte = df[df["CNPJ"].astype(str) == cnpj]
    if parte.empty:
        raise HTTPException(status_code=404, detail="Histórico não encontrado")

    # ordenar por Ano + Trimestre para ficar legível
    parte = parte.sort_values(["Ano", "Trimestre"])
    registros = parte[["Ano", "Trimestre", "ValorDespesas_num"]].to_dict(orient="records")
    return {"cnpj": cnpj, "historico": registros}

@app.get("/api/estatisticas")
def estatisticas():
    # total e média geral
    validos = df[df["ValorDespesas_num"].notna() & (df["ValorDespesas_num"] > 0)]
    total_despesas = float(validos["ValorDespesas_num"].sum())
    media_despesas = float(validos["ValorDespesas_num"].mean())

    # top 5 operadoras por total
    grupo = validos.groupby(["CNPJ", "RazaoSocial"])["ValorDespesas_num"].sum().reset_index()
    grupo = grupo.sort_values("ValorDespesas_num", ascending=False).head(5)

    top5 = []
    for _, row in grupo.iterrows():
        top5.append({
            "CNPJ": str(row["CNPJ"]),
            "RazaoSocial": row["RazaoSocial"],
            "TotalDespesas": float(row["ValorDespesas_num"]),
        })

    return {
        "total_despesas": total_despesas,
        "media_despesas": media_despesas,
        "top5_operadoras": top5,
    }
