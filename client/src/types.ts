export type ChatRequestPayload = {
    message: string;
    context?: Record<string, string | number | null>;
};

export type ScholarshipResult = {
    "Scholarship Name": string;
    "Minimum GWA": string;
    "Year Level restrictions": string;
    "Specific Program": string;
    "Employment status preference": string;
    "Required Documents": string[];
    Deadline: string;
};

export type MessageRole = "user" | "assistant";

export type ChatMessage = {
    id: string;
    role: MessageRole;
    content: string;
    result?: ScholarshipResult[];
    options?: string[];
    showNewChat?: boolean;
    timestamp: number;
};