# ThinkAloud AI

A voice-first learning companion that listens to students explain their reasoning in real-time. Powered by Google Gemini, LiveKit, and Cartesia.

## Project Structure

- `/agent` - Python backend for LiveKit Agent
- `/frontend` - Next.js application

## Prerequisites

- **Node.js** (v18 or higher) and **pnpm**
- **Python** 3.10 or higher
- API keys for LiveKit, Google Gemini, Cartesia, and Deepgram

## Setup

### Frontend

1. Install pnpm globally (if not already installed):
   ```bash
   npm install -g pnpm
   ```

2. Install dependencies:
   ```bash
   # From the project root
   pnpm install
   
   # OR from the frontend directory
   cd frontend
   pnpm install
   ```

3. Run the development server:
   ```bash
   # From the project root (recommended)
   pnpm dev
   
   # OR from the frontend directory
   cd frontend
   pnpm dev
   ```

   The app will be available at `http://localhost:3000`

### Agent

1. Navigate to the agent directory:
   ```bash
   cd agent
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   ```

3. Activate the virtual environment:
   ```bash
   # On macOS/Linux:
   source .venv/bin/activate
   
   # On Windows:
   .venv\Scripts\activate
   ```

4. Verify you're using the venv Python:
   ```bash
   # Should show path to .venv/bin/python3
   which python3
   ```

5. Install dependencies:
   ```bash
   # Use the venv's pip explicitly
   python3 -m pip install -r requirements.txt
   
   # OR if pip is available in venv:
   pip install -r requirements.txt
   ```

6. Set up environment variables (see Configuration section below)

7. Run the agent:
   ```bash
   python3 main.py
   ```

## Configuration

1. Copy `.env.example` to `.env` in the project root:
   ```bash
   cp .env.example .env
   ```

2. Fill in your API keys in the `.env` file:
   - `LIVEKIT_URL` - Your LiveKit server URL (e.g., `wss://your-project.livekit.cloud`)
   - `LIVEKIT_API_KEY` - LiveKit API key
   - `LIVEKIT_API_SECRET` - LiveKit API secret
   - `GOOGLE_API_KEY` - Google Gemini API key
   - `CARTESIA_API_KEY` - Cartesia API key for text-to-speech
   - `DEEPGRAM_API_KEY` - Deepgram API key for speech-to-text

3. Verify your environment variables are loaded:
   ```bash
   cd agent
   source .venv/bin/activate
   python3 main.py
   ```
   
   The agent will check and report any missing environment variables.

## Troubleshooting

### Frontend Issues

- **"node_modules missing"**: Run `pnpm install` to install dependencies
- **"next: command not found"**: Make sure dependencies are installed with `pnpm install`

### Agent Issues

- **"externally-managed-environment" error**: Ensure the virtual environment is activated and you're using `python3 -m pip` or the venv's pip
- **"ModuleNotFoundError"**: Make sure dependencies are installed in the virtual environment, not globally
- **"pip: command not found"**: Use `python3 -m pip` instead, or ensure the venv is activated

