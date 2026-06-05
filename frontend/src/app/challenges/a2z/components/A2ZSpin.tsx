import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { A2Z_LETTERS } from '../data';

interface A2ZSpinProps {
  target: string | null;
  level: { id: number; name: string; words: number; time: number };
  reduceMotion: boolean;
  onDone: (letter: string) => void;
  onClose: () => void;
}

export function A2ZSpin({ target, level, reduceMotion, onDone, onClose }: A2ZSpinProps) {
  const [phase, setPhase] = useState<'intro' | 'spinning' | 'landed'>('intro');
  const [displayLetter, setDisplayLetter] = useState(target || 'A');

  useEffect(() => {
    if (phase === 'intro') {
      const t = setTimeout(() => {
        setPhase('spinning');
      }, 500);
      return () => clearTimeout(t);
    }
    
    if (phase === 'spinning') {
      let interval: NodeJS.Timeout;
      if (!reduceMotion) {
        let i = 0;
        interval = setInterval(() => {
          setDisplayLetter(A2Z_LETTERS[i % A2Z_LETTERS.length]);
          i++;
        }, 50);
      }
      
      const t = setTimeout(() => {
        if (interval) clearInterval(interval);
        setDisplayLetter(target || 'A');
        setPhase('landed');
      }, reduceMotion ? 500 : 2000);
      
      return () => {
        if (interval) clearInterval(interval);
        clearTimeout(t);
      };
    }
  }, [phase, target, reduceMotion]);

  return (
    <div className="a2z-stage fade-in">
      <button className="a2z-icon-btn-square a2z-stage-close" onClick={onClose} aria-label="Close">
        <X size={20} />
      </button>

      <div className={`a2z-spin-cap ${phase === 'landed' ? 'landed' : ''}`}>
        {phase === 'landed' ? 'YOUR LETTER' : 'SPINNING...'}
      </div>

      <div className={`a2z-spin-ring ${phase === 'spinning' ? 'spinning' : ''}`}>
        <div className="ringfx"></div>
        <div className="a2z-spin-pointer"></div>
        <div className="a2z-spin-disc">
          <div className={`a2z-spin-letter ${phase === 'landed' ? 'pop' : ''}`}>
            {displayLetter}
          </div>
        </div>
      </div>

      <div className="a2z-spin-cta-wrap">
        {phase === 'landed' && (
          <div style={{ textAlign: 'center' }}>
            <div className="a2z-spin-target-note">
              You drew <b>{displayLetter}</b> — name <b>{level.words}</b> words in <b>{level.time}s</b>.
            </div>
            <button className="a2z-btn-primary-lg green" style={{ marginTop: 14 }} onClick={() => onDone(displayLetter)}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
              Start round <span style={{ marginLeft: 6 }}>›</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
