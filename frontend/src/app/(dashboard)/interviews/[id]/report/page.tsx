"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { reportService } from "@/services/report.service";
import { interviewService } from "@/services/interview.service";
import { toast } from "sonner";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Download,
  Award,
  TrendingUp,
  MessageSquare,
  BookOpen,
  Target,
  Lightbulb,
} from "lucide-react";
import type { Report } from "@/types/report";
import type { Interview } from "@/types/interview";

export default function InterviewReportPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [report, setReport] = useState<Report | null>(null);
  const [interview, setInterview] = useState<Interview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [rpt, intv] = await Promise.all([
          reportService.getByInterview(id),
          interviewService.getById(id),
        ]);
        setReport(rpt);
        setInterview(intv);
      } catch {
        toast.error("Report not found");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  async function handleDownloadPdf() {
    try {
      const blob = await reportService.downloadPdf(id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `interview_report_${id.slice(0, 8)}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success("PDF downloaded");
    } catch {
      toast.error("PDF download failed");
    }
  }

  const gradeColor = (g?: string) => {
    if (!g) return "text-muted-foreground";
    if (g.startsWith("A")) return "text-emerald-600";
    if (g.startsWith("B")) return "text-blue-600";
    if (g.startsWith("C")) return "text-amber-600";
    return "text-red-600";
  };

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-40" />
        <Skeleton className="h-60" />
      </div>
    );
  }

  if (!report) {
    return (
      <div className="text-center py-20">
        <p className="text-muted-foreground">Report not available yet.</p>
        <Button variant="outline" onClick={() => router.back()} className="mt-4">
          Go Back
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => router.push("/reports")} className="gap-1">
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-xl font-bold">Interview Report</h1>
            <p className="text-sm text-muted-foreground">
              {interview?.target_role} · {interview?.interview_type?.replace("_", " ")} · {interview?.duration_minutes}min
            </p>
          </div>
        </div>
        <Button onClick={handleDownloadPdf} variant="outline" className="gap-2">
          <Download className="h-4 w-4" />
          PDF
        </Button>
      </div>

      {/* Grade Card */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card className="bg-gradient-to-br from-primary/5 to-violet-500/5 border-primary/20">
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Overall Grade</p>
              <p className={`text-5xl font-bold ${gradeColor(report.overall_grade)}`}>
                {report.overall_grade || "—"}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground mb-1">Overall Score</p>
              <p className="text-3xl font-bold">{report.overall_score?.toFixed(1) || 0}/10</p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Executive Summary */}
      {report.executive_summary && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Award className="h-4 w-4 text-primary" />
              Executive Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed text-muted-foreground">
              {report.executive_summary}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Technical Assessment */}
      {report.technical_assessment && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-primary" />
              Technical Assessment — {(report.technical_assessment as Record<string, unknown>).score as number}/10
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              {(report.technical_assessment as Record<string, unknown>).summary as string}
            </p>
            {((report.technical_assessment as Record<string, unknown>).key_strengths as string[] || []).length > 0 && (
              <div>
                <p className="text-xs font-medium text-emerald-600 mb-1.5">Strengths</p>
                <div className="flex flex-wrap gap-1.5">
                  {((report.technical_assessment as Record<string, unknown>).key_strengths as string[]).map((s: string, i: number) => (
                    <Badge key={i} variant="secondary" className="text-xs">{s}</Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Improvement Areas */}
      {report.improvement_areas && report.improvement_areas.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Target className="h-4 w-4 text-primary" />
              Improvement Areas
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {report.improvement_areas.map((item, i) => (
              <div key={i} className="flex gap-3 p-3 rounded-lg bg-muted/50">
                <Badge
                  variant={
                    item.priority === "high" ? "destructive" : item.priority === "medium" ? "default" : "secondary"
                  }
                  className="text-xs h-5 shrink-0"
                >
                  {item.priority}
                </Badge>
                <div>
                  <p className="text-sm font-medium">{item.area}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{item.recommendation}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Learning Path */}
      {report.learning_path && report.learning_path.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-primary" />
              Suggested Learning Path
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {report.learning_path.map((item, i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg border">
                <BookOpen className="h-4 w-4 text-primary mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-medium">{item.topic}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{item.description}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
