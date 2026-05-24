"""Feedback memory module — RAG layer for personalized session feedback.

Owns the pipeline: build memory doc → embed → store in Pinecone → retrieve
for mentor note generation. PostgreSQL stays the source of truth; Pinecone
is the query layer for semantic similarity.
"""
