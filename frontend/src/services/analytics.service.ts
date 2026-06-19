import api from "./api";
import type { DashboardData } from "@/types/analytics";

export const analyticsService = {
  async getDashboard(): Promise<DashboardData> {
    const res = await api.get("/analytics/dashboard");
    return res.data;
  },

  async getTrends() {
    const res = await api.get("/analytics/trends");
    return res.data;
  },

  async getSkills() {
    const res = await api.get("/analytics/skills");
    return res.data;
  },
};
