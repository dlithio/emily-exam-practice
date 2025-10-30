# Pandas & SQL Practice App

A Streamlit application that generates pandas and SQL practice problems on-the-fly using Claude API. Get instant feedback by comparing your code output to expected results.

## Setup

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) package manager
- Anthropic API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd emily-exam-practice
```

2. Install dependencies:
```bash
uv sync
```

### API Key Configuration

This app requires an Anthropic API key to generate practice problems. You can configure it in two ways:

#### Option 1: Environment Variable (Recommended)

Set the `ANTHROPIC_API_KEY` environment variable:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

To make it permanent, add it to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.).

#### Option 2: Streamlit Secrets

1. Copy the example secrets file:
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

2. Edit `.streamlit/secrets.toml` and add your API key:
```toml
ANTHROPIC_API_KEY = "your-api-key-here"
```

**Note:** The `secrets.toml` file is already in `.gitignore` and will not be committed to version control.

### Getting an API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key

### Testing the Connection

Verify your API key is configured correctly:

```bash
uv run python claude_client.py
```

You should see: ` API connection successful!`

## Running the App

```bash
uv run streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Features

- **On-demand problem generation**: Get fresh practice problems using Claude API
- **Dual language support**: Solve problems using either pandas or SQL
- **Instant feedback**: Compare your output to expected results
- **Skill-focused practice**: Target specific skills like filtering, grouping, joins, etc.
- **Interactive data display**: View input tables and results clearly formatted

## Development

See `docs/plan.md` for the detailed development roadmap and implementation steps.

## License

[Add your license here]
