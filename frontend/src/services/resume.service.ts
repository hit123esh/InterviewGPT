import api from "./api";
import type { Resume, ResumeListResponse } from "@/types/resume";

export const resumeService = {
  async upload(file: File): Promise<Resume> {
    const formData = new FormData();
    formData.append("file", file);
    const res = await api.post("/resumes/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  },

  async list(): Promise<ResumeListResponse> {
    const res = await api.get("/resumes/");
    return res.data;
  },

  async getById(id: string): Promise<Resume> {
    const res = await api.get(`/resumes/${id}`);
    return res.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/resumes/${id}`);
  },

  async getSkills(id: string): Promise<{ skills: string[] }> {
    const res = await api.get(`/resumes/${id}/skills`);
    return res.data;
  },
};
