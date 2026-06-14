"use client";

import { useState, useCallback } from "react";
import { api } from "@/lib/api";
import type { QuestionResponse, SubmitAnswerResponse } from "@/types";

interface InterviewState {
  sessionId: string | null;
  currentQuestion: QuestionResponse | null;
  answeredCount: number;
  isSubmitting: boolean;
  isLoadingQuestion: boolean;
  error: string | null;
}

export function useInterview() {
  const [state, setState] = useState<InterviewState>({
    sessionId: null,
    currentQuestion: null,
    answeredCount: 0,
    isSubmitting: false,
    isLoadingQuestion: false,
    error: null,
  });

  const loadQuestion = useCallback(async (sessionId: string) => {
    setState((s) => ({ ...s, isLoadingQuestion: true, error: null }));
    try {
      const q = await api.getQuestion(sessionId);
      setState((s) => ({ ...s, currentQuestion: q, isLoadingQuestion: false }));
      return q;
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Failed to load question";
      setState((s) => ({ ...s, error: msg, isLoadingQuestion: false }));
      return null;
    }
  }, []);

  const submitAnswer = useCallback(
    async (answer: string): Promise<SubmitAnswerResponse | null> => {
      if (!state.sessionId || !state.currentQuestion) return null;
      setState((s) => ({ ...s, isSubmitting: true, error: null }));
      try {
        const res = await api.submitAnswer(
          state.sessionId,
          state.currentQuestion.question_id,
          answer
        );
        setState((s) => ({
          ...s,
          isSubmitting: false,
          answeredCount: s.answeredCount + 1,
        }));
        return res;
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : "Failed to submit answer";
        setState((s) => ({ ...s, error: msg, isSubmitting: false }));
        return null;
      }
    },
    [state.sessionId, state.currentQuestion]
  );

  const init = useCallback((sessionId: string) => {
    setState((s) => ({ ...s, sessionId }));
  }, []);

  return { state, init, loadQuestion, submitAnswer };
}
