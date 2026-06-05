"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronRight, Search, Bell, ChevronLeft } from 'lucide-react';
import { useQuery } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { authApi } from "@/lib/auth-api";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { useAuthStore } from "@/store/authStore";
import { A2Z_LETTERS, A2Z_LEVELS } from './data';
import { A2ZHome } from './components/A2ZHome';
import { A2ZSpin } from './components/A2ZSpin';
import { A2ZSpeak } from './components/A2ZSpeak';
import { A2ZResult } from './components/A2ZResult';
import './a2z.css';

const STORE_KEY = 'lingosai_a2z_progress_v1';

function loadProgress() {
  if (typeof window === 'undefined') return { cleared: { 1: [], 2: [], 3: [] } };
  try {
    const raw = JSON.parse(localStorage.getItem(STORE_KEY) || 'null');
    if (raw && raw.cleared) return raw;
  } catch (e) {}
  // Default believable starting state
  return { cleared: { 1: ['A','B','C','D','E','G','H'], 2: [], 3: [] } };
}

function saveProgress(p: any) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(STORE_KEY, JSON.stringify(p));
  } catch (e) {}
}

export default function A2ZGamePage() {
  const router = useRouter();
  const { logout } = useAuthStore();
  const { isReady } = useRequireAuth();

  const { data: user, isLoading: userLoading } = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isReady,
  });

  const [progress, setProgress] = useState<{ cleared: Record<number, string[]> }>({ cleared: { 1: [], 2: [], 3: [] } });
  const [screen, setScreen] = useState<'home' | 'spin' | 'speak' | 'result'>('home');
  const [activeLetter, setActiveLetter] = useState<string | null>(null);
  const [result, setResult] = useState<{ pass: boolean; words: string[]; target: number; levelId: number; letter: string | null } | null>(null);
  
  // Simulation settings (would normally be in TweaksPanel)
  const [simSpeed] = useState(1);
  const [outcome] = useState('auto');
  const [reduceMotion] = useState(false);
  const [jumpLevel] = useState('current');

  useEffect(() => {
    if (user && !user.diagnosis_completed) router.replace("/diagnosis");
  }, [user, router]);

  useEffect(() => {
    setProgress(loadProgress());
  }, []);

  useEffect(() => {
    if (Object.keys(progress.cleared).length > 0) {
      saveProgress(progress);
    }
  }, [progress]);

  // derive the level being played: first level not fully cleared
  const naturalLevelIdx = (() => {
    for (let i = 0; i < A2Z_LEVELS.length; i++) {
      if ((progress.cleared[A2Z_LEVELS[i].id] || []).length < A2Z_LETTERS.length) return i;
    }
    return A2Z_LEVELS.length - 1;
  })();
  
  const levelIdx = jumpLevel === 'current' ? naturalLevelIdx
    : Math.max(0, Math.min(A2Z_LEVELS.length - 1, parseInt(jumpLevel, 10) - 1));
    
  const level = A2Z_LEVELS[levelIdx];
  const clearedHere = progress.cleared[level.id] || [];
  const openLetters = A2Z_LETTERS.filter(l => !clearedHere.includes(l));

  const startSpin = useCallback((forced: string | null) => {
    const pool = openLetters.length ? openLetters : A2Z_LETTERS;
    const letter = forced || pool[Math.floor(Math.random() * pool.length)];
    setActiveLetter(letter);
    setScreen('spin');
  }, [openLetters]);

  const onSpinDone = useCallback((letter: string) => { 
    setActiveLetter(letter); 
    setScreen('speak'); 
  }, []);

  const onRoundFinish = useCallback(({ pass, words }: { pass: boolean, words: string[] }) => {
    setResult({ pass, words, target: level.words, levelId: level.id, letter: activeLetter });
    if (pass && activeLetter) {
      setProgress(p => {
        const set = new Set(p.cleared[level.id] || []);
        set.add(activeLetter);
        return { ...p, cleared: { ...p.cleared, [level.id]: Array.from(set) } };
      });
    }
    setScreen('result');
  }, [level, activeLetter]);

  if (!isReady) return null;

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        background: "oklch(91% 0.04 245)",
        position: "relative",
      }}
    >
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />

      {/* Dot grid overlay */}
      <div
        aria-hidden="true"
        style={{
          position: "fixed",
          inset: 0,
          pointerEvents: "none",
          backgroundImage:
            "radial-gradient(circle, rgba(90,130,210,0.13) 1px, transparent 1px)",
          backgroundSize: "22px 22px",
          zIndex: 0,
        }}
      />

      <div style={{ position: "relative", zIndex: 1 }}>
        <DashboardLayout
        user={user}
        onSignOut={handleLogout}
        mainStyle={{
          maxWidth: 1240,
          margin: "0 auto",
          padding: "20px 20px 76px",
        }}
      >
        <button
          className="a2z-back-link"
          onClick={() => router.push("/challenges")}
          style={{ border: 'none', background: 'none', padding: 0, margin: '0 0 20px 0', display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 14, fontWeight: 600, color: '#0f172a', cursor: 'pointer' }}
        >
          <ChevronLeft size={18} />
          Challenges
        </button>
        <div className="a2z-wrapper" style={{ background: "transparent", minHeight: "auto" }}>
      {screen === 'home' && (
        <A2ZHome
          level={level} 
          levelIdx={levelIdx} 
          clearedHere={clearedHere}
          allCleared={progress.cleared}
          onSpin={() => startSpin(null)} 
          onPick={(l) => startSpin(l)} 
          levels={A2Z_LEVELS}
        />
      )}
      {screen === 'spin' && (
        <A2ZSpin 
          target={activeLetter} 
          level={level} 
          reduceMotion={reduceMotion}
          onDone={onSpinDone} 
          onClose={() => setScreen('home')} 
        />
      )}
      {screen === 'speak' && (
        <A2ZSpeak 
          letter={activeLetter} 
          level={level}
          outcome={outcome} 
          simSpeed={simSpeed} 
          reduceMotion={reduceMotion}
          onFinish={onRoundFinish} 
          onClose={() => setScreen('home')} 
        />
      )}
      {screen === 'result' && result && (
        <A2ZResult 
          result={result} 
          level={level} 
          reduceMotion={reduceMotion}
          onAgain={() => startSpin(result.letter)}
          onNext={() => startSpin(null)}
          onMap={() => setScreen('home')} 
        />
      )}
        </div>
      </DashboardLayout>
      </div>
    </div>
  );
}
