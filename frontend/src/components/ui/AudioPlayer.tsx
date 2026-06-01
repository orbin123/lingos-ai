"use client";

import { useEffect, useRef, useState, type MouseEvent } from "react";
import { Pause, Play, Volume2 } from "lucide-react";

interface AudioPlayerProps {
  /** Object URL or remote URL of the audio to play. */
  src: string;
  className?: string;
}

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) seconds = 0;
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

/**
 * A compact, branded audio player — replaces the default browser <audio
 * controls> chrome. Play/pause, a seekable progress bar, and time readouts.
 *
 * Handles the MediaRecorder quirk where blob durations report `Infinity`
 * until the element is seeked once.
 */
export function AudioPlayer({ src, className = "" }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playing, setPlaying] = useState(false);
  const [current, setCurrent] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const resolveDuration = () => {
      if (audio.duration === Infinity || Number.isNaN(audio.duration)) {
        // WebM blobs from MediaRecorder often have no duration until we seek
        // past the end once — this forces the browser to compute it.
        const onFix = () => {
          audio.currentTime = 0;
          setDuration(Number.isFinite(audio.duration) ? audio.duration : 0);
          audio.removeEventListener("timeupdate", onFix);
        };
        audio.addEventListener("timeupdate", onFix);
        audio.currentTime = 1e101;
      } else {
        setDuration(audio.duration);
      }
    };

    const onTime = () => setCurrent(audio.currentTime);
    const onEnded = () => {
      setPlaying(false);
      setCurrent(0);
    };

    audio.addEventListener("loadedmetadata", resolveDuration);
    audio.addEventListener("timeupdate", onTime);
    audio.addEventListener("ended", onEnded);
    // metadata may already be available if the element resolved synchronously
    if (audio.readyState >= 1) resolveDuration();

    return () => {
      audio.removeEventListener("loadedmetadata", resolveDuration);
      audio.removeEventListener("timeupdate", onTime);
      audio.removeEventListener("ended", onEnded);
    };
  }, [src]);

  const toggle = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (playing) {
      audio.pause();
      setPlaying(false);
    } else {
      void audio.play();
      setPlaying(true);
    }
  };

  const seek = (e: MouseEvent<HTMLDivElement>) => {
    const audio = audioRef.current;
    if (!audio || !duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const ratio = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width));
    audio.currentTime = ratio * duration;
    setCurrent(audio.currentTime);
  };

  const pct = duration ? Math.min(100, (current / duration) * 100) : 0;

  return (
    <div
      className={`flex items-center gap-3 rounded-full border border-slate-200 bg-white px-2.5 py-2 shadow-[0_2px_10px_rgba(15,23,42,0.04)] ${className}`}
    >
      <audio ref={audioRef} src={src} preload="metadata" className="hidden" />

      <button
        type="button"
        onClick={toggle}
        aria-label={playing ? "Pause" : "Play"}
        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-blue-600 text-white shadow-[0_3px_10px_rgba(37,99,235,0.3)] transition-all hover:bg-blue-700 active:scale-95"
      >
        {playing ? (
          <Pause className="h-4 w-4" fill="currentColor" />
        ) : (
          <Play className="ml-0.5 h-4 w-4" fill="currentColor" />
        )}
      </button>

      <span className="w-9 text-[12.5px] font-semibold tabular-nums text-[#0a1f44]">
        {formatTime(current)}
      </span>

      <div
        onClick={seek}
        role="slider"
        aria-label="Seek"
        aria-valuemin={0}
        aria-valuemax={Math.round(duration)}
        aria-valuenow={Math.round(current)}
        className="group relative h-2 flex-1 cursor-pointer rounded-full bg-slate-100"
      >
        <div
          className="absolute left-0 top-0 h-full rounded-full bg-blue-600"
          style={{ width: `${pct}%` }}
        />
        <div
          className="absolute top-1/2 h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-blue-600 bg-white opacity-0 shadow transition-opacity group-hover:opacity-100"
          style={{ left: `${pct}%` }}
        />
      </div>

      <span className="w-9 text-right text-[12.5px] font-medium tabular-nums text-slate-400">
        {formatTime(duration)}
      </span>

      <Volume2 className="mr-1 h-4 w-4 shrink-0 text-slate-400" />
    </div>
  );
}
