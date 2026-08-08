# Research ReAct Agent

Agente autônomo construído com **LangGraph** que implementa a arquitetura **ReAct (Reasoning + Acting)** — o agente raciocina sobre a pergunta do usuário, decide se precisa pesquisar na web, executa a busca, injeta o contexto no histórico e responde com base nas informações coletadas.

---

## Como funciona

O agente segue um grafo de decisão com três nodes:

```
__start__
    ↓
call_llm → router → tool_calling → call_llm (loop)
                ↓
            __end__
```

1. **call_llm** — o LLM recebe a pergunta e decide se usa a tool de pesquisa ou responde direto
2. **router** — verifica se a resposta do LLM contém tool calls
3. **tool_calling** — executa a busca na web, extrai o conteúdo das páginas e injeta no histórico
4. O LLM lê o novo contexto e gera a resposta final

A pesquisa usa **DuckDuckGo** para encontrar os links e **Trafilatura** para extrair o conteúdo das páginas. Se a extração falhar, o fallback é o **Jina AI Reader**.

---

## Stack

- [LangGraph](https://github.com/langchain-ai/langgraph) — orquestração do grafo de agente
- [LangChain](https://github.com/langchain-ai/langchain) — integração com LLMs e tools
- [Groq](https://groq.com) — inferência do modelo (`openai/gpt-oss-20b`)
- [DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/) — busca na web
- [Trafilatura](https://trafilatura.readthedocs.io) — extração de conteúdo de páginas
- [Rich](https://rich.readthedocs.io) — output formatado no terminal

---

## Instalação

```bash
git clone https://github.com/louuispy/research-react-agent.git
cd research-react-agent
pip install -r requirements.txt
```

Configure sua chave da Groq:

```bash
export GROQ_API_KEY=sua_chave_aqui
```

---

## Como rodar

```bash
python main.py
```

O agente entra em loop interativo. Digite sua pergunta e pressione Enter. Para sair, digite `Q`.

```
Digite sua pergunta ([Q] para sair): Quais são as últimas notícias sobre IA?
>>> Call LLM
>>> Router
>>> Tool
>>> Tool Calling
>>> Call LLM
>>> Router

De acordo com as pesquisas mais recentes...
```

---

## Estrutura do projeto

```
research-react-agent/
├── .vscode          # pasta com meu settings.json de ambiente de desenvolvimento em Python
├── .gitignore
├── .python-version  # versão do Python utilizada no projeto
├── README.md
├── main.py          # código principal do agente
├── pyproject.toml
└── uv.lock         
```

---

## Autor

**Luís Henrique** — [github.com/louuispy](https://github.com/louuispy) · [linkedin.com/in/luishenrique-ia](https://linkedin.com/in/luishenrique-ia)
