"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  TARGET_ROLES,
  INTERVIEW_TYPES,
  DIFFICULTIES,
  DURATIONS,
  COMPANIES,
} from "@/types/interview";
import type { InterviewCreate } from "@/types/interview";
import { interviewService } from "@/services/interview.service";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft,
  ArrowRight,
  Loader2,
  Briefcase,
  Clock,
  Building2,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";

const steps = ["Role", "Type", "Difficulty", "Duration", "Company"];

export default function NewInterviewPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState<InterviewCreate>({
    target_role: "",
    interview_type: "technical",
    difficulty: "intermediate",
    duration_minutes: 30,
    company: undefined,
  });

  async function handleCreate() {
    if (!form.target_role) {
      toast.error("Please select a target role");
      return;
    }
    setLoading(true);
    try {
      const interview = await interviewService.create(form);
      toast.success("Interview created! Starting...");
      router.push(`/interviews/${interview.id}`);
    } catch {
      toast.error("Failed to create interview");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <Button variant="ghost" size="sm" onClick={() => router.back()} className="gap-1.5 mb-4">
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
        <h1 className="text-2xl font-bold tracking-tight">New Interview</h1>
        <p className="text-muted-foreground mt-1">
          Configure your mock interview session
        </p>
      </div>

      {/* Step Indicator */}
      <div className="flex items-center gap-2">
        {steps.map((s, i) => (
          <div key={s} className="flex items-center gap-2">
            <button
              onClick={() => i <= step && setStep(i)}
              className={cn(
                "h-8 px-3 rounded-full text-xs font-medium transition-colors",
                i === step
                  ? "bg-primary text-primary-foreground"
                  : i < step
                  ? "bg-primary/10 text-primary"
                  : "bg-muted text-muted-foreground"
              )}
            >
              {s}
            </button>
            {i < steps.length - 1 && (
              <div className={cn("w-6 h-px", i < step ? "bg-primary" : "bg-border")} />
            )}
          </div>
        ))}
      </div>

      {/* Step Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={step}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.2 }}
        >
          {step === 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Briefcase className="h-5 w-5 text-primary" />
                  Select Target Role
                </CardTitle>
                <CardDescription>What position are you interviewing for?</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-3">
                {TARGET_ROLES.map((role) => (
                  <button
                    key={role}
                    onClick={() => {
                      setForm({ ...form, target_role: role });
                      setStep(1);
                    }}
                    className={cn(
                      "flex items-center gap-3 p-4 rounded-xl border text-left transition-all hover:shadow-sm",
                      form.target_role === role
                        ? "border-primary bg-primary/5 shadow-sm"
                        : "hover:border-primary/30"
                    )}
                  >
                    <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <Briefcase className="h-5 w-5 text-primary" />
                    </div>
                    <span className="font-medium">{role}</span>
                    {form.target_role === role && (
                      <Badge className="ml-auto" variant="default">Selected</Badge>
                    )}
                  </button>
                ))}
              </CardContent>
            </Card>
          )}

          {step === 1 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  Interview Type
                </CardTitle>
                <CardDescription>Choose the type of interview to practice</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-3">
                {INTERVIEW_TYPES.map((type) => (
                  <button
                    key={type.value}
                    onClick={() => {
                      setForm({ ...form, interview_type: type.value });
                      setStep(2);
                    }}
                    className={cn(
                      "flex items-center gap-3 p-4 rounded-xl border text-left transition-all hover:shadow-sm",
                      form.interview_type === type.value
                        ? "border-primary bg-primary/5 shadow-sm"
                        : "hover:border-primary/30"
                    )}
                  >
                    <span className="text-2xl">{type.icon}</span>
                    <span className="font-medium">{type.label}</span>
                  </button>
                ))}
              </CardContent>
            </Card>
          )}

          {step === 2 && (
            <Card>
              <CardHeader>
                <CardTitle>Difficulty Level</CardTitle>
                <CardDescription>Select the starting difficulty (it adapts during the interview)</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-3">
                {DIFFICULTIES.map((diff) => (
                  <button
                    key={diff.value}
                    onClick={() => {
                      setForm({ ...form, difficulty: diff.value });
                      setStep(3);
                    }}
                    className={cn(
                      "flex items-center gap-3 p-4 rounded-xl border text-left transition-all hover:shadow-sm",
                      form.difficulty === diff.value
                        ? "border-primary bg-primary/5 shadow-sm"
                        : "hover:border-primary/30"
                    )}
                  >
                    <div
                      className="h-3 w-3 rounded-full"
                      style={{ backgroundColor: diff.color }}
                    />
                    <span className="font-medium">{diff.label}</span>
                  </button>
                ))}
              </CardContent>
            </Card>
          )}

          {step === 3 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-primary" />
                  Duration
                </CardTitle>
                <CardDescription>How long do you want to practice?</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-3">
                {DURATIONS.map((dur) => (
                  <button
                    key={dur}
                    onClick={() => {
                      setForm({ ...form, duration_minutes: dur });
                      setStep(4);
                    }}
                    className={cn(
                      "flex flex-col items-center gap-1 p-6 rounded-xl border transition-all hover:shadow-sm",
                      form.duration_minutes === dur
                        ? "border-primary bg-primary/5 shadow-sm"
                        : "hover:border-primary/30"
                    )}
                  >
                    <span className="text-2xl font-bold">{dur}</span>
                    <span className="text-sm text-muted-foreground">minutes</span>
                  </button>
                ))}
              </CardContent>
            </Card>
          )}

          {step === 4 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-5 w-5 text-primary" />
                  Company (Optional)
                </CardTitle>
                <CardDescription>Practice with a company-specific interview style</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <button
                  onClick={() => setForm({ ...form, company: undefined })}
                  className={cn(
                    "flex items-center gap-3 p-4 rounded-xl border w-full text-left transition-all",
                    !form.company
                      ? "border-primary bg-primary/5 shadow-sm"
                      : "hover:border-primary/30"
                  )}
                >
                  <span className="font-medium">General Interview</span>
                  <span className="text-sm text-muted-foreground ml-auto">No company-specific style</span>
                </button>
                {COMPANIES.map((company) => (
                  <button
                    key={company.value}
                    onClick={() => setForm({ ...form, company: company.value })}
                    className={cn(
                      "flex items-center gap-3 p-4 rounded-xl border w-full text-left transition-all",
                      form.company === company.value
                        ? "border-primary bg-primary/5 shadow-sm"
                        : "hover:border-primary/30"
                    )}
                  >
                    <div
                      className="h-8 w-8 rounded-lg flex items-center justify-center text-white font-bold text-xs"
                      style={{ backgroundColor: company.color }}
                    >
                      {company.label[0]}
                    </div>
                    <span className="font-medium">{company.label}</span>
                  </button>
                ))}

                {/* Summary & Create */}
                <div className="pt-4 border-t mt-6">
                  <div className="bg-muted/50 rounded-xl p-4 mb-4 space-y-1.5 text-sm">
                    <p><span className="text-muted-foreground">Role:</span> <span className="font-medium">{form.target_role}</span></p>
                    <p><span className="text-muted-foreground">Type:</span> <span className="font-medium">{form.interview_type.replace("_", " ")}</span></p>
                    <p><span className="text-muted-foreground">Difficulty:</span> <span className="font-medium capitalize">{form.difficulty}</span></p>
                    <p><span className="text-muted-foreground">Duration:</span> <span className="font-medium">{form.duration_minutes} minutes</span></p>
                    {form.company && <p><span className="text-muted-foreground">Company:</span> <span className="font-medium capitalize">{form.company}</span></p>}
                  </div>
                  <Button
                    className="w-full h-11 text-base gap-2"
                    onClick={handleCreate}
                    disabled={loading}
                  >
                    {loading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Sparkles className="h-4 w-4" />
                    )}
                    Start Interview
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Navigation Buttons */}
      {step > 0 && step < 4 && (
        <div className="flex justify-between">
          <Button variant="outline" onClick={() => setStep(step - 1)} className="gap-1.5">
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
          <Button onClick={() => setStep(step + 1)} className="gap-1.5">
            Next
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
