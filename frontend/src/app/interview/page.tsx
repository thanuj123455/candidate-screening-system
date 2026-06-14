"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { difficultyColor, cn } from "@/lib/utils";
import type { QuestionResponse } from "@/types";

function InterviewContent() {
  const router = useRouter();
  const params = useSearchParams();
  const sessionId = params.get("session") ?? "";

  const [question, setQuestion] = useState<QuestionResponse | null>(null);
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [answeredCount, setAnsweredCount] = useState(0);

  useEffect(() => {
    if (sessionId) loadQuestion();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  async function loadQuestion() {
    setLoading(true);
    setError("");
    try {
      const q = await api.getQuestion(sessionId);
      setQuestion(q);
      setAnswer("");
    } catch {
      // No more questions — go straight to results
      await api.endSession(sessionId).catch(() => {});
      router.push(`/results?session=${sessionId}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit() {
    if (!question || !answer.trim()) return;
    setSubmitting(true);
    setError("");
    try {
      await api.submitAnswer(sessionId, question.question_id, answer.trim());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to submit answer. Please try again.");
      setSubmitting(false);
      return;
    }

    // Answer saved — unblock the UI immediately
    const newCount = answeredCount + 1;
    setAnsweredCount(newCount);
    setSubmitting(false);

    const done = question.is_last || newCount >= question.total_questions;
    if (done) {
      await api.endSession(sessionId).catch(() => {});
      router.push(`/results?session=${sessionId}`);
    } else {
      // loadQuestion triggers LLM — runs independently of submit state
      await loadQuestion();
    }
  }

  async function handleFinishEarly() {
    await api.endSession(sessionId).catch(() => {});
    router.push(`/results?session=${sessionId}`);
  }

  const progress = question
    ? ((answeredCount) / question.total_questions) * 100
    : 0;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Technical Interview</h1>
        <button
          onClick={handleFinishEarly}
          className="text-sm text-gray-500 hover:text-gray-700 underline"
        >
          Finish early
        </button>
      </div>

      {/* Progress bar */}
      {question && (
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs text-gray-500">
            <span>Question {answeredCount + 1} of {question.total_questions}</span>
            <span>{Math.round(progress)}% complete</span>
          </div>
          <div className="h-2 w-full rounded-full bg-gray-200">
            <div
              className="h-2 rounded-full bg-indigo-500 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-red-700 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="bg-white rounded-2xl shadow-sm border p-12 flex items-center justify-center">
          <div className="space-y-3 text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent" />
            <p className="text-sm text-gray-500">Generating your question...</p>
          </div>
        </div>
      ) : question ? (
        <div className="bg-white rounded-2xl shadow-sm border p-8 space-y-6">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-1">
              <span
                className={cn(
                  "inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize",
                  difficultyColor(question.difficulty)
                )}
              >
                {question.difficulty}
              </span>
              <p className="text-xs text-gray-400">Q{question.order_index + 1}</p>
            </div>
          </div>

          <p className="text-lg font-medium leading-relaxed">{question.question_text}</p>

          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-700">
              Your Answer
            </label>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              rows={8}
              placeholder="Type your answer here. Be specific and include examples where relevant..."
              className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
            />
            <div className="flex justify-between items-center text-xs text-gray-400">
              <span>{answer.length} characters</span>
              <span>Minimum: 20 characters</span>
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={submitting || answer.trim().length < 20}
            className="w-full rounded-lg bg-indigo-600 px-4 py-3 text-white font-semibold hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {submitting
              ? "Submitting..."
              : question.is_last
              ? "Submit Final Answer"
              : "Submit & Next Question"}
          </button>
        </div>
      ) : null}
    </div>
  );
}

export default function InterviewPage() {
  return (
    <Suspense fallback={<div className="text-center py-20 text-gray-400">Loading...</div>}>
      <InterviewContent />
    </Suspense>
  );
}
