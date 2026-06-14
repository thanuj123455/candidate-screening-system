"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { recommendationColor, difficultyColor, cn } from "@/lib/utils";
import type { ReportResponse } from "@/types";

function ScoreRing({ score }: { score: number }) {
  const pct = Math.min(100, Math.max(0, score));
  const color =
    pct >= 70 ? "text-green-500" : pct >= 45 ? "text-yellow-500" : "text-red-500";
  return (
    <div className="relative inline-flex items-center justify-center">
      <svg className="h-28 w-28 -rotate-90" viewBox="0 0 36 36">
        <circle cx="18" cy="18" r="15.9" fill="none" stroke="#e5e7eb" strokeWidth="3" />
        <circle
          cx="18"
          cy="18"
          r="15.9"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          strokeDasharray={`${pct} ${100 - pct}`}
          strokeLinecap="round"
          className={color}
        />
      </svg>
      <span className={`absolute text-2xl font-bold ${color}`}>{Math.round(pct)}</span>
    </div>
  );
}

function ResultsContent() {
  const params = useSearchParams();
  const router = useRouter();
  const sessionId = params.get("session") ?? "";

  const [report, setReport] = useState<ReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!sessionId) return;
    api
      .getReport(sessionId)
      .then(setReport)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent" />
        <p className="text-gray-500 text-sm">Generating your interview report...</p>
        <p className="text-gray-400 text-xs">This may take 15–30 seconds</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="text-center py-20 space-y-4">
        <p className="text-red-500">{error || "Report not found."}</p>
        <button onClick={() => router.push("/")} className="text-indigo-600 underline text-sm">
          Back to home
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-1">
        <h1 className="text-3xl font-bold">Interview Report</h1>
        <p className="text-gray-500">
          {report.candidate_name} — {report.role}
        </p>
      </div>

      {/* Score + Recommendation */}
      <div className="bg-white rounded-2xl shadow-sm border p-8 flex flex-col sm:flex-row items-center gap-8">
        <div className="flex flex-col items-center gap-2">
          <ScoreRing score={report.overall_score ?? 0} />
          <p className="text-sm text-gray-500 font-medium">Overall Score</p>
        </div>
        <div className="flex-1 space-y-4">
          <div className="flex items-center gap-3">
            <span
              className={cn(
                "rounded-full px-4 py-1.5 text-sm font-bold text-white",
                recommendationColor(report.recommendation)
              )}
            >
              {report.recommendation}
            </span>
            <span className="text-sm text-gray-500">Recommendation</span>
          </div>
          <p className="text-sm text-gray-700 leading-relaxed">{report.summary}</p>
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid sm:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow-sm border p-6 space-y-3">
          <h2 className="font-semibold text-green-700 flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-green-500 inline-block" />
            Strengths
          </h2>
          <ul className="space-y-2">
            {report.strengths.map((s, i) => (
              <li key={i} className="text-sm text-gray-700 flex gap-2">
                <span className="text-green-500 mt-0.5">✓</span>
                {s}
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border p-6 space-y-3">
          <h2 className="font-semibold text-red-700 flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-red-400 inline-block" />
            Areas to Improve
          </h2>
          <ul className="space-y-2">
            {report.weaknesses.map((w, i) => (
              <li key={i} className="text-sm text-gray-700 flex gap-2">
                <span className="text-red-400 mt-0.5">△</span>
                {w}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Q&A Transcript */}
      <div className="bg-white rounded-2xl shadow-sm border p-6 space-y-6">
        <h2 className="font-semibold text-lg">Interview Transcript</h2>
        <div className="space-y-6 divide-y divide-gray-100">
          {report.qa_pairs.map((pair, i) => (
            <div key={i} className="pt-6 first:pt-0 space-y-3">
              <div className="flex items-start gap-3">
                <span className="rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold px-2 py-0.5 shrink-0 mt-0.5">
                  Q{i + 1}
                </span>
                <p className="text-sm font-medium text-gray-800">{pair.question}</p>
              </div>
              <div className="flex items-start gap-3 ml-7">
                <p className="text-sm text-gray-600 leading-relaxed">{pair.answer}</p>
              </div>
              {pair.quality_score !== null && (
                <div className="ml-7">
                  <div className="inline-flex items-center gap-2 rounded-full bg-gray-100 px-3 py-0.5">
                    <span className="text-xs text-gray-500">Score:</span>
                    <span className="text-xs font-semibold">
                      {(pair.quality_score * 10).toFixed(1)}/10
                    </span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-center">
        <button
          onClick={() => router.push("/")}
          className="rounded-lg bg-indigo-600 px-8 py-3 text-white font-semibold hover:bg-indigo-700 transition-colors"
        >
          Start New Interview
        </button>
      </div>
    </div>
  );
}

export default function ResultsPage() {
  return (
    <Suspense fallback={<div className="text-center py-20 text-gray-400">Loading...</div>}>
      <ResultsContent />
    </Suspense>
  );
}
