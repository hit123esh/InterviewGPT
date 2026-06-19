export interface Resume {
  id: string;
  user_id: string;
  file_name: string;
  file_type: string;
  parsed_data?: ParsedResumeData;
  is_active: boolean;
  created_at: string;
  raw_text?: string;
}

export interface ParsedResumeData {
  name?: string;
  skills: string[];
  education: EducationItem[];
  experience: ExperienceItem[];
  projects: ProjectItem[];
  certifications: string[];
}

export interface EducationItem {
  degree: string;
  institution: string;
  year: string;
  gpa?: string;
}

export interface ExperienceItem {
  title: string;
  company: string;
  duration: string;
  description: string;
}

export interface ProjectItem {
  name: string;
  description: string;
  technologies: string[];
}

export interface ResumeListResponse {
  resumes: Resume[];
  total: number;
}
