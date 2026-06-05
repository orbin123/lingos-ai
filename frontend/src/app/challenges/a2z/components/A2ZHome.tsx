import React from 'react';
import { Trophy, Check } from 'lucide-react';
import { A2Z_LETTERS } from '../data';

interface A2ZHomeProps {
  level: { id: number; name: string; words: number; time: number };
  levelIdx: number;
  clearedHere: string[];
  allCleared: Record<number, string[]>;
  onSpin: () => void;
  onPick: (l: string) => void;
  levels: { id: number; name: string; words: number; time: number }[];
}

export function A2ZHome({ level, levelIdx, clearedHere, allCleared, onSpin, onPick, levels }: A2ZHomeProps) {
  return (
    <div className="a2z-page fade-in">
      <div className="a2z-page-label">
        <Trophy size={14} /> Challenges · Vocabulary
      </div>
      
      <div className="a2z-hero">
        <div className="a2z-glass a2z-info-card">
          <div className="a2z-wordmark">a<span className="twotone">2</span>z</div>
          <p className="a2z-page-sub">
            Spin for a letter, then race the clock naming words that start with it. Clear all 24 letters to climb to the next level.
          </p>
        </div>
        
        <div className="a2z-how-card">
          <h3 className="a2z-how-head">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            Three levels, one alphabet
          </h3>
          <p className="a2z-how-blurb">
            Each level asks for more words in a little more time. Pass every letter to advance.
          </p>
          <div className="a2z-how-levels">
            {levels.map((l, i) => (
              <div key={l.id} className={`a2z-how-box ${i === levelIdx ? 'active' : ''}`}>
                <div className="lname">{l.name}</div>
                <div className="lnum">{l.words}</div>
                <div className="lwords">words</div>
                <div className="lsec">
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                  {l.time} s
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="a2z-glass a2z-play-panel">
        <div className="a2z-play-left">
          <div className="a2z-play-level">
            <span className="lv">Level {level.id}</span>
            <span className="lv-name">{level.name}</span>
          </div>
          <div className="a2z-progress-track">
            <div className="a2z-progress-fill" style={{ width: `${(clearedHere.length / A2Z_LETTERS.length) * 100}%` }}></div>
          </div>
          <div className="a2z-play-meta">
            <span><b>{clearedHere.length}</b> / {A2Z_LETTERS.length} letters cleared</span>
            <span>·</span>
            <span><b>{level.words}</b> words in <b>{level.time}s</b> each</span>
          </div>
        </div>
        <div className="a2z-play-right">
          <button className="a2z-btn-spin" onClick={onSpin}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.92-10.44l5.67-5.67"/></svg>
            Spin for a letter
          </button>
          <div className="a2z-play-hint">or tap any letter below</div>
        </div>
      </div>

      <div className="a2z-map-head">
        <h3 className="a2z-map-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>
          Your alphabet
        </h3>
        <div className="a2z-map-legend">
          <span className="a2z-legend-dot"><i style={{ background: 'var(--green)' }}></i> Cleared</span>
          <span className="a2z-legend-dot"><i style={{ background: 'white', border: '1px solid var(--line)' }}></i> Open</span>
        </div>
      </div>

      <div className="a2z-letter-grid">
        {A2Z_LETTERS.map(letter => {
          const isCleared = clearedHere.includes(letter);
          return (
            <div 
              key={letter} 
              className={`a2z-tile ${isCleared ? 'cleared' : 'open'}`}
              onClick={() => onPick(letter)}
            >
              {letter}
              {isCleared && (
                <div className="a2z-tile-check">
                  <Check strokeWidth={4} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
