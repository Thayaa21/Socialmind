# Social Intelligence Project (Working Title)

This project is an autonomous MLOps pipeline for real-time social intelligence. It detects major AI announcements and analyzes public sentiment in real-time.

## Architecture (Week 1 Demo)

Here is the flow for the initial end-to-end system:

```text
[System 1: RSS Monitor] --(Event Trigger)--> [System 2: Data Pipeline]
       (AWS Lambda)                               (Local Script)
           |                                             |
           v                                             v
     [Detects Event] --> [Collects 1,000 Posts] --> [Runs Sentiment] --> [System 3: Dashboard]
    (e.g., "Sora")        (Reddit API)            (Hugging Face)       (Streamlit)
                                                       |
                                                       v
                                            [Google Drive Storage]
                                            (/raw/ & /processed/)
```

## Setup

1.  Clone this repository.
2.  Create and activate the virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Create your environment file:
    ```bash
    cp config/.env.template config/.env
    ```
5.  Edit `config/.env` and `config/settings.yaml` with your API keys and settings.