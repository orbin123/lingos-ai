import type { AnswerView, CourseTrack } from "../teaching/source";

export type EvaluationTier = "excellent" | "good" | "average" | "needs_work";

export interface EvaluatorInputSchema {
  archetypeId: string;
  widget: string;
  taskContentRef: string;
  userResponseRef: string;
}

export interface PronunciationPhonemeScore {
  phoneme: string;
  accuracyScore: number;
}

export interface PronunciationWordScore {
  word: string;
  accuracyScore: number;
  errorType: "none" | "mispronunciation" | "omission" | "insertion";
  phonemes: PronunciationPhonemeScore[];
}

export interface PronunciationAssessment {
  overallScore: number;
  accuracyScore: number;
  fluencyScore: number;
  completenessScore: number;
  prosodyScore?: number;
  words: PronunciationWordScore[];
}

export interface ActivityEvaluationOutput {
  rawScore: number;
  percentage: number;
  tier: EvaluationTier;
  attendedLabel: string;
  rubricScores: Record<string, number>;
  subSkillBreakdown: Record<string, number>;
  pronunciationAssessment?: PronunciationAssessment;
}

export interface ActivityEvaluation {
  taskId: string;
  evaluatorInput: EvaluatorInputSchema;
  outputs: Record<AnswerView, ActivityEvaluationOutput>;
}

export interface ScorecardActivity {
  taskId: string;
  sequence: number;
  archetypeId: string;
  label: string;
  rawScore: number;
  tier: EvaluationTier;
  baseReward: number;
}

export interface OverallScorecard {
  dayId: string;
  pointsApplied: boolean;
  activities: Record<AnswerView, ScorecardActivity[]>;
  pointsEarned: Record<AnswerView, Record<string, number>>;
  skillLabels: Record<string, string>;
}

export interface EvaluationDayData {
  dayId: string;
  activityEvaluations: ActivityEvaluation[];
  overallScorecard: OverallScorecard;
}

const skillLabels = {
  grammar: "Grammar",
  vocabulary: "Vocabulary",
  pronunciation: "Pronunciation",
  fluency: "Fluency",
  expression: "Expression",
  comprehension: "Comprehension",
  tone: "Tone",
};

