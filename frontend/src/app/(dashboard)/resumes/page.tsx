"use client";

import { useEffect, useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { resumeService } from "@/services/resume.service";
import { toast } from "sonner";
import { motion } from "framer-motion";
import {
  Upload,
  FileText,
  Trash2,
  CheckCircle2,
  Loader2,
  X,
} from "lucide-react";
import type { Resume, ExperienceItem, ProjectItem, EducationItem } from "@/types/resume";
import { useDropzone } from "react-dropzone";

export default function ResumesPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedResume, setSelectedResume] = useState<Resume | null>(null);

  useEffect(() => {
    loadResumes();
  }, []);

  async function loadResumes() {
    try {
      const data = await resumeService.list();
      setResumes(data.resumes);
    } catch {
      // Silently handle
    } finally {
      setLoading(false);
    }
  }

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    const validTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];
    if (!validTypes.includes(file.type)) {
      toast.error("Please upload a PDF or DOCX file");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast.error("File too large. Maximum 10MB.");
      return;
    }

    setUploading(true);
    try {
      await resumeService.upload(file);
      toast.success("Resume uploaded and parsed successfully!");
      await loadResumes();
    } catch {
      toast.error("Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  async function handleDelete(id: string) {
    try {
      await resumeService.delete(id);
      toast.success("Resume deleted");
      setResumes((prev) => prev.filter((r) => r.id !== id));
      if (selectedResume?.id === id) setSelectedResume(null);
    } catch {
      toast.error("Failed to delete resume");
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Resumes</h1>
        <p className="text-muted-foreground mt-1">
          Upload and manage your resumes for personalized interviews
        </p>
      </div>

      {/* Upload Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
          isDragActive
            ? "border-primary bg-primary/5"
            : "border-border hover:border-primary/40 hover:bg-accent/30"
        } ${uploading ? "pointer-events-none opacity-60" : ""}`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-3">
          {uploading ? (
            <>
              <Loader2 className="h-10 w-10 text-primary animate-spin" />
              <p className="text-sm font-medium">Uploading & parsing your resume...</p>
              <p className="text-xs text-muted-foreground">
                AI is extracting your skills, projects, and experience
              </p>
            </>
          ) : (
            <>
              <div className="h-14 w-14 rounded-2xl bg-primary/10 flex items-center justify-center">
                <Upload className="h-7 w-7 text-primary" />
              </div>
              <p className="text-sm font-medium">
                {isDragActive ? "Drop your resume here" : "Drag & drop your resume, or click to browse"}
              </p>
              <p className="text-xs text-muted-foreground">
                Supports PDF and DOCX · Max 10MB
              </p>
            </>
          )}
        </div>
      </div>

      {/* Resume List + Detail */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* List */}
        <div className="lg:col-span-1 space-y-3">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
            Your Resumes
          </h2>
          {loading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-16" />
              ))}
            </div>
          ) : resumes.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4">No resumes uploaded yet</p>
          ) : (
            resumes.map((resume, i) => (
              <motion.div
                key={resume.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <button
                  onClick={() => setSelectedResume(resume)}
                  className={`w-full text-left p-3 rounded-xl border transition-all ${
                    selectedResume?.id === resume.id
                      ? "border-primary bg-primary/5"
                      : "hover:border-primary/30 hover:bg-accent/50"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-primary shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{resume.file_name}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(resume.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    {resume.is_active && (
                      <Badge variant="default" className="text-xs shrink-0">Active</Badge>
                    )}
                  </div>
                </button>
              </motion.div>
            ))
          )}
        </div>

        {/* Detail */}
        <div className="lg:col-span-2">
          {selectedResume ? (
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-base">{selectedResume.file_name}</CardTitle>
                  <p className="text-xs text-muted-foreground mt-1">
                    Uploaded {new Date(selectedResume.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="gap-1.5 text-destructive hover:text-destructive"
                    onClick={() => handleDelete(selectedResume.id)}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                    Delete
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {selectedResume.parsed_data ? (
                  <>
                    {/* Name */}
                    {selectedResume.parsed_data.name && (
                      <div>
                        <p className="text-xs font-medium text-muted-foreground mb-1 uppercase tracking-wider">Name</p>
                        <p className="font-semibold">{selectedResume.parsed_data.name}</p>
                      </div>
                    )}

                    {/* Skills */}
                    {selectedResume.parsed_data.skills?.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wider">Skills</p>
                        <div className="flex flex-wrap gap-1.5">
                          {selectedResume.parsed_data.skills.map((skill: string) => (
                            <Badge key={skill} variant="secondary" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Experience */}
                    {selectedResume.parsed_data.experience?.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wider">Experience</p>
                        <div className="space-y-3">
                          {selectedResume.parsed_data.experience.map((exp: ExperienceItem, i: number) => (
                            <div key={i} className="p-3 rounded-lg bg-muted/50">
                              <p className="text-sm font-medium">{exp.title}</p>
                              <p className="text-xs text-muted-foreground">{exp.company} · {exp.duration}</p>
                              {exp.description && (
                                <p className="text-xs text-muted-foreground mt-1">{exp.description}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Projects */}
                    {selectedResume.parsed_data.projects?.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wider">Projects</p>
                        <div className="space-y-3">
                          {selectedResume.parsed_data.projects.map((proj: ProjectItem, i: number) => (
                            <div key={i} className="p-3 rounded-lg bg-muted/50">
                              <p className="text-sm font-medium">{proj.name}</p>
                              <p className="text-xs text-muted-foreground mt-0.5">{proj.description}</p>
                              {proj.technologies?.length > 0 && (
                                <div className="flex flex-wrap gap-1 mt-2">
                                  {proj.technologies.map((t: string) => (
                                    <Badge key={t} variant="outline" className="text-[10px]">
                                      {t}
                                    </Badge>
                                  ))}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Education */}
                    {selectedResume.parsed_data.education?.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wider">Education</p>
                        <div className="space-y-2">
                          {selectedResume.parsed_data.education.map((edu: EducationItem, i: number) => (
                            <div key={i} className="p-3 rounded-lg bg-muted/50">
                              <p className="text-sm font-medium">{edu.degree}</p>
                              <p className="text-xs text-muted-foreground">{edu.institution} · {edu.year}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <p className="text-sm text-muted-foreground">Parsed data not available</p>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card className="flex items-center justify-center h-80">
              <div className="text-center">
                <FileText className="h-10 w-10 text-muted-foreground/30 mx-auto mb-3" />
                <p className="text-sm text-muted-foreground">Select a resume to view details</p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
