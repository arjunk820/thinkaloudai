# ThinkAloud AI

A voice-first learning companion that listens to students explain their reasoning in real-time, catches logical gaps through Socratic questioning, and helps them discover answers themselves.

## Architecture

- **Frontend**: Next.js 14 + React 18 + Tailwind CSS
- **Agent**: Python with LiveKit Agents SDK v1.x
- **Speech-to-Text**: Deepgram
- **LLM**: Google Gemini 2.0 Flash
- **Text-to-Speech**: Cartesia

## Prerequisites

- Node.js 18+ and pnpm
- Python 3.9–3.13 (3.14 not supported yet)
- API keys for:
  - [LiveKit Cloud](https://cloud.livekit.io/) (LIVEKIT_URL, API_KEY, API_SECRET)
  - [Google AI Studio](https://aistudio.google.com/) (GOOGLE_API_KEY)
  - [Deepgram](https://deepgram.com/) (DEEPGRAM_API_KEY)
  - [Cartesia](https://cartesia.ai/) (CARTESIA_API_KEY)

## Setup

### 1. Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required variables:
```
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
GOOGLE_API_KEY=your-gemini-key
DEEPGRAM_API_KEY=your-deepgram-key
CARTESIA_API_KEY=your-cartesia-key
```

### 2. Frontend Setup

```bash
# Install dependencies (from project root)
pnpm install

# Run development server
pnpm dev
```

The frontend will be available at http://localhost:3000

### 3. Agent Setup

```bash
# Navigate to agent directory
cd agent

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the agent
python main.py dev
```

## Usage

1. Start both the frontend (`pnpm dev`) and agent (`python main.py dev`)
2. Open http://localhost:3000 in your browser
3. Click "Start Learning Session"
4. Allow microphone access when prompted
5. Wait for the AI tutor to connect
6. Start explaining your reasoning out loud!

## How It Works

1. You speak into your microphone
2. Audio streams to LiveKit Cloud via WebRTC
3. The Python agent receives audio and transcribes it using Deepgram
4. Your words are sent to Gemini with a Socratic tutor prompt
5. Gemini's response is converted to speech using Cartesia
6. You hear the AI tutor's response through your speakers

## Development

### Project Structure

```
thinkaloudai/
├── frontend/           # Next.js application
│   ├── app/           # App router pages and API routes
│   └── components/    # React components
├── agent/             # Python LiveKit agent
│   ├── main.py       # Agent entrypoint
│   └── requirements.txt
├── .env               # Environment variables (not in git)
└── .env.example       # Template for environment variables
```

### Useful Commands

```bash
# Frontend
pnpm dev          # Start development server
pnpm build        # Build for production
pnpm lint         # Run ESLint

# Agent
python main.py dev      # Run in development mode
python main.py start    # Run in production mode
```

## Troubleshooting

### "Waiting for AI tutor to join..."
- Make sure the Python agent is running (`python main.py dev`)
- Check that your LiveKit credentials are correct
- Verify the agent connected by checking its console output

### Agent won't start
- Ensure you're using Python 3.9–3.13 (not 3.14)
- Make sure the virtual environment is activated
- Check that all dependencies installed successfully

### No audio
- Check browser microphone permissions
- Ensure your microphone is working
- Try refreshing the page
