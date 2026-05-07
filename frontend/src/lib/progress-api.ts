import { api } from "./api";

export interface SkillScoreSnapshot {
  skill_id: number;
  skill_name: string;
  score: number;
}

export interface WeeklySnapshot {
  overall_score_change: number;
  tasks_completed: number;
  weekly_task_goal: number;
  best_skill_name: string | null;
  best_skill_score: number | null;
}

export interface StatsMistake {
  label: string;
  issue: string;
  correction: string | null;
}

export interface RecentActivity {
  id: number;
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

export interface StatsDashboard {
  weekly_snapshot: WeeklySnapshot;
  skill_scores: SkillScoreSnapshot[];
  feedback: StatsFeedback;
  recent_activities: RecentActivity[];
}

export const progressApi = {
  getStats: () => api.get<StatsDashboard>("/progress/stats").then((r) => r.data),
};
