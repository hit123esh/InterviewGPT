"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { interviewService } from "@/services/interview.service";
import { Plus, MessageSquare } from "lucide-react";
import { motion } from "framer-motion";
import type { Interview } from "@/types/interview";

export default function InterviewsListPage() {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    interviewService.list().then((data) => {
      setInterviews(data.interviews);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const statusColor = (s: string) => {
    switch (s) {
      case "completed": return "default";
      case "in_progress": return "secondary";
      default: return "outline";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Interviews</h1>
          <p className="text-muted-foreground mt-1">Your mock interview history</p>
        </div>
        <Link href="/interviews/new">
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            New Interview
          </Button>
        </Link>
      </div>

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-20" />
          ))}
        </div>
      ) : interviews.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <MessageSquare className="h-12 w-12 text-muted-foreground/30 mb-4" />
            <h3 className="text-lg font-semibold mb-1">No interviews yet</h3>
            <p className="text-sm text-muted-foreground mb-4">Start your first mock interview to begin improving</p>
            <Link href="/interviews/new">
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                Start First Interview
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {interviews.map((interview, i) => (
            <motion.div
              key={interview.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Link
                href={
                  interview.status === "completed"
                    ? `/interviews/${interview.id}/report`
                    : `/interviews/${interview.id}`
                }
              >
                <Card className="hover:shadow-md hover:border-primary/20 transition-all">
                  <CardContent className="flex items-center gap-4 p-4">
                    <div className="h-11 w-11 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
                      <MessageSquare className="h-5 w-5 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{interview.target_role}</p>
                      <p className="text-xs text-muted-foreground">
                        {interview.interview_type.replace("_", " ")} · {interview.difficulty} · {interview.duration_minutes}min
                        {interview.company && ` · ${interview.company}`}
                      </p>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      <Badge variant={statusColor(interview.status) as "default" | "secondary" | "outline"} className="capitalize text-xs">
                        {interview.status.replace("_", " ")}
                      </Badge>
                      {interview.current_score > 0 && (
                        <span className="text-sm font-semibold text-primary">
                          {interview.current_score.toFixed(1)}
                        </span>
                      )}
                      <span className="text-xs text-muted-foreground">
                        {new Date(interview.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
