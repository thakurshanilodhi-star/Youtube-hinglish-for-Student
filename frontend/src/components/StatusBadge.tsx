import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
}

const statusColors: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300",
  processing: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
  transcribing: "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300",
  translating: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300",
  synthesizing: "bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300",
  completed: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
  failed: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
  cancelled: "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300",
  active: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
  stopped: "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300",
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize",
        statusColors[status] || statusColors.pending
      )}
    >
      {status}
    </span>
  );
}
