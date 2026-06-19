export interface DashboardStats {
  total_interviews: number;
  completed_interviews: number;
  average_score: number;
  best_score: number;
  total_questions_answered: number;
  most_practiced_type?: string;
}

export interface ScoreTrend {
  date: string;
  score: number;
  interview_type: string;
}

export interface SkillScore {
  skill: string;
  score: number;
  count: number;
}

export interface DashboardData {
  stats: DashboardStats;
  recent_scores: ScoreTrend[];
  skill_scores: SkillScore[];
  interview_type_distribution: Record<string, number>;
  score_by_type: Record<string, number>;
}
