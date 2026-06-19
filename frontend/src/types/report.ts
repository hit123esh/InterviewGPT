export interface Report {
  id: string;
  interview_id: string;
  executive_summary?: string;
  technical_assessment?: AssessmentSection;
  behavioral_assessment?: AssessmentSection;
  project_knowledge?: AssessmentSection;
  communication_skills?: CommunicationSection;
  improvement_areas?: ImprovementItem[];
  learning_path?: LearningItem[];
  overall_score?: number;
  overall_grade?: string;
  created_at: string;
}

export interface AssessmentSection {
  score: number;
  summary: string;
  key_strengths?: string[];
  areas_for_improvement?: string[];
  [key: string]: unknown;
}

export interface CommunicationSection {
  score: number;
  clarity: string;
  confidence: string;
  articulation: string;
}

export interface ImprovementItem {
  area: string;
  recommendation: string;
  priority: "high" | "medium" | "low";
}

export interface LearningItem {
  topic: string;
  resource_type: string;
  description: string;
}
