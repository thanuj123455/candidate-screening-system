import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function difficultyColor(level: string) {
  return {
    easy: "bg-green-100 text-green-800",
    medium: "bg-yellow-100 text-yellow-800",
    hard: "bg-red-100 text-red-800",
  }[level] ?? "bg-gray-100 text-gray-800";
}

export function recommendationColor(rec: string) {
  return {
    Hire:   "bg-green-600 text-white ring-2 ring-green-300",
    Maybe:  "bg-amber-400 text-gray-900 ring-2 ring-amber-200",
    Reject: "bg-red-600   text-white ring-2 ring-red-300",
  }[rec] ?? "bg-gray-200 text-gray-800";
}
