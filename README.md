# Teste Técnico - Felipe Heidenblut

## 📋 Estrutura do Projeto

```text
Teste_FelipeHeidenblut/
├── Parte1_download/       # Scripts de extração (Scraping)
├── Parte2_transformacao/  # Scripts de limpeza, validação e agregação
├── Parte3_banco/          # Criação do banco e queries analíticas
├── Parte4_Vue_API/      # Backend FastAPI e Frontend Vue
└── README.md

🛠️ Pré-requisitos

Certifique-se de ter o Python instalado. Instale as dependências globais ou em um ambiente virtual:
Bash

pip install pandas requests beautifulsoup4 fastapi uvicorn

-> Como Rodar o Projeto

Siga a ordem abaixo para garantir o fluxo correto dos dados.
Parte 1 - Download e Consolidação

Responsável por baixar os dados da ANS e fazer a primeira consolidação.
Bash

cd parte1_download
python arquivosans.py
# Resultado: Baixa e extrai os CSVs em DownloadsAns/2025/extraido/

Bash

python consolidacao.py
# Resultado: Gera consolidado_despesas.zip

Parte 2 - Validação e Agregação

Enriquece os dados com informações cadastrais, valida a qualidade e gera os números finais.
Bash

cd parte2_transformacao
python enriquecimento.py        # Cruza com dados do Cadop (Razão Social, UF)
python validacao_simplificada.py # Gera flags de erro (CNPJ, Valores)
python agregacao.py             # Gera o CSV final agregado

Parte 3 - Banco de Dados (MySQL)

    Abra o seu cliente MySQL (ex: Workbench ou DBeaver).

    Abra o arquivo banco_dados.sql.

    Atenção: Ajuste os caminhos dos arquivos CSV dentro do script SQL para o caminho local da sua máquina.

    Execute o script para criar o banco ans_teste, tabelas e importar os dados.

    As queries analíticas estão ao final do arquivo script.

Parte 4 - API + Frontend

Para iniciar o servidor da API e visualizar os dados:
Bash

cd Parte4_Vue_API
uvicorn main:app --reload

    Acesse no navegador: Abra o arquivo parte4_api_front/frontend/index.html (ou via Live Server).

    Rotas da API disponíveis:

        GET /api/operadoras (Lista paginada)

        GET /api/operadoras/{cnpj} (Detalhes)

        GET /api/estatisticas (Resumo geral)

🧠 Explicação dos Scripts
arquivosans.py

    Acessa o FTP da ANS via scraping.

    Identifica e baixa os 3 últimos trimestres disponíveis do ano mais recente.

    Extrai os ZIPs automaticamente.

consolidacao.py

    Lê os CSVs brutos e filtra apenas linhas relevantes ("despesa", "sinistro", "evento").

    Consolida tudo em um único arquivo consolidado_despesas_parte1.csv (~497k linhas).

enriquecimento.py

    Baixa o Relatorio_cadop.csv (fonte oficial da ANS).

    Realiza o join utilizando o campo REG_ANS (chave mais confiável que o CNPJ neste contexto).

validacao.py

Gera um arquivo com flags de qualidade, sem deletar os dados originais:

    ✅ Valores: Identifica não numéricos e negativos/zero.

    ✅ CNPJ: Verifica tamanho (14 dígitos).

    ✅ Razão Social: Identifica campos vazios.

agregacao.py

    Aplica os filtros de negócio (apenas valores válidos e positivos).

    Agrupa por RazaoSocial + UF.

    Calcula estatísticas: Total, Média e Desvio Padrão.

💡 Decisões de Projeto

Durante o desenvolvimento, tomei as seguintes decisões técnicas:

    Tratamento de Erros (Soft Delete): Optei por criar colunas de flags (flag_cnpj_invalido, flag_valor_zero) em vez de excluir as linhas inválidas imediatamente. Isso permite auditoria dos dados descartados.

    Chave de Join: Utilizei o REG_ANS para cruzar as tabelas, pois o CNPJ nos arquivos de despesas muitas vezes apresentava formatação inconsistente.

    Performance: Para o escopo do teste, o carregamento dos CSVs (~500k linhas) é feito em memória com Pandas, o que garante rapidez sem complexidade de infraestrutura.

    SQL: Utilizei DECIMAL(18,2) para garantir precisão monetária e normalizei os dados em 3 tabelas para evitar redundância.

📊 Resultados Alcançados

    Total de linhas processadas: 497.784

    Dados válidos para análise: 13.354 (após filtros rigorosos de valores positivos e CNPJs válidos)

    Problemas identificados: Alto índice de CNPJs com formatação inválida nos arquivos originais (~79%), contornado via uso do REG_ANS.

Obrigado pela oportunidade! 🚀