export interface ParsedResume {
  name: string;
  email: string;
  phone: string;
  skills: string[];
  programming_languages: string[];
  frameworks: string[];
  tools: string[];
  projects: string[];
  experience: string[];
  education: string;
  certifications: string[];
}

export interface ResumeUploadResponse {
  candidate_id: string;
  name: string;
  email: string;
  parsed_data: ParsedResume;
}

export interface StartInterviewResponse {
  session_id: string;
  candidate_id: string;
  role: string;
  status: string;
}

export interface QuestionResponse {
  question_id: string;
  session_id: string;
  question_text: string;
  order_index: number;
  difficulty: "easy" | "medium" | "hard";
  total_questions: number;
  is_last: boolean;
}

export interface SubmitAnswerResponse {
  answer_id: string;
  question_id: string;
  submitted_at: string;
}

export interface QAPair {
  question: string;
  answer: string;
  quality_score: number | null;
}

export interface ReportResponse {
  report_id: string;
  session_id: string;
  role: string;
  candidate_name: string;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  overall_score: number | null;
  recommendation: "Hire" | "Maybe" | "Reject";
  qa_pairs: QAPair[];
  generated_at: string;
}

export type Role =
  | "AI/ML Engineer"
  | "Backend Engineer"
  | "Frontend Engineer"
  | "Full Stack Engineer"
  | "DevOps Engineer"
  | "Data Scientist";

export const SUPPORTED_ROLES: Role[] = [
  "AI/ML Engineer",
  "Backend Engineer",
  "Frontend Engineer",
  "Full Stack Engineer",
  "DevOps Engineer",
  "Data Scientist",
];
