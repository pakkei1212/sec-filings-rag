from langchain_ollama import ChatOllama
from langchain.agents import initialize_agent, AgentType, create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.retrieval.retriever_tool import sec_retriever_tool
from configs.prompts import SYSTEM_PROMPT
from configs.models import AGENT_MODEL, OLLAMA_HOST

SYSTEM_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

llm = ChatOllama(
    model=AGENT_MODEL,
    temperature=0,
    base_url=OLLAMA_HOST,
)

agent = create_tool_calling_agent(
    llm=llm,          # Qwen 2.5 7B
    tools=[sec_retriever_tool],
    prompt=SYSTEM_PROMPT_TEMPLATE
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=[sec_retriever_tool],
    handle_parsing_errors=True,
    return_intermediate_steps=True,
    verbose=True
)

'''agent_executor = initialize_agent(
    tools=[sec_retriever_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    return_intermediate_steps=True,
    handle_parsing_errors=True,
    agent_kwargs={
        "prefix": SYSTEM_PROMPT
    },
)'''
