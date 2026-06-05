import React, { useState, useEffect, useRef } from 'react';
import { X, Mic } from 'lucide-react';

interface A2ZSpeakProps {
  letter: string | null;
  level: { id: number; name: string; words: number; time: number };
  outcome: string;
  simSpeed: number;
  reduceMotion: boolean;
  onFinish: (result: { pass: boolean; words: string[] }) => void;
  onClose: () => void;
}

export function A2ZSpeak({ letter, level, outcome, simSpeed, reduceMotion, onFinish, onClose }: A2ZSpeakProps) {
  const [phase, setPhase] = useState<'idle' | 'listening'>('idle');
  const [timeLeft, setTimeLeft] = useState(level.time);
  const [words, setWords] = useState<string[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Simulated word lists for the demo
  const mockWords: Record<string, string[]> = {
    A: ['apple', 'avocado', 'airport', 'animal', 'awesome', 'alien', 'anchor', 'artist', 'arrow', 'autumn', 'athlete', 'avenue', 'alert', 'amount', 'angle', 'alarm', 'answer', 'attack', 'author', 'award', 'action', 'active'],
    B: ['banana', 'butterfly', 'basket', 'button', 'bottle', 'bubble', 'bridge', 'branch', 'breeze', 'bronze', 'bakery', 'bamboo', 'barrel', 'beacon', 'beauty', 'beaver', 'beetle', 'biscuit', 'blanket', 'blizzard', 'blossom', 'border'],
    O: ['ocean', 'orange', 'octopus', 'orbit', 'onion', 'oasis', 'object', 'office', 'oxygen', 'oyster', 'oatmeal', 'obvious', 'ocelot', 'octagon', 'offense', 'officer', 'olympic', 'omelet', 'ongoing', 'opinion', 'optimal', 'orchard']
  };

  const getMockWord = () => {
    const list = mockWords[letter || 'A'] || mockWords['A'];
    // For random simulation
    return list[Math.floor(Math.random() * list.length)];
  };

  useEffect(() => {
    if (phase === 'listening') {
      timerRef.current = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            clearInterval(timerRef.current!);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      // Simulation of speech recognition
      const simInterval = setInterval(() => {
        setWords(prev => {
          const newWord = getMockWord();
          if (!prev.includes(newWord)) {
            const next = [...prev, newWord];
            // If they reached the target, we can end early or keep going until time's up.
            // Let's end early if outcome='pass' or auto and reached target.
            return next;
          }
          return prev;
        });
      }, 2000 / simSpeed);

      return () => {
        if (timerRef.current) clearInterval(timerRef.current);
        clearInterval(simInterval);
      };
    }
  }, [phase, simSpeed, letter]);

  // Check win/loss condition
  useEffect(() => {
    if (phase === 'listening') {
      const isPass = outcome === 'pass' || (outcome === 'auto' && words.length >= level.words);
      const isFail = outcome === 'fail' || (outcome === 'auto' && timeLeft === 0 && words.length < level.words);

      if (isPass || isFail || timeLeft === 0) {
        if (timerRef.current) clearInterval(timerRef.current);
        // Add a slight delay before showing result
        const t = setTimeout(() => {
          onFinish({
            pass: words.length >= level.words || outcome === 'pass',
            words: words
          });
        }, 800);
        return () => clearTimeout(t);
      }
    }
  }, [words.length, timeLeft, phase, outcome, level.words, onFinish]);

  const progressPct = Math.min(100, (words.length / level.words) * 100);
  const timePct = Math.max(0, (timeLeft / level.time) * 100);

  return (
    <div className="a2z-stage fade-in">
      <button className="a2z-icon-btn-square a2z-stage-close" onClick={onClose} aria-label="Close">
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
          {phase === 'listening' && (
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
            if (phase === 'idle') setPhase('listening');
          }}
        >
          {phase === 'idle' ? (
            <>
              <Mic size={36} strokeWidth={2.5} />
              <div className="a2z-mic-start-cta">Tap to start</div>
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

      {phase === 'idle' && (
        <div className="a2z-demo-tag">✨ Simulated Speech Demo</div>
      )}
    </div>
  );
}
