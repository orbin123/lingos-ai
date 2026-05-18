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

export interface StatsDashboard {
  weekly_snapshot: WeeklySnapshot;
  skill_scores: SkillScoreSnapshot[];
  weekly_points_by_skill: Record<number, number>;
  difficulty_distribution: DifficultyDistribution;
  skill_history_labels: string[];
  skill_history: SkillHistorySeries[];
  feedback: StatsFeedback;
  recent_activities: RecentActivity[];
}

export const progressApi = {
  getStats: () => api.get<StatsDashboard>("/progress/stats").then((r) => r.data),
  getActivities: (limit = 50, offset = 0) =>
    api
      .get<RecentActivity[]>("/progress/activities", { params: { limit, offset } })
      .then((r) => r.data),
};
