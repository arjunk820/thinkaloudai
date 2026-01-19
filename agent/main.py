import os
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import deepgram, cartesia, silero
from google import genai

# Load environment variables from .env file in project root
load_dotenv(dotenv_path="../.env")

# Socratic tutor system prompt
SYSTEM_PROMPT = """You are a Socratic learning companion called ThinkAloud AI. Your role is to help students learn by guiding them to discover answers themselves, not by giving direct answers.

Core principles:
1. NEVER give direct answers to problems. Instead, ask probing questions.
2. When a student explains their reasoning, identify logical gaps or misconceptions.
3. Use questions like "What makes you think that?", "Can you think of a case where that might not work?", "What would happen if...?"
4. Celebrate when students have breakthroughs in understanding.
5. Be patient and encouraging, even when students struggle.
6. Keep responses concise (1-3 sentences) since this is a voice conversation.

When a student is stuck:
- Ask them to explain what they understand so far
- Break the problem into smaller parts
- Suggest they consider a simpler example first

Remember: Your goal is to develop the student's thinking skills, not to solve problems for them."""


class SocraticTutor(Agent):
    """A Socratic tutor agent that helps students learn through questioning."""

    def __init__(self) -> None:
        super().__init__(
            instructions=SYSTEM_PROMPT,
        )
        # Configure Gemini client
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.conversation_history: list[dict] = []

    async def on_user_turn_completed(
        self, turn_ctx: agents.ChatContext, new_message: agents.ChatMessage
    ) -> None:
        """Called when the user finishes speaking."""
        user_text = new_message.text_content if hasattr(new_message, "text_content") else (new_message.content if hasattr(new_message, "content") else None)
        if not user_text:
            return

        # Get response from Gemini
        response = await self._get_gemini_response(user_text)

        # Queue the response for TTS
        turn_ctx.response_text = response

    async def _get_gemini_response(self, user_message: str) -> str:
        """Get a Socratic response from Gemini."""
        try:
            # Add user message to history
            self.conversation_history.append({"role": "user", "parts": [{"text": user_message}]})
            
            # Build contents with system instruction and history
            contents = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}] + self.conversation_history
            
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents,
            )
            
            assistant_text = response.text
            # Add assistant response to history
            self.conversation_history.append({"role": "model", "parts": [{"text": assistant_text}]})
            
            return assistant_text
        except Exception as e:
            print(f"Error getting Gemini response: {e}")
            return "I'm having trouble thinking right now. Could you repeat what you said?"


async def entrypoint(ctx: agents.JobContext):
    """Main entrypoint for the agent."""
    # Wait for a participant to connect
    await ctx.connect()

    # Create the Socratic tutor agent
    tutor = SocraticTutor()

    # Create the agent session with voice pipeline
    session = AgentSession(
        stt=deepgram.STT(
            model="nova-2-general",
            language="en",
        ),
        tts=cartesia.TTS(
            model="sonic-2",
            voice="d46abd1d-2f1b-4e60-9e66-8f205d4c8ea3",  # Friendly, warm voice
        ),
        vad=silero.VAD.load(),
    )

    # Start the session
    await session.start(
        room=ctx.room,
        agent=tutor,
        room_input_options=RoomInputOptions(
            # Enable audio input from the room
            audio_enabled=True,
        ),
    )

    # Note: Initial greeting is commented out due to known TTS issue in LiveKit Agents 1.1.0+
    # See: https://github.com/livekit/agents/issues/3306
    # The agent will still respond to user messages via on_user_turn_completed
    # Uncomment below once TTS issue is resolved or after downgrading to livekit-agents==1.0.23
    #
    # await session.say(
    #     "Hello! I'm ThinkAloud AI, your Socratic learning companion. What are you working on today?",
    #     allow_interruptions=False
    # )


if __name__ == "__main__":
    # Run the agent
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
