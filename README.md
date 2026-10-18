# Resume RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot designed to retrieve relevant information from resume documents and provide answers based on the available content.

## Project Overview

This project demonstrates how a RAG-based chatbot can combine document processing, information retrieval, vector search, and a language model workflow to answer questions using resume-related information.

## Technologies Used

- **Python** — application logic and data processing
- **PostgreSQL** — database storage
- **Vector Search** — finding semantically relevant document chunks
- **RAG Architecture** — retrieving relevant context before generating answers
- **Git and GitHub** — version control and project collaboration

## Main Project Files

| File | Purpose |
|---|---|
| `app.py` | Application interface |
| `chat.py` | Chatbot functionality |
| `ingest.py` | Document ingestion and processing |
| `search.py` | Retrieval and search |
| `check_chunks.py` | Inspecting document chunks |
| `test_connection.py` | Testing database connectivity |

## How the RAG Workflow Works

1. **Document ingestion:** Resume documents are processed.
2. **Chunking:** Documents are divided into smaller text sections.
3. **Storage:** Processed information and, where configured, vector embeddings are stored in the database.
4. **Retrieval:** A user's question is used to find relevant document content.
5. **Answer generation:** Retrieved context is used to help generate a relevant response.

## Git Workflow Practice

This repository also demonstrates practical Git version-control concepts.

### 1. Git Branching

Branches allow development work to be performed separately from the main branch.

```bash
git switch -c feature/chatbot-ui
git switch -c feature/rebase-demo
```

### 2. Git Merge

Merge combines changes from one branch into another.

```bash
git switch main
git merge feature/chatbot-ui
```

**Purpose:** Integrate feature work into the main branch while preserving the branch history.

### 3. Git Rebase

Rebase reapplies a feature branch's commits on top of another branch's latest commit.

```bash
git switch feature/rebase-demo
git rebase main
```

**Purpose:** Demonstrate how a feature branch can be updated using a different commit history from a merge.

### 4. Merge Conflict Resolution

A merge conflict occurs when Git cannot automatically combine competing changes.

The conflict in this project was resolved by editing the conflicted file, staging the resolution, and committing it.

```bash
git status
notepad conflict-demo.txt
git add conflict-demo.txt
git commit -m "Resolve merge conflict"
```

**Purpose:** Practice identifying conflicting changes and resolving them manually.

## Useful Git Commands

```bash
git status
git branch
git log --oneline --graph --all
git add .
git commit -m "Describe your changes"
git push
git pull
```

## Repository Safety

- Keep `.env` files and credentials out of version control.
- Do not commit the `.venv/` virtual environment.
- Review resume documents for personal or confidential information before sharing them publicly.

## Learning Outcomes

- Understanding Git repositories and branches
- Practicing merge and rebase workflows
- Creating and resolving a merge conflict
- Publishing project changes to GitHub
- Documenting a Python-based RAG chatbot

