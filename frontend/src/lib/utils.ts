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
    Hire: "bg-green-500",
    Maybe: "bg-yellow-500",
    Reject: "bg-red-500",
  }[rec] ?? "bg-gray-400";
}
