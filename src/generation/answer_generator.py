from configs.prompts import ANSWER_PROMPT


def generate_answer(question: str, results: dict) -> str:
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return "No relevant SEC disclosures were found."

    context_blocks = []
    for i, (doc, meta) in enumerate(zip(documents, metadatas), 1):
        context_blocks.append(
            f"[{i}] {meta['company']} "
            f"Form 10-K ({meta['fiscal_year']}), "
            f"{meta['section']}\n{doc}"
        )

    context = "\n\n".join(context_blocks)

    return ANSWER_PROMPT.format(
        question=question,
        context=context,
    )

def build_context(docs, metas):
    blocks = []
    for doc, meta in zip(docs, metas):
        block = f"""
[Fiscal Year: {meta['fiscal_year']} | Accession: {meta['accession']} | Chunk: {meta['chunk_index']}]
{doc}
"""
        blocks.append(block.strip())
    return "\n\n".join(blocks)



