from src.retrieval.agent import agent_executor
from src.generation.answer_generator import build_context
from configs.prompts import ANSWER_PROMPT

from langchain_ollama import ChatOllama
from configs.models import AGENT_MODEL, OLLAMA_HOST


# ✅ Generation-only LLM (CRITICAL FIX)
generation_llm = ChatOllama(
    model=AGENT_MODEL,
    temperature=0,
    base_url=OLLAMA_HOST,
)


def ask(question: str):
    print("A: entered ask()")

    result = agent_executor.invoke({"input": question})
    print("B: agent_executor finished")

    intermediate_steps = result.get("intermediate_steps", [])
    print("C: intermediate_steps =", len(intermediate_steps))

    retrieved_docs = []
    retrieved_metas = []

    for action, observation in intermediate_steps:
        if action.tool == "sec_retriever_tool":
            print("D: sec_retriever_tool executed")
            retrieved_docs.extend(observation["documents"][0])
            retrieved_metas.extend(observation["metadatas"][0])

    if not retrieved_docs:
        print("E: no documents retrieved")
        return "No relevant SEC disclosures were found."

    print("F: retrieved_docs =", len(retrieved_docs))
    print("Retrieval Output:", retrieved_docs)
    print("Metadata:", retrieved_metas)

    context = build_context(retrieved_docs, retrieved_metas)
    print("G: context length =", len(context))

    summary_prompt = ANSWER_PROMPT.format(
        question=question,
        context=context,
    )

    print("H: ABOUT TO GENERATE ANSWER")
    final_answer = generation_llm.invoke(summary_prompt)

    print("I: RAW LLM RESPONSE =", final_answer)
    print("J: CONTENT =", repr(final_answer.content))

    return final_answer.content


if __name__ == "__main__":
    q = "How did Apple’s management oversee legal proceedings in 2019?"
    print("FINAL ANSWER:")
    print(ask(q))