const weekOneDayOneEvaluation: EvaluationDayData = {
  dayId: "day_24_01_01",
  activityEvaluations: [
    {
      taskId: "w1d1-read-cloze",
      evaluatorInput: {
        archetypeId: "READ_CLOZE",
        widget: "fill_blanks",
        taskContentRef: "tasks.source.day_24_01_01.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "5 of 5 blanks correct",
          rubricScores: { accuracy: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { grammar: 10, comprehension: 9 },
        },
        wrong: {
          rawScore: 8,
          percentage: 80,
          tier: "good",
          attendedLabel: "4 of 5 blanks correct",
          rubricScores: { accuracy: 8, grammatical_accuracy: 8 },
          subSkillBreakdown: { grammar: 8, comprehension: 8 },
        },
      },
    },
    {
      taskId: "w1d1-listen-mcq",
      evaluatorInput: {
        archetypeId: "LISTEN_MCQ",
        widget: "listen_mcq",
        taskContentRef: "tasks.source.day_24_01_01.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "4 of 4 questions correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, grammar: 9 },
        },
        wrong: {
          rawScore: 7.5,
          percentage: 75,
          tier: "good",
          attendedLabel: "3 of 4 questions correct",
          rubricScores: { comprehension: 7.5, accuracy: 7.5 },
          subSkillBreakdown: { comprehension: 8, grammar: 7 },
        },
      },
    },
    {
      taskId: "w1d1-write-open-sent",
      evaluatorInput: {
        archetypeId: "WRITE_OPEN_SENT",
        widget: "open_text",
        taskContentRef: "tasks.source.day_24_01_01.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.5,
          percentage: 95,
          tier: "excellent",
          attendedLabel: "3 of 3 sentences accepted",
          rubricScores: { grammatical_accuracy: 10, expression: 9, vocabulary: 9 },
          subSkillBreakdown: { grammar: 10, expression: 9, vocabulary: 9 },
        },
        wrong: {
          rawScore: 7,
          percentage: 70,
          tier: "good",
          attendedLabel: "2 of 3 sentences accepted",
          rubricScores: { grammatical_accuracy: 6.5, expression: 8, vocabulary: 7 },
          subSkillBreakdown: { grammar: 7, expression: 8, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w1d1-speak-timed",
      evaluatorInput: {
        archetypeId: "SPEAK_TIMED",
        widget: "speak_record",
        taskContentRef: "tasks.source.day_24_01_01.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.2,
          percentage: 92,
          tier: "excellent",
          attendedLabel: "3 of 3 recordings clear",
          rubricScores: { fluency: 9, pronunciation: 9, grammatical_accuracy: 9.5 },
          subSkillBreakdown: { fluency: 9, pronunciation: 9, grammar: 9 },
        },
        wrong: {
          rawScore: 7.2,
          percentage: 72,
          tier: "good",
          attendedLabel: "2 of 3 recordings clear",
          rubricScores: { fluency: 8, pronunciation: 8, grammatical_accuracy: 6 },
          subSkillBreakdown: { fluency: 8, pronunciation: 8, grammar: 6 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_01_01",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w1d1-read-cloze", sequence: 1, archetypeId: "READ_CLOZE", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d1-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d1-write-open-sent", sequence: 3, archetypeId: "WRITE_OPEN_SENT", label: "Write", rawScore: 9.5, tier: "excellent", baseReward: 9 },
        { taskId: "w1d1-speak-timed", sequence: 4, archetypeId: "SPEAK_TIMED", label: "Speak", rawScore: 9.2, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w1d1-read-cloze", sequence: 1, archetypeId: "READ_CLOZE", label: "Read", rawScore: 8, tier: "good", baseReward: 8 },
        { taskId: "w1d1-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 7.5, tier: "good", baseReward: 7 },
        { taskId: "w1d1-write-open-sent", sequence: 3, archetypeId: "WRITE_OPEN_SENT", label: "Write", rawScore: 7, tier: "good", baseReward: 7 },
        { taskId: "w1d1-speak-timed", sequence: 4, archetypeId: "SPEAK_TIMED", label: "Speak", rawScore: 7.2, tier: "good", baseReward: 7 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 20,
        vocabulary: 6,
        pronunciation: 9,
        fluency: 9,
        expression: 9,
        comprehension: 14,
        tone: 3,
      },
      wrong: {
        grammar: 14,
        vocabulary: 5,
        pronunciation: 7,
        fluency: 7,
        expression: 7,
        comprehension: 10,
        tone: 2,
      },
    },
    skillLabels,
  },
};

const weekOneDayTwoEvaluation: EvaluationDayData = {
  dayId: "day_24_01_02",
  activityEvaluations: [
    {
      taskId: "w1d2-read-error-spot",
      evaluatorInput: {
        archetypeId: "READ_ERROR_SPOT",
        widget: "error_spotting",
        taskContentRef: "tasks.source.day_24_01_02.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "5 of 5 errors found",
          rubricScores: { accuracy: 10, grammatical_awareness: 10 },
          subSkillBreakdown: { grammar: 10, comprehension: 9 },
        },
        wrong: {
          rawScore: 8,
          percentage: 80,
          tier: "good",
          attendedLabel: "4 of 5 errors found",
          rubricScores: { accuracy: 8, grammatical_awareness: 8 },
          subSkillBreakdown: { grammar: 8, comprehension: 8 },
        },
      },
    },
    {
      taskId: "w1d2-listen-cloze",
      evaluatorInput: {
        archetypeId: "LISTEN_CLOZE",
        widget: "listen_cloze",
        taskContentRef: "tasks.source.day_24_01_02.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "5 of 5 blanks correct",
          rubricScores: { comprehension: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, grammar: 10 },
        },
        wrong: {
          rawScore: 8,
          percentage: 80,
          tier: "good",
          attendedLabel: "4 of 5 blanks correct",
          rubricScores: { comprehension: 8, grammatical_accuracy: 8 },
          subSkillBreakdown: { comprehension: 8, grammar: 8 },
        },
      },
    },
    {
      taskId: "w1d2-write-error-corr",
      evaluatorInput: {
        archetypeId: "WRITE_ERROR_CORR",
        widget: "error_correction",
        taskContentRef: "tasks.source.day_24_01_02.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.4,
          percentage: 94,
          tier: "excellent",
          attendedLabel: "3 of 3 sentences corrected",
          rubricScores: { grammatical_accuracy: 9.5, expression: 9, vocabulary: 9 },
          subSkillBreakdown: { grammar: 10, expression: 9, vocabulary: 8 },
        },
        wrong: {
          rawScore: 7,
          percentage: 70,
          tier: "good",
          attendedLabel: "2 of 3 sentences corrected",
          rubricScores: { grammatical_accuracy: 6.5, expression: 8, vocabulary: 7 },
          subSkillBreakdown: { grammar: 7, expression: 8, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w1d2-speak-read-aloud",
      evaluatorInput: {
        archetypeId: "SPEAK_READ_ALOUD",
        widget: "read_aloud",
        taskContentRef: "tasks.source.day_24_01_02.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.1,
          percentage: 91,
          tier: "excellent",
          attendedLabel: "Read-aloud pronunciation clear",
          rubricScores: { pronunciation: 9, fluency: 9, grammatical_accuracy: 9 },
          subSkillBreakdown: { pronunciation: 9, fluency: 9, grammar: 9 },
          pronunciationAssessment: {
            overallScore: 91,
            accuracyScore: 92,
            fluencyScore: 88,
            completenessScore: 96,
            prosodyScore: 89,
            words: [
              { word: "Yesterday", accuracyScore: 94, errorType: "none", phonemes: [{ phoneme: "j", accuracyScore: 93 }, { phoneme: "e", accuracyScore: 95 }] },
              { word: "Liam", accuracyScore: 91, errorType: "none", phonemes: [{ phoneme: "l", accuracyScore: 90 }, { phoneme: "i", accuracyScore: 92 }] },
              { word: "walked", accuracyScore: 90, errorType: "none", phonemes: [{ phoneme: "w", accuracyScore: 93 }, { phoneme: "t", accuracyScore: 88 }] },
              { word: "played", accuracyScore: 93, errorType: "none", phonemes: [{ phoneme: "p", accuracyScore: 92 }, { phoneme: "d", accuracyScore: 91 }] },
              { word: "listened", accuracyScore: 89, errorType: "none", phonemes: [{ phoneme: "l", accuracyScore: 90 }, { phoneme: "d", accuracyScore: 86 }] },
              { word: "ate", accuracyScore: 95, errorType: "none", phonemes: [{ phoneme: "eɪ", accuracyScore: 96 }, { phoneme: "t", accuracyScore: 94 }] },
              { word: "drank", accuracyScore: 92, errorType: "none", phonemes: [{ phoneme: "d", accuracyScore: 91 }, { phoneme: "æ", accuracyScore: 90 }] },
              { word: "wanted", accuracyScore: 88, errorType: "none", phonemes: [{ phoneme: "w", accuracyScore: 90 }, { phoneme: "ɪd", accuracyScore: 84 }] },
              { word: "started", accuracyScore: 90, errorType: "none", phonemes: [{ phoneme: "s", accuracyScore: 92 }, { phoneme: "ɪd", accuracyScore: 87 }] },
              { word: "grabbed", accuracyScore: 91, errorType: "none", phonemes: [{ phoneme: "g", accuracyScore: 93 }, { phoneme: "d", accuracyScore: 89 }] },
              { word: "went", accuracyScore: 94, errorType: "none", phonemes: [{ phoneme: "w", accuracyScore: 95 }, { phoneme: "t", accuracyScore: 93 }] },
            ],
          },
        },
        wrong: {
          rawScore: 7,
          percentage: 70,
          tier: "good",
          attendedLabel: "Read-aloud mostly clear",
          rubricScores: { pronunciation: 7.5, fluency: 8, grammatical_accuracy: 6 },
          subSkillBreakdown: { pronunciation: 8, fluency: 8, grammar: 6 },
          pronunciationAssessment: {
            overallScore: 70,
            accuracyScore: 68,
            fluencyScore: 78,
            completenessScore: 82,
            prosodyScore: 62,
            words: [
              { word: "Yesterday", accuracyScore: 88, errorType: "none", phonemes: [{ phoneme: "j", accuracyScore: 86 }, { phoneme: "e", accuracyScore: 89 }] },
              { word: "Liam", accuracyScore: 84, errorType: "none", phonemes: [{ phoneme: "l", accuracyScore: 83 }, { phoneme: "i", accuracyScore: 85 }] },
              { word: "walked", accuracyScore: 72, errorType: "mispronunciation", phonemes: [{ phoneme: "w", accuracyScore: 84 }, { phoneme: "t", accuracyScore: 55 }] },
              { word: "played", accuracyScore: 86, errorType: "none", phonemes: [{ phoneme: "p", accuracyScore: 88 }, { phoneme: "d", accuracyScore: 82 }] },
              { word: "listened", accuracyScore: 74, errorType: "mispronunciation", phonemes: [{ phoneme: "l", accuracyScore: 80 }, { phoneme: "d", accuracyScore: 57 }] },
              { word: "ate", accuracyScore: 42, errorType: "mispronunciation", phonemes: [{ phoneme: "eɪ", accuracyScore: 36 }, { phoneme: "t", accuracyScore: 48 }] },
              { word: "drank", accuracyScore: 83, errorType: "none", phonemes: [{ phoneme: "d", accuracyScore: 82 }, { phoneme: "æ", accuracyScore: 78 }] },
              { word: "wanted", accuracyScore: 71, errorType: "mispronunciation", phonemes: [{ phoneme: "w", accuracyScore: 82 }, { phoneme: "ɪd", accuracyScore: 52 }] },
              { word: "started", accuracyScore: 73, errorType: "mispronunciation", phonemes: [{ phoneme: "s", accuracyScore: 80 }, { phoneme: "ɪd", accuracyScore: 54 }] },
              { word: "grabbed", accuracyScore: 76, errorType: "mispronunciation", phonemes: [{ phoneme: "g", accuracyScore: 84 }, { phoneme: "d", accuracyScore: 58 }] },
              { word: "went", accuracyScore: 86, errorType: "none", phonemes: [{ phoneme: "w", accuracyScore: 88 }, { phoneme: "t", accuracyScore: 83 }] },
            ],
          },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_01_02",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w1d2-read-error-spot", sequence: 1, archetypeId: "READ_ERROR_SPOT", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d2-listen-cloze", sequence: 2, archetypeId: "LISTEN_CLOZE", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d2-write-error-corr", sequence: 3, archetypeId: "WRITE_ERROR_CORR", label: "Write", rawScore: 9.4, tier: "excellent", baseReward: 9 },
        { taskId: "w1d2-speak-read-aloud", sequence: 4, archetypeId: "SPEAK_READ_ALOUD", label: "Speak", rawScore: 9.1, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w1d2-read-error-spot", sequence: 1, archetypeId: "READ_ERROR_SPOT", label: "Read", rawScore: 8, tier: "good", baseReward: 8 },
        { taskId: "w1d2-listen-cloze", sequence: 2, archetypeId: "LISTEN_CLOZE", label: "Listen", rawScore: 8, tier: "good", baseReward: 8 },
        { taskId: "w1d2-write-error-corr", sequence: 3, archetypeId: "WRITE_ERROR_CORR", label: "Write", rawScore: 7, tier: "good", baseReward: 7 },
        { taskId: "w1d2-speak-read-aloud", sequence: 4, archetypeId: "SPEAK_READ_ALOUD", label: "Speak", rawScore: 7, tier: "good", baseReward: 7 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 21,
        vocabulary: 5,
        pronunciation: 9,
        fluency: 9,
        expression: 9,
        comprehension: 14,
        tone: 3,
      },
      wrong: {
        grammar: 15,
        vocabulary: 4,
        pronunciation: 7,
        fluency: 7,
        expression: 7,
        comprehension: 11,
        tone: 2,
      },
    },
    skillLabels,
  },
};

const weekOneDayThreeEvaluation: EvaluationDayData = {
  dayId: "day_24_01_03",
  activityEvaluations: [
    {
      taskId: "w1d3-read-comp-mcq",
      evaluatorInput: {
        archetypeId: "READ_COMP_MCQ",
        widget: "read_comp_mcq",
        taskContentRef: "tasks.source.day_24_01_03.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "4 of 4 questions correct",
          rubricScores: { comprehension: 10, grammatical_awareness: 10 },
          subSkillBreakdown: { comprehension: 10, grammar: 10 },
        },
        wrong: {
          rawScore: 7.5,
          percentage: 75,
          tier: "good",
          attendedLabel: "3 of 4 questions correct",
          rubricScores: { comprehension: 7.5, grammatical_awareness: 8 },
          subSkillBreakdown: { comprehension: 8, grammar: 7 },
        },
      },
    },
    {
      taskId: "w1d3-listen-dictation",
      evaluatorInput: {
        archetypeId: "LISTEN_DICTATION",
        widget: "listen_dictation",
        taskContentRef: "tasks.source.day_24_01_03.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "4 of 4 sentences exact",
          rubricScores: { comprehension: 10, grammatical_accuracy: 10, spelling: 10 },
          subSkillBreakdown: { comprehension: 10, grammar: 10, vocabulary: 8 },
        },
        wrong: {
          rawScore: 7.5,
          percentage: 75,
          tier: "good",
          attendedLabel: "3 of 4 sentences exact",
          rubricScores: { comprehension: 8, grammatical_accuracy: 7, spelling: 8 },
          subSkillBreakdown: { comprehension: 8, grammar: 7, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w1d3-write-sent-trans",
      evaluatorInput: {
        archetypeId: "WRITE_SENT_TRANS",
        widget: "sentence_transform",
        taskContentRef: "tasks.source.day_24_01_03.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.5,
          percentage: 95,
          tier: "excellent",
          attendedLabel: "3 of 3 sentences transformed",
          rubricScores: { grammatical_accuracy: 10, expression: 9, vocabulary: 9 },
          subSkillBreakdown: { grammar: 10, expression: 9, vocabulary: 8 },
        },
        wrong: {
          rawScore: 7,
          percentage: 70,
          tier: "good",
          attendedLabel: "2 of 3 sentences transformed",
          rubricScores: { grammatical_accuracy: 6.5, expression: 8, vocabulary: 7 },
          subSkillBreakdown: { grammar: 7, expression: 8, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w1d3-speak-timed",
      evaluatorInput: {
        archetypeId: "SPEAK_TIMED",
        widget: "speak_record",
        taskContentRef: "tasks.source.day_24_01_03.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.2,
          percentage: 92,
          tier: "excellent",
          attendedLabel: "3 of 3 recordings clear",
          rubricScores: { fluency: 9, pronunciation: 9, grammatical_accuracy: 9.5 },
          subSkillBreakdown: { fluency: 9, pronunciation: 9, grammar: 9 },
        },
        wrong: {
          rawScore: 7.2,
          percentage: 72,
          tier: "good",
          attendedLabel: "2 of 3 recordings clear",
          rubricScores: { fluency: 8, pronunciation: 8, grammatical_accuracy: 6 },
          subSkillBreakdown: { fluency: 8, pronunciation: 8, grammar: 6 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_01_03",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w1d3-read-comp-mcq", sequence: 1, archetypeId: "READ_COMP_MCQ", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d3-listen-dictation", sequence: 2, archetypeId: "LISTEN_DICTATION", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d3-write-sent-trans", sequence: 3, archetypeId: "WRITE_SENT_TRANS", label: "Write", rawScore: 9.5, tier: "excellent", baseReward: 9 },
        { taskId: "w1d3-speak-timed", sequence: 4, archetypeId: "SPEAK_TIMED", label: "Speak", rawScore: 9.2, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w1d3-read-comp-mcq", sequence: 1, archetypeId: "READ_COMP_MCQ", label: "Read", rawScore: 7.5, tier: "good", baseReward: 7 },
        { taskId: "w1d3-listen-dictation", sequence: 2, archetypeId: "LISTEN_DICTATION", label: "Listen", rawScore: 7.5, tier: "good", baseReward: 7 },
        { taskId: "w1d3-write-sent-trans", sequence: 3, archetypeId: "WRITE_SENT_TRANS", label: "Write", rawScore: 7, tier: "good", baseReward: 7 },
        { taskId: "w1d3-speak-timed", sequence: 4, archetypeId: "SPEAK_TIMED", label: "Speak", rawScore: 7.2, tier: "good", baseReward: 7 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 22,
        vocabulary: 6,
        pronunciation: 9,
        fluency: 9,
        expression: 9,
        comprehension: 15,
        tone: 3,
      },
      wrong: {
        grammar: 14,
        vocabulary: 5,
        pronunciation: 7,
        fluency: 7,
        expression: 7,
        comprehension: 11,
        tone: 2,
      },
    },
    skillLabels,
  },
};

const evaluationDays: Partial<Record<CourseTrack, Record<number, Record<number, EvaluationDayData>>>> = {
  "24w": {
    1: {
      1: weekOneDayOneEvaluation,
      2: weekOneDayTwoEvaluation,
      3: weekOneDayThreeEvaluation,
    },
  },
  "48w": {},
};

export function getEvaluationDay(
  courseTrack: CourseTrack,
  week: number,
  day: number,
): EvaluationDayData | null {
  return evaluationDays[courseTrack]?.[week]?.[day] ?? null;
}

export function getActivityEvaluation(
  dayData: EvaluationDayData | null,
  taskId: string,
): ActivityEvaluation | null {
  return dayData?.activityEvaluations.find((entry) => entry.taskId === taskId) ?? null;
}
