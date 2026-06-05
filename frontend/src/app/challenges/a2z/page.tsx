"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronLeft } from 'lucide-react';
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { authApi } from "@/lib/auth-api";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { useAuthStore } from "@/store/authStore";
import { a2zApi } from "@/lib/a2z-api";
import { A2Z_LETTERS, A2Z_LEVELS } from './data';
import { A2ZHome } from './components/A2ZHome';
import { A2ZSpin } from './components/A2ZSpin';
import { A2ZSpeak } from './components/A2ZSpeak';
import { A2ZResult } from './components/A2ZResult';
import './a2z.css';

export default function A2ZGamePage() {
  const router = useRouter();
  const { logout } = useAuthStore();
  const { isReady } = useRequireAuth();
  const queryClient = useQueryClient();

  const { data: user } = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isReady,
  });

  const { data: progressData, isLoading: progressLoading } = useQuery({
    queryKey: ["a2zProgress"],
    queryFn: a2zApi.getProgress,
    enabled: isReady,
  });

  const [screen, setScreen] = useState<'home' | 'spin' | 'speak' | 'result'>('home');
  const [activeLetter, setActiveLetter] = useState<string | null>(null);
  const [activeRoundId, setActiveRoundId] = useState<number | null>(null);
  const [result, setResult] = useState<{ pass: boolean; words: string[]; target: number; levelId: number; letter: string | null } | null>(null);
  const [reduceMotion] = useState(false);
  const [isStartingRound, setIsStartingRound] = useState(false);

  useEffect(() => {
    if (user && !user.diagnosis_completed) router.replace("/diagnosis");
  }, [user, router]);

  const clearedHere = progressData ? (progressData.cleared_by_level[progressData.current_level_number] || []) : [];
  const allCleared = progressData ? progressData.cleared_by_level : { 1: [], 2: [], 3: [] };
  const levelIdx = progressData ? Math.min(progressData.current_level_number - 1, A2Z_LEVELS.length - 1) : 0;
  const level = A2Z_LEVELS[levelIdx];

  const startSpin = useCallback(async (forced: string | null) => {
    try {
      setIsStartingRound(true);
      const mode = forced ? "pick" : "spin";
      const res = await a2zApi.startRound(mode, forced || undefined);
      setActiveLetter(res.letter);
      setActiveRoundId(res.round_id);
      setScreen('spin');
    } catch (e) {
      console.error("Failed to start round", e);
    } finally {
      setIsStartingRound(false);
    }
  }, []);

  const onSpinDone = useCallback(() => { 
    setScreen('speak'); 
  }, []);

  const onRoundFinish = useCallback(async ({ pass, words }: { pass: boolean, words: string[] }) => {
    if (activeRoundId === null) return;
    
    try {
      const finishRes = await a2zApi.finishRound(activeRoundId);
      setResult({ 
        pass: finishRes.passed, 
        words: finishRes.valid_words, 
        target: finishRes.target_words, 
        levelId: finishRes.level_number, 
        letter: finishRes.letter 
      });
      queryClient.setQueryData(["a2zProgress"], finishRes.progress);
      setScreen('result');
    } catch (e) {
      console.error("Failed to finish round", e);
      setResult({ pass, words, target: level.words, levelId: level.id, letter: activeLetter });
      setScreen('result');
    }
  }, [activeRoundId, level, activeLetter, queryClient]);

  if (!isReady || progressLoading) return null;

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
          disabled={isStartingRound}
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
          allCleared={allCleared}
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
          roundId={activeRoundId!}
          letter={activeLetter} 
          level={level}
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
