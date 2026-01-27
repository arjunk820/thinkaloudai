"use client";

import { useEffect, useRef } from "react";

interface Transcript {
  speaker: string;
  text: string;
  timestamp: Date;
}

interface TranscriptDisplayProps {
  transcripts: Transcript[];
}

export function TranscriptDisplay({ transcripts }: TranscriptDisplayProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new transcripts arrive
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [transcripts]);

  if (transcripts.length === 0) {
    return (
      <div className="w-full h-64 bg-gray-900/50 rounded-2xl border border-gray-800 flex items-center justify-center">
        <p className="text-gray-500 text-center px-8">
          Start speaking to see the conversation here...
        </p>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="w-full h-64 bg-gray-900/50 rounded-2xl border border-gray-800 overflow-y-auto p-4 space-y-4"
    >
      {transcripts.map((transcript, index) => (
        <div
          key={index}
          className={`flex flex-col ${
            transcript.speaker === "user" ? "items-end" : "items-start"
          }`}
        >
          <span className="text-xs text-gray-500 mb-1">
            {transcript.speaker === "user" ? "You" : "AI Tutor"}
          </span>
          <p> {transcript.timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })} </p>
          <div
            className={`max-w-[80%] px-4 py-2 rounded-2xl ${
              transcript.speaker === "user"
                ? "bg-primary-600 text-white rounded-br-md"
                : "bg-gray-800 text-gray-200 rounded-bl-md"
            }`}
          >
            <p>{transcript.text}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
