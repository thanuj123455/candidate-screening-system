"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { SUPPORTED_ROLES, type Role, type ResumeUploadResponse } from "@/types";
import { cn } from "@/lib/utils";

export default function CandidatePage() {
  const router = useRouter();
  const fileRef = useRef<HTMLInputElement>(null);

  const [step, setStep] = useState<"upload" | "role">("upload");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [parsed, setParsed] = useState<ResumeUploadResponse | null>(null);
  const [selectedRole, setSelectedRole] = useState<Role | "">("");
  const [uploading, setUploading] = useState(false);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState("");

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file || !name || !email) return;
    setUploading(true);
    setError("");
    try {
      const fd = new FormData();
      fd.append("name", name);
      fd.append("email", email);
      fd.append("file", file);
      const res = await api.uploadResume(fd);
      setParsed(res);
      setStep("role");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function handleStart() {
    if (!parsed || !selectedRole) return;
    setStarting(true);
    setError("");
    try {
      const res = await api.startInterview(parsed.candidate_id, selectedRole);
      router.push(`/interview?session=${res.session_id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to start interview");
      setStarting(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">
          AI-Powered Technical Interview
        </h1>
        <p className="text-gray-500">
          Upload your resume, select a role, and start your personalized interview.
        </p>
      </div>

      {/* Step indicators */}
      <div className="flex items-center gap-4 justify-center">
        {(["upload", "role"] as const).map((s, i) => (
          <div key={s} className="flex items-center gap-2">
            <div
              className={cn(
                "h-8 w-8 rounded-full flex items-center justify-center text-sm font-semibold",
                step === s || (s === "upload" && step === "role")
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-200 text-gray-500"
              )}
            >
              {i + 1}
            </div>
            <span className="text-sm font-medium capitalize">{s === "upload" ? "Upload Resume" : "Select Role"}</span>
            {i < 1 && <div className="h-px w-8 bg-gray-300" />}
          </div>
        ))}
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-red-700 text-sm">
          {error}
        </div>
      )}

      {step === "upload" && (
        <form onSubmit={handleUpload} className="bg-white rounded-2xl shadow-sm border p-8 space-y-6">
          <h2 className="text-xl font-semibold">Your Information</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="Jane Smith"
                className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="jane@example.com"
                className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5">Resume (PDF)</label>
              <div
                onClick={() => fileRef.current?.click()}
                className={cn(
                  "cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-colors",
                  file
                    ? "border-indigo-400 bg-indigo-50"
                    : "border-gray-300 hover:border-indigo-400 hover:bg-gray-50"
                )}
              >
                <input
                  ref={fileRef}
                  type="file"
                  accept="application/pdf"
                  className="hidden"
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                />
                {file ? (
                  <div className="space-y-1">
                    <p className="font-medium text-indigo-700">{file.name}</p>
                    <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                ) : (
                  <div className="space-y-1">
                    <p className="text-gray-600 font-medium">Click to upload your resume</p>
                    <p className="text-xs text-gray-400">PDF only, max 10 MB</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={uploading || !file || !name || !email}
            className="w-full rounded-lg bg-indigo-600 px-4 py-3 text-white font-semibold hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {uploading ? "Parsing Resume..." : "Upload & Continue"}
          </button>
        </form>
      )}

      {step === "role" && parsed && (
        <div className="space-y-6">
          {/* Parsed preview */}
          <div className="bg-white rounded-2xl shadow-sm border p-6 space-y-4">
            <h2 className="text-xl font-semibold">Resume Parsed Successfully</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              {parsed.parsed_data.programming_languages?.length > 0 && (
                <Chip label="Languages" items={parsed.parsed_data.programming_languages} />
              )}
              {parsed.parsed_data.frameworks?.length > 0 && (
                <Chip label="Frameworks" items={parsed.parsed_data.frameworks} />
              )}
              {parsed.parsed_data.skills?.length > 0 && (
                <Chip label="Skills" items={parsed.parsed_data.skills} />
              )}
              {parsed.parsed_data.tools?.length > 0 && (
                <Chip label="Tools" items={parsed.parsed_data.tools} />
              )}
            </div>
          </div>

          {/* Role selection */}
          <div className="bg-white rounded-2xl shadow-sm border p-6 space-y-4">
            <h2 className="text-xl font-semibold">Select Target Role</h2>
            <div className="grid grid-cols-2 gap-3">
              {SUPPORTED_ROLES.map((role) => (
                <button
                  key={role}
                  onClick={() => setSelectedRole(role)}
                  className={cn(
                    "rounded-xl border-2 p-4 text-left transition-all",
                    selectedRole === role
                      ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                      : "border-gray-200 hover:border-gray-300"
                  )}
                >
                  <p className="font-medium text-sm">{role}</p>
                </button>
              ))}
            </div>

            <button
              onClick={handleStart}
              disabled={!selectedRole || starting}
              className="w-full rounded-lg bg-indigo-600 px-4 py-3 text-white font-semibold hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {starting ? "Starting Interview..." : "Start Interview"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function Chip({ label, items }: { label: string; items: string[] }) {
  return (
    <div className="col-span-2 sm:col-span-1">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">{label}</p>
      <div className="flex flex-wrap gap-1.5">
        {items.slice(0, 6).map((item) => (
          <span
            key={item}
            className="inline-block rounded-md bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700"
          >
            {item}
          </span>
        ))}
        {items.length > 6 && (
          <span className="text-xs text-gray-400">+{items.length - 6} more</span>
        )}
      </div>
    </div>
  );
}
