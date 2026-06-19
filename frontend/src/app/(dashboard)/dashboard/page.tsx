"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  MessageSquare,
  FileText,
  BarChart3,
  TrendingUp,
  Plus,
  ArrowRight,
  Clock,
  Target,
  Zap,
  Award,
} from "lucide-react";
import { motion } from "framer-motion";
import { analyticsService } from "@/services/analytics.service";
import { interviewService } from "@/services/interview.service";
import type { DashboardData } from "@/types/analytics";
import type { Interview } from "@/types/interview";

const fadeIn = {
  hidden: { opacity: 0, y: 15 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.35 },
  }),
};

export default function DashboardPage() {
  const { user } = useAuth();
  const [dashData, setDashData] = useState<DashboardData | null>(null);
  const [recentInterviews, setRecentInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [analytics, interviews] = await Promise.all([
          analyticsService.getDashboard().catch(() => null),
          interviewService.list().catch(() => ({ interviews: [] })),
        ]);
        setDashData(analytics);
        setRecentInterviews(interviews.interviews.slice(0, 5));
      } catch {
        // Silently fail for dashboard
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const stats = dashData?.stats || {
    total_interviews: 0,
    completed_interviews: 0,
    average_score: 0,
    best_score: 0,
    total_questions_answered: 0,
  };

  const statCards = [
    {
      label: "Total Interviews",
      value: stats.total_interviews,
      icon: MessageSquare,
      color: "text-blue-600",
      bg: "bg-blue-50",
    },
    {
      label: "Average Score",
      value: stats.average_score ? `${stats.average_score}/10` : "—",
      icon: TrendingUp,
      color: "text-emerald-600",
      bg: "bg-emerald-50",
    },
    {
      label: "Best Score",
      value: stats.best_score ? `${stats.best_score}/10` : "—",
      icon: Award,
      color: "text-amber-600",
      bg: "bg-amber-50",
    },
    {
      label: "Questions Answered",
      value: stats.total_questions_answered,
      icon: Target,
      color: "text-violet-600",
      bg: "bg-violet-50",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Welcome back, {user?.full_name?.split(" ")[0] || "there"} 👋
          </h1>
          <p className="text-muted-foreground mt-1">
            Here&apos;s an overview of your interview preparation progress.
          </p>
        </div>
        <Link href="/interviews/new">
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            New Interview
          </Button>
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial="hidden"
            animate="visible"
            custom={i}
            variants={fadeIn}
          >
            <Card className="hover:shadow-md transition-shadow">
              <CardContent className="p-5">
                {loading ? (
                  <div className="space-y-3">
                    <Skeleton className="h-10 w-10 rounded-xl" />
                    <Skeleton className="h-8 w-20" />
                    <Skeleton className="h-4 w-28" />
                  </div>
                ) : (
                  <>
                    <div className={`h-10 w-10 rounded-xl ${stat.bg} flex items-center justify-center mb-3`}>
                      <stat.icon className={`h-5 w-5 ${stat.color}`} />
                    </div>
                    <div className="text-2xl font-bold">{stat.value}</div>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {stat.label}
                    </p>
                  </>
                )}
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <motion.div
          initial="hidden"
          animate="visible"
          custom={4}
          variants={fadeIn}
        >
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Zap className="h-4 w-4 text-primary" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Link href="/interviews/new" className="block">
                <div className="flex items-center gap-3 p-3 rounded-lg border hover:bg-accent transition-colors group">
                  <div className="h-9 w-9 rounded-lg bg-blue-50 flex items-center justify-center">
                    <MessageSquare className="h-4.5 w-4.5 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Start Interview</p>
                    <p className="text-xs text-muted-foreground">Begin a new practice session</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                </div>
              </Link>
              <Link href="/resumes" className="block">
                <div className="flex items-center gap-3 p-3 rounded-lg border hover:bg-accent transition-colors group">
                  <div className="h-9 w-9 rounded-lg bg-emerald-50 flex items-center justify-center">
                    <FileText className="h-4.5 w-4.5 text-emerald-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Upload Resume</p>
                    <p className="text-xs text-muted-foreground">Add or update your resume</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                </div>
              </Link>
              <Link href="/analytics" className="block">
                <div className="flex items-center gap-3 p-3 rounded-lg border hover:bg-accent transition-colors group">
                  <div className="h-9 w-9 rounded-lg bg-violet-50 flex items-center justify-center">
                    <BarChart3 className="h-4.5 w-4.5 text-violet-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">View Analytics</p>
                    <p className="text-xs text-muted-foreground">Track your progress</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                </div>
              </Link>
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent Interviews */}
        <motion.div
          className="lg:col-span-2"
          initial="hidden"
          animate="visible"
          custom={5}
          variants={fadeIn}
        >
          <Card className="h-full">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <Clock className="h-4 w-4 text-primary" />
                Recent Interviews
              </CardTitle>
              <Link href="/interviews">
                <Button variant="ghost" size="sm" className="text-xs gap-1">
                  View All <ArrowRight className="h-3 w-3" />
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <Skeleton key={i} className="h-14 w-full" />
                  ))}
                </div>
              ) : recentInterviews.length === 0 ? (
                <div className="text-center py-8">
                  <MessageSquare className="h-10 w-10 text-muted-foreground/30 mx-auto mb-3" />
                  <p className="text-sm text-muted-foreground mb-3">
                    No interviews yet
                  </p>
                  <Link href="/interviews/new">
                    <Button size="sm" variant="outline" className="gap-1.5">
                      <Plus className="h-3.5 w-3.5" />
                      Start Your First Interview
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="space-y-2">
                  {recentInterviews.map((interview) => (
                    <Link
                      key={interview.id}
                      href={
                        interview.status === "completed"
                          ? `/interviews/${interview.id}/report`
                          : interview.status === "in_progress"
                          ? `/interviews/${interview.id}`
                          : `/interviews/${interview.id}`
                      }
                    >
                      <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-accent transition-colors">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">
                            {interview.target_role} — {interview.interview_type.replace("_", " ")}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(interview.created_at).toLocaleDateString()} ·{" "}
                            {interview.duration_minutes} min
                          </p>
                        </div>
                        <Badge
                          variant={
                            interview.status === "completed"
                              ? "default"
                              : interview.status === "in_progress"
                              ? "secondary"
                              : "outline"
                          }
                          className="text-xs capitalize"
                        >
                          {interview.status.replace("_", " ")}
                        </Badge>
                        {interview.current_score > 0 && (
                          <span className="text-sm font-semibold text-primary">
                            {interview.current_score.toFixed(1)}
                          </span>
                        )}
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
