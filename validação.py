import pandas as pd

arq_entrada = "consolidado_despesas_enriquecido.csv"
arq_saida = "consolidado_despesas_validado_final.csv"

def carregar():
    df = pd.read_csv(arq_entrada, encoding="utf-8")
    print("Colunas:", df.columns.tolist())
    return df

def validar_valores(df):
    df = df.copy()
    df["ValorDespesas_num"] = pd.to_numeric(df["ValorDespesas"], errors="coerce")
    df["flag_valor_invalido"] = df["ValorDespesas_num"].isna()
    df["flag_valor_negativo_ou_zero"] = df["ValorDespesas_num"] <= 0
    return df

def limpar_cnpj_basico(cnpj_str):
    
    return "".join(ch for ch in str(cnpj_str) if ch.isdigit())

def validar_cnpj_basico(cnpj_str):
    cnpj = limpar_cnpj_basico(cnpj_str)
    
    return len(cnpj) == 14

def aplicar_validacao_cnpj_razao(df):
    df = df.copy()

    
    if "CNPJ" not in df.columns:
        df["flag_cnpj_invalido"] = False
    else:
        df["CNPJ_limpo"] = df["CNPJ"].apply(limpar_cnpj_basico)
        df["flag_cnpj_invalido"] = ~df["CNPJ_limpo"].apply(validar_cnpj_basico)

    if "RazaoSocial" not in df.columns:
        df["flag_razao_vazia"] = False
    else:
        df["flag_razao_vazia"] = df["RazaoSocial"].isna() | (df["RazaoSocial"].astype(str).str.strip() == "")

    return df

if __name__ == "__main__":
    df = carregar()

    df = validar_valores(df)
    df = aplicar_validacao_cnpj_razao(df)

    print("\nResumo de validação (simplificado):")
    print("Total linhas:", len(df))
    print("Valores inválidos (não numéricos):", df["flag_valor_invalido"].sum())
    print("Valores negativos ou zero:", df["flag_valor_negativo_ou_zero"].sum())
    print("CNPJs inválidos (comprimento != 14 dígitos):", df["flag_cnpj_invalido"].sum())
    print("Razão Social vazia:", df["flag_razao_vazia"].sum())

    df.to_csv(arq_saida, index=False, encoding="utf-8")
    print(f"\nArquivo {arq_saida} gerado.")