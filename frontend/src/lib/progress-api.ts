import { api } from "./api";

export interface SkillScoreSnapshot {
  skill_id: number;
  /** Backend internal identifier — keys data by this. */
  skill_name: string;
  /** User-facing label shipped by the API (Phase 5+). Frontend renders this. */
  display_label: string;
  score: number;
}

export interface WeeklySnapshot {
  overall_score: number;
  overall_score_change: number;
  tasks_completed: number;
  weekly_task_goal: number;
  best_skill_name: string | null;
  best_skill_display_label: string | null;
  best_skill_score: number | null;
}

export interface StatsMistake {
  label: string;
  issue: string;
  correction: string | null;
}

export interface RecentActivity {
  id: number;
  user_task_id: number;
  task_name: string;
  task_type: string;
  completed_at: string;
  score: number;
  mistake_count: number;
  mistakes: StatsMistake[];
  strength: StatsMistake | null;
}

export interface StatsFeedback {
  strengths: string[];
  focus_areas: string[];
}

export interface SkillHistorySeries {
  skill_id: number;
  skill_name: string;
  display_label: string;
  scores: number[];
}

export interface DifficultyDistribution {
  beginner: number;
  intermediate: number;
  advanced: number;
  total: number;
}

export interface PracticePatterns {
  /** Formatted "Day N" — N is the curriculum day-in-week (1–7), not a weekday. */
  most_active_day: string | null;
  best_day: string | null;
  avg_session_seconds: number | null;
  sessions_count: number;
  subtitle: string;
}

export interface StatsDashboard {
  weekly_snapshot: WeeklySnapshot;
  practice_patterns: PracticePatterns;
  skill_scores: SkillScoreSnapshot[];
  weekly_points_by_skill: Record<number, number>;
  difficulty_distribution: DifficultyDistribution;
  skill_history_labels: string[];
  skill_history: SkillHistorySeries[];
  feedback: StatsFeedback;
  recent_activities: RecentActivity[];
  /** Completed speaking/pronunciation activities in the selected period. */
  speaking_tasks_completed: number;
}

export type StatsRange = "week" | "month" | "all";

export interface YesterdayWin {
  kind: string;
  badge: string;
  text: string;
}

export const progressApi = {
  getStats: (range?: StatsRange) =>
    api
      .get<StatsDashboard>("/progress/stats", {
        params: range ? { range } : undefined,
      })
      .then((r) => r.data),
  /** Current display score (0–10) for every tracked skill — seeded by diagnosis. */
  getScores: () =>
    api.get<SkillScoreSnapshot[]>("/progress/scores").then((r) => r.data),
  getActivities: (limit = 50, offset = 0) =>
    api
      .get<RecentActivity[]>("/progress/activities", { params: { limit, offset } })
      .then((r) => r.data),
  /** Up to three positive highlights from the learner's previous local day. */
  getYesterdayWins: () =>
    api
      .get<{ wins: YesterdayWin[] }>("/progress/yesterday-wins")
      .then((r) => r.data.wins),
};
