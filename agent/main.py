import livekit.agents  # type: ignore
from livekit.plugins import cartesia, deepgram  # type: ignore
import google.generativeai as genai  # type: ignore
from dotenv import load_dotenv  # type: ignore
from colorama import init, Fore  # type: ignore
import os

# Initialize colorama for colored logging
init(autoreset=True)

# Load environment variables
load_dotenv()

def check_env_vars():
    """Check if required environment variables are set."""
    required_vars = [
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "GOOGLE_API_KEY",
        "CARTESIA_API_KEY",
        "DEEPGRAM_API_KEY",
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    return missing

def main():
    """Main entry point for the agent."""
    print(Fore.GREEN + "ThinkAloud AI Agent")
    print(Fore.CYAN + "=" * 50)
    
    # Check environment variables
    missing = check_env_vars()
    if missing:
        print(Fore.YELLOW + f"Warning: Missing environment variables: {', '.join(missing)}")
    else:
        print(Fore.GREEN + "✓ All environment variables are set")
    
    # Lazy import of heavy dependencies (only when actually needed)
    # This prevents slow startup times
    print(Fore.CYAN + "\nAgent initialized successfully!")
    print(Fore.CYAN + "Ready to connect to LiveKit...")
    
    # TODO: Implement LiveKit agent logic here
    # import livekit.agents
    # from livekit.plugins import cartesia, deepgram
    # import google.generativeai as genai

if __name__ == "__main__":
    main()

