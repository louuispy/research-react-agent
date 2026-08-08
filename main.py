from collections.abc import Sequence
from operator import add
from typing import Annotated, Literal, TypedDict

import requests
import trafilatura
from ddgs import DDGS
from langchain.chat_models import BaseChatModel, init_chat_model
from langchain.tools import BaseTool, tool
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import StateGraph
from rich import print


class State(TypedDict):
    messages: Annotated[
        Sequence[BaseMessage | ToolMessage | HumanMessage | AIMessage | SystemMessage],
        add,
    ]


@tool
def web_search_tool(search_subject: str) -> dict:
    """Use this tool (called `web_search_tool`) everytime when the user ask you something that you neeed to research to get
    the information suficiently to answer the user question.

    Args:
        search_subject (str): this arg is a string that contains the subject of the search

    Returns: a dictionary with all data of research

    """
    print(">>> Tool")
    with DDGS() as ddgs:
        dict_dados_pesquisa = {}

        results = ddgs.text(
            query=f"{search_subject}",
            region="wt-wt",
            safesearch="moderate",
            timelimit="y",
            max_results=3,
        )

        for result in results:
            link = result["href"]
            title = result["title"]

            html = trafilatura.fetch_url(link)
            texto = trafilatura.extract(html)
            if texto:
                dict_dados_pesquisa[f"{title=}"] = texto[:1000]
            else:
                texto = requests.get(f"https://r.jina.ai/{link}", timeout=15).text
                dict_dados_pesquisa[f"{title=}"] = texto[:1000]

    return dict_dados_pesquisa


tools: list[BaseTool] = [web_search_tool]
tool_by_name = {tool.name: tool for tool in tools}


def call_llm(state: State) -> State:
    print(">>>  Call LLM")

    system_message: SystemMessage = SystemMessage("""
    You're an intelligent and helpfull assistant, that answer every user doubt with a directly response.
    If the question requires a long response, you'll generate a long response. Else, you'll generate a short response.
    Every doubt that the user send you, before answer it, you'll look if you have a tool that solves the user problem. 
    """)

    llm: BaseChatModel = init_chat_model(
        model="openai/gpt-oss-20b", model_provider="groq", temperature=0.4
    )

    llm_with_tools = llm.bind_tools(tools=tools)

    llm_response: BaseMessage = llm_with_tools.invoke(
        [system_message, *state["messages"]]
    )

    output_state: State = {"messages": [llm_response]}

    return output_state


def tool_calling(state: State) -> State:
    print(">>>  Tool Calling")

    llm_response = state["messages"][-1]

    call = llm_response.tool_calls[-1]  # pyright: ignore[reportAttributeAccessIssue]
    name, args, tool_id = call["name"], call["args"], call["id"]

    try:
        content_tool_call = tool_by_name[name].invoke(args)
        status = "success"
    except (KeyError, IndexError, TypeError) as error:
        content_tool_call = f"Por favor, corrija os seus erros: {error}"
        status = "error"

    tool_message: ToolMessage = ToolMessage(
        content=content_tool_call, tool_call_id=tool_id, status=status
    )

    output_state: State = {"messages": [tool_message]}

    return output_state


def router(state: State) -> Literal["tool_calling", "__end__"]:
    print(">>> Router")
    if isinstance(state["messages"][-1], AIMessage) and getattr(
        state["messages"][-1], "tool_calls", None
    ):
        return "tool_calling"
    return "__end__"


state_graph = StateGraph(State)

state_graph.add_node("call_llm", call_llm)
state_graph.add_node("tool_calling", tool_calling)

state_graph.add_edge("__start__", "call_llm")

state_graph.add_conditional_edges(source="call_llm", path=router)

state_graph.add_edge("tool_calling", "call_llm")

compiled_graph = state_graph.compile()

while True:
    input_user: str = input("Digite sua pergunta ([Q] para sair): ")

    if input_user in ["Q", "q"]:
        print("Até logo!")
        break

    resposta = compiled_graph.invoke({"messages": [HumanMessage(input_user)]})

    print(resposta["messages"][-1].content)
