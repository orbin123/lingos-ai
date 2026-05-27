export type CourseTrack = "24w" | "48w";
export type AnswerView = "correct" | "wrong";
export type SessionPreviewState = "default" | AnswerView;

export interface CourseTrackOption {
  id: CourseTrack;
  label: string;
  weekCount: number;
}

export interface TeachingMessage {
  id: string;
  role: "ai" | "you";
  name?: string;
  content: string;
  actions?: string[];
}

export interface TeachingDayData {
  dayId: string;
  courseTrack: CourseTrack;
  week: number;
  day: number;
  title: string;
  theme: string;
  cefr: string;
  focus: string;
  isAuthored: boolean;
  messages: TeachingMessage[];
}

export const COURSE_TRACK_OPTIONS: CourseTrackOption[] = [
  { id: "24w", label: "24 weeks", weekCount: 24 },
  { id: "48w", label: "48 weeks", weekCount: 48 },
];

const weekOneDayOne: TeachingDayData = {
  dayId: "day_24_01_01",
  courseTrack: "24w",
  week: 1,
  day: 1,
  title: "Simple Present Tense - Subject-Verb Agreement",
  theme: "Grammar",
  cefr: "A1",
  focus: "Simple present routines, third-person -s, frequency adverbs",
  isAuthored: true,
  messages: [
    {
      id: "teach-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Today we will use simple present for facts, routines, and habits. Tense shows when something happens; simple present shows what happens regularly. Write one real daily routine in one sentence.",
    },
    {
      id: "teach-user-1",
      role: "you",
      content: "I drink tea every morning.",
    },
    {
      id: "teach-ai-2",
      role: "ai",
      content:
        "Good. With I, you use the base verb: I drink. With he or she, add -s: she drinks. Now say the same routine with she as the subject.",
    },
    {
      id: "teach-user-2",
      role: "you",
      content: "She drinks tea every morning.",
    },
    {
      id: "teach-ai-3",
      role: "ai",
      content:
        "Exactly. Frequency adverbs show how often: always, usually, often, sometimes, never. Write one routine sentence with a frequency adverb and the correct verb form.",
    },
    {
      id: "teach-user-3",
      role: "you",
      content: "My brother usually walks to school.",
    },
    {
      id: "teach-ai-4",
      role: "ai",
      content: "Ready to try the practice task?",
      actions: ["Start practice"],
    },
  ],
};

const weekOneDayTwo: TeachingDayData = {
  dayId: "day_24_01_02",
  courseTrack: "24w",
  week: 1,
  day: 2,
  title: "Simple Past Tense - Regular and Irregular Verbs",
  theme: "Grammar",
  cefr: "A1",
  focus: "Completed actions, regular -ed verbs, irregular past forms, and read-aloud pronunciation",
  isAuthored: true,
  messages: [
    {
      id: "teach-w1d2-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Today we will use simple past for actions that are already finished. Regular verbs usually add -ed, like walk becomes walked. Tell me one thing you did yesterday in one sentence.",
    },
    {
      id: "teach-w1d2-user-1",
      role: "you",
      content: "I visited my friend yesterday.",
    },
    {
      id: "teach-w1d2-ai-2",
      role: "ai",
      content:
        "Nice. Visited is a regular past verb. Some common verbs are irregular: go becomes went, eat becomes ate, and have becomes had. Write one sentence using went, ate, or had.",
    },
    {
      id: "teach-w1d2-user-2",
      role: "you",
      content: "I went to the market last night.",
    },
    {
      id: "teach-w1d2-ai-3",
      role: "ai",
      content:
        "Good control. Now correct this sentence: I goed to school. Explain why it is wrong in one short sentence.",
    },
    {
      id: "teach-w1d2-user-3",
      role: "you",
      content: "I went to school. Go is irregular, so the past form is went.",
    },
    {
      id: "teach-w1d2-ai-4",
      role: "ai",
      content: "Ready to try the practice task?",
      actions: ["Start practice"],
    },
  ],
};

const weekOneDayThree: TeachingDayData = {
  dayId: "day_24_01_03",
  courseTrack: "24w",
  week: 1,
  day: 3,
  title: "Present Continuous - Actions Happening Now",
  theme: "Grammar",
  cefr: "A1",
  focus: "Present continuous with am, is, are, and verb-ing for actions happening right now",
  isAuthored: true,
  messages: [
    {
      id: "teach-w1d3-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Today we will use present continuous for actions happening now. The pattern is am, is, or are plus verb-ing: I am reading, she is cooking, they are playing. Look around you and write one action happening right now.",
    },
    {
      id: "teach-w1d3-user-1",
      role: "you",
      content: "My sister is watching TV.",
    },
    {
      id: "teach-w1d3-ai-2",
      role: "ai",
      content:
        "Good. Sister is one person, so is watching is correct. With I, use am. With you, we, or they, use are. Change this simple present sentence into present continuous: She walks to school.",
    },
    {
      id: "teach-w1d3-user-2",
      role: "you",
      content: "She is walking to school.",
    },
    {
      id: "teach-w1d3-ai-3",
      role: "ai",
      content:
        "Exactly. Simple present can describe routines; present continuous describes what is happening now. Write one sentence with they and one action happening right now.",
    },
    {
      id: "teach-w1d3-user-3",
      role: "you",
      content: "They are studying English now.",
    },
    {
      id: "teach-w1d3-ai-4",
      role: "ai",
      content: "Ready to try the practice task?",
      actions: ["Start practice"],
    },
  ],
};

const teachingDays: Partial<Record<CourseTrack, Record<number, Record<number, TeachingDayData>>>> = {
  "24w": {
    1: {
      1: weekOneDayOne,
      2: weekOneDayTwo,
      3: weekOneDayThree,
    },
  },
  "48w": {},
};

function buildPlaceholderDay(courseTrack: CourseTrack, week: number, day: number): TeachingDayData {
  return {
    dayId: `day_${courseTrack}_${String(week).padStart(2, "0")}_${String(day).padStart(2, "0")}`,
    courseTrack,
    week,
    day,
    title: `Week ${week} Day ${day}`,
    theme: "Preview",
    cefr: courseTrack === "24w" ? "24 week track" : "48 week track",
    focus: "Reusable chat-session preview",
    isAuthored: false,
    messages: [
      {
        id: "placeholder-ai",
        role: "ai",
        name: "LingosAI",
        content:
          "This day is available in the selector, but its frontend source data is not authored yet. Add teaching, task, evaluation, and feedback data for this week/day to preview the full completed chat flow.",
      },
    ],
  };
}

export function getTeachingDay(
  courseTrack: CourseTrack,
  week: number,
  day: number,
): TeachingDayData {
  return teachingDays[courseTrack]?.[week]?.[day] ?? buildPlaceholderDay(courseTrack, week, day);
}
