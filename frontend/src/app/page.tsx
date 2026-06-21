"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Brain,
  Mic,
  FileText,
  BarChart3,
  Target,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Zap,
  Shield,
} from "lucide-react";

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.5, ease: "easeOut" as const },
  }),
};

const features = [
  {
    icon: FileText,
    title: "Resume-Aware Questions",
    description:
      "Upload your resume and get personalized questions based on your actual projects, skills, and experience.",
    color: "text-blue-600",
    bg: "bg-blue-50",
  },
  {
    icon: Brain,
    title: "AI Interviewer Agent",
    description:
      "Powered by local Ollama LLM with LangGraph for realistic, adaptive interview conversations with follow-up questions.",
    color: "text-violet-600",
    bg: "bg-violet-50",
  },
  {
    icon: Mic,
    title: "Voice Interviews",
    description:
      "Answer questions verbally with real-time transcription powered by Faster Whisper speech recognition.",
    color: "text-emerald-600",
    bg: "bg-emerald-50",
  },
  {
    icon: Target,
    title: "Adaptive Difficulty",
    description:
      "Questions dynamically adjust based on your performance — harder when you excel, easier when you struggle.",
    color: "text-amber-600",
    bg: "bg-amber-50",
  },
  {
    icon: BarChart3,
    title: "Detailed Analytics",
    description:
      "Track your progress with score trends, skill heatmaps, and performance breakdowns over time.",
    color: "text-rose-600",
    bg: "bg-rose-50",
  },
  {
    icon: Sparkles,
    title: "Company-Specific Prep",
    description:
      "Practice with interview styles from Google, Microsoft, Amazon, Meta, and NVIDIA.",
    color: "text-cyan-600",
    bg: "bg-cyan-50",
  },
];

const interviewTypes = [
  "HR / Behavioral",
  "Technical Deep Dive",
  "Data Structures & Algorithms",
  "System Design",
  "Project Discussion",
];

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* ── Navbar ── */}
      <nav className="sticky top-0 z-50 glass border-b border-border/50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-xl bg-primary flex items-center justify-center">
              <Brain className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold tracking-tight">
              Interview<span className="text-primary">GPT</span>
            </span>
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm" className="font-medium">
                Sign In
              </Button>
            </Link>
            <Link href="/register">
              <Button size="sm" className="font-medium gap-1.5">
                Get Started <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative overflow-hidden pt-20 pb-32">
        {/* Background gradient decorations */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-violet-500/5 rounded-full blur-3xl" />
        </div>

        <div className="max-w-7xl mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center">
            <motion.div
              initial="hidden"
              animate="visible"
              custom={0}
              variants={fadeUp}
            >
              <Badge
                variant="secondary"
                className="mb-6 px-4 py-1.5 text-sm font-medium gap-1.5"
              >
                <Zap className="h-3.5 w-3.5 text-primary" />
                AI-Powered Interview Preparation
              </Badge>
            </motion.div>

            <motion.h1
              className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.08] mb-6"
              initial="hidden"
              animate="visible"
              custom={1}
              variants={fadeUp}
            >
              Ace Your Next
              <br />
              <span className="bg-gradient-to-r from-primary via-violet-500 to-primary bg-clip-text text-transparent animate-gradient">
                Technical Interview
              </span>
            </motion.h1>

            <motion.p
              className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed"
              initial="hidden"
              animate="visible"
              custom={2}
              variants={fadeUp}
            >
              Upload your resume. Choose your role. Practice with an AI
              interviewer that asks personalized questions, adapts to your level,
              and gives you detailed feedback.
            </motion.p>

            <motion.div
              className="flex flex-col sm:flex-row gap-4 justify-center"
              initial="hidden"
              animate="visible"
              custom={3}
              variants={fadeUp}
            >
              <Link href="/register">
                <Button size="lg" className="text-base px-8 h-12 gap-2 w-full sm:w-auto">
                  Start Practicing Free
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link href="/login">
                <Button
                  variant="outline"
                  size="lg"
                  className="text-base px-8 h-12 w-full sm:w-auto"
                >
                  Sign In
                </Button>
              </Link>
            </motion.div>

            {/* Interview types pills */}
            <motion.div
              className="flex flex-wrap gap-2 justify-center mt-12"
              initial="hidden"
              animate="visible"
              custom={4}
              variants={fadeUp}
            >
              {interviewTypes.map((type) => (
                <span
                  key={type}
                  className="px-3 py-1.5 text-xs font-medium rounded-full bg-secondary text-secondary-foreground"
                >
                  {type}
                </span>
              ))}
            </motion.div>
          </div>
        </div>
      </section>

      {/* ── Features Grid ── */}
      <section className="py-24 bg-secondary/30">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <Badge variant="secondary" className="mb-4">
              Features
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              Everything you need to prepare
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              A complete interview preparation platform built with cutting-edge AI
              technology.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                className="group relative bg-card rounded-2xl border p-6 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300 hover:-translate-y-1"
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: "-50px" }}
                custom={i}
                variants={fadeUp}
              >
                <div
                  className={`h-12 w-12 rounded-xl ${feature.bg} flex items-center justify-center mb-4`}
                >
                  <feature.icon className={`h-6 w-6 ${feature.color}`} />
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <Badge variant="secondary" className="mb-4">
              How It Works
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              Three steps to interview readiness
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Upload Your Resume",
                description:
                  "Upload your PDF or DOCX resume. Our AI extracts your skills, projects, and experience to personalize your interview.",
                icon: FileText,
              },
              {
                step: "02",
                title: "Choose Your Interview",
                description:
                  "Select your target role, interview type, difficulty level, and even a specific company to practice for.",
                icon: Target,
              },
              {
                step: "03",
                title: "Practice & Improve",
                description:
                  "Have a real conversation with our AI interviewer. Get scored, receive feedback, and track your progress over time.",
                icon: BarChart3,
              },
            ].map((item, i) => (
              <motion.div
                key={item.step}
                className="relative text-center"
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                custom={i}
                variants={fadeUp}
              >
                <div className="inline-flex h-16 w-16 rounded-2xl bg-primary/10 items-center justify-center mb-6">
                  <item.icon className="h-7 w-7 text-primary" />
                </div>
                <div className="text-xs font-bold text-primary mb-2 tracking-widest">
                  STEP {item.step}
                </div>
                <h3 className="text-xl font-semibold mb-3">{item.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {item.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary to-violet-600 p-12 sm:p-16 text-center">
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIxIiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMSkiLz48L3N2Zz4=')] opacity-50" />
            <div className="relative">
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                Ready to ace your interview?
              </h2>
              <p className="text-white/80 text-lg mb-8 max-w-xl mx-auto">
                Join thousands of candidates who improved their interview
                performance with AI-powered practice.
              </p>
              <Link href="/register">
                <Button
                  size="lg"
                  variant="secondary"
                  className="text-base px-8 h-12 font-semibold gap-2"
                >
                  Get Started — It&apos;s Free
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <div className="flex items-center justify-center gap-6 mt-8 text-white/70 text-sm">
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4" /> No credit card
                </span>
                <span className="flex items-center gap-1.5">
                  <Shield className="h-4 w-4" /> Secure & private
                </span>
                <span className="flex items-center gap-1.5">
                  <Zap className="h-4 w-4" /> Instant setup
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t py-10 mt-auto">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-primary flex items-center justify-center">
              <Brain className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="font-semibold text-sm">InterviewGPT</span>
          </div>
          <p className="text-xs text-muted-foreground">
            © {new Date().getFullYear()} InterviewGPT. Built with AI for
            interview excellence.
          </p>
        </div>
      </footer>
    </div>
  );
}
