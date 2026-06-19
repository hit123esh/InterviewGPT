export interface Interview {
  id: string;
  user_id: string;
  resume_id?: string;
  target_role: string;
  interview_type: InterviewType;
  difficulty: Difficulty;
  duration_minutes: number;
  company?: string;
  status: InterviewStatus;
  current_score: number;
  total_questions: number;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

export type InterviewType = "hr" | "technical" | "dsa" | "system_design" | "project_discussion";
export type Difficulty = "beginner" | "intermediate" | "advanced";
export type InterviewStatus = "pending" | "in_progress" | "completed" | "cancelled";

export interface InterviewCreate {
  target_role: string;
  interview_type: InterviewType;
  difficulty: Difficulty;
  duration_minutes: number;
  resume_id?: string;
  company?: string;
}

export interface AnswerSubmit {
  answer: string;
}

export interface QuestionResponse {
  question: string;
  question_number: number;
  difficulty: string;
  evaluation?: AnswerEvaluation;
  current_score?: number;
  is_finished: boolean;
  final_report?: Record<string, unknown>;
}

export interface AnswerEvaluation {
  score: number;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  follow_up_recommended?: boolean;
  difficulty_adjustment?: string;
}

export interface InterviewQuestion {
  id: string;
  question_number: number;
  question_text: string;
  question_type?: string;
  difficulty_level?: string;
  candidate_answer?: string;
  answer_mode: string;
  ai_evaluation?: AnswerEvaluation;
  score?: number;
  created_at: string;
}

export const TARGET_ROLES = [
  "Software Engineer",
  "AI Engineer",
  "Data Scientist",
  "Backend Engineer",
  "Frontend Engineer",
] as const;

export const INTERVIEW_TYPES: { value: InterviewType; label: string; icon: string }[] = [
  { value: "hr", label: "HR / Behavioral", icon: "👥" },
  { value: "technical", label: "Technical", icon: "⚙️" },
  { value: "dsa", label: "DSA / Coding", icon: "🧮" },
  { value: "system_design", label: "System Design", icon: "🏗️" },
  { value: "project_discussion", label: "Project Discussion", icon: "📋" },
];

export const DIFFICULTIES: { value: Difficulty; label: string; color: string }[] = [
  { value: "beginner", label: "Beginner", color: "#22c55e" },
  { value: "intermediate", label: "Intermediate", color: "#eab308" },
  { value: "advanced", label: "Advanced", color: "#ef4444" },
];

export const DURATIONS = [15, 30, 45, 60] as const;

export const COMPANIES = [
  { value: "google", label: "Google", color: "#4285F4" },
  { value: "microsoft", label: "Microsoft", color: "#00A4EF" },
  { value: "amazon", label: "Amazon", color: "#FF9900" },
  { value: "meta", label: "Meta", color: "#0084FF" },
  { value: "nvidia", label: "NVIDIA", color: "#76B900" },
] as const;
