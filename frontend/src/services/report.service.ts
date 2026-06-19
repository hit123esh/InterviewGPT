import api from "./api";
import type { Report } from "@/types/report";

export const reportService = {
  async list(): Promise<Report[]> {
    const res = await api.get("/reports/");
    return res.data;
  },

  async getByInterview(interviewId: string): Promise<Report> {
    const res = await api.get(`/reports/${interviewId}`);
    return res.data;
  },

  async downloadPdf(interviewId: string): Promise<Blob> {
    const res = await api.get(`/reports/${interviewId}/pdf`, {
      responseType: "blob",
    });
    return res.data;
  },
};
