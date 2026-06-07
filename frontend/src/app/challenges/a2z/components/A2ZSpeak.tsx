import React, { useState, useEffect, useRef } from 'react';
import { X, Mic, MicOff } from 'lucide-react';

interface A2ZSpeakProps {
  roundId: number;
  letter: string | null;
  level: { id: number; name: string; words: number; time: number };
  reduceMotion: boolean;
  onFinish: (result: { pass: boolean; words: string[] }) => void;
  onClose: () => void;
}

export function A2ZSpeak({ roundId, letter, level, reduceMotion, onFinish, onClose }: A2ZSpeakProps) {
  const [phase, setPhase] = useState<'idle' | 'listening' | 'finishing'>('idle');
  const [timeLeft, setTimeLeft] = useState(level.time);
  const [words, setWords] = useState<string[]>([]);
  const [micError, setMicError] = useState<string | null>(null);

  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const isFinishingRef = useRef(false);
  // Set once we've surfaced an explicit error so onclose doesn't also show a
  // generic "connection lost" message on top of it.
  const errorShownRef = useRef(false);
  // wordsRef mirrors the words state so callbacks always see the latest value
  const wordsRef = useRef<string[]>([]);

  const showError = (message: string) => {
    errorShownRef.current = true;
    setMicError(message);
    stopRecording();
    setPhase('idle');
    setTimeLeft(level.time);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close();
    }
    if (timerRef.current) clearInterval(timerRef.current);
  };

  const handleFinish = (currentWords: string[]) => {
    if (isFinishingRef.current) return;
    isFinishingRef.current = true;
    setPhase('finishing');
    stopRecording();
    const pass = currentWords.length >= level.words;
    onFinish({ pass, words: currentWords });
  };

  const startListening = async () => {
    setMicError(null);
    errorShownRef.current = false;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Pick the best mimeType the browser supports (Chrome: webm/opus,
      // Firefox: ogg/opus, Safari: browser default / mp4)
      const mimeType =
        MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' :
        MediaRecorder.isTypeSupported('audio/webm')             ? 'audio/webm' :
        MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')  ? 'audio/ogg;codecs=opus' :
        '';
      const mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      mediaRecorderRef.current = mediaRecorder;

      // Build WebSocket URL — swap http(s) → ws(s), add JWT as query param
      // (browsers cannot set Authorization headers on WebSocket connections)
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const wsBase = apiBase.replace(/^http/, 'ws');
      const token = encodeURIComponent(localStorage.getItem('token') || '');
      const wsUrl = `${wsBase}/api/v1/challenges/a2z/rounds/${roundId}/stream?token=${token}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data as string) as {
            type?: string;
            code?: string;
            message?: string;
            accepted_words?: string[];
            passed_so_far?: boolean;
          };

          // Structured server error (auth, streaming not configured, round
          // not found, upstream failure). Show it explicitly — don't finish.
          if (data.type === 'error') {
            if (!isFinishingRef.current) {
              showError(data.message || 'Something went wrong. Please try again.');
            }
            return;
          }

          if (!isFinishingRef.current) {
            wordsRef.current = data.accepted_words || [];
            setWords(data.accepted_words || []);
            if (data.passed_so_far) {
              handleFinish(data.accepted_words || []);
            }
          }
        } catch (e) {
          console.error('Failed to parse WS message', e);
        }
      };

      ws.onerror = () => {
        if (!isFinishingRef.current && !errorShownRef.current) {
          showError('Connection error. Please check your network and try again.');
        }
      };

      ws.onclose = () => {
        // A clean finish (target reached or timer) already set isFinishingRef
        // before closing. Any other close here is abnormal — surface it as an
        // error instead of silently dumping the user to a 0-word result.
        if (!isFinishingRef.current && !errorShownRef.current) {
          showError('Connection lost. Please try again.');
        }
      };

      ws.onopen = () => {
        // Send audio chunks as binary frames every 250 ms
        mediaRecorder.ondataavailable = (e) => {
          if (e.data && e.data.size > 0 && ws.readyState === WebSocket.OPEN) {
            ws.send(e.data);
          }
        };

        mediaRecorder.start(250); // 250 ms timeslice → ~4 chunks/second
        setPhase('listening');

        timerRef.current = setInterval(() => {
          setTimeLeft(prev => {
            if (prev <= 1) {
              clearInterval(timerRef.current!);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      };

    } catch (err) {
      console.error('Microphone access denied or error', err);
      setMicError('Microphone access denied. Please allow mic access and try again.');
    }
  };

  // When the countdown reaches zero, finish the round
  useEffect(() => {
    if (timeLeft === 0 && phase === 'listening') {
      handleFinish(wordsRef.current);
    }
  }, [timeLeft, phase]);

  useEffect(() => {
    return () => {
      stopRecording();
    };
  }, []);

  const progressPct = Math.min(100, (words.length / level.words) * 100);
  const timePct = Math.max(0, (timeLeft / level.time) * 100);

  return (
    <div className="a2z-stage fade-in">
      <button className="a2z-icon-btn-square a2z-stage-close" onClick={onClose} aria-label="Close" disabled={phase === 'finishing'}>
        <X size={20} />
      </button>

      <div className="a2z-speak-top">
        <div className="a2z-lvl-pill">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>
          Level {level.id} · {level.name}
        </div>
        <div className="a2z-speak-letterbadge">
          <div className="a2z-speak-bigletter">{letter}</div>
          <div className="a2z-speak-instruction">
            Say <b>{level.words}</b> words starting with <b>{letter}</b>
          </div>
        </div>
      </div>

      <div className={`a2z-mic-wrap ${phase === 'listening' ? 'live' : ''}`}>
        <svg className="a2z-ring-svg" viewBox="0 0 200 200">
          <circle className="a2z-ring-bg" cx="100" cy="100" r="90" />
          {(phase === 'listening' || phase === 'finishing') && (
             <circle className="a2z-ring-fg" cx="100" cy="100" r="90" strokeDasharray="565.48" strokeDashoffset={565.48 * (1 - timePct / 100)} />
          )}
        </svg>

        {phase === 'listening' && !reduceMotion && (
          <>
            <div className="a2z-mic-pulse p1"></div>
            <div className="a2z-mic-pulse p2"></div>
            <div className="a2z-mic-pulse p3"></div>
          </>
        )}

        <div
          className={`a2z-mic-core ${phase === 'idle' ? 'idle' : 'listening'}`}
          onClick={() => {
            if (phase === 'idle') startListening();
          }}
        >
          {phase === 'idle' ? (
            <>
              {micError ? <MicOff size={36} strokeWidth={2.5} /> : <Mic size={36} strokeWidth={2.5} />}
              <div className="a2z-mic-start-cta">{micError ? 'Mic error' : 'Tap to start'}</div>
            </>
          ) : phase === 'finishing' ? (
            <>
              <div className="a2z-mic-label">Finishing...</div>
            </>
          ) : (
            <>
              <div className="a2z-eq">
                <i></i><i></i><i></i><i></i><i></i><i></i><i></i>
              </div>
              <div className="a2z-mic-label">Listening...</div>
              <div style={{ fontSize: 13, fontWeight: 700 }}>{timeLeft}s</div>
            </>
          )}
        </div>
      </div>

      {micError && (
        <div style={{ color: 'var(--color-error, #ef4444)', fontSize: 13, textAlign: 'center', padding: '0 16px' }}>
          {micError}
        </div>
      )}

      <div className="a2z-speak-counter">
        <div className="a2z-counter-num">
          {words.length} <span className="target">/{level.words}</span>
        </div>
        <div className="a2z-counter-bar">
          <i style={{ width: `${progressPct}%` }}></i>
        </div>
      </div>

      <div className="a2z-word-feed">
        {words.map((w, i) => (
          <div key={i} className="a2z-word-chip">{w}</div>
        ))}
      </div>
    </div>
  );
}
