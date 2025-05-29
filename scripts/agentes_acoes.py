import os
import pandas as pd
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import AzureChatOpenAI
# from crewai.tools import SerperDevTool

# Load environment variables from .env file
load_dotenv

# tool = SerperDevTool()
from langchain_community.tools import DuckDuckGoSearchRun

tool = DuckDuckGoSearchRun()


llm = AzureChatOpenAI(
    model="azure/" + os.getenv("AZURE_OPENAI_DEPLOYMENT_LLM"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_API_VERSION"),
    temperature=0.3
)

# === Ler os novos arquivos CSV localmente ===
try:
    df_top_10_acoes = pd.read_csv("data/top_10_acoes.csv")
    df_noticias_investimento = pd.read_csv("data/noticias_investimentos.csv")
    df_indices = pd.read_csv("data/indicadores_economicos.csv")
except FileNotFoundError as e:
    print(f"Erro: Arquivo CSV não encontrado. Verifique os nomes e caminhos dos arquivos: {e}")
    print("Certifique-se que 'top_10_acoes.csv', 'noticias_investimento.csv' e 'indicadores_economicos.csv' estão na raiz do projeto.")
    exit()

# === Transformar os DataFrames em texto de contexto ===
contexto_top_10_acoes = df_top_10_acoes.to_markdown(index=False)
contexto_indices = df_indices.to_markdown(index=False)

# Assumindo que df_noticias_investimento tem colunas 'titulo', 'resumo', 'link'
# Ajuste se os nomes das colunas forem diferentes
contexto_noticias_investimentos = "\n".join([
    f"Título: {row['titulo']}\nLink: {row['link']}"
    for _, row in df_noticias_investimento.iterrows()
]) if not df_noticias_investimento.empty else "Nenhuma notícia de investimento carregada do CSV."

# === Juntar todo o contexto BASE (dos CSVs) ===
contexto_geral_csv = f"""
=== 📉 Dados Históricos de Índices Econômicos ===
{contexto_indices}

=== 📰 Notícias de Investimento Recentes (do CSV) ===
{contexto_noticias_investimentos}

=== 📊 Top 10 Ações (do CSV) ===
{contexto_top_10_acoes}
"""

azure_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_LLM")

from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool

# Converte para Tool compatível com CrewAI
search_tool = Tool.from_function(
    func=tool.run,
    name="Search",
    description="Use esta ferramenta para buscar informações atualizadas na web sobre economia, empresas ou ações."
)


# === Definir os agentes ===
analista_macroeconomico = Agent(
    role="Analista Macroeconômico Sênior",
    goal="Analisar o cenário macroeconômico brasileiro, com foco nos indicadores econômicos e nas notícias de investimento, para identificar tendências.",
    backstory="Economista com vasta experiência na análise da conjuntura econômica brasileira, indicadores econômicos e seus efeitos sobre o mercado de ações.",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
    llm=llm,
    model_name=f"azure/{azure_deployment_name}"
)

especialista_em_acoes = Agent(
    role="Especialista em Análise de Ações da Bovespa",
    goal="Avaliar ações da Bovespa, com ênfase nas 'top_10_acoes.csv' mas não se limitando a elas, com base na análise macroeconômica, dados financeiros e notícias.",
    backstory="Analista de investimentos (CNPI) focado no mercado de ações brasileiro, com expertise em valuation de empresas e estratégias de investimento.",
    verbose=True,
    allow_delegation=False,  # Pode se tornar True se houver um agente de pesquisa de dados fundamentalistas dedicado
    tools=[search_tool],
    llm=llm,
    model_name=f"azure/{azure_deployment_name}"
)
redator_de_relatorios_de_investimento = Agent(
    role="Redator de Relatórios de Investimento",
    goal="Consolidar a análise macroeconômica e as recomendações de ações em um relatório final claro, conciso e bem estruturado para investidores.",
    backstory="Profissional de comunicação com foco no mercado financeiro, especializado em transformar análises técnicas complexas em relatórios acessíveis e objetivos.",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
    llm=llm,
    model_name=f"azure/{azure_deployment_name}"
)

# === Criar as tarefas ===
tarefa_analise_cenario = Task(
    description=(
        "1. Analise os dados dos indicadores econômicos fornecidos no 'contexto_geral_csv' para entender as tendências recentes do mercado.\n"
        "2. Revise as 'Notícias de Investimento Recentes (do CSV)' para capturar o sentimento e os eventos atuais do mercado.\n"
        "3. Utilize a ferramenta SerPerDevTool para buscar informações atualizadas (últimos 1–3 meses) sobre: \n"
        "   a) Perspectivas para o IPCA, PIB, dólar, IGP-M e a taxa Selic no Brasil. \n"
        "   b) Principais fatores macroeconômicos que estão afetando o mercado de ações brasileiro. \n"
        "   c) Notícias relevantes sobre a economia brasileira que possam impactar investimentos.\n"
        "4. Sintetize essas informações para construir um panorama do cenário macroeconômico atual e suas implicações para investidores em geral.\n"
        "Contexto dos CSVs:\n"
        f"{contexto_geral_csv}"
    ),
    expected_output=(
        "Um relatório conciso sobre o cenário macroeconômico brasileiro, destacando: \n"
        "- Análise da trajetória recente dos índices econômicos obtidos e suas perspectivas.\n"
        "- Principais notícias e eventos de investimento relevantes (do CSV e da pesquisa online).\n"
        "- Impactos esperados desse cenário no mercado de ações brasileiro em geral."
    ),
    agent=analista_macroeconomico
)

tarefa_indicacao_acoes = Task(
    description=(
        "1. Com base na análise do cenário macroeconômico (fornecida pela tarefa anterior), avalie as ações listadas no arquivo 'top_10_acoes.csv'.\n"
        "2. Para cada ação no 'top_10_acoes.csv', utilize a ferramenta SerperDevTool para buscar:\n"
        "   a) Notícias recentes e específicas sobre a empresa e seu setor. \n"
        "   b) Análises e perspectivas de mercado para essa ação (preço-alvo, recomendações de outras casas de análise, etc.). \n"
        "   c) Informações sobre os fundamentos da empresa, se não estiverem detalhados no CSV (ex: P/L, dividend yield, endividamento).\n"
        "3. Se julgar pertinente, pesquise também outras ações da Bovespa que possam representar boas oportunidades ou riscos no cenário atual.\n"
        "4. Formule recomendações de INVESTIMENTO (COMPRA, VENDA ou MANTER) para pelo menos 5 ações (priorizando as do 'top_10_acoes.csv').\n"
        "Contexto dos CSVs (especialmente 'Top 10 Ações'):\n"
        f"{contexto_top_10_acoes}  # Foco principal, mas não exclusivo"
    ),
    expected_output=(
        "Um relatório de indicações de ações contendo:\n"
        "- Recomendações claras de COMPRA, VENDA ou MANTER para 3 a 5 ações da Bovespa (com seus tickers).\n"
        "- Justificativa detalhada para cada recomendação, explicando os fatores considerados (macroeconômicos, setoriais, específicos da empresa).\n"
        "- Priorizar as ações do 'top_10_acoes.csv' na análise, mas incluir outras se forem identificadas oportunidades/ricos relevantes."
    ),
    agent=especialista_em_acoes
)

tarefa_compilacao_relatorio_final = Task(
    description=(
        "**Sua responsabilidade é GERAR e ESCREVER O CONTEÚDO COMPLETO do relatório de investimento final em formato markdown. NÃO descreva a tarefa, execute-a.**\n"
        "Para fazer isso, você DEVE:\n"
        "1. Unificar a 'análise do cenário macroeconômico' (fornecida pelo Analista Macroeconômico) e as 'indicações de ações' (fornecidas pelo Especialista em Ações).\n"
        "2. Escrever o relatório em linguagem clara, profissional e acessível para investidores, utilizando a sintaxe markdown para uma estrutura bem organizada.\n"
        "3. Detalhar as principais conclusões da análise macroeconômica e explicar explicitamente como elas fundamentam as estratégias de investimento.\n"
        "4. Apresentar de forma proeminente e individualizada cada indicação de ação (COMPRA, VENDA, MANTER), incluindo o ticker da ação e a justificativa.\n"
        "5. Incluir um breve apêndice ao final do relatório mencionando as fontes de dados primárias (os arquivos CSV: 'indicadores_economicos.csv', 'top_10_acoes.csv' e 'noticias_investimentos.csv').\n"
        "**Utilize as informações das análises das tarefas anteriores, que estão disponíveis no contexto, como base fundamental para escrever.**"
    ),
    expected_output=(
        "O TEXTO COMPLETO e FINAL de um Relatório de Investimento em formato markdown na língua portuguesa do Brasil. O relatório DEVE seguir a seguinte estrutura:\n"
        "### Sumário Executivo\n"
        " - (Texto do sumário com as principais conclusões e recomendações de investimento.)\n"
        "### Análise do Cenário Macroeconômico\n"
        " - (Texto da análise detalhada dos indicadores econômicos, notícias relevantes e seus impactos esperados no mercado de ações.)\n"
        "### Indicações de Ações Detalhadas\n"
        " - (Para cada ação recomendada: Ticker, Recomendação [COMPRA/VENDA/MANTER], e Justificativa completa e bem fundamentada.)\n"
        "### Breves Considerações sobre Riscos e Oportunidades\n"
        " - (Texto com uma visão geral dos riscos e oportunidades identificados no cenário atual.)\n"
        "### Apêndice: Fontes de Dados\n"
        " - (Texto mencionando as fontes de dados utilizadas.)"
    ),
    agent=redator_de_relatorios_de_investimento,
    context=[tarefa_analise_cenario, tarefa_indicacao_acoes],
)

# === Criar o time (Crew) ===
crew_recomendacao_de_acoes = Crew(
    agents=[analista_macroeconomico, especialista_em_acoes, redator_de_relatorios_de_investimento],
    tasks=[tarefa_analise_cenario, tarefa_indicacao_acoes, tarefa_compilacao_relatorio_final],
    verbose=True,  # verbose=True para ver os pensamentos dos agentes
    manager_llm=llm,
    # process=Process.hierarchical,  # Habilita o "gerente" para orquestrar com mais "raciocínio"
)

# === Executar o Crew ===
print("Iniciando a análise da Crew para recomendação de ações...")
resultado_crew = crew_recomendacao_de_acoes.kickoff()  # Mudei o nome da variável para clareza

print("\n\n=== OBJETO CrewOutput COMPLETO (para depuração) ===\n")
print(resultado_crew)  # Isso vai mostrar a estrutura do objeto CrewOutput

if hasattr(resultado_crew, 'raw') and isinstance(resultado_crew.raw, str):
    texto_para_salvar = resultado_crew.raw
elif hasattr(resultado_crew, 'result') and isinstance(resultado_crew.result, str):  # Comum em versões mais antigas ou específicas
    texto_para_salvar = resultado_crew.result
else:
    # Se não houver um atributo óbvio, converter o objeto todo para string
    texto_para_salvar = str(resultado_crew)

print("\n\n=== RELATÓRIO FINAL DE INVESTIMENTO GERADO PELA CREW (TEXTO) ===\n")
print(texto_para_salvar)

# === Salvar o resultado em um arquivo .md ===
nome_arquivo_saida = "../data/relatorio_indicacao_acoes.md"
with open(nome_arquivo_saida, "w", encoding="utf-8") as f:
    f.write(texto_para_salvar)  # Agora estamos passando uma string
print(f"\n\nRelatório salvo em '{nome_arquivo_saida}'")
