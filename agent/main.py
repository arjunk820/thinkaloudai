import os
from dotenv import load_dotenv # pyright: ignore[reportMissingImports]

from livekit import agents  # pyright: ignore[reportMissingImports]
from livekit.agents import AgentSession, Agent, RoomInputOptions  # pyright: ignore[reportMissingImports]
from livekit.plugins import deepgram, cartesia, silero  # pyright: ignore[reportMissingImports]
from google import genai

import json
import time

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
    """A Socratic tutor agent that helps students learn through questioning and conversation."""

    def __init__(self) -> None:
        super().__init__(
            instructions=SYSTEM_PROMPT,
        )
        # Configure Gemini client
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.conversation_history: list[dict] = []
        self.room = None  # set when session starts

    async def on_user_turn_completed(
        self, turn_ctx: agents.ChatContext, new_message: agents.ChatMessage
    ) -> None:
        user_text = new_message.text_content if hasattr(new_message, "text_content") else (new_message.content if hasattr(new_message, "content") else None)
        if not user_text:
            return

        # Gemini's response
        response = await self._get_gemini_response(user_text)

        # TTS
        await self.session.say(response)

    async def _get_gemini_response(self, user_message: str) -> str:
        try:
            # Add user message to history
            self.conversation_history.append({"role": "user", "parts": [{"text": user_message}]})

            # Stream the user message to the frontend
            if self.room:
                try:
                    transcript_data = json.dumps({
                        "type": "transcript",
                        "speaker": "user",
                        "text": user_message,
                        "timestamp": time.time(), # timestamp of the user message
                    })
                    await self.room.local_participant.publish_data(
                        transcript_data.encode('utf-8'),
                        topic="transcripts"
                    )
                except Exception as e:
                    print(f"Error sending user transcript: {e}")
            
            # Build contents with system instruction and history
            contents = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}] + self.conversation_history
            
            # Use async API call with faster model
            response = await self.client.aio.models.generate_content(
                model="gemini-2.5-flash-lite", # lite, faster model
                contents=contents,
            )
            
            assistant_text = response.text
            # Add assistant response to history
            self.conversation_history.append({"role": "model", "parts": [{"text": assistant_text}]})

            # Stream the assistant response to the frontend
            if self.room:
                try:
                    transcript_data = json.dumps({
                        "type": "transcript",
                        "speaker": "AI",
                        "text": assistant_text,
                        "timestamp": time.time(), # timestamp of the response
                    })
                    await self.room.local_participant.publish_data(
                        transcript_data.encode('utf-8'),
                        topic="transcripts"
                    )
                except Exception as e:
                    print(f"Error sending assistant transcript: {e}")
            
            return assistant_text

        except Exception as e:
            print(f"Error getting Gemini response: {e}")
            return "I'm having trouble thinking right now. Could you repeat what you said?"


async def entrypoint(ctx: agents.JobContext):
    # Wait for a participant to connect
    await ctx.connect()

    # Create the Socratic tutor agent
    tutor = SocraticTutor()

    # Create the agent session with voice pipeline
    session = AgentSession(
        stt=deepgram.STT(
            model="nova-2-general", # general, faster model
            language="en",
        ),
        tts=cartesia.TTS(
            model="sonic-2", # sonic-2, faster model
            voice="a0e99841-438c-4a64-b679-ae501e7d6091",  # barbershop voice
        ),
        vad=silero.VAD.load(),
    )

    # Store room reference in the agent
    tutor.room = ctx.room
    
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
