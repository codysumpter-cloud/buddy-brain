# Project Omega: Life Wiki Specification

## 1. Vision
Move from passive RAG (Retrieval Augmented Generation) to an active, AI-maintained Knowledge Base. The agent does not just "search" documents; it maintains a structured, interlinked "Life Wiki" that evolves as the user's life and knowledge grow.

## 2. Architecture: The Knowledge Graph
The Wiki is stored as a hierarchy of Markdown files. This ensures human-readability, version control, and easy portability.

### Directory Structure
```text
life-wiki/
├── 00_index.md              # The Global Map: High-level entry points & core identities
├── 01_identity/             # User's core values, preferences, and a "Who I Am" profile
├── 02_relationships/        # People, networks, and interaction histories
├── 03_projects/             # Active goals, technical specs, and project logs
├── 04_knowledge/            # Topic-based notes (e.g., "AI Research", "Home Automation")
├── 05_archive/              # Completed projects and outdated information
└── .meta/                   # AI-only metadata, indices, and linting logs
```

### Page Schema
Every page follows a strict header format for AI parsing:
- **Title**: `# Page Name`
- **Tags**: `Tags: #tag1 #tag2`
- **Links**: `Links: [[Page A]], [[Page B]]`
- **Last Linted**: `LastLinted: YYYY-MM-DD`
- **Content**: The primary Markdown body.

## 3. The Core Operations (The "God-Tools")

### A. Ingest
**Process**: Raw Input $\rightarrow$ Analysis $\rightarrow$ Page Placement $\rightarrow$ Linking.
- **Logic**: When the agent receives a significant piece of information (e.g., "I love this specific type of coffee"), it doesn't just remember it in session memory. It finds the `Identity` or `Preferences` page and updates it, or creates a new page in `Knowledge`.
- **Atomic Updates**: Changes are made as targeted patches, not full-page rewrites, to preserve human edits.

### B. Lint
**Process**: Scan $\rightarrow$ Detect $\rightarrow$ Resolve $\rightarrow$ Log.
- **Logic**: A background routine that runs periodically.
- **Checks**:
    - **Contradiction**: "User said X on Monday, but Y on Friday." $\rightarrow$ Trigger a clarification request.
    - **Dead Links**: Link to a page that no longer exists.
    - **Silos**: A page with no links to others $\rightarrow$ Suggest connections.
    - **Redundancy**: Two pages covering the same topic $\rightarrow$ Propose a merge.

### C. Query
**Process**: Intent $\rightarrow$ Wiki Traversal $\rightarrow$ Synthesis.
- **Logic**: Instead of a vector search over a database, the agent uses the Wiki's structure.
- **Traversal**: "Find the 'Home Automation' page $\rightarrow$ Follow the link to 'Lighting' $\rightarrow$ Extract the current state."
- **Context Injection**: The query results are injected into the prompt as a structured context block, not a list of disjointed chunks.

## 4. Implementation Roadmap

### Step 1: The Bootstrap (v0.1)
- Create the `life-wiki/` directory.
- Implement the basic `Ingest` tool to migrate current `memory.md` and `USER.md` data into the Wiki.
- Establish the `00_index.md`.

### Step 2: The Intelligence Layer (v0.2)
- Implement the `Lint` routine as a scheduled cron job.
- Build the `Query` system to prioritize Wiki links over raw vector search.

### Step 3: The Interface (v0.3)
- Create a "Wiki View" for the user to browse and edit their knowledge base.
- Integrate "Deep Research" capabilities to automatically expand Wiki pages from external sources.
