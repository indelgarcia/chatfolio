# chatfolio

ChatFolio is an AI-powered conversational investment advisor that helps beginner investors build a starter portfolio through natural dialogue instead of traditional forms. It is a senior year Human-AI Interaction (HAI) term project built by Chris, Indel, Nate, and Matt.

## Getting Started

### Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/chatfolio.git
   cd chatfolio
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate   # Windows (Git Bash)
   # or
   source venv/bin/activate       # macOS / Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-key-here
   ```

### Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.