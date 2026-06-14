import type {
  ResumeUploadResponse,
  StartInterviewResponse,
  QuestionResponse,
  SubmitAnswerResponse,
  ReportResponse,
} from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Request failed");
  }
  return res.json() as Promise<T>;
}

export const api = {
  uploadResume: (formData: FormData): Promise<ResumeUploadResponse> =>
    request("/resume/upload", { method: "POST", body: formData }),

  startInterview: (
    candidate_id: string,
    role: string
  ): Promise<StartInterviewResponse> =>
    request("/interview/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidate_id, role }),
    }),

  getQuestion: (session_id: string): Promise<QuestionResponse> =>
    request(`/interview/question/${session_id}`),

  submitAnswer: (
    session_id: string,
    question_id: string,
    answer_text: string
  ): Promise<SubmitAnswerResponse> =>
    request("/interview/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id, question_id, answer_text }),
    }),

  endSession: (session_id: string): Promise<{ status: string }> =>
    request(`/interview/end/${session_id}`, { method: "POST" }),

  getReport: (session_id: string): Promise<ReportResponse> =>
    request(`/report/${session_id}`),
};
