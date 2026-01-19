"use client";

import { useState } from "react";
import { VoiceRoom } from "@/components/VoiceRoom";

export default function Home() {
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [roomName, setRoomName] = useState<string | null>(null);

  const startSession = async () => {
    // Generate a unique room name
    const newRoomName = `session-${Date.now()}`;
    setRoomName(newRoomName);
    setIsSessionActive(true);
  };

  const endSession = () => {
    setIsSessionActive(false);
    setRoomName(null);
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      {!isSessionActive ? (
        <div className="text-center max-w-2xl">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
            ThinkAloud AI
          </h1>
          <p className="text-xl text-gray-400 mb-8">
            Your voice-first learning companion. Explain your reasoning out loud,
            and I&apos;ll help you discover answers through thoughtful questions.
          </p>
          <button
            onClick={startSession}
            className="px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white rounded-full text-lg font-semibold transition-all hover:scale-105 active:scale-95"
          >
            Start Learning Session
          </button>
          <p className="mt-6 text-sm text-gray-500">
            Tip: Think out loud as you work through problems. I&apos;ll listen and ask
            questions to help deepen your understanding.
          </p>
        </div>
      ) : (
        <VoiceRoom roomName={roomName!} onDisconnect={endSession} />
      )}
    </main>
  );
}
