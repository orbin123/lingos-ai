# 4. AI, LangChain, LangGraph, and vector embeddings

## AI capability boundaries

Each capability in `backend/app/ai/` follows an interface + concrete client + exceptions + factory pattern. This makes providers replaceable and lets tests inject stubs. The capabilities are LLM text generation, text-to-speech, speech-to-text, Azure pronunciation assessment, image generation, and embeddings.

## LangChain

LangChain supplies reusable abstractions around model calls, prompts, structured output, and tracing. In this application, agents combine a prompt template, domain input, and an LLM client. Structured Pydantic output schemas constrain the response so downstream code receives a known shape instead of parsing arbitrary prose.

## LangGraph

LangGraph models a workflow as a graph of nodes operating on shared state. `learning_session_graph.py` and `nodes.py` document a flow such as teaching/task/evaluation/feedback. A node reads the current state, performs one bounded operation, and returns state updates. Edges define sequencing or conditional branching. The graph is useful for explicit, testable orchestration; it is not the owner of SQL commits in the live product. `SessionService.submit_activity` remains the transaction authority.

## Agents

The teacher, task generator, evaluator, feedback, planner, personalization, and relevance classifier are prompt-driven collaborators. Session-specific wrappers in `ai/sessions/` adapt those agents to the session service. Prompts live in Markdown and are loaded by `prompt_loader.py`; `{{variable}}` placeholders are substituted without corrupting JSON examples.

## What an embedding is

An embedding is a numeric vector representing semantic meaning. Similar texts tend to be close under a distance metric such as cosine similarity. The model does not store the original lesson as a vector; it transforms text into coordinates in a high-dimensional space.

```text
learner mistake/feedback text
  -> chunk/normalize
  -> embedding model
  -> vector + metadata
  -> Pinecone index
```

At recall time, a new query is embedded with the same model, Pinecone finds nearby vectors, metadata filters by learner/context, and the retrieved memories are inserted into the feedback prompt. This is Retrieval-Augmented Generation (RAG): retrieval supplies relevant external context; generation writes the answer.

## Feedback memory

The `feedback_memory` module stores durable memory records and the embedding service handles vector representation/search. The goal is continuity: if a learner repeatedly makes a tense or article mistake, later feedback can mention the recurring pattern. Retrieval is assistance, not authority; the current answer and deterministic product rules still control what gets persisted.

## Other media AI

STT turns learner audio into a transcript. TTS creates tutor audio. Pronunciation assessment uses Azure Speech. Image generation produces lesson visuals. Local blob storage caches generated artifacts and FastAPI serves them in development. Production storage is a deployment concern, not an invitation to place binary data in the database.

## Observability

LangSmith tracing records model/chain activity when enabled. AI usage logging and evaluation modules support cost and quality review. Never log secrets or raw sensitive learner data unnecessarily.
