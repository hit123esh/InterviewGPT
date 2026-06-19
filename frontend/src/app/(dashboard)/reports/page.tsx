"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { reportService } from "@/services/report.service";
import { ClipboardList, Download, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import { motion } from "framer-motion";
import type { Report } from "@/types/report";

export default function ReportsListPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    reportService
      .list()
      .then(setReports)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const gradeColor = (g?: string) => {
    if (!g) return "bg-muted text-muted-foreground";
    if (g.startsWith("A")) return "bg-emerald-50 text-emerald-700";
    if (g.startsWith("B")) return "bg-blue-50 text-blue-700";
    if (g.startsWith("C")) return "bg-amber-50 text-amber-700";
    return "bg-red-50 text-red-700";
  };

  async function downloadPdf(interviewId: string) {
    try {
      const blob = await reportService.downloadPdf(interviewId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `report_${interviewId.slice(0, 8)}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      toast.error("PDF download failed");
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Reports</h1>
        <p className="text-muted-foreground mt-1">View and download your interview reports</p>
      </div>

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-20" />
          ))}
        </div>
      ) : reports.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <ClipboardList className="h-12 w-12 text-muted-foreground/30 mb-4" />
            <h3 className="text-lg font-semibold mb-1">No reports yet</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Complete an interview to generate your first report
            </p>
            <Link href="/interviews/new">
              <Button className="gap-2">Start an Interview</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {reports.map((report, i) => (
            <motion.div
              key={report.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Card className="hover:shadow-md transition-all">
                <CardContent className="flex items-center gap-4 p-4">
                  <div
                    className={`h-12 w-12 rounded-xl flex items-center justify-center font-bold text-lg shrink-0 ${gradeColor(
                      report.overall_grade
                    )}`}
                  >
                    {report.overall_grade || "—"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      {report.executive_summary?.slice(0, 100) || "Interview Report"}
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Score: {report.overall_score?.toFixed(1) || 0}/10 ·{" "}
                      {new Date(report.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => downloadPdf(report.interview_id)}
                      className="gap-1"
                    >
                      <Download className="h-3.5 w-3.5" />
                    </Button>
                    <Link href={`/interviews/${report.interview_id}/report`}>
                      <Button variant="outline" size="sm" className="gap-1">
                        View <ArrowRight className="h-3 w-3" />
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
