import React, { useState, useEffect, useRef } from 'react';
import { X, Mic } from 'lucide-react';
import { a2zApi } from '@/lib/a2z-api';

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
  
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const dataIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunkIndexRef = useRef(0);
  const pendingRequestsRef = useRef(0);
  const isFinishingRef = useRef(false);
  const allChunksRef = useRef<BlobPart[]>([]);

  // Clean up function
  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    if (timerRef.current) clearInterval(timerRef.current);
    if (dataIntervalRef.current) clearInterval(dataIntervalRef.current);
  };

  const handleFinish = (currentWords: string[]) => {
    if (isFinishingRef.current) return;
    isFinishingRef.current = true;
    setPhase('finishing');
    stopRecording();
    
    // We need to wait for any pending audio chunks to finish uploading
    // before we inform the parent to call finishRound.
    const checkPendingAndFinish = () => {
      if (pendingRequestsRef.current > 0) {
        setTimeout(checkPendingAndFinish, 100);
      } else {
        const pass = currentWords.length >= level.words;
        onFinish({ pass, words: currentWords });
      }
    };
    checkPendingAndFinish();
  };

  const startListening = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      chunkIndexRef.current = 0;
      allChunksRef.current = [];
      
      mediaRecorder.ondataavailable = async (e) => {
        if (e.data && e.data.size > 0 && !isFinishingRef.current) {
          allChunksRef.current.push(e.data);
          
          // Create a blob containing all audio up to this point
          const currentBlob = new Blob(allChunksRef.current, { type: mediaRecorder.mimeType });
          const index = chunkIndexRef.current++;
          pendingRequestsRef.current++;
          try {
            const res = await a2zApi.sendAudioChunk(roundId, currentBlob, index);
            if (!isFinishingRef.current) {
              setWords(res.accepted_words);
              if (res.passed_so_far) {
                handleFinish(res.accepted_words);
              }
            }
          } catch (err) {
            console.error("Failed to send audio chunk", err);
          } finally {
            pendingRequestsRef.current--;
          }
        }
      };

      mediaRecorder.start(); // Start without timeslice
      setPhase('listening');
      
      // Request data every 3 seconds
      dataIntervalRef.current = setInterval(() => {
        if (mediaRecorder.state === 'recording') {
          mediaRecorder.requestData();
        }
      }, 3000);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            clearInterval(timerRef.current!);
            if (dataIntervalRef.current) clearInterval(dataIntervalRef.current);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

    } catch (err) {
      console.error("Microphone access denied or error", err);
    }
  };

  useEffect(() => {
    if (timeLeft === 0 && phase === 'listening') {
      handleFinish(words);
    }
  }, [timeLeft, phase, words]);

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
              <Mic size={36} strokeWidth={2.5} />
              <div className="a2z-mic-start-cta">Tap to start</div>
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
