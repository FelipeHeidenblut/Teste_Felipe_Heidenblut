import pandas as pd
import os

pasta_arquivos = "DownloadsAns"
palavras_chave = ["despesa", "despesas", "sinistro", "evento"]

def listar_arquivos_extraidos():
    arquivos_encontrados = []

    for raiz, pastas, arquivos in os.walk(pasta_arquivos):
        if "extraido" not in raiz:
            continue

        for nome in arquivos:
            caminho = os.path.join(raiz, nome)
            arquivos_encontrados.append(caminho)

    return arquivos_encontrados

def ler_arquivo(caminho):
    ext = os.path.splitext(caminho)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(caminho, sep=";", engine="python")
    elif ext in [".txt"]:
        df = pd.read_csv(caminho, sep=";", engine="python")
    else:
        print(f"Pulei (extensão não suportada ainda): {caminho}")
        return None
    return df

def extrair_ano_trimestre(caminho):
    partes = caminho.split(os.sep)
    # Ex.: ["DownloadsAns", "2025", "extraido", "2T2025.csv"]
    ano = None
    trimestre = None

    for p in partes:
        if p.isdigit() and len(p) == 4:
            ano = p
        if "T" in p and p.endswith(".csv"):
            trimestre = p.replace(".csv", "")

    return ano, trimestre

def extrair_despesas_de_arquivo(caminho):
    df = ler_arquivo(caminho)
    if df is None:
        return None

    df_cols_upper = {c.upper().strip(): c for c in df.columns}

    col_desc = None
    col_reg_ans = None
    col_valor_final = None

    for nome_upper, nome_original in df_cols_upper.items():
        if "DESCRICAO" in nome_upper:
            col_desc = nome_original
        if "REG_ANS" in nome_upper or "REG ANS" in nome_upper:
            col_reg_ans = nome_original
        if "VL_SALDO_FINAL" in nome_upper or "SALDO FINAL" in nome_upper:
            col_valor_final = nome_original

    if not col_desc or not col_reg_ans or not col_valor_final:
        print(f"Arquivo sem colunas necessárias (DESCRICAO/REG_ANS/VL_SALDO_FINAL): {caminho}")
        return None

    mask = df[col_desc].astype(str).str.lower().str.contains("|".join(palavras_chave))
    df_filtrado = df[mask].copy()

    if df_filtrado.empty:
        print(f"Nenhuma linha de despesas encontrada em: {caminho}")
        return None

    ano, trimestre = extrair_ano_trimestre(caminho)

    df_saida = pd.DataFrame()
    df_saida["REG_ANS"] = df_filtrado[col_reg_ans].astype(str)
    df_saida["ValorDespesas"] = pd.to_numeric(df_filtrado[col_valor_final], errors="coerce")
    df_saida["Ano"] = ano
    df_saida["Trimestre"] = trimestre

    return df_saida

def consolidar_despesas():
    arquivos = listar_arquivos_extraidos()
    dfs = []

    for arq in arquivos:
        print(f"\nProcessando arquivo: {arq}")
        df_desp = extrair_despesas_de_arquivo(arq)
        if df_desp is not None:
            dfs.append(df_desp)

    if not dfs:
        print("Nenhum dado de despesas foi encontrado.")
        return None

    df_final = pd.concat(dfs, ignore_index=True)

    df_final["flag_valor_zero_ou_negativo"] = df_final["ValorDespesas"] <= 0

    return df_final

if __name__ == "__main__":
    print("Arquivos extraídos:")
    arquivos = listar_arquivos_extraidos()
    for arq in arquivos:
        print(" -", arq)

    print("\nInspecionando colunas de cada arquivo...")
    for arq in arquivos:
        df = ler_arquivo(arq)
        if df is None:
            continue

    print(f"\nArquivo: {arq}")
    print("Colunas:")
    for c in df.columns:
        print(" -", c)

    df_consolidado = consolidar_despesas()

    if df_consolidado is not None:
        df_consolidado.to_csv("consolidado_despesas_parte1.csv", index=False, encoding="utf-8")

        import zipfile
        with zipfile.ZipFile("consolidado_despesas.zip", "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write("consolidado_despesas_parte1.csv")

        print("consolidado_despesas_parte1.csv e consolidado_despesas.zip gerados.")