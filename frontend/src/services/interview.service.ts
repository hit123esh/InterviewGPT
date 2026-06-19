import api from "./api";
import type { Interview, InterviewCreate, QuestionResponse } from "@/types/interview";

export const interviewService = {
  async create(data: InterviewCreate): Promise<Interview> {
    const res = await api.post("/interviews/create", data);
    return res.data;
  },

  async list(): Promise<{ interviews: Interview[]; total: number }> {
    const res = await api.get("/interviews/");
    return res.data;
  },

  async getById(id: string): Promise<Interview> {
    const res = await api.get(`/interviews/${id}`);
    return res.data;
  },

  async start(id: string): Promise<QuestionResponse> {
    const res = await api.post(`/interviews/${id}/start`);
    return res.data;
  },

  async submitAnswer(id: string, answer: string): Promise<QuestionResponse> {
    const res = await api.post(`/interviews/${id}/answer`, { answer });
    return res.data;
  },

  async endEarly(id: string): Promise<Record<string, unknown>> {
    const res = await api.post(`/interviews/${id}/end`);
    return res.data;
  },

  async getQuestions(id: string) {
    const res = await api.get(`/interviews/${id}/questions`);
    return res.data;
  },
};
