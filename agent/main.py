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

        # Queue the response for TTS - use session.say() (provided by Agent base class)
        await self.session.say(response)

    async def _get_gemini_response(self, user_message: str) -> str:
        """Get a Socratic response from Gemini."""
        try:
            # Add user message to history
            self.conversation_history.append({"role": "user", "parts": [{"text": user_message}]})
            
            # Build contents with system instruction and history
            contents = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}] + self.conversation_history
            
            # Use async API call with faster model (lite version for real-time voice)
            response = await self.client.aio.models.generate_content(
                model="gemini-2.5-flash-lite",
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
            voice="a0e99841-438c-4a64-b679-ae501e7d6091",  # barbershop voice
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


if __name__ == "__main__":
    # Run the agent
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
