import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import zipfile

url_base = "https://dadosabertos.ans.gov.br/FTP/PDA/"
pasta_arquivos = "DownloadsAns"

#Criar diretório para baixar arquivos
def diretorio_arquivos(caminho):
    if not os.path.exists(caminho):
        os.makedirs(caminho)

#Buscar pasta "Demonstrações contábeis"
def obter_soup(url):
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

#Encontrar pastas no link da ANS
def encontrar_pasta():
    soup = obter_soup(url_base)

    for link in soup.find_all("a"):
        texto = link.get_text(strip=True).lower()
        href = link.get("href", "").lower()
        print(f"Texto: {texto} | Href: {href}")

        if "demonstrac" in texto or "demonstrac" in href:
            url_completa = urljoin(url_base, link.get("href"))
            print("Encontrei a pasta de demonstrações:")
            print("Texto:", texto)
            print("Href:", href)
            print("URL completa:", url_completa)
            return url_completa

    print("Não encontrei pasta de demonstrações.")
    return None

#listar os anos das pastas do mais recente para o mais antigo
def listar_anos(url_demonstracoes):
    soup = obter_soup(url_demonstracoes)
    if not soup:
        return []

    anos = []

    for link in soup.find_all("a"):
        texto = link.get_text(strip=True).replace("/", "")
        href = link.get("href", "")

        if texto.isdigit() and len(texto) == 4:
            ano = int(texto)
            url_ano = urljoin(url_demonstracoes, href)
            anos.append({"ano": ano, "url": url_ano})

    anos.sort(key=lambda x: x["ano"], reverse=True)
    return anos

#Listar trimestres do mais recente para o mais antigo
def listar_trimestres(ano_info):
    soup = obter_soup(ano_info["url"])
    if not soup:
        return []
    
    trimestres = []

    for link in soup.find_all("a"):
        texto = link.get_text(strip=True)
        href = link.get("href", "")

        # queremos só arquivos .zip
        if not href.endswith(".zip"):
            continue

        # nome do arquivo (3T2025.zip, etc.)
        nome = texto.replace("/", "")
        trimestres.append({
            "ano": ano_info["ano"],
            "trimestre": nome,
            "url": urljoin(ano_info["url"], href)
        })

    trimestres.sort(key=lambda x: x["trimestre"], reverse=True)
    return trimestres

#Criar lista com os ultimos 3 trimestres
def lista_trimestres(qtd = 3):
    url_demonstracoes = encontrar_pasta()
    if not url_demonstracoes:
        print("Não achei a pasta de demonstrações.")
        return []

    anos = listar_anos(url_demonstracoes)
    if not anos:
        print("Nenhum ano encontrado.")
        return []

    ano_recente = anos[0]
    trimestres_ano = listar_trimestres(ano_recente)

    if not trimestres_ano:
        print("Nenhum trimestre encontrado para o ano mais recente.")
        return []

    return trimestres_ano[:qtd]

#Baixar arquivos zip
def baixar_arquivos(trimestre_info):
    ano = str(trimestre_info["ano"])
    nome_arquivo = trimestre_info["trimestre"]
    url_zip = trimestre_info["url"]

    pasta_ano = os.path.join(pasta_arquivos, ano)
    diretorio_arquivos(pasta_ano)

    caminho_arquivos = os.path.join(pasta_ano, nome_arquivo)
    print(f"Baixando {url_zip}...")

    try:
        resp = requests.get(url_zip, stream=True, timeout=60)
        resp.raise_for_status()

        with open(caminho_arquivos, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"Salvo em: {caminho_arquivos}")
    except Exception as e:
        print(f"Erro ao baixar {url_zip}: {e}")

#Extrair arquivos Zip
def extrair_zip(caminho_zip):
    pasta_zip = os.path.dirname(caminho_zip)
    pasta_extraido = os.path.join(pasta_zip, "extraido")

    if not os.path.exists(pasta_extraido):
        os.makedirs(pasta_extraido)

    print(f"Extraindo {caminho_zip} para {pasta_extraido}...")
    try:
        with zipfile.ZipFile(caminho_zip, "r") as zf:
            zf.extractall(pasta_extraido)
        print("Extração concluída.")
    except Exception as e:
        print(f"Erro ao extrair {caminho_zip}: {e}")

#Listar arquivos
def listar_arquivos_extraidos():
    arquivos_encontrados = []

    for raiz, pastas, arquivos in os.walk(pasta_arquivos):
        if "extraido" not in raiz:
            continue

        for nome in arquivos:
            caminho = os.path.join(raiz, nome)
            arquivos_encontrados.append(caminho)

    return arquivos_encontrados

#Main
if __name__ == "__main__":
    url_demonstracoes = encontrar_pasta()
    print("URL demonstracoes:", url_demonstracoes)

    if not url_demonstracoes:
        print("Não foi possível localizar a pasta de demonstrações.")
    else:
        anos = listar_anos(url_demonstracoes)
        for item in anos:
            print(item["ano"], "->", item["url"])

    ano_recente = anos[0]
    print("\nAno mais recente:", ano_recente["ano"])
    print("URL do ano mais recente:", ano_recente["url"])

    ultimos = lista_trimestres(qtd=3)

    print("Últimos 3 trimestres do ano mais recente:")
    for t in ultimos:
        print(f"Ano: {t['ano']} | Trimestre: {t['trimestre']} | URL: {t['url']}")

    print("\nIniciando downloads...")
    caminhos_zips = []
    for t in ultimos:
        ano = str(t["ano"])
        nome_arquivo = t["trimestre"]
        pasta_ano = os.path.join(pasta_arquivos, ano)
        caminho_zip = os.path.join(pasta_ano, nome_arquivo)
        # garante que o zip existe, senão baixa
        if not os.path.exists(caminho_zip):
            baixar_arquivos(t)
        caminhos_zips.append(caminho_zip)

    print("\nExtraindo arquivos ZIP...")
    for caminho in caminhos_zips:
        extrair_zip(caminho)

    print("\nListando arquivos extraídos...")
    todos_extraidos = listar_arquivos_extraidos()
    print(f"Total de arquivos extraídos: {len(todos_extraidos)}")
