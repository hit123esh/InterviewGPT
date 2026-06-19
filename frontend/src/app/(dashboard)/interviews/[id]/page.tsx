"use client";

import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { interviewService } from "@/services/interview.service";
import { useVoiceRecorder } from "@/hooks/use-voice-recorder";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send,
  Mic,
  MicOff,
  Clock,
  Brain,
  Loader2,
  ArrowLeft,
  StopCircle,
  User,
  AlertTriangle,
} from "lucide-react";
import type { Interview, QuestionResponse } from "@/types/interview";
import api from "@/services/api";

interface ChatMessage {
  role: "ai" | "user";
  content: string;
  evaluation?: Record<string, unknown>;
  score?: number;
}

export default function InterviewSessionPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [interview, setInterview] = useState<Interview | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [isFinished, setIsFinished] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [timeLeft, setTimeLeft] = useState(0);
  const [currentScore, setCurrentScore] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);
  const { isRecording, audioBlob, startRecording, stopRecording, resetRecording } = useVoiceRecorder();

  // Timer
  useEffect(() => {
    if (!interview || interview.status !== "in_progress" || isFinished) return;
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 0) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [interview, isFinished]);

  // Auto-scroll
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load interview
  useEffect(() => {
    async function load() {
      try {
        const data = await interviewService.getById(id);
        setInterview(data);
        setTimeLeft(data.duration_minutes * 60);
        setTotalQuestions(Math.max(3, Math.floor(data.duration_minutes / 4)));

        if (data.status === "pending") {
          // Start the interview
          const result = await interviewService.start(id);
          setMessages([{ role: "ai", content: result.question }]);
          setCurrentQuestion(result.question_number);
          setInterview({ ...data, status: "in_progress" });
        } else if (data.status === "in_progress") {
          // Load existing questions
          const questions = await interviewService.getQuestions(id);
          const msgs: ChatMessage[] = [];
          for (const q of questions) {
            msgs.push({ role: "ai", content: q.question_text });
            if (q.candidate_answer) {
              msgs.push({
                role: "user",
                content: q.candidate_answer,
                evaluation: q.ai_evaluation || undefined,
                score: q.score || undefined,
              });
            }
          }
          setMessages(msgs);
          setCurrentQuestion(questions.length);
        } else if (data.status === "completed") {
          setIsFinished(true);
          router.push(`/interviews/${id}/report`);
        }
      } catch {
        toast.error("Failed to load interview");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id, router]);

  async function handleSubmitAnswer() {
    if (!answer.trim() || submitting) return;
    const userAnswer = answer.trim();
    setAnswer("");
    setSubmitting(true);

    setMessages((prev) => [...prev, { role: "user", content: userAnswer }]);

    try {
      const result: QuestionResponse = await interviewService.submitAnswer(id, userAnswer);

      if (result.current_score) setCurrentScore(result.current_score);

      if (result.is_finished) {
        setIsFinished(true);
        toast.success("Interview complete! Generating report...");
        setTimeout(() => router.push(`/interviews/${id}/report`), 2000);
      } else {
        setCurrentQuestion(result.question_number);
        setMessages((prev) => [
          ...prev,
          { role: "ai", content: result.question },
        ]);
      }
    } catch {
      toast.error("Failed to submit answer");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleVoiceSubmit() {
    if (!audioBlob) return;
    setSubmitting(true);

    try {
      const formData = new FormData();
      formData.append("file", audioBlob, "answer.webm");
      const res = await api.post("/speech/transcribe", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      const transcript = res.data.text;
      if (transcript) {
        setAnswer(transcript);
        resetRecording();
        toast.success("Transcription complete");
      }
    } catch {
      toast.error("Transcription failed");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleEndEarly() {
    try {
      await interviewService.endEarly(id);
      toast.success("Interview ended. Generating report...");
      setTimeout(() => router.push(`/interviews/${id}/report`), 2000);
    } catch {
      toast.error("Failed to end interview");
    }
  }

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${sec.toString().padStart(2, "0")}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto" />
          <p className="text-muted-foreground">Setting up your interview...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto flex flex-col h-[calc(100vh-8rem)]">
      {/* Top Bar */}
      <div className="flex items-center justify-between mb-4 flex-shrink-0">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => router.push("/interviews")} className="gap-1">
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-lg font-semibold">
              {interview?.target_role} — {interview?.interview_type?.replace("_", " ")}
            </h1>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Badge variant="outline" className="text-xs capitalize">
                {interview?.difficulty}
              </Badge>
              <span>Q{currentQuestion}/{totalQuestions}</span>
              {currentScore > 0 && (
                <span className="text-primary font-medium">
                  Score: {currentScore.toFixed(1)}/10
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-sm font-mono">
            <Clock className={`h-4 w-4 ${timeLeft < 120 ? "text-destructive" : "text-muted-foreground"}`} />
            <span className={timeLeft < 120 ? "text-destructive font-bold" : ""}>
              {formatTime(timeLeft)}
            </span>
          </div>
          <Button variant="destructive" size="sm" onClick={handleEndEarly} className="gap-1.5">
            <StopCircle className="h-3.5 w-3.5" />
            End
          </Button>
        </div>
      </div>

      {/* Progress */}
      <Progress value={(currentQuestion / totalQuestions) * 100} className="mb-4 h-1.5 flex-shrink-0" />

      {/* Chat Area */}
      <Card className="flex-1 flex flex-col overflow-hidden">
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            <AnimatePresence>
              {messages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
                >
                  {msg.role === "ai" && (
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <Brain className="h-4 w-4 text-primary" />
                    </div>
                  )}
                  <div
                    className={`max-w-[75%] p-4 text-sm leading-relaxed ${
                      msg.role === "ai"
                        ? "chat-bubble-ai"
                        : "chat-bubble-user"
                    }`}
                  >
                    {msg.content}
                    {msg.score !== undefined && (
                      <div className="mt-2 pt-2 border-t border-border/50 text-xs text-muted-foreground">
                        Score: <span className="font-semibold text-primary">{msg.score}/10</span>
                      </div>
                    )}
                  </div>
                  {msg.role === "user" && (
                    <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
                      <User className="h-4 w-4 text-secondary-foreground" />
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>

            {submitting && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex gap-3"
              >
                <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <Brain className="h-4 w-4 text-primary" />
                </div>
                <div className="chat-bubble-ai p-4 flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="h-2 w-2 rounded-full bg-primary/40 animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="h-2 w-2 rounded-full bg-primary/40 animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="h-2 w-2 rounded-full bg-primary/40 animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                  <span className="text-xs text-muted-foreground ml-2">Evaluating & generating next question...</span>
                </div>
              </motion.div>
            )}
            <div ref={scrollRef} />
          </div>
        </ScrollArea>

        {/* Input Area */}
        {!isFinished && (
          <CardContent className="border-t p-4">
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <Textarea
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Type your answer..."
                  className="min-h-[60px] max-h-[120px] resize-none pr-12"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmitAnswer();
                    }
                  }}
                  disabled={submitting}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Button
                  onClick={handleSubmitAnswer}
                  disabled={!answer.trim() || submitting}
                  size="icon"
                  className="h-10 w-10"
                >
                  {submitting ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
                <Button
                  variant={isRecording ? "destructive" : "outline"}
                  size="icon"
                  className="h-10 w-10"
                  onClick={() => {
                    if (isRecording) {
                      stopRecording();
                      setTimeout(handleVoiceSubmit, 500);
                    } else {
                      startRecording().catch(() =>
                        toast.error("Microphone access denied")
                      );
                    }
                  }}
                >
                  {isRecording ? (
                    <MicOff className="h-4 w-4" />
                  ) : (
                    <Mic className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
            {isRecording && (
              <div className="flex items-center gap-2 mt-2 text-xs text-destructive">
                <div className="h-2 w-2 rounded-full bg-destructive animate-pulse" />
                Recording... Click mic button to stop and transcribe
              </div>
            )}
            {audioBlob && !isRecording && (
              <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                <AlertTriangle className="h-3 w-3" />
                Audio recorded — transcribing...
              </div>
            )}
          </CardContent>
        )}
      </Card>
    </div>
  );
}
