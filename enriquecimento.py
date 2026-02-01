import os
import requests
import pandas as pd

url_cadastro = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"
arquivo_cadastro = "Relatorio_cadop.csv"
arquivo_consolidado = "consolidado_despesas_parte1.csv"

def baixar_cadastros():
    if os.path.exists(arquivo_cadastro):
        print(f"{arquivo_cadastro} já existe.")
        return

    print(f"Baixando cadastro de operadoras em {url_cadastro}...")
    resp = requests.get(url_cadastro, timeout=60)
    resp.raise_for_status()

    with open(arquivo_cadastro, "wb") as f:
        f.write(resp.content)

    print(f"Salvo em {arquivo_cadastro}")

def carregar_cadastro():
    df = pd.read_csv(arquivo_cadastro, sep=";", encoding="latin1")
    print("Colunas do cadastro:", df.columns.tolist())
    return df

def carregar_consolidado():
    df = pd.read_csv(arquivo_consolidado, encoding="utf-8")
    print("Colunas do consolidado:", df.columns.tolist())
    return df

def normalizar_registro(df, nome_coluna):
    df = df.copy()
    df[nome_coluna] = df[nome_coluna].astype(str).str.strip()
    return df

def preparar_para_join(df_cons, df_cad):
    
    df_cad_ren = df_cad.rename(columns={
        "REGISTRO_OPERADORA": "REG_ANS",
        "Razao_Social": "RazaoSocial"
    })

    
    df_cad_ren = normalizar_registro(df_cad_ren, "REG_ANS")
    df_cons_norm = normalizar_registro(df_cons, "REG_ANS")

    return df_cons_norm, df_cad_ren

def juntar_consolidado_cadastro(df_cons, df_cad_ren):
    
    colunas_cad = ["REG_ANS", "CNPJ", "RazaoSocial", "Modalidade", "UF"]
    df_cad_use = df_cad_ren[colunas_cad]

    
    df_join = df_cons.merge(df_cad_use, on="REG_ANS", how="left", suffixes=("", "_cad"))

    
    df_join["flag_sem_cadastro"] = df_join["CNPJ"].isna()

    
    dup = df_cad_ren["REG_ANS"].duplicated(keep=False)
    regs_duplicados = set(df_cad_ren.loc[dup, "REG_ANS"])
    df_join["flag_reg_ans_duplicado_cad"] = df_join["REG_ANS"].isin(regs_duplicados)

    return df_join

if __name__ == "__main__":
    baixar_cadastros()
    df_cad = carregar_cadastro()
    df_cons = carregar_consolidado()

    df_cons_norm, df_cad_ren = preparar_para_join(df_cons, df_cad)
    df_join = juntar_consolidado_cadastro(df_cons_norm, df_cad_ren)

    print("\nColunas após join:")
    print(df_join.columns.tolist())

    print("\nResumo de cadastro:")
    print("Total linhas:", len(df_join))
    print("Sem cadastro (flag_sem_cadastro):", df_join["flag_sem_cadastro"].sum())
    print("REG_ANS com cadastro duplicado:", df_join["flag_reg_ans_duplicado_cad"].sum())

    df_join.to_csv("consolidado_despesas_enriquecido.csv", index=False, encoding="utf-8")
    print("\nArquivo consolidado_despesas_enriquecido.csv gerado.")