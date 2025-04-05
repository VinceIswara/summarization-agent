def get_assistant_profile(profile: str, model: str) -> dict:
    """
    Returns assistant profile configuration by name.
    Each profile includes assistant name, description, model, and tools.
    """
    profiles = {
        "pdf_summarizer": {
            "name": "PDF Summarizer Assistant",
            "description": "Assistant that summarizes PDF documents including text and visuals.",
            "model": model,
            "tools": [{"type": "file_search"}]
        },
        # Example additional profiles:
        "legal_analyzer": {
            "name": "Legal Analyzer Assistant",
            "description": "Assistant that analyzes legal documents and highlights key clauses.",
            "model": model,
            "tools": [{"type": "file_search"}]
        },
        "research_helper": {
            "name": "Research Helper Assistant",
            "description": "Assistant that helps summarize and organize research papers.",
            "model": model,
            "tools": [{"type": "file_search"}]
        }
    }

    if profile not in profiles:
        raise ValueError(f"Unknown assistant profile: {profile}")

    return profiles[profile]
