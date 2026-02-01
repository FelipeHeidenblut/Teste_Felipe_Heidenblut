import pandas as pd

arq_entrada = "consolidado_despesas_validado_final.csv"
arq_saida = "despesas_agregadas.csv"

def carregar():
    df = pd.read_csv(arq_entrada, encoding="utf-8")
    print("Colunas:", df.columns.tolist())
    return df

def filtrar_dados(df):
    # usar apenas linhas com valor numérico válido e positivo
    df = df.copy()
    if "ValorDespesas_num" in df.columns:
        valor = df["ValorDespesas_num"]
    else:
        valor = pd.to_numeric(df["ValorDespesas"], errors="coerce")

    df["ValorDespesas_num"] = valor
    df = df[df["ValorDespesas_num"].notna()]
    df = df[df["ValorDespesas_num"] > 0]
    # também filtrar quem não tem RazaoSocial ou UF
    df = df[df["RazaoSocial"].notna() & (df["RazaoSocial"].astype(str).str.strip() != "")]
    df = df[df["UF"].notna() & (df["UF"].astype(str).str.strip() != "")]
    return df

def agregar(df):
    # agrupar por RazaoSocial e UF
    grupo = df.groupby(["RazaoSocial", "UF"])["ValorDespesas_num"]

    # total, média e desvio padrão
    agg = grupo.agg(
        TotalDespesas="sum",
        MediaDespesas="mean",
        DesvioPadrao="std"
    ).reset_index()

    # ordenar por total (maior para menor)
    agg = agg.sort_values("TotalDespesas", ascending=False)

    return agg

if __name__ == "__main__":
    df = carregar()
    df_filtrado = filtrar_dados(df)
    print("Linhas após filtro:", len(df_filtrado))

    df_agregado = agregar(df_filtrado)
    print("Linhas agregadas:", len(df_agregado))

    df_agregado.to_csv(arq_saida, index=False, encoding="utf-8")
    print(f"Arquivo {arq_saida} gerado.")