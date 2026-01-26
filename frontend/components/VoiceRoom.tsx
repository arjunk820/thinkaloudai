"use client";

import { useCallback, useEffect, useState } from "react";
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useRoomContext,
  useConnectionState,
  useLocalParticipant,
  useRemoteParticipants,
  useDataChannel,
} from "@livekit/components-react";
import "@livekit/components-styles";
import { ConnectionState, RemoteParticipant } from "livekit-client";
import { MicButton } from "./MicButton";
import { TranscriptDisplay } from "./TranscriptDisplay";

interface VoiceRoomProps {
  roomName: string;
  onDisconnect: () => void;
}

export function VoiceRoom({ roomName, onDisconnect }: VoiceRoomProps) {
  const [token, setToken] = useState<string | null>(null);
  const [wsUrl, setWsUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchToken = async () => {
      try {
        const response = await fetch("/api/token", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            roomName,
            participantName: `user-${Date.now()}`,
          }),
        });

        if (!response.ok) {
          throw new Error("Failed to get token");
        }

        const data = await response.json();
        setToken(data.token);
        setWsUrl(data.wsUrl);
      } catch (err) {
        setError("Failed to connect. Please check your configuration.");
        console.error(err);
      }
    };

    fetchToken();
  }, [roomName]);

  if (error) {
    return (
      <div className="text-center">
        <p className="text-red-400 mb-4">{error}</p>
        <button
          onClick={onDisconnect}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
        >
          Go Back
        </button>
      </div>
    );
  }

  if (!token || !wsUrl) {
    return (
      <div className="flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        <span className="ml-3 text-gray-400">Connecting...</span>
      </div>
    );
  }

  return (
    <LiveKitRoom
      token={token}
      serverUrl={wsUrl}
      connect={true}
      audio={true}
      video={false}
      onDisconnected={onDisconnect}
      className="w-full max-w-4xl"
    >
      <RoomContent onDisconnect={onDisconnect} />
      <RoomAudioRenderer />
    </LiveKitRoom>
  );
}

function RoomContent({ onDisconnect }: { onDisconnect: () => void }) {
  const room = useRoomContext();
  const connectionState = useConnectionState();
  const { localParticipant } = useLocalParticipant();
  const remoteParticipants = useRemoteParticipants();
  const [transcripts, setTranscripts] = useState<Array<{ speaker: string; text: string; timestamp: Date }>>([]);

  const agentConnected = remoteParticipants.some(
    (p: RemoteParticipant) => p.identity.startsWith("agent")
  );

  // Handle transcription data from the agent
  const onDataReceived = useCallback((msg: { payload: Uint8Array }) => {
    try {
      const text = new TextDecoder().decode(msg.payload);
      const data = JSON.parse(text);
      console.log("Received data channel message:", data);
      if (data.type === "transcript") {
        console.log("Adding transcript:", data.speaker, data.text);
        setTranscripts((prev) => [
          ...prev,
          {
            speaker: data.speaker,
            text: data.text,
            timestamp: new Date(),
          },
        ]);
      }
    } catch (e) {
      console.error("Error parsing data channel message:", e);
    }
  }, []);

  useDataChannel("transcripts", onDataReceived);

  const handleDisconnect = useCallback(() => {
    room.disconnect();
    onDisconnect();
  }, [room, onDisconnect]);

  const getStatusMessage = () => {
    switch (connectionState) {
      case ConnectionState.Connecting:
        return "Connecting to session...";
      case ConnectionState.Connected:
        return agentConnected
          ? "AI tutor connected. Start speaking!"
          : "Waiting for AI tutor to join...";
      case ConnectionState.Reconnecting:
        return "Reconnecting...";
      case ConnectionState.Disconnected:
        return "Disconnected";
      default:
        return "";
    }
  };

  const isConnected = connectionState === ConnectionState.Connected;
  const isMicEnabled = localParticipant?.isMicrophoneEnabled ?? false;

  const toggleMic = useCallback(async () => {
    if (localParticipant) {
      await localParticipant.setMicrophoneEnabled(!isMicEnabled);
    }
  }, [localParticipant, isMicEnabled]);

  return (
    <div className="flex flex-col items-center gap-8 w-full">
      {/* Status indicator */}
      <div className="flex items-center gap-2">
        <div
          className={`w-3 h-3 rounded-full ${
            isConnected && agentConnected
              ? "bg-green-500"
              : isConnected
              ? "bg-yellow-500"
              : "bg-gray-500"
          }`}
        />
        <span className="text-gray-400">{getStatusMessage()}</span>
      </div>

      {/* Transcript display */}
      <TranscriptDisplay transcripts={transcripts} />

      {/* Mic button */}
      <MicButton
        isEnabled={isMicEnabled}
        isConnected={isConnected && agentConnected}
        onClick={toggleMic}
      />

      {/* End session button */}
      <button
        onClick={handleDisconnect}
        className="px-4 py-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
      >
        End Session
      </button>
    </div>
  );
}
