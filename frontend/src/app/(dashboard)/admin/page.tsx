"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Shield, Users, MessageSquare, TrendingUp } from "lucide-react";
import api from "@/services/api";
import { motion } from "framer-motion";

export default function AdminPage() {
  const [stats, setStats] = useState<Record<string, number> | null>(null);
  const [users, setUsers] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [statsRes, usersRes] = await Promise.all([
          api.get("/admin/stats"),
          api.get("/admin/users"),
        ]);
        setStats(statsRes.data);
        setUsers(usersRes.data);
      } catch {
        // Not admin
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Shield className="h-6 w-6 text-primary" />
          Admin Panel
        </h1>
        <p className="text-muted-foreground mt-1">Platform-wide statistics and user management</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Total Users", value: stats?.total_users || 0, icon: Users, color: "text-blue-600", bg: "bg-blue-50" },
          { label: "Total Interviews", value: stats?.total_interviews || 0, icon: MessageSquare, color: "text-emerald-600", bg: "bg-emerald-50" },
          { label: "Completed", value: stats?.completed_interviews || 0, icon: TrendingUp, color: "text-violet-600", bg: "bg-violet-50" },
          { label: "Avg Score", value: stats?.average_score ? `${stats.average_score}/10` : "—", icon: TrendingUp, color: "text-amber-600", bg: "bg-amber-50" },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
            <Card>
              <CardContent className="p-4">
                <div className={`h-9 w-9 rounded-lg ${s.bg} flex items-center justify-center mb-2`}>
                  <s.icon className={`h-4.5 w-4.5 ${s.color}`} />
                </div>
                <p className="text-xl font-bold">{s.value}</p>
                <p className="text-xs text-muted-foreground">{s.label}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Users</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {users.map((u, i) => (
              <div
                key={i}
                className="flex items-center gap-3 p-3 rounded-lg border"
              >
                <div className="flex-1">
                  <p className="text-sm font-medium">{u.full_name as string}</p>
                  <p className="text-xs text-muted-foreground">{u.email as string}</p>
                </div>
                <Badge variant="outline" className="text-xs capitalize">
                  {u.role as string}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {new Date(u.created_at as string).toLocaleDateString()}
                </span>
              </div>
            ))}
            {users.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-4">No users found</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
