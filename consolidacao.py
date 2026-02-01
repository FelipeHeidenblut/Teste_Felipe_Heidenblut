import pandas as pd

arquivo_consolidado = "consolidado_despesas_parte1.csv"

def carregar_consolidado():
    df = pd.read_csv(arquivo_consolidado, encoding="utf-8")
    return df

def validar_valores(df):
    df["valor_numerico"] = pd.to_numeric(df["ValorDespesas"], errors="coerce")
    df["flag_valor_invalido"] = df["valor_numerico"].isna()
    df["flag_valor_negativo_ou_zero"] = df["valor_numerico"] <= 0
    return df

if __name__ == "__main__":
    df = carregar_consolidado()
    print("Colunas iniciais:", df.columns.tolist())

    df = validar_valores(df)

    print("\nResumo de validação de valores:")
    print("Total de linhas:", len(df))
    print("Valores inválidos (não numéricos):", df["flag_valor_invalido"].sum())
    print("Valores negativos ou zero:", df["flag_valor_negativo_ou_zero"].sum())

    df.to_csv("consolidado_despesas_validado_parcial.csv", index=False, encoding="utf-8")
    print("\nArquivo consolidado_despesas_validado_parcial.csv gerado.")