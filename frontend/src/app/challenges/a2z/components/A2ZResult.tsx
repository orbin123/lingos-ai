import React from 'react';
import { X, Check, ArrowRight, RotateCcw } from 'lucide-react';

interface A2ZResultProps {
  result: { pass: boolean; words: string[]; target: number; levelId: number; letter: string | null };
  level: { id: number; name: string; words: number; time: number };
  reduceMotion: boolean;
  onAgain: () => void;
  onNext: () => void;
  onMap: () => void;
}

export function A2ZResult({ result, level, reduceMotion, onAgain, onNext, onMap }: A2ZResultProps) {
  const isPass = result.pass;

  return (
    <div className="a2z-stage fade-in" style={{ backgroundColor: isPass ? 'rgba(40,160,90,0.03)' : 'rgba(220,150,40,0.03)' }}>
      {isPass && !reduceMotion && (
        <div className="a2z-confetti">
          {Array.from({ length: 40 }).map((_, i) => (
            <i 
              key={i}
              style={{
                left: `${Math.random() * 100}%`,
                background: ['#0070C4', '#28a05a', '#ffb547', '#ff7a18'][Math.floor(Math.random() * 4)],
                animationDelay: `${Math.random() * 0.5}s`,
                animationDuration: `${1.5 + Math.random() * 2}s`
              }}
            />
          ))}
        </div>
      )}

      <button className="a2z-icon-btn-square a2z-stage-close" onClick={onMap} aria-label="Close">
        <X size={20} />
      </button>

      <div className="a2z-glass a2z-result-card">
        <div className={`a2z-result-medal ${isPass ? 'pass' : 'fail'}`}>
          {isPass ? (
            <Check size={40} strokeWidth={3} />
          ) : (
            <X size={40} strokeWidth={3} />
          )}
        </div>

        <div className={`a2z-result-eyebrow ${isPass ? 'pass' : 'fail'}`}>
          {isPass ? 'Letter Cleared!' : 'Time\'s Up'}
        </div>

        <h2 className="a2z-result-title">
          {isPass ? `You nailed ${result.letter}!` : `Almost got ${result.letter}`}
        </h2>
        <p className="a2z-result-sub">
          {isPass 
            ? `Great job. You found ${result.words.length} valid words starting with ${result.letter} in time.`
            : `You found ${result.words.length} out of the ${result.target} required words. Give it another shot!`}
        </p>

        <div className="a2z-result-stats">
          <div className="a2z-rstat">
            <div className="rv">{result.words.length} <span style={{ fontSize: 16, color: 'var(--ink-muted)' }}>/ {result.target}</span></div>
            <div className="rl">Words</div>
          </div>
          <div className="a2z-rstat">
            <div className="rv">{level.time}s</div>
            <div className="rl">Time</div>
          </div>
          <div className="a2z-rstat">
            <div className="rv">{(result.words.length / level.time * 60).toFixed(0)}</div>
            <div className="rl">WPM</div>
          </div>
        </div>

        {result.words.length > 0 && (
          <div className="a2z-result-words">
            <div className="rw-head">Words found</div>
            <div className="rw-chips">
              {result.words.map((w, i) => (
                <div key={i} className="a2z-rw-chip">{w}</div>
              ))}
            </div>
          </div>
        )}

        <div className="a2z-result-actions">
          {!isPass && (
            <button className="a2z-btn-solid" onClick={onAgain}>
              <RotateCcw size={16} /> Try {result.letter} again
            </button>
          )}
          {isPass && (
            <button className="a2z-btn-solid green" onClick={onNext}>
              Next letter <ArrowRight size={16} />
            </button>
          )}
          <button className="a2z-btn-ghost" onClick={onMap}>
            Back to map
          </button>
        </div>
      </div>
    </div>
  );
}
