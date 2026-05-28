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


const weekOneDayFourEvaluation: EvaluationDayData = {
  dayId: "day_24_01_04",
  activityEvaluations: [
    {
      taskId: "w1d4-read-word-match",
      evaluatorInput: {
        archetypeId: "READ_WORD_MATCH",
        widget: "read_word_match",
        taskContentRef: "tasks.source.day_24_01_04.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 items matched",
          rubricScores: { grammar: 10, vocabulary: 10 },
          subSkillBreakdown: { grammar: 10, vocabulary: 10 },
        },
        wrong: {
          rawScore: 6.6,
          percentage: 66,
          tier: "good",
          attendedLabel: "2 of 3 items matched",
          rubricScores: { grammar: 6.6, vocabulary: 6.6 },
          subSkillBreakdown: { grammar: 6.6, vocabulary: 6.6 },
        },
      },
    },
    {
      taskId: "w1d4-listen-mcq",
      evaluatorInput: {
        archetypeId: "LISTEN_MCQ",
        widget: "listen_mcq",
        taskContentRef: "tasks.source.day_24_01_04.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "2 of 2 questions correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, grammar: 10 },
        },
        wrong: {
          rawScore: 5,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "1 of 2 questions correct",
          rubricScores: { comprehension: 5, accuracy: 5 },
          subSkillBreakdown: { comprehension: 5, grammar: 5 },
        },
      },
    },
    {
      taskId: "w1d4-write-open-sent",
      evaluatorInput: {
        archetypeId: "WRITE_OPEN_SENT",
        widget: "open_text",
        taskContentRef: "tasks.source.day_24_01_04.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 sentences correct",
          rubricScores: { grammatical_accuracy: 10, expression: 10 },
          subSkillBreakdown: { grammar: 10, expression: 10 },
        },
        wrong: {
          rawScore: 6.6,
          percentage: 66,
          tier: "good",
          attendedLabel: "2 of 3 sentences correct",
          rubricScores: { grammatical_accuracy: 6.6, expression: 6.6 },
          subSkillBreakdown: { grammar: 6.6, expression: 6.6 },
        },
      },
    },
    {
      taskId: "w1d4-speak-pic-desc",
      evaluatorInput: {
        archetypeId: "SPEAK_PIC_DESC",
        widget: "speak_pic_desc",
        taskContentRef: "tasks.source.day_24_01_04.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Description clear and accurate",
          rubricScores: { fluency: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { fluency: 10, grammar: 10 },
        },
        wrong: {
          rawScore: 5,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "Description had grammar errors",
          rubricScores: { fluency: 8, grammatical_accuracy: 2 },
          subSkillBreakdown: { fluency: 8, grammar: 2 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_01_04",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w1d4-read-word-match", sequence: 1, archetypeId: "READ_WORD_MATCH", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d4-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d4-write-open-sent", sequence: 3, archetypeId: "WRITE_OPEN_SENT", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d4-speak-pic-desc", sequence: 4, archetypeId: "SPEAK_PIC_DESC", label: "Speak", rawScore: 10, tier: "excellent", baseReward: 10 },
      ],
      wrong: [
        { taskId: "w1d4-read-word-match", sequence: 1, archetypeId: "READ_WORD_MATCH", label: "Read", rawScore: 6.6, tier: "good", baseReward: 6 },
        { taskId: "w1d4-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 5, tier: "needs_work", baseReward: 5 },
        { taskId: "w1d4-write-open-sent", sequence: 3, archetypeId: "WRITE_OPEN_SENT", label: "Write", rawScore: 6.6, tier: "good", baseReward: 6 },
        { taskId: "w1d4-speak-pic-desc", sequence: 4, archetypeId: "SPEAK_PIC_DESC", label: "Speak", rawScore: 5, tier: "needs_work", baseReward: 5 },
      ],
    },
    pointsEarned: {
      correct: { grammar: 20, fluency: 10, comprehension: 10, expression: 10 },
      wrong: { grammar: 10, fluency: 8, comprehension: 5, expression: 6 },
    },
    skillLabels,
  },
};

const weekOneDayFiveEvaluation: EvaluationDayData = {
  dayId: "day_24_01_05",
  activityEvaluations: [
    {
      taskId: "w1d5-read-cloze",
      evaluatorInput: {
        archetypeId: "READ_CLOZE",
        widget: "fill_blanks",
        taskContentRef: "tasks.source.day_24_01_05.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "4 of 4 blanks correct",
          rubricScores: { accuracy: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { grammar: 10, comprehension: 10 },
        },
        wrong: {
          rawScore: 7.5,
          percentage: 75,
          tier: "good",
          attendedLabel: "3 of 4 blanks correct",
          rubricScores: { accuracy: 7.5, grammatical_accuracy: 7.5 },
          subSkillBreakdown: { grammar: 7.5, comprehension: 7.5 },
        },
      },
    },
    {
      taskId: "w1d5-listen-mcq",
      evaluatorInput: {
        archetypeId: "LISTEN_INFER",
        widget: "listen_mcq",
        taskContentRef: "tasks.source.day_24_01_05.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "2 of 2 questions correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, grammar: 10 },
        },
        wrong: {
          rawScore: 5,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "1 of 2 questions correct",
          rubricScores: { comprehension: 5, accuracy: 5 },
          subSkillBreakdown: { comprehension: 5, grammar: 5 },
        },
      },
    },
    {
      taskId: "w1d5-write-paragraph",
      evaluatorInput: {
        archetypeId: "WRITE_PARA",
        widget: "write_paragraph",
        taskContentRef: "tasks.source.day_24_01_05.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Paragraph accepted as clear",
          rubricScores: { grammatical_accuracy: 10, expression: 10 },
          subSkillBreakdown: { grammar: 10, expression: 10 },
        },
        wrong: {
          rawScore: 6.6,
          percentage: 66,
          tier: "good",
          attendedLabel: "Paragraph had grammar issues",
          rubricScores: { grammatical_accuracy: 6, expression: 7.2 },
          subSkillBreakdown: { grammar: 6, expression: 7.2 },
        },
      },
    },
    {
      taskId: "w1d5-speak-roleplay",
      evaluatorInput: {
        archetypeId: "SPEAK_ROLEPLAY",
        widget: "speak_roleplay",
        taskContentRef: "tasks.source.day_24_01_05.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Roleplay responses clear and natural",
          rubricScores: { fluency: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { fluency: 10, grammar: 10 },
        },
        wrong: {
          rawScore: 5,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "Roleplay had pronoun error",
          rubricScores: { fluency: 8, grammatical_accuracy: 2 },
          subSkillBreakdown: { fluency: 8, grammar: 2 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_01_05",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w1d5-read-cloze", sequence: 1, archetypeId: "READ_CLOZE", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d5-listen-mcq", sequence: 2, archetypeId: "LISTEN_INFER", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d5-write-paragraph", sequence: 3, archetypeId: "WRITE_PARA", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d5-speak-roleplay", sequence: 4, archetypeId: "SPEAK_ROLEPLAY", label: "Speak", rawScore: 10, tier: "excellent", baseReward: 10 },
      ],
      wrong: [
        { taskId: "w1d5-read-cloze", sequence: 1, archetypeId: "READ_CLOZE", label: "Read", rawScore: 7.5, tier: "good", baseReward: 7 },
        { taskId: "w1d5-listen-mcq", sequence: 2, archetypeId: "LISTEN_INFER", label: "Listen", rawScore: 5, tier: "needs_work", baseReward: 5 },
        { taskId: "w1d5-write-paragraph", sequence: 3, archetypeId: "WRITE_PARA", label: "Write", rawScore: 6.6, tier: "good", baseReward: 6 },
        { taskId: "w1d5-speak-roleplay", sequence: 4, archetypeId: "SPEAK_ROLEPLAY", label: "Speak", rawScore: 5, tier: "needs_work", baseReward: 5 },
      ],
    },
    pointsEarned: {
      correct: { grammar: 20, fluency: 10, comprehension: 10, expression: 10 },
      wrong: { grammar: 10, fluency: 8, comprehension: 5, expression: 6 },
    },
    skillLabels,
  },
};

const weekOneDaySixEvaluation: EvaluationDayData = {
  dayId: "day_24_01_06",
  activityEvaluations: [
    {
      taskId: "w1d6-read-tfng",
      evaluatorInput: {
        archetypeId: "READ_TFNG",
        widget: "read_tfng",
        taskContentRef: "tasks.source.day_24_01_06.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "5 of 5 statements correct",
          rubricScores: { accuracy: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { grammar: 10, comprehension: 10 },
        },
        wrong: {
          rawScore: 8,
          percentage: 80,
          tier: "good",
          attendedLabel: "4 of 5 statements correct",
          rubricScores: { accuracy: 8, grammatical_accuracy: 8 },
          subSkillBreakdown: { grammar: 8, comprehension: 8 },
        },
      },
    },
    {
      taskId: "w1d6-listen-shadow",
      evaluatorInput: {
        archetypeId: "LISTEN_SHADOW",
        widget: "listen_shadow",
        taskContentRef: "tasks.source.day_24_01_06.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Shadowing exactly clear",
          rubricScores: { pronunciation: 10, fluency: 10 },
          subSkillBreakdown: { pronunciation: 10, fluency: 10 },
        },
        wrong: {
          rawScore: 5,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "Shadowing had word omissions",
          rubricScores: { pronunciation: 6, fluency: 4 },
          subSkillBreakdown: { pronunciation: 6, fluency: 4 },
        },
      },
    },
    {
      taskId: "w1d6-write-email",
      evaluatorInput: {
        archetypeId: "WRITE_EMAIL",
        widget: "write_email",
        taskContentRef: "tasks.source.day_24_01_06.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Email accepted as natural",
          rubricScores: { grammatical_accuracy: 10, expression: 10 },
          subSkillBreakdown: { grammar: 10, expression: 10 },
        },
        wrong: {
          rawScore: 6.6,
          percentage: 66,
          tier: "good",
          attendedLabel: "Email had possessive noun error",
          rubricScores: { grammatical_accuracy: 6, expression: 7.2 },
          subSkillBreakdown: { grammar: 6, expression: 7.2 },
        },
      },
    },
    {
      taskId: "w1d6-speak-smalltalk",
      evaluatorInput: {
        archetypeId: "SPEAK_SMALLTALK",
        widget: "speak_smalltalk",
        taskContentRef: "tasks.source.day_24_01_06.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Smalltalk responses clear",
          rubricScores: { fluency: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { fluency: 10, grammar: 10 },
        },
        wrong: {
          rawScore: 5,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "Smalltalk had possessive error",
          rubricScores: { fluency: 8, grammatical_accuracy: 2 },
          subSkillBreakdown: { fluency: 8, grammar: 2 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_01_06",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w1d6-read-tfng", sequence: 1, archetypeId: "READ_TFNG", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d6-listen-shadow", sequence: 2, archetypeId: "LISTEN_SHADOW", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d6-write-email", sequence: 3, archetypeId: "WRITE_EMAIL", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d6-speak-smalltalk", sequence: 4, archetypeId: "SPEAK_SMALLTALK", label: "Speak", rawScore: 10, tier: "excellent", baseReward: 10 },
      ],
      wrong: [
        { taskId: "w1d6-read-tfng", sequence: 1, archetypeId: "READ_TFNG", label: "Read", rawScore: 8, tier: "good", baseReward: 8 },
        { taskId: "w1d6-listen-shadow", sequence: 2, archetypeId: "LISTEN_SHADOW", label: "Listen", rawScore: 5, tier: "needs_work", baseReward: 5 },
        { taskId: "w1d6-write-email", sequence: 3, archetypeId: "WRITE_EMAIL", label: "Write", rawScore: 6.6, tier: "good", baseReward: 6 },
        { taskId: "w1d6-speak-smalltalk", sequence: 4, archetypeId: "SPEAK_SMALLTALK", label: "Speak", rawScore: 5, tier: "needs_work", baseReward: 5 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 20,
        fluency: 10,
        comprehension: 10,
        expression: 10,
      },
      wrong: {
        grammar: 10,
        fluency: 8,
        comprehension: 5,
        expression: 6,
      },
    },
    skillLabels,
  },
};

const weekOneDaySevenEvaluation: EvaluationDayData = {
  dayId: "day_24_01_07",
  activityEvaluations: [
    {
      taskId: "w1d7-read-context-mcq",
      evaluatorInput: {
        archetypeId: "READ_CONTEXT_MCQ",
        widget: "read_comp_mcq",
        taskContentRef: "tasks.source.day_24_01_07.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]"
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "4 of 4 questions correct",
          rubricScores: { accuracy: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { grammar: 10, comprehension: 10 }
        },
        wrong: {
          rawScore: 7.5,
          percentage: 75,
          tier: "good",
          attendedLabel: "3 of 4 questions correct",
          rubricScores: { accuracy: 7.5, grammatical_accuracy: 8 },
          subSkillBreakdown: { grammar: 8, comprehension: 7 }
        }
      }
    },
    {
      taskId: "w1d7-listen-retell",
      evaluatorInput: {
        archetypeId: "LISTEN_RETELL",
        widget: "listen_retell",
        taskContentRef: "tasks.source.day_24_01_07.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]"
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Retell recording clear",
          rubricScores: { comprehension: 10, fluency: 10 },
          subSkillBreakdown: { comprehension: 10, fluency: 10 }
        },
        wrong: {
          rawScore: 5,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "Retell had minor preposition error",
          rubricScores: { comprehension: 6, fluency: 8 },
          subSkillBreakdown: { comprehension: 6, fluency: 8 }
        }
      }
    },
    {
      taskId: "w1d7-write-paraphrase",
      evaluatorInput: {
        archetypeId: "WRITE_PARAPHRASE",
        widget: "write_paraphrase",
        taskContentRef: "tasks.source.day_24_01_07.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]"
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 sentences correct",
          rubricScores: { accuracy: 10, expression: 10 },
          subSkillBreakdown: { grammar: 10, expression: 10 }
        },
        wrong: {
          rawScore: 6.6,
          percentage: 66,
          tier: "good",
          attendedLabel: "2 of 3 sentences correct",
          rubricScores: { accuracy: 6.6, expression: 7 },
          subSkillBreakdown: { grammar: 7, expression: 6 }
        }
      }
    },
    {
      taskId: "w1d7-speak-present",
      evaluatorInput: {
        archetypeId: "SPEAK_PRESENT",
        widget: "speak_present",
        taskContentRef: "tasks.source.day_24_01_07.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]"
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Room presentation clear",
          rubricScores: { fluency: 10, pronunciation: 10 },
          subSkillBreakdown: { fluency: 10, pronunciation: 10 }
        },
        wrong: {
          rawScore: 5,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "Presentation had location errors",
          rubricScores: { fluency: 8, pronunciation: 6 },
          subSkillBreakdown: { fluency: 8, pronunciation: 6 }
        }
      }
    }
  ],
  overallScorecard: {
    dayId: "day_24_01_07",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w1d7-read-context-mcq", sequence: 1, archetypeId: "READ_CONTEXT_MCQ", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d7-listen-retell", sequence: 2, archetypeId: "LISTEN_RETELL", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d7-write-paraphrase", sequence: 3, archetypeId: "WRITE_PARAPHRASE", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w1d7-speak-present", sequence: 4, archetypeId: "SPEAK_PRESENT", label: "Speak", rawScore: 10, tier: "excellent", baseReward: 10 }
      ],
      wrong: [
        { taskId: "w1d7-read-context-mcq", sequence: 1, archetypeId: "READ_CONTEXT_MCQ", label: "Read", rawScore: 7.5, tier: "good", baseReward: 7 },
        { taskId: "w1d7-listen-retell", sequence: 2, archetypeId: "LISTEN_RETELL", label: "Listen", rawScore: 5, tier: "needs_work", baseReward: 5 },
        { taskId: "w1d7-write-paraphrase", sequence: 3, archetypeId: "WRITE_PARAPHRASE", label: "Write", rawScore: 6.6, tier: "good", baseReward: 6 },
        { taskId: "w1d7-speak-present", sequence: 4, archetypeId: "SPEAK_PRESENT", label: "Speak", rawScore: 5, tier: "needs_work", baseReward: 5 }
      ]
    },
    pointsEarned: {
      correct: {
        grammar: 20,
        fluency: 10,
        comprehension: 10,
        expression: 10
      },
      wrong: {
        grammar: 10,
        fluency: 8,
        comprehension: 5,
        expression: 6
      }
    },
    skillLabels
  }
};

const weekTwoDayOneEvaluation: EvaluationDayData = {
  dayId: "day_24_02_01",
  activityEvaluations: [
    {
      taskId: "w2d1-read-intro-mcq",
      evaluatorInput: {
        archetypeId: "READ_COMP_MCQ",
        widget: "read_comp_mcq",
        taskContentRef: "tasks.source.day_24_02_01.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 questions correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, tone: 8 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "good",
          attendedLabel: "2 of 3 questions correct",
          rubricScores: { comprehension: 6.7, accuracy: 6.7 },
          subSkillBreakdown: { comprehension: 7, tone: 6 },
        },
      },
    },
    {
      taskId: "w2d1-listen-greeting-mcq",
      evaluatorInput: {
        archetypeId: "LISTEN_MCQ",
        widget: "listen_mcq",
        taskContentRef: "tasks.source.day_24_02_01.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 questions correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, tone: 8 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "good",
          attendedLabel: "2 of 3 questions correct",
          rubricScores: { comprehension: 6.7, accuracy: 6.7 },
          subSkillBreakdown: { comprehension: 7, tone: 6 },
        },
      },
    },
    {
      taskId: "w2d1-write-intro-transform",
      evaluatorInput: {
        archetypeId: "WRITE_SENT_TRANS",
        widget: "sentence_transform",
        taskContentRef: "tasks.source.day_24_02_01.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.6,
          percentage: 96,
          tier: "excellent",
          attendedLabel: "3 of 3 introductions accepted",
          rubricScores: { grammatical_accuracy: 10, expression: 9, tone: 9.5 },
          subSkillBreakdown: { grammar: 10, expression: 9, tone: 9 },
        },
        wrong: {
          rawScore: 7.2,
          percentage: 72,
          tier: "good",
          attendedLabel: "2 of 3 introductions accepted",
          rubricScores: { grammatical_accuracy: 7, expression: 7.5, tone: 7 },
          subSkillBreakdown: { grammar: 7, expression: 8, tone: 7 },
        },
      },
    },
    {
      taskId: "w2d1-speak-intro-roleplay",
      evaluatorInput: {
        archetypeId: "SPEAK_ROLEPLAY",
        widget: "speak_roleplay",
        taskContentRef: "tasks.source.day_24_02_01.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.4,
          percentage: 94,
          tier: "excellent",
          attendedLabel: "Roleplay responses clear and natural",
          rubricScores: { fluency: 9, grammatical_accuracy: 9.5, tone: 9.5 },
          subSkillBreakdown: { fluency: 9, grammar: 9, tone: 10 },
        },
        wrong: {
          rawScore: 5.5,
          percentage: 55,
          tier: "needs_work",
          attendedLabel: "Roleplay had one introduction error",
          rubricScores: { fluency: 8, grammatical_accuracy: 3, tone: 5.5 },
          subSkillBreakdown: { fluency: 8, grammar: 3, tone: 6 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_02_01",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w2d1-read-intro-mcq", sequence: 1, archetypeId: "READ_COMP_MCQ", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w2d1-listen-greeting-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w2d1-write-intro-transform", sequence: 3, archetypeId: "WRITE_SENT_TRANS", label: "Write", rawScore: 9.6, tier: "excellent", baseReward: 9 },
        { taskId: "w2d1-speak-intro-roleplay", sequence: 4, archetypeId: "SPEAK_ROLEPLAY", label: "Speak", rawScore: 9.4, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w2d1-read-intro-mcq", sequence: 1, archetypeId: "READ_COMP_MCQ", label: "Read", rawScore: 6.7, tier: "good", baseReward: 6 },
        { taskId: "w2d1-listen-greeting-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 6.7, tier: "good", baseReward: 6 },
        { taskId: "w2d1-write-intro-transform", sequence: 3, archetypeId: "WRITE_SENT_TRANS", label: "Write", rawScore: 7.2, tier: "good", baseReward: 7 },
        { taskId: "w2d1-speak-intro-roleplay", sequence: 4, archetypeId: "SPEAK_ROLEPLAY", label: "Speak", rawScore: 5.5, tier: "needs_work", baseReward: 5 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 18,
        vocabulary: 4,
        fluency: 9,
        expression: 9,
        comprehension: 20,
        tone: 10,
      },
      wrong: {
        grammar: 10,
        vocabulary: 3,
        fluency: 8,
        expression: 7,
        comprehension: 14,
        tone: 6,
      },
    },
    skillLabels,
  },
};

const weekTwoDayTwoEvaluation: EvaluationDayData = {
  dayId: "day_24_02_02",
  activityEvaluations: [
    {
      taskId: "w2d2-read-tfng",
      evaluatorInput: {
        archetypeId: "READ_TFNG",
        widget: "read_tfng",
        taskContentRef: "tasks.source.day_24_02_02.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "4 of 4 statements correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, grammar: 8 },
        },
        wrong: {
          rawScore: 7.5,
          percentage: 75,
          tier: "good",
          attendedLabel: "3 of 4 statements correct",
          rubricScores: { comprehension: 7.5, accuracy: 7.5 },
          subSkillBreakdown: { comprehension: 8, grammar: 7 },
        },
      },
    },
    {
      taskId: "w2d2-listen-infer",
      evaluatorInput: {
        archetypeId: "LISTEN_INFER",
        widget: "listen_infer",
        taskContentRef: "tasks.source.day_24_02_02.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "4 of 4 intent questions correct",
          rubricScores: { comprehension: 10, inference: 10 },
          subSkillBreakdown: { comprehension: 10, tone: 8 },
        },
        wrong: {
          rawScore: 7.5,
          percentage: 75,
          tier: "good",
          attendedLabel: "3 of 4 intent questions correct",
          rubricScores: { comprehension: 8, inference: 7 },
          subSkillBreakdown: { comprehension: 8, tone: 6 },
        },
      },
    },
    {
      taskId: "w2d2-write-email",
      evaluatorInput: {
        archetypeId: "WRITE_EMAIL",
        widget: "write_email",
        taskContentRef: "tasks.source.day_24_02_02.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.4,
          percentage: 94,
          tier: "excellent",
          attendedLabel: "Question message accepted",
          rubricScores: { expression: 9.5, grammatical_accuracy: 9, tone: 10 },
          subSkillBreakdown: { expression: 9, grammar: 9, tone: 10, vocabulary: 8 },
        },
        wrong: {
          rawScore: 7,
          percentage: 70,
          tier: "good",
          attendedLabel: "Question message has one grammar issue",
          rubricScores: { expression: 8, grammatical_accuracy: 6, tone: 8 },
          subSkillBreakdown: { expression: 8, grammar: 6, tone: 8, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w2d2-speak-interview",
      evaluatorInput: {
        archetypeId: "SPEAK_INTERVIEW",
        widget: "speak_interview",
        taskContentRef: "tasks.source.day_24_02_02.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.3,
          percentage: 93,
          tier: "excellent",
          attendedLabel: "3 of 3 interview answers clear",
          rubricScores: { fluency: 9, pronunciation: 9, grammatical_accuracy: 9.5 },
          subSkillBreakdown: { fluency: 9, pronunciation: 9, grammar: 9, tone: 9 },
        },
        wrong: {
          rawScore: 7.1,
          percentage: 71,
          tier: "good",
          attendedLabel: "2 of 3 interview answers clear",
          rubricScores: { fluency: 8, pronunciation: 8, grammatical_accuracy: 5.5 },
          subSkillBreakdown: { fluency: 8, pronunciation: 8, grammar: 6, tone: 7 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_02_02",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w2d2-read-tfng", sequence: 1, archetypeId: "READ_TFNG", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w2d2-listen-infer", sequence: 2, archetypeId: "LISTEN_INFER", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w2d2-write-email", sequence: 3, archetypeId: "WRITE_EMAIL", label: "Write", rawScore: 9.4, tier: "excellent", baseReward: 9 },
        { taskId: "w2d2-speak-interview", sequence: 4, archetypeId: "SPEAK_INTERVIEW", label: "Speak", rawScore: 9.3, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w2d2-read-tfng", sequence: 1, archetypeId: "READ_TFNG", label: "Read", rawScore: 7.5, tier: "good", baseReward: 7 },
        { taskId: "w2d2-listen-infer", sequence: 2, archetypeId: "LISTEN_INFER", label: "Listen", rawScore: 7.5, tier: "good", baseReward: 7 },
        { taskId: "w2d2-write-email", sequence: 3, archetypeId: "WRITE_EMAIL", label: "Write", rawScore: 7, tier: "good", baseReward: 7 },
        { taskId: "w2d2-speak-interview", sequence: 4, archetypeId: "SPEAK_INTERVIEW", label: "Speak", rawScore: 7.1, tier: "good", baseReward: 7 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 18,
        vocabulary: 8,
        pronunciation: 9,
        fluency: 9,
        expression: 9,
        comprehension: 20,
        tone: 17,
      },
      wrong: {
        grammar: 12,
        vocabulary: 7,
        pronunciation: 8,
        fluency: 8,
        expression: 8,
        comprehension: 16,
        tone: 13,
      },
    },
    skillLabels,
  },
};

const weekTwoDayThreeEvaluation: EvaluationDayData = {
  dayId: "day_24_02_03",
  activityEvaluations: [
    {
      taskId: "w2d3-read-structure",
      evaluatorInput: {
        archetypeId: "READ_STRUCTURE_ID",
        widget: "read_structure",
        taskContentRef: "tasks.source.day_24_02_03.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 structure labels correct",
          rubricScores: { comprehension: 10, structure_awareness: 10 },
          subSkillBreakdown: { comprehension: 10, expression: 8 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "average",
          attendedLabel: "2 of 3 structure labels correct",
          rubricScores: { comprehension: 7, structure_awareness: 6.5 },
          subSkillBreakdown: { comprehension: 7, expression: 6 },
        },
      },
    },
    {
      taskId: "w2d3-listen-retell",
      evaluatorInput: {
        archetypeId: "LISTEN_RETELL",
        widget: "listen_retell",
        taskContentRef: "tasks.source.day_24_02_03.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.4,
          percentage: 94,
          tier: "excellent",
          attendedLabel: "Main routine actions retold clearly",
          rubricScores: { comprehension: 9.5, recall: 9, sequence: 9.5 },
          subSkillBreakdown: { comprehension: 10, fluency: 9, vocabulary: 8 },
        },
        wrong: {
          rawScore: 7.1,
          percentage: 71,
          tier: "good",
          attendedLabel: "Retell includes one changed detail",
          rubricScores: { comprehension: 7, recall: 7, sequence: 7.5 },
          subSkillBreakdown: { comprehension: 7, fluency: 8, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w2d3-write-para",
      evaluatorInput: {
        archetypeId: "WRITE_PARA",
        widget: "write_paragraph",
        taskContentRef: "tasks.source.day_24_02_03.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.2,
          percentage: 92,
          tier: "excellent",
          attendedLabel: "Routine paragraph accepted",
          rubricScores: { grammatical_accuracy: 9, organization: 9.5, fluency: 9 },
          subSkillBreakdown: { grammar: 9, expression: 9, fluency: 9, vocabulary: 8 },
        },
        wrong: {
          rawScore: 7.2,
          percentage: 72,
          tier: "good",
          attendedLabel: "Routine paragraph has one grammar slip",
          rubricScores: { grammatical_accuracy: 6.5, organization: 9, fluency: 7.5 },
          subSkillBreakdown: { grammar: 6, expression: 8, fluency: 8, vocabulary: 8 },
        },
      },
    },
    {
      taskId: "w2d3-speak-opinion",
      evaluatorInput: {
        archetypeId: "SPEAK_OPINION",
        widget: "speak_record",
        taskContentRef: "tasks.source.day_24_02_03.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.1,
          percentage: 91,
          tier: "excellent",
          attendedLabel: "Opinion response clear and natural",
          rubricScores: { fluency: 9, pronunciation: 9, grammatical_accuracy: 9, expression: 9.5 },
          subSkillBreakdown: { fluency: 9, pronunciation: 9, grammar: 9, expression: 9 },
        },
        wrong: {
          rawScore: 7,
          percentage: 70,
          tier: "good",
          attendedLabel: "Opinion response has one grammar slip",
          rubricScores: { fluency: 8, pronunciation: 8, grammatical_accuracy: 5.5, expression: 7.5 },
          subSkillBreakdown: { fluency: 8, pronunciation: 8, grammar: 6, expression: 7 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_02_03",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w2d3-read-structure", sequence: 1, archetypeId: "READ_STRUCTURE_ID", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w2d3-listen-retell", sequence: 2, archetypeId: "LISTEN_RETELL", label: "Listen", rawScore: 9.4, tier: "excellent", baseReward: 9 },
        { taskId: "w2d3-write-para", sequence: 3, archetypeId: "WRITE_PARA", label: "Write", rawScore: 9.2, tier: "excellent", baseReward: 9 },
        { taskId: "w2d3-speak-opinion", sequence: 4, archetypeId: "SPEAK_OPINION", label: "Speak", rawScore: 9.1, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w2d3-read-structure", sequence: 1, archetypeId: "READ_STRUCTURE_ID", label: "Read", rawScore: 6.7, tier: "average", baseReward: 6 },
        { taskId: "w2d3-listen-retell", sequence: 2, archetypeId: "LISTEN_RETELL", label: "Listen", rawScore: 7.1, tier: "good", baseReward: 7 },
        { taskId: "w2d3-write-para", sequence: 3, archetypeId: "WRITE_PARA", label: "Write", rawScore: 7.2, tier: "good", baseReward: 7 },
        { taskId: "w2d3-speak-opinion", sequence: 4, archetypeId: "SPEAK_OPINION", label: "Speak", rawScore: 7, tier: "good", baseReward: 7 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 18,
        vocabulary: 8,
        pronunciation: 9,
        fluency: 18,
        expression: 18,
        comprehension: 20,
        tone: 4,
      },
      wrong: {
        grammar: 12,
        vocabulary: 7,
        pronunciation: 8,
        fluency: 16,
        expression: 15,
        comprehension: 14,
        tone: 3,
      },
    },
    skillLabels,
  },
};

const weekTwoDayFourEvaluation: EvaluationDayData = {
  dayId: "day_24_02_04",
  activityEvaluations: [
    {
      taskId: "w2d4-read-comp-mcq",
      evaluatorInput: {
        archetypeId: "READ_COMP_MCQ",
        widget: "read_comp_mcq",
        taskContentRef: "tasks.source.day_24_02_04.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 questions correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 8 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "good",
          attendedLabel: "2 of 3 questions correct",
          rubricScores: { comprehension: 6.7, accuracy: 6.7 },
          subSkillBreakdown: { comprehension: 7, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w2d4-listen-mcq",
      evaluatorInput: {
        archetypeId: "LISTEN_MCQ",
        widget: "listen_mcq",
        taskContentRef: "tasks.source.day_24_02_04.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 questions correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, tone: 8 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "good",
          attendedLabel: "2 of 3 questions correct",
          rubricScores: { comprehension: 6.7, accuracy: 6.7 },
          subSkillBreakdown: { comprehension: 7, tone: 6 },
        },
      },
    },
    {
      taskId: "w2d4-write-bullets-para",
      evaluatorInput: {
        archetypeId: "WRITE_BULLETS_TO_PARA",
        widget: "write_bullets_to_para",
        taskContentRef: "tasks.source.day_24_02_04.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.3,
          percentage: 93,
          tier: "excellent",
          attendedLabel: "Message paragraph accepted",
          rubricScores: { expression: 9.5, grammatical_accuracy: 9, tone: 9.5 },
          subSkillBreakdown: { expression: 9, grammar: 9, tone: 9, vocabulary: 8 },
        },
        wrong: {
          rawScore: 7,
          percentage: 70,
          tier: "good",
          attendedLabel: "Message paragraph has grammar slips",
          rubricScores: { expression: 7.5, grammatical_accuracy: 6, tone: 7.5 },
          subSkillBreakdown: { expression: 7, grammar: 6, tone: 7, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w2d4-speak-roleplay",
      evaluatorInput: {
        archetypeId: "SPEAK_ROLEPLAY",
        widget: "speak_roleplay",
        taskContentRef: "tasks.source.day_24_02_04.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.4,
          percentage: 94,
          tier: "excellent",
          attendedLabel: "Roleplay responses clear and natural",
          rubricScores: { fluency: 9, grammatical_accuracy: 9.5, tone: 9.5 },
          subSkillBreakdown: { fluency: 9, grammar: 9, tone: 10 },
        },
        wrong: {
          rawScore: 5.5,
          percentage: 55,
          tier: "needs_work",
          attendedLabel: "Roleplay had one ordering error",
          rubricScores: { fluency: 8, grammatical_accuracy: 3, tone: 5.5 },
          subSkillBreakdown: { fluency: 8, grammar: 3, tone: 6 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_02_04",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w2d4-read-comp-mcq", sequence: 1, archetypeId: "READ_COMP_MCQ", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w2d4-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w2d4-write-bullets-para", sequence: 3, archetypeId: "WRITE_BULLETS_TO_PARA", label: "Write", rawScore: 9.3, tier: "excellent", baseReward: 9 },
        { taskId: "w2d4-speak-roleplay", sequence: 4, archetypeId: "SPEAK_ROLEPLAY", label: "Speak", rawScore: 9.4, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w2d4-read-comp-mcq", sequence: 1, archetypeId: "READ_COMP_MCQ", label: "Read", rawScore: 6.7, tier: "good", baseReward: 6 },
        { taskId: "w2d4-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 6.7, tier: "good", baseReward: 6 },
        { taskId: "w2d4-write-bullets-para", sequence: 3, archetypeId: "WRITE_BULLETS_TO_PARA", label: "Write", rawScore: 7, tier: "good", baseReward: 7 },
        { taskId: "w2d4-speak-roleplay", sequence: 4, archetypeId: "SPEAK_ROLEPLAY", label: "Speak", rawScore: 5.5, tier: "needs_work", baseReward: 5 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 18,
        vocabulary: 8,
        fluency: 9,
        expression: 9,
        comprehension: 20,
        tone: 10,
      },
      wrong: {
        grammar: 10,
        vocabulary: 6,
        fluency: 8,
        expression: 7,
        comprehension: 14,
        tone: 6,
      },
    },
    skillLabels,
  },
};

const weekTwoDayFiveEvaluation: EvaluationDayData = {
  dayId: "day_24_02_05",
  activityEvaluations: [
    {
      taskId: "w2d5-read-directions-tfng",
      evaluatorInput: {
        archetypeId: "READ_TFNG",
        widget: "read_tfng",
        taskContentRef: "tasks.source.day_24_02_05.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "4 of 4 direction statements correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 8 },
        },
        wrong: {
          rawScore: 7.5,
          percentage: 75,
          tier: "good",
          attendedLabel: "3 of 4 direction statements correct",
          rubricScores: { comprehension: 7.5, accuracy: 7.5 },
          subSkillBreakdown: { comprehension: 7, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w2d5-listen-help-infer",
      evaluatorInput: {
        archetypeId: "LISTEN_INFER",
        widget: "listen_infer",
        taskContentRef: "tasks.source.day_24_02_05.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "4 of 4 help-intent questions correct",
          rubricScores: { comprehension: 10, inference: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 8 },
        },
        wrong: {
          rawScore: 7.5,
          percentage: 75,
          tier: "good",
          attendedLabel: "3 of 4 help-intent questions correct",
          rubricScores: { comprehension: 7.5, inference: 7 },
          subSkillBreakdown: { comprehension: 7, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w2d5-write-station-help",
      evaluatorInput: {
        archetypeId: "WRITE_IDEA_PARA",
        widget: "write_paragraph",
        taskContentRef: "tasks.source.day_24_02_05.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.3,
          percentage: 93,
          tier: "excellent",
          attendedLabel: "Direction request clear and polite",
          rubricScores: { expression: 9.5, grammatical_accuracy: 9, organization: 9 },
          subSkillBreakdown: { expression: 9, grammar: 9, vocabulary: 8, tone: 9 },
        },
        wrong: {
          rawScore: 7,
          percentage: 70,
          tier: "good",
          attendedLabel: "Direction request understandable with grammar slips",
          rubricScores: { expression: 8, grammatical_accuracy: 6, organization: 7 },
          subSkillBreakdown: { expression: 8, grammar: 6, vocabulary: 7, tone: 8 },
        },
      },
    },
    {
      taskId: "w2d5-speak-map-desc",
      evaluatorInput: {
        archetypeId: "SPEAK_PIC_DESC",
        widget: "speak_pic_desc",
        taskContentRef: "tasks.source.day_24_02_05.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.2,
          percentage: 92,
          tier: "excellent",
          attendedLabel: "Map description clear and accurate",
          rubricScores: { fluency: 9, pronunciation: 9, location_language: 9.5 },
          subSkillBreakdown: { fluency: 9, pronunciation: 9, expression: 9, vocabulary: 8 },
        },
        wrong: {
          rawScore: 7,
          percentage: 70,
          tier: "good",
          attendedLabel: "Map description clear with one location error",
          rubricScores: { fluency: 8, pronunciation: 8, location_language: 6 },
          subSkillBreakdown: { fluency: 8, pronunciation: 8, expression: 7, vocabulary: 6 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_02_05",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w2d5-read-directions-tfng", sequence: 1, archetypeId: "READ_TFNG", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w2d5-listen-help-infer", sequence: 2, archetypeId: "LISTEN_INFER", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w2d5-write-station-help", sequence: 3, archetypeId: "WRITE_IDEA_PARA", label: "Write", rawScore: 9.3, tier: "excellent", baseReward: 9 },
        { taskId: "w2d5-speak-map-desc", sequence: 4, archetypeId: "SPEAK_PIC_DESC", label: "Speak", rawScore: 9.2, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w2d5-read-directions-tfng", sequence: 1, archetypeId: "READ_TFNG", label: "Read", rawScore: 7.5, tier: "good", baseReward: 7 },
        { taskId: "w2d5-listen-help-infer", sequence: 2, archetypeId: "LISTEN_INFER", label: "Listen", rawScore: 7.5, tier: "good", baseReward: 7 },
        { taskId: "w2d5-write-station-help", sequence: 3, archetypeId: "WRITE_IDEA_PARA", label: "Write", rawScore: 7, tier: "good", baseReward: 7 },
        { taskId: "w2d5-speak-map-desc", sequence: 4, archetypeId: "SPEAK_PIC_DESC", label: "Speak", rawScore: 7, tier: "good", baseReward: 7 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 18,
        vocabulary: 24,
        pronunciation: 9,
        fluency: 9,
        expression: 18,
        comprehension: 20,
        tone: 9,
      },
      wrong: {
        grammar: 12,
        vocabulary: 20,
        pronunciation: 8,
        fluency: 8,
        expression: 15,
        comprehension: 14,
        tone: 8,
      },
    },
    skillLabels,
  },
};

const weekTwoDaySixEvaluation: EvaluationDayData = {
  dayId: "day_24_02_06",
  activityEvaluations: [
    {
      taskId: "w2d6-read-tone",
      evaluatorInput: {
        archetypeId: "READ_TONE_ID",
        widget: "read_tone_id",
        taskContentRef: "tasks.source.day_24_02_06.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "2 of 2 message tones identified",
          rubricScores: { tone_awareness: 10, comprehension: 10 },
          subSkillBreakdown: { tone: 10, comprehension: 9 },
        },
        wrong: {
          rawScore: 5,
          percentage: 50,
          tier: "average",
          attendedLabel: "1 of 2 message tones identified",
          rubricScores: { tone_awareness: 5, comprehension: 6 },
          subSkillBreakdown: { tone: 5, comprehension: 6 },
        },
      },
    },
    {
      taskId: "w2d6-listen-tone",
      evaluatorInput: {
        archetypeId: "LISTEN_TONE",
        widget: "listen_mcq",
        taskContentRef: "tasks.source.day_24_02_06.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Phone-call tone identified",
          rubricScores: { listening_comprehension: 10, tone_awareness: 10 },
          subSkillBreakdown: { comprehension: 10, tone: 10 },
        },
        wrong: {
          rawScore: 6,
          percentage: 60,
          tier: "average",
          attendedLabel: "Tone choice missed the urgency cue",
          rubricScores: { listening_comprehension: 6.5, tone_awareness: 5.5 },
          subSkillBreakdown: { comprehension: 6, tone: 6 },
        },
      },
    },
    {
      taskId: "w2d6-write-paraphrase",
      evaluatorInput: {
        archetypeId: "WRITE_PARAPHRASE",
        widget: "write_paraphrase",
        taskContentRef: "tasks.source.day_24_02_06.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.4,
          percentage: 94,
          tier: "excellent",
          attendedLabel: "2 of 2 message rewrites accepted",
          rubricScores: { register_control: 9.5, expression: 9, accuracy: 9.5 },
          subSkillBreakdown: { expression: 9, tone: 10, vocabulary: 8 },
        },
        wrong: {
          rawScore: 7,
          percentage: 70,
          tier: "good",
          attendedLabel: "1 of 2 message rewrites accepted",
          rubricScores: { register_control: 6.5, expression: 7.5, accuracy: 7 },
          subSkillBreakdown: { expression: 7, tone: 6, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w2d6-speak-smalltalk",
      evaluatorInput: {
        archetypeId: "SPEAK_SMALLTALK",
        widget: "speak_smalltalk",
        taskContentRef: "tasks.source.day_24_02_06.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.2,
          percentage: 92,
          tier: "excellent",
          attendedLabel: "2 of 2 smalltalk turns clear",
          rubricScores: { fluency: 9, pronunciation: 9, interaction: 9.5 },
          subSkillBreakdown: { fluency: 9, pronunciation: 9, expression: 9, tone: 9 },
        },
        wrong: {
          rawScore: 7.2,
          percentage: 72,
          tier: "good",
          attendedLabel: "1 of 2 smalltalk turns clear",
          rubricScores: { fluency: 8, pronunciation: 8, grammatical_accuracy: 6 },
          subSkillBreakdown: { fluency: 8, pronunciation: 8, expression: 7, grammar: 6 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_02_06",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w2d6-read-tone", sequence: 1, archetypeId: "READ_TONE_ID", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w2d6-listen-tone", sequence: 2, archetypeId: "LISTEN_TONE", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w2d6-write-paraphrase", sequence: 3, archetypeId: "WRITE_PARAPHRASE", label: "Write", rawScore: 9.4, tier: "excellent", baseReward: 9 },
        { taskId: "w2d6-speak-smalltalk", sequence: 4, archetypeId: "SPEAK_SMALLTALK", label: "Speak", rawScore: 9.2, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w2d6-read-tone", sequence: 1, archetypeId: "READ_TONE_ID", label: "Read", rawScore: 5, tier: "average", baseReward: 5 },
        { taskId: "w2d6-listen-tone", sequence: 2, archetypeId: "LISTEN_TONE", label: "Listen", rawScore: 6, tier: "average", baseReward: 6 },
        { taskId: "w2d6-write-paraphrase", sequence: 3, archetypeId: "WRITE_PARAPHRASE", label: "Write", rawScore: 7, tier: "good", baseReward: 7 },
        { taskId: "w2d6-speak-smalltalk", sequence: 4, archetypeId: "SPEAK_SMALLTALK", label: "Speak", rawScore: 7.2, tier: "good", baseReward: 7 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 6,
        vocabulary: 8,
        pronunciation: 9,
        fluency: 9,
        expression: 18,
        comprehension: 19,
        tone: 29,
      },
      wrong: {
        grammar: 6,
        vocabulary: 7,
        pronunciation: 8,
        fluency: 8,
        expression: 14,
        comprehension: 12,
        tone: 17,
      },
    },
    skillLabels,
  },
};

const weekTwoDaySevenEvaluation: EvaluationDayData = {
  dayId: "day_24_02_07",
  activityEvaluations: [
    {
      taskId: "w2d7-read-structure",
      evaluatorInput: {
        archetypeId: "READ_STRUCTURE_ID",
        widget: "read_structure",
        taskContentRef: "tasks.source.day_24_02_07.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 chat parts connected correctly",
          rubricScores: { comprehension: 10, structure_awareness: 10 },
          subSkillBreakdown: { comprehension: 10, expression: 8, tone: 8 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "average",
          attendedLabel: "2 of 3 chat parts connected correctly",
          rubricScores: { comprehension: 7, structure_awareness: 6.5 },
          subSkillBreakdown: { comprehension: 7, expression: 6, tone: 6 },
        },
      },
    },
    {
      taskId: "w2d7-listen-retell",
      evaluatorInput: {
        archetypeId: "LISTEN_RETELL",
        widget: "listen_retell",
        taskContentRef: "tasks.source.day_24_02_07.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.4,
          percentage: 94,
          tier: "excellent",
          attendedLabel: "Conversation key points retold clearly",
          rubricScores: { comprehension: 9.5, recall: 9, sequence: 9.5 },
          subSkillBreakdown: { comprehension: 10, fluency: 9, vocabulary: 8 },
        },
        wrong: {
          rawScore: 7.2,
          percentage: 72,
          tier: "good",
          attendedLabel: "Retell includes one changed detail",
          rubricScores: { comprehension: 7, recall: 7, sequence: 7.5 },
          subSkillBreakdown: { comprehension: 7, fluency: 8, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w2d7-write-email",
      evaluatorInput: {
        archetypeId: "WRITE_EMAIL",
        widget: "write_email",
        taskContentRef: "tasks.source.day_24_02_07.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.3,
          percentage: 93,
          tier: "excellent",
          attendedLabel: "Friendly weekly message accepted",
          rubricScores: { grammatical_accuracy: 9, organization: 9.5, tone: 9.5 },
          subSkillBreakdown: { grammar: 9, expression: 9, fluency: 9, tone: 9 },
        },
        wrong: {
          rawScore: 7.1,
          percentage: 71,
          tier: "good",
          attendedLabel: "Friendly message has one tense slip",
          rubricScores: { grammatical_accuracy: 6.5, organization: 9, tone: 8 },
          subSkillBreakdown: { grammar: 6, expression: 8, fluency: 8, tone: 8 },
        },
      },
    },
    {
      taskId: "w2d7-speak-present",
      evaluatorInput: {
        archetypeId: "SPEAK_PRESENT",
        widget: "speak_present",
        taskContentRef: "tasks.source.day_24_02_07.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.2,
          percentage: 92,
          tier: "excellent",
          attendedLabel: "60-second week summary clear and structured",
          rubricScores: { fluency: 9, pronunciation: 9, organization: 9.5, expression: 9 },
          subSkillBreakdown: { fluency: 9, pronunciation: 9, expression: 9, grammar: 9 },
        },
        wrong: {
          rawScore: 7.1,
          percentage: 71,
          tier: "good",
          attendedLabel: "Week summary has one tense slip",
          rubricScores: { fluency: 8, pronunciation: 8, grammatical_accuracy: 6, organization: 8 },
          subSkillBreakdown: { fluency: 8, pronunciation: 8, expression: 8, grammar: 6 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_02_07",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w2d7-read-structure", sequence: 1, archetypeId: "READ_STRUCTURE_ID", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w2d7-listen-retell", sequence: 2, archetypeId: "LISTEN_RETELL", label: "Listen", rawScore: 9.4, tier: "excellent", baseReward: 9 },
        { taskId: "w2d7-write-email", sequence: 3, archetypeId: "WRITE_EMAIL", label: "Write", rawScore: 9.3, tier: "excellent", baseReward: 9 },
        { taskId: "w2d7-speak-present", sequence: 4, archetypeId: "SPEAK_PRESENT", label: "Speak", rawScore: 9.2, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w2d7-read-structure", sequence: 1, archetypeId: "READ_STRUCTURE_ID", label: "Read", rawScore: 6.7, tier: "average", baseReward: 6 },
        { taskId: "w2d7-listen-retell", sequence: 2, archetypeId: "LISTEN_RETELL", label: "Listen", rawScore: 7.2, tier: "good", baseReward: 7 },
        { taskId: "w2d7-write-email", sequence: 3, archetypeId: "WRITE_EMAIL", label: "Write", rawScore: 7.1, tier: "good", baseReward: 7 },
        { taskId: "w2d7-speak-present", sequence: 4, archetypeId: "SPEAK_PRESENT", label: "Speak", rawScore: 7.1, tier: "good", baseReward: 7 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 18,
        vocabulary: 8,
        pronunciation: 9,
        fluency: 18,
        expression: 26,
        comprehension: 20,
        tone: 17,
      },
      wrong: {
        grammar: 12,
        vocabulary: 7,
        pronunciation: 8,
        fluency: 16,
        expression: 22,
        comprehension: 14,
        tone: 14,
      },
    },
    skillLabels,
  },
};

const weekThreeDayOneEvaluation: EvaluationDayData = {
  dayId: "day_24_03_01",
  activityEvaluations: [
    {
      taskId: "w3d1-read-word-match",
      evaluatorInput: {
        archetypeId: "READ_WORD_MATCH",
        widget: "read_word_match",
        taskContentRef: "tasks.source.day_24_03_01.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "4 of 4 items matched",
          rubricScores: { vocabulary: 10, accuracy: 10 },
          subSkillBreakdown: { vocabulary: 10, grammar: 8 },
        },
        wrong: {
          rawScore: 7.5,
          percentage: 75,
          tier: "good",
          attendedLabel: "3 of 4 items matched",
          rubricScores: { vocabulary: 7.5, accuracy: 7.5 },
          subSkillBreakdown: { vocabulary: 7, grammar: 7 },
        },
      },
    },
    {
      taskId: "w3d1-listen-mcq",
      evaluatorInput: {
        archetypeId: "LISTEN_MCQ",
        widget: "listen_mcq",
        taskContentRef: "tasks.source.day_24_03_01.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 questions correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 8 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "good",
          attendedLabel: "2 of 3 questions correct",
          rubricScores: { comprehension: 6.7, accuracy: 6.7 },
          subSkillBreakdown: { comprehension: 7, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w3d1-write-sent-trans",
      evaluatorInput: {
        archetypeId: "WRITE_SENT_TRANS",
        widget: "sentence_transform",
        taskContentRef: "tasks.source.day_24_03_01.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "2 of 2 sentences transformed",
          rubricScores: { expression: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { expression: 10, grammar: 10, vocabulary: 8 },
        },
        wrong: {
          rawScore: 5,
          percentage: 50,
          tier: "average",
          attendedLabel: "1 of 2 sentences transformed",
          rubricScores: { expression: 6, grammatical_accuracy: 4 },
          subSkillBreakdown: { expression: 6, grammar: 4, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w3d1-speak-pic-desc",
      evaluatorInput: {
        archetypeId: "SPEAK_PIC_DESC",
        widget: "speak_pic_desc",
        taskContentRef: "tasks.source.day_24_03_01.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.5,
          percentage: 95,
          tier: "excellent",
          attendedLabel: "Description clear and fluent",
          rubricScores: { fluency: 9.5, pronunciation: 9.5, grammatical_accuracy: 9.5 },
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          rawScore: 6,
          percentage: 60,
          tier: "average",
          attendedLabel: "Description has word choice error",
          rubricScores: { fluency: 8, pronunciation: 8, grammatical_accuracy: 6 },
          subSkillBreakdown: { fluency: 8, pronunciation: 8, grammar: 6, vocabulary: 5 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_03_01",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w3d1-read-word-match", sequence: 1, archetypeId: "READ_WORD_MATCH", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d1-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d1-write-sent-trans", sequence: 3, archetypeId: "WRITE_SENT_TRANS", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d1-speak-pic-desc", sequence: 4, archetypeId: "SPEAK_PIC_DESC", label: "Speak", rawScore: 9.5, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w3d1-read-word-match", sequence: 1, archetypeId: "READ_WORD_MATCH", label: "Read", rawScore: 7.5, tier: "good", baseReward: 7 },
        { taskId: "w3d1-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 6.7, tier: "good", baseReward: 6 },
        { taskId: "w3d1-write-sent-trans", sequence: 3, archetypeId: "WRITE_SENT_TRANS", label: "Write", rawScore: 5, tier: "average", baseReward: 5 },
        { taskId: "w3d1-speak-pic-desc", sequence: 4, archetypeId: "SPEAK_PIC_DESC", label: "Speak", rawScore: 6, tier: "average", baseReward: 6 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 27,
        vocabulary: 28,
        pronunciation: 9,
        fluency: 10,
        expression: 10,
        comprehension: 10,
        tone: 0,
      },
      wrong: {
        grammar: 17,
        vocabulary: 18,
        pronunciation: 8,
        fluency: 8,
        expression: 6,
        comprehension: 7,
        tone: 0,
      },
    },
    skillLabels,
  },
};

const weekThreeDayTwoEvaluation: EvaluationDayData = {
  dayId: "day_24_03_02",
  activityEvaluations: [
    {
      taskId: "w3d2-read-context-mcq",
      evaluatorInput: {
        archetypeId: "READ_CONTEXT_MCQ",
        widget: "read_comp_mcq",
        taskContentRef: "tasks.source.day_24_03_02.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "1 of 1 questions correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 10 },
        },
        wrong: {
          rawScore: 0,
          percentage: 0,
          tier: "needs_work",
          attendedLabel: "0 of 1 questions correct",
          rubricScores: { comprehension: 0, accuracy: 0 },
          subSkillBreakdown: { comprehension: 0, vocabulary: 0 },
        },
      },
    },
    {
      taskId: "w3d2-listen-dictation",
      evaluatorInput: {
        archetypeId: "LISTEN_DICTATION",
        widget: "listen_dictation",
        taskContentRef: "tasks.source.day_24_03_02.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "1 of 1 dictations exact",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 10 },
        },
        wrong: {
          rawScore: 0,
          percentage: 0,
          tier: "needs_work",
          attendedLabel: "0 of 1 dictations exact",
          rubricScores: { comprehension: 4, accuracy: 2 },
          subSkillBreakdown: { comprehension: 4, vocabulary: 4 },
        },
      },
    },
    {
      taskId: "w3d2-write-word-upgrade",
      evaluatorInput: {
        archetypeId: "WRITE_WORD_UPGRADE",
        widget: "write_word_upgrade",
        taskContentRef: "tasks.source.day_24_03_02.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 sentences upgraded",
          rubricScores: { expression: 10, accuracy: 10 },
          subSkillBreakdown: { expression: 10, vocabulary: 10, grammar: 10 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "good",
          attendedLabel: "2 of 3 sentences upgraded",
          rubricScores: { expression: 7, accuracy: 6 },
          subSkillBreakdown: { expression: 7, vocabulary: 7, grammar: 6 },
        },
      },
    },
    {
      taskId: "w3d2-speak-timed",
      evaluatorInput: {
        archetypeId: "SPEAK_TIMED",
        widget: "speak_timed",
        taskContentRef: "tasks.source.day_24_03_02.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.5,
          percentage: 95,
          tier: "excellent",
          attendedLabel: "Speech fluent and accurate",
          rubricScores: { fluency: 9.5, pronunciation: 9.5, grammatical_accuracy: 9.5 },
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          rawScore: 6,
          percentage: 60,
          tier: "average",
          attendedLabel: "Speech has vocabulary gaps",
          rubricScores: { fluency: 7, pronunciation: 7, grammatical_accuracy: 5 },
          subSkillBreakdown: { fluency: 7, pronunciation: 7, grammar: 5, vocabulary: 5 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_03_02",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w3d2-read-context-mcq", sequence: 1, archetypeId: "READ_CONTEXT_MCQ", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d2-listen-dictation", sequence: 2, archetypeId: "LISTEN_DICTATION", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d2-write-word-upgrade", sequence: 3, archetypeId: "WRITE_WORD_UPGRADE", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d2-speak-timed", sequence: 4, archetypeId: "SPEAK_TIMED", label: "Speak", rawScore: 9.5, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w3d2-read-context-mcq", sequence: 1, archetypeId: "READ_CONTEXT_MCQ", label: "Read", rawScore: 0, tier: "needs_work", baseReward: 0 },
        { taskId: "w3d2-listen-dictation", sequence: 2, archetypeId: "LISTEN_DICTATION", label: "Listen", rawScore: 0, tier: "needs_work", baseReward: 0 },
        { taskId: "w3d2-write-word-upgrade", sequence: 3, archetypeId: "WRITE_WORD_UPGRADE", label: "Write", rawScore: 6.7, tier: "good", baseReward: 6 },
        { taskId: "w3d2-speak-timed", sequence: 4, archetypeId: "SPEAK_TIMED", label: "Speak", rawScore: 6, tier: "average", baseReward: 6 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 28,
        vocabulary: 29,
        pronunciation: 9,
        fluency: 10,
        expression: 10,
        comprehension: 10,
        tone: 0,
      },
      wrong: {
        grammar: 11,
        vocabulary: 12,
        pronunciation: 7,
        fluency: 7,
        expression: 7,
        comprehension: 4,
        tone: 0,
      },
    },
    skillLabels,
  },
};

const weekThreeDayFourEvaluation: EvaluationDayData = {
  dayId: "day_24_03_04",
  activityEvaluations: [
    {
      taskId: "w3d4-read-context-mcq",
      evaluatorInput: {
        archetypeId: "READ_CONTEXT_MCQ",
        widget: "read_comp_mcq",
        taskContentRef: "tasks.source.day_24_03_04.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "1 of 1 questions correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 10 },
        },
        wrong: {
          rawScore: 0,
          percentage: 0,
          tier: "needs_work",
          attendedLabel: "0 of 1 questions correct",
          rubricScores: { comprehension: 0, accuracy: 0 },
          subSkillBreakdown: { comprehension: 0, vocabulary: 0 },
        },
      },
    },
    {
      taskId: "w3d4-listen-dictation",
      evaluatorInput: {
        archetypeId: "LISTEN_DICTATION",
        widget: "listen_dictation",
        taskContentRef: "tasks.source.day_24_03_04.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "1 of 1 dictations exact",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 10 },
        },
        wrong: {
          rawScore: 4,
          percentage: 40,
          tier: "needs_work",
          attendedLabel: "0 of 1 dictations exact",
          rubricScores: { comprehension: 5, accuracy: 3 },
          subSkillBreakdown: { comprehension: 5, vocabulary: 4 },
        },
      },
    },
    {
      taskId: "w3d4-write-paraphrase",
      evaluatorInput: {
        archetypeId: "WRITE_PARAPHRASE",
        widget: "write_paraphrase",
        taskContentRef: "tasks.source.day_24_03_04.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.5,
          percentage: 95,
          tier: "excellent",
          attendedLabel: "2 of 2 rewrites accepted",
          rubricScores: { expression: 9.5, accuracy: 9.5, vocabulary_range: 9.5 },
          subSkillBreakdown: { expression: 10, vocabulary: 9, grammar: 9 },
        },
        wrong: {
          rawScore: 7,
          percentage: 70,
          tier: "good",
          attendedLabel: "1 of 2 rewrites accepted",
          rubricScores: { expression: 7, accuracy: 7, vocabulary_range: 7 },
          subSkillBreakdown: { expression: 7, vocabulary: 7, grammar: 7 },
        },
      },
    },
    {
      taskId: "w3d4-speak-timed",
      evaluatorInput: {
        archetypeId: "SPEAK_TIMED",
        widget: "speak_timed",
        taskContentRef: "tasks.source.day_24_03_04.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.5,
          percentage: 95,
          tier: "excellent",
          attendedLabel: "Speech fluent and accurate",
          rubricScores: { fluency: 9.5, pronunciation: 9.5, grammatical_accuracy: 9.5 },
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          rawScore: 6,
          percentage: 60,
          tier: "average",
          attendedLabel: "Speech has vocabulary gaps",
          rubricScores: { fluency: 7, pronunciation: 7, grammatical_accuracy: 5 },
          subSkillBreakdown: { fluency: 7, pronunciation: 7, grammar: 5, vocabulary: 5 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_03_04",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w3d4-read-context-mcq", sequence: 1, archetypeId: "READ_CONTEXT_MCQ", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d4-listen-dictation", sequence: 2, archetypeId: "LISTEN_DICTATION", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d4-write-paraphrase", sequence: 3, archetypeId: "WRITE_PARAPHRASE", label: "Write", rawScore: 9.5, tier: "excellent", baseReward: 9 },
        { taskId: "w3d4-speak-timed", sequence: 4, archetypeId: "SPEAK_TIMED", label: "Speak", rawScore: 9.5, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w3d4-read-context-mcq", sequence: 1, archetypeId: "READ_CONTEXT_MCQ", label: "Read", rawScore: 0, tier: "needs_work", baseReward: 0 },
        { taskId: "w3d4-listen-dictation", sequence: 2, archetypeId: "LISTEN_DICTATION", label: "Listen", rawScore: 4, tier: "needs_work", baseReward: 4 },
        { taskId: "w3d4-write-paraphrase", sequence: 3, archetypeId: "WRITE_PARAPHRASE", label: "Write", rawScore: 7, tier: "good", baseReward: 7 },
        { taskId: "w3d4-speak-timed", sequence: 4, archetypeId: "SPEAK_TIMED", label: "Speak", rawScore: 6, tier: "average", baseReward: 6 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 18,
        vocabulary: 29,
        pronunciation: 9,
        fluency: 10,
        expression: 10,
        comprehension: 20,
        tone: 0,
      },
      wrong: {
        grammar: 12,
        vocabulary: 12,
        pronunciation: 7,
        fluency: 7,
        expression: 7,
        comprehension: 5,
        tone: 0,
      },
    },
    skillLabels,
  },
};

const weekThreeDayFiveEvaluation: EvaluationDayData = {
  dayId: "day_24_03_05",
  activityEvaluations: [
    {
      taskId: "w3d5-read-word-match",
      evaluatorInput: {
        archetypeId: "READ_WORD_MATCH",
        widget: "read_word_match",
        taskContentRef: "tasks.source.day_24_03_05.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "4 of 4 items matched",
          rubricScores: { vocabulary: 10, accuracy: 10 },
          subSkillBreakdown: { vocabulary: 10, grammar: 8 },
        },
        wrong: {
          rawScore: 7.5,
          percentage: 75,
          tier: "good",
          attendedLabel: "3 of 4 items matched",
          rubricScores: { vocabulary: 7.5, accuracy: 7.5 },
          subSkillBreakdown: { vocabulary: 7, grammar: 7 },
        },
      },
    },
    {
      taskId: "w3d5-listen-mcq",
      evaluatorInput: {
        archetypeId: "LISTEN_MCQ",
        widget: "listen_mcq",
        taskContentRef: "tasks.source.day_24_03_05.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 questions correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 9 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "good",
          attendedLabel: "2 of 3 questions correct",
          rubricScores: { comprehension: 6.7, accuracy: 6.7 },
          subSkillBreakdown: { comprehension: 7, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w3d5-write-sent-trans",
      evaluatorInput: {
        archetypeId: "WRITE_SENT_TRANS",
        widget: "sentence_transform",
        taskContentRef: "tasks.source.day_24_03_05.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 sentences transformed",
          rubricScores: { expression: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { expression: 10, grammar: 10, vocabulary: 9 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "good",
          attendedLabel: "2 of 3 sentences transformed",
          rubricScores: { expression: 7, grammatical_accuracy: 6.5 },
          subSkillBreakdown: { expression: 7, grammar: 6, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w3d5-speak-pic-desc",
      evaluatorInput: {
        archetypeId: "SPEAK_PIC_DESC",
        widget: "speak_pic_desc",
        taskContentRef: "tasks.source.day_24_03_05.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.3,
          percentage: 93,
          tier: "excellent",
          attendedLabel: "Planner description clear and accurate",
          rubricScores: { fluency: 9.5, pronunciation: 9, grammatical_accuracy: 9.5 },
          subSkillBreakdown: { fluency: 9, pronunciation: 9, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          rawScore: 6.5,
          percentage: 65,
          tier: "average",
          attendedLabel: "Description has time-word inaccuracies",
          rubricScores: { fluency: 8, pronunciation: 8, grammatical_accuracy: 6 },
          subSkillBreakdown: { fluency: 8, pronunciation: 8, grammar: 6, vocabulary: 5 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_03_05",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w3d5-read-word-match", sequence: 1, archetypeId: "READ_WORD_MATCH", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d5-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d5-write-sent-trans", sequence: 3, archetypeId: "WRITE_SENT_TRANS", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d5-speak-pic-desc", sequence: 4, archetypeId: "SPEAK_PIC_DESC", label: "Speak", rawScore: 9.3, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w3d5-read-word-match", sequence: 1, archetypeId: "READ_WORD_MATCH", label: "Read", rawScore: 7.5, tier: "good", baseReward: 7 },
        { taskId: "w3d5-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 6.7, tier: "good", baseReward: 6 },
        { taskId: "w3d5-write-sent-trans", sequence: 3, archetypeId: "WRITE_SENT_TRANS", label: "Write", rawScore: 6.7, tier: "good", baseReward: 6 },
        { taskId: "w3d5-speak-pic-desc", sequence: 4, archetypeId: "SPEAK_PIC_DESC", label: "Speak", rawScore: 6.5, tier: "average", baseReward: 6 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 27,
        vocabulary: 29,
        pronunciation: 9,
        fluency: 9,
        expression: 10,
        comprehension: 10,
        tone: 0,
      },
      wrong: {
        grammar: 18,
        vocabulary: 19,
        pronunciation: 8,
        fluency: 8,
        expression: 7,
        comprehension: 7,
        tone: 0,
      },
    },
    skillLabels,
  },
};

const weekThreeDaySixEvaluation: EvaluationDayData = {
  dayId: "day_24_03_06",
  activityEvaluations: [
    {
      taskId: "w3d6-read-context-mcq",
      evaluatorInput: {
        archetypeId: "READ_CONTEXT_MCQ",
        widget: "read_context_mcq",
        taskContentRef: "tasks.source.day_24_03_06.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 questions correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 10 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "good",
          attendedLabel: "2 of 3 questions correct",
          rubricScores: { comprehension: 6.7, accuracy: 6.7 },
          subSkillBreakdown: { comprehension: 7, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w3d6-listen-dictation",
      evaluatorInput: {
        archetypeId: "LISTEN_DICTATION",
        widget: "listen_dictation",
        taskContentRef: "tasks.source.day_24_03_06.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "2 of 2 dictations exact",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 10 },
        },
        wrong: {
          rawScore: 5,
          percentage: 50,
          tier: "average",
          attendedLabel: "1 of 2 dictations exact",
          rubricScores: { comprehension: 5, accuracy: 5 },
          subSkillBreakdown: { comprehension: 5, vocabulary: 5 },
        },
      },
    },
    {
      taskId: "w3d6-write-word-upgrade",
      evaluatorInput: {
        archetypeId: "WRITE_WORD_UPGRADE",
        widget: "write_word_upgrade",
        taskContentRef: "tasks.source.day_24_03_06.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 sentences upgraded",
          rubricScores: { expression: 10, accuracy: 10 },
          subSkillBreakdown: { expression: 10, vocabulary: 10, grammar: 10 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "good",
          attendedLabel: "2 of 3 sentences upgraded",
          rubricScores: { expression: 7, accuracy: 6 },
          subSkillBreakdown: { expression: 7, vocabulary: 7, grammar: 6 },
        },
      },
    },
    {
      taskId: "w3d6-speak-timed",
      evaluatorInput: {
        archetypeId: "SPEAK_TIMED",
        widget: "speak_timed",
        taskContentRef: "tasks.source.day_24_03_06.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.5,
          percentage: 95,
          tier: "excellent",
          attendedLabel: "Speech fluent and accurate",
          rubricScores: { fluency: 9.5, pronunciation: 9.5, grammatical_accuracy: 9.5 },
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          rawScore: 6,
          percentage: 60,
          tier: "average",
          attendedLabel: "Speech has vocabulary gaps",
          rubricScores: { fluency: 7, pronunciation: 7, grammatical_accuracy: 5 },
          subSkillBreakdown: { fluency: 7, pronunciation: 7, grammar: 5, vocabulary: 5 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_03_06",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w3d6-read-context-mcq", sequence: 1, archetypeId: "READ_CONTEXT_MCQ", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d6-listen-dictation", sequence: 2, archetypeId: "LISTEN_DICTATION", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d6-write-word-upgrade", sequence: 3, archetypeId: "WRITE_WORD_UPGRADE", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d6-speak-timed", sequence: 4, archetypeId: "SPEAK_TIMED", label: "Speak", rawScore: 9.5, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w3d6-read-context-mcq", sequence: 1, archetypeId: "READ_CONTEXT_MCQ", label: "Read", rawScore: 6.7, tier: "good", baseReward: 6 },
        { taskId: "w3d6-listen-dictation", sequence: 2, archetypeId: "LISTEN_DICTATION", label: "Listen", rawScore: 5, tier: "average", baseReward: 5 },
        { taskId: "w3d6-write-word-upgrade", sequence: 3, archetypeId: "WRITE_WORD_UPGRADE", label: "Write", rawScore: 6.7, tier: "good", baseReward: 6 },
        { taskId: "w3d6-speak-timed", sequence: 4, archetypeId: "SPEAK_TIMED", label: "Speak", rawScore: 6, tier: "average", baseReward: 6 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 19,
        vocabulary: 40,
        pronunciation: 9,
        fluency: 10,
        expression: 10,
        comprehension: 20,
        tone: 0,
      },
      wrong: {
        grammar: 11,
        vocabulary: 23,
        pronunciation: 7,
        fluency: 7,
        expression: 7,
        comprehension: 12,
        tone: 0,
      },
    },
    skillLabels,
  },
};


const weekThreeDayThreeEvaluation: EvaluationDayData = {
  dayId: "day_24_03_03",
  activityEvaluations: [
    {
      taskId: "w3d3-read-word-match",
      evaluatorInput: {
        archetypeId: "READ_WORD_MATCH",
        widget: "read_word_match",
        taskContentRef: "tasks.source.day_24_03_03.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "4 of 4 items matched",
          rubricScores: { vocabulary: 10, accuracy: 10 },
          subSkillBreakdown: { vocabulary: 10, grammar: 8 },
        },
        wrong: {
          rawScore: 7.5,
          percentage: 75,
          tier: "good",
          attendedLabel: "3 of 4 items matched",
          rubricScores: { vocabulary: 7.5, accuracy: 7.5 },
          subSkillBreakdown: { vocabulary: 7, grammar: 7 },
        },
      },
    },
    {
      taskId: "w3d3-listen-mcq",
      evaluatorInput: {
        archetypeId: "LISTEN_MCQ",
        widget: "listen_mcq",
        taskContentRef: "tasks.source.day_24_03_03.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 questions correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 8 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "good",
          attendedLabel: "2 of 3 questions correct",
          rubricScores: { comprehension: 6.7, accuracy: 6.7 },
          subSkillBreakdown: { comprehension: 7, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w3d3-write-para",
      evaluatorInput: {
        archetypeId: "WRITE_PARA",
        widget: "write_paragraph",
        taskContentRef: "tasks.source.day_24_03_03.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Paragraph clear and accurate",
          rubricScores: { expression: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { expression: 10, grammar: 10, vocabulary: 8 },
        },
        wrong: {
          rawScore: 6,
          percentage: 60,
          tier: "average",
          attendedLabel: "Paragraph has grammar slips",
          rubricScores: { expression: 7, grammatical_accuracy: 5 },
          subSkillBreakdown: { expression: 7, grammar: 5, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w3d3-speak-pic-desc",
      evaluatorInput: {
        archetypeId: "SPEAK_PIC_DESC",
        widget: "speak_pic_desc",
        taskContentRef: "tasks.source.day_24_03_03.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.5,
          percentage: 95,
          tier: "excellent",
          attendedLabel: "Description clear and fluent",
          rubricScores: { fluency: 9.5, pronunciation: 9.5, grammatical_accuracy: 9.5 },
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          rawScore: 6,
          percentage: 60,
          tier: "average",
          attendedLabel: "Description missing some words",
          rubricScores: { fluency: 8, pronunciation: 8, grammatical_accuracy: 6 },
          subSkillBreakdown: { fluency: 8, pronunciation: 8, grammar: 6, vocabulary: 5 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_03_03",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w3d3-read-word-match", sequence: 1, archetypeId: "READ_WORD_MATCH", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d3-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d3-write-para", sequence: 3, archetypeId: "WRITE_PARA", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d3-speak-pic-desc", sequence: 4, archetypeId: "SPEAK_PIC_DESC", label: "Speak", rawScore: 9.5, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w3d3-read-word-match", sequence: 1, archetypeId: "READ_WORD_MATCH", label: "Read", rawScore: 7.5, tier: "good", baseReward: 7 },
        { taskId: "w3d3-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 6.7, tier: "good", baseReward: 6 },
        { taskId: "w3d3-write-para", sequence: 3, archetypeId: "WRITE_PARA", label: "Write", rawScore: 6, tier: "average", baseReward: 6 },
        { taskId: "w3d3-speak-pic-desc", sequence: 4, archetypeId: "SPEAK_PIC_DESC", label: "Speak", rawScore: 6, tier: "average", baseReward: 6 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 27,
        vocabulary: 28,
        pronunciation: 9,
        fluency: 10,
        expression: 10,
        comprehension: 10,
        tone: 0,
      },
      wrong: {
        grammar: 17,
        vocabulary: 18,
        pronunciation: 8,
        fluency: 8,
        expression: 6,
        comprehension: 7,
        tone: 0,
      },
    },
    skillLabels,
  },
};

const weekThreeDaySevenEvaluation: EvaluationDayData = {
  dayId: "day_24_03_07",
  activityEvaluations: [
    {
      taskId: "w3d7-read-word-match",
      evaluatorInput: {
        archetypeId: "READ_WORD_MATCH",
        widget: "read_word_match",
        taskContentRef: "tasks.source.day_24_03_07.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "6 of 6 items matched",
          rubricScores: { vocabulary: 10, accuracy: 10 },
          subSkillBreakdown: { vocabulary: 10, grammar: 8 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "average",
          attendedLabel: "4 of 6 items matched",
          rubricScores: { vocabulary: 6.5, accuracy: 6.5 },
          subSkillBreakdown: { vocabulary: 6, grammar: 6 },
        },
      },
    },
    {
      taskId: "w3d7-listen-mcq",
      evaluatorInput: {
        archetypeId: "LISTEN_MCQ",
        widget: "listen_mcq",
        taskContentRef: "tasks.source.day_24_03_07.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 questions correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 8 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "good",
          attendedLabel: "2 of 3 questions correct",
          rubricScores: { comprehension: 6.7, accuracy: 6.7 },
          subSkillBreakdown: { comprehension: 7, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w3d7-write-para",
      evaluatorInput: {
        archetypeId: "WRITE_PARA",
        widget: "write_paragraph",
        taskContentRef: "tasks.source.day_24_03_07.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Paragraph clear and accurate",
          rubricScores: { expression: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { expression: 10, grammar: 10, vocabulary: 8 },
        },
        wrong: {
          rawScore: 6,
          percentage: 60,
          tier: "average",
          attendedLabel: "Paragraph has grammar slips",
          rubricScores: { expression: 7, grammatical_accuracy: 5 },
          subSkillBreakdown: { expression: 7, grammar: 5, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w3d7-speak-timed",
      evaluatorInput: {
        archetypeId: "SPEAK_TIMED",
        widget: "speak_timed",
        taskContentRef: "tasks.source.day_24_03_07.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.5,
          percentage: 95,
          tier: "excellent",
          attendedLabel: "Description clear and fluent",
          rubricScores: { fluency: 9.5, pronunciation: 9.5, grammatical_accuracy: 9.5 },
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          rawScore: 6,
          percentage: 60,
          tier: "average",
          attendedLabel: "Description missing some words",
          rubricScores: { fluency: 8, pronunciation: 8, grammatical_accuracy: 6 },
          subSkillBreakdown: { fluency: 8, pronunciation: 8, grammar: 6, vocabulary: 5 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_03_07",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w3d7-read-word-match", sequence: 1, archetypeId: "READ_WORD_MATCH", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d7-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d7-write-para", sequence: 3, archetypeId: "WRITE_PARA", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w3d7-speak-timed", sequence: 4, archetypeId: "SPEAK_TIMED", label: "Speak", rawScore: 9.5, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w3d7-read-word-match", sequence: 1, archetypeId: "READ_WORD_MATCH", label: "Read", rawScore: 6.7, tier: "average", baseReward: 6 },
        { taskId: "w3d7-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 6.7, tier: "good", baseReward: 6 },
        { taskId: "w3d7-write-para", sequence: 3, archetypeId: "WRITE_PARA", label: "Write", rawScore: 6, tier: "average", baseReward: 6 },
        { taskId: "w3d7-speak-timed", sequence: 4, archetypeId: "SPEAK_TIMED", label: "Speak", rawScore: 6, tier: "average", baseReward: 6 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 27,
        vocabulary: 28,
        pronunciation: 9,
        fluency: 10,
        expression: 10,
        comprehension: 10,
        tone: 0,
      },
      wrong: {
        grammar: 17,
        vocabulary: 18,
        pronunciation: 8,
        fluency: 8,
        expression: 6,
        comprehension: 7,
        tone: 0,
      },
    },
    skillLabels,
  },
};

const weekFourDayOneEvaluation: EvaluationDayData = {
  dayId: "day_24_04_01",
  activityEvaluations: [
    {
      taskId: "w4d1-read-mcq",
      evaluatorInput: {
        archetypeId: "READ_COMP_MCQ",
        widget: "read_comp_mcq",
        taskContentRef: "tasks.source.day_24_04_01.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "4 of 4 questions correct",
          rubricScores: { accuracy: 10, comprehension: 10 },
          subSkillBreakdown: { comprehension: 10, grammar: 9 },
        },
        wrong: {
          rawScore: 7.5,
          percentage: 75,
          tier: "good",
          attendedLabel: "3 of 4 questions correct",
          rubricScores: { accuracy: 7.5, comprehension: 7.5 },
          subSkillBreakdown: { comprehension: 8, grammar: 7 },
        },
      },
    },
    {
      taskId: "w4d1-listen-shadow",
      evaluatorInput: {
        archetypeId: "LISTEN_SHADOW",
        widget: "listen_shadow",
        taskContentRef: "tasks.source.day_24_04_01.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Shadowing exact and fluent",
          rubricScores: { comprehension: 10, fluency: 10 },
          subSkillBreakdown: { comprehension: 10, fluency: 10, pronunciation: 9 },
        },
        wrong: {
          rawScore: 6.0,
          percentage: 60,
          tier: "average",
          attendedLabel: "Shadowing has omissions/slips",
          rubricScores: { comprehension: 6, fluency: 6 },
          subSkillBreakdown: { comprehension: 6, fluency: 6, pronunciation: 6 },
        },
      },
    },
    {
      taskId: "w4d1-write-transform",
      evaluatorInput: {
        archetypeId: "WRITE_SENT_TRANS",
        widget: "sentence_transform",
        taskContentRef: "tasks.source.day_24_04_01.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 sentences transformed",
          rubricScores: { grammatical_accuracy: 10, expression: 10 },
          subSkillBreakdown: { grammar: 10, expression: 10, vocabulary: 9 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "good",
          attendedLabel: "2 of 3 sentences transformed",
          rubricScores: { grammatical_accuracy: 6.7, expression: 6.7 },
          subSkillBreakdown: { grammar: 7, expression: 6, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w4d1-speak-aloud",
      evaluatorInput: {
        archetypeId: "SPEAK_READ_ALOUD",
        widget: "read_aloud",
        taskContentRef: "tasks.source.day_24_04_01.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.4,
          percentage: 94,
          tier: "excellent",
          attendedLabel: "Read-aloud clear and expressive",
          rubricScores: { pronunciation: 9.5, fluency: 9.2, grammatical_accuracy: 9.5 },
          subSkillBreakdown: { pronunciation: 10, fluency: 9, grammar: 9 },
          pronunciationAssessment: {
            overallScore: 94,
            accuracyScore: 95,
            fluencyScore: 92,
            completenessScore: 98,
            prosodyScore: 91,
            words: [
              { word: "My", accuracyScore: 95, errorType: "none", phonemes: [{ phoneme: "m", accuracyScore: 95 }, { phoneme: "aɪ", accuracyScore: 95 }] },
              { word: "voice", accuracyScore: 96, errorType: "none", phonemes: [{ phoneme: "v", accuracyScore: 96 }, { phoneme: "ɔɪs", accuracyScore: 96 }] },
              { word: "has", accuracyScore: 94, errorType: "none", phonemes: [{ phoneme: "h", accuracyScore: 94 }, { phoneme: "æz", accuracyScore: 94 }] },
              { word: "value", accuracyScore: 95, errorType: "none", phonemes: [{ phoneme: "v", accuracyScore: 95 }, { phoneme: "æljuː", accuracyScore: 95 }] },
              { word: "Every", accuracyScore: 93, errorType: "none", phonemes: [{ phoneme: "e", accuracyScore: 93 }, { phoneme: "vri", accuracyScore: 93 }] },
              { word: "time", accuracyScore: 96, errorType: "none", phonemes: [{ phoneme: "t", accuracyScore: 96 }, { phoneme: "aɪm", accuracyScore: 96 }] },
              { word: "I", accuracyScore: 97, errorType: "none", phonemes: [{ phoneme: "aɪ", accuracyScore: 97 }] },
              { word: "practice", accuracyScore: 94, errorType: "none", phonemes: [{ phoneme: "p", accuracyScore: 94 }, { phoneme: "æktɪs", accuracyScore: 94 }] },
              { word: "I", accuracyScore: 97, errorType: "none", phonemes: [{ phoneme: "aɪ", accuracyScore: 97 }] },
              { word: "build", accuracyScore: 95, errorType: "none", phonemes: [{ phoneme: "b", accuracyScore: 95 }, { phoneme: "ɪld", accuracyScore: 95 }] },
              { word: "my", accuracyScore: 96, errorType: "none", phonemes: [{ phoneme: "m", accuracyScore: 96 }, { phoneme: "aɪ", accuracyScore: 96 }] },
              { word: "confidence", accuracyScore: 92, errorType: "none", phonemes: [{ phoneme: "k", accuracyScore: 92 }, { phoneme: "ɒnfɪdəns", accuracyScore: 92 }] },
              { word: "I", accuracyScore: 97, errorType: "none", phonemes: [{ phoneme: "aɪ", accuracyScore: 97 }] },
              { word: "do", accuracyScore: 95, errorType: "none", phonemes: [{ phoneme: "d", accuracyScore: 95 }, { phoneme: "uː", accuracyScore: 95 }] },
              { word: "not", accuracyScore: 96, errorType: "none", phonemes: [{ phoneme: "n", accuracyScore: 96 }, { phoneme: "ɒt", accuracyScore: 96 }] },
              { word: "need", accuracyScore: 95, errorType: "none", phonemes: [{ phoneme: "n", accuracyScore: 95 }, { phoneme: "iːd", accuracyScore: 95 }] },
              { word: "to", accuracyScore: 96, errorType: "none", phonemes: [{ phoneme: "t", accuracyScore: 96 }, { phoneme: "uː", accuracyScore: 96 }] },
              { word: "be", accuracyScore: 95, errorType: "none", phonemes: [{ phoneme: "b", accuracyScore: 95 }, { phoneme: "iː", accuracyScore: 95 }] },
              { word: "perfect", accuracyScore: 93, errorType: "none", phonemes: [{ phoneme: "p", accuracyScore: 93 }, { phoneme: "ɜːfɪkt", accuracyScore: 93 }] },
              { word: "to", accuracyScore: 96, errorType: "none", phonemes: [{ phoneme: "t", accuracyScore: 96 }, { phoneme: "uː", accuracyScore: 96 }] },
              { word: "start", accuracyScore: 94, errorType: "none", phonemes: [{ phoneme: "s", accuracyScore: 94 }, { phoneme: "tɑːt", accuracyScore: 94 }] },
              { word: "I", accuracyScore: 97, errorType: "none", phonemes: [{ phoneme: "aɪ", accuracyScore: 97 }] },
              { word: "just", accuracyScore: 94, errorType: "none", phonemes: [{ phoneme: "dʒ", accuracyScore: 94 }, { phoneme: "ʌst", accuracyScore: 94 }] },
              { word: "need", accuracyScore: 95, errorType: "none", phonemes: [{ phoneme: "n", accuracyScore: 95 }, { phoneme: "iːd", accuracyScore: 95 }] },
              { word: "to", accuracyScore: 96, errorType: "none", phonemes: [{ phoneme: "t", accuracyScore: 96 }, { phoneme: "uː", accuracyScore: 96 }] },
              { word: "speak", accuracyScore: 95, errorType: "none", phonemes: [{ phoneme: "s", accuracyScore: 95 }, { phoneme: "piːk", accuracyScore: 95 }] },
              { word: "up", accuracyScore: 96, errorType: "none", phonemes: [{ phoneme: "ʌ", accuracyScore: 96 }, { phoneme: "p", accuracyScore: 96 }] },
            ],
          },
        },
        wrong: {
          rawScore: 7.0,
          percentage: 70,
          tier: "good",
          attendedLabel: "Read-aloud has some hesitation/mispronunciation",
          rubricScores: { pronunciation: 7.0, fluency: 7.2, grammatical_accuracy: 6.5 },
          subSkillBreakdown: { pronunciation: 7, fluency: 7, grammar: 6 },
          pronunciationAssessment: {
            overallScore: 70,
            accuracyScore: 68,
            fluencyScore: 75,
            completenessScore: 80,
            prosodyScore: 64,
            words: [
              { word: "My", accuracyScore: 90, errorType: "none", phonemes: [{ phoneme: "m", accuracyScore: 90 }, { phoneme: "aɪ", accuracyScore: 90 }] },
              { word: "voice", accuracyScore: 88, errorType: "none", phonemes: [{ phoneme: "v", accuracyScore: 88 }, { phoneme: "ɔɪs", accuracyScore: 88 }] },
              { word: "has", accuracyScore: 85, errorType: "none", phonemes: [{ phoneme: "h", accuracyScore: 85 }, { phoneme: "æz", accuracyScore: 85 }] },
              { word: "value", accuracyScore: 42, errorType: "mispronunciation", phonemes: [{ phoneme: "v", accuracyScore: 42 }, { phoneme: "æljuː", accuracyScore: 42 }] },
              { word: "Every", accuracyScore: 91, errorType: "none", phonemes: [{ phoneme: "e", accuracyScore: 91 }, { phoneme: "vri", accuracyScore: 91 }] },
              { word: "time", accuracyScore: 89, errorType: "none", phonemes: [{ phoneme: "t", accuracyScore: 89 }, { phoneme: "aɪm", accuracyScore: 89 }] },
              { word: "I", accuracyScore: 92, errorType: "none", phonemes: [{ phoneme: "aɪ", accuracyScore: 92 }] },
              { word: "practice", accuracyScore: 91, errorType: "none", phonemes: [{ phoneme: "p", accuracyScore: 91 }, { phoneme: "æktɪs", accuracyScore: 91 }] },
              { word: "I", accuracyScore: 92, errorType: "none", phonemes: [{ phoneme: "aɪ", accuracyScore: 92 }] },
              { word: "build", accuracyScore: 35, errorType: "mispronunciation", phonemes: [{ phoneme: "b", accuracyScore: 35 }, { phoneme: "ɪld", accuracyScore: 35 }] },
              { word: "my", accuracyScore: 91, errorType: "none", phonemes: [{ phoneme: "m", accuracyScore: 91 }, { phoneme: "aɪ", accuracyScore: 91 }] },
              { word: "confidence", accuracyScore: 45, errorType: "mispronunciation", phonemes: [{ phoneme: "k", accuracyScore: 45 }, { phoneme: "ɒnfɪdəns", accuracyScore: 45 }] },
              { word: "I", accuracyScore: 92, errorType: "none", phonemes: [{ phoneme: "aɪ", accuracyScore: 92 }] },
              { word: "do", accuracyScore: 90, errorType: "none", phonemes: [{ phoneme: "d", accuracyScore: 90 }, { phoneme: "uː", accuracyScore: 90 }] },
              { word: "not", accuracyScore: 91, errorType: "none", phonemes: [{ phoneme: "n", accuracyScore: 91 }, { phoneme: "ɒt", accuracyScore: 91 }] },
              { word: "need", accuracyScore: 88, errorType: "none", phonemes: [{ phoneme: "n", accuracyScore: 88 }, { phoneme: "iːd", accuracyScore: 88 }] },
              { word: "to", accuracyScore: 90, errorType: "none", phonemes: [{ phoneme: "t", accuracyScore: 90 }, { phoneme: "uː", accuracyScore: 90 }] },
              { word: "be", accuracyScore: 91, errorType: "none", phonemes: [{ phoneme: "b", accuracyScore: 91 }, { phoneme: "iː", accuracyScore: 91 }] },
              { word: "perfect", accuracyScore: 41, errorType: "mispronunciation", phonemes: [{ phoneme: "p", accuracyScore: 41 }, { phoneme: "ɜːfɪkt", accuracyScore: 41 }] },
              { word: "to", accuracyScore: 90, errorType: "none", phonemes: [{ phoneme: "t", accuracyScore: 90 }, { phoneme: "uː", accuracyScore: 90 }] },
              { word: "start", accuracyScore: 88, errorType: "none", phonemes: [{ phoneme: "s", accuracyScore: 88 }, { phoneme: "tɑːt", accuracyScore: 88 }] },
              { word: "I", accuracyScore: 92, errorType: "none", phonemes: [{ phoneme: "aɪ", accuracyScore: 92 }] },
              { word: "just", accuracyScore: 89, errorType: "none", phonemes: [{ phoneme: "dʒ", accuracyScore: 89 }, { phoneme: "ʌst", accuracyScore: 89 }] },
              { word: "need", accuracyScore: 90, errorType: "none", phonemes: [{ phoneme: "n", accuracyScore: 90 }, { phoneme: "iːd", accuracyScore: 90 }] },
              { word: "to", accuracyScore: 91, errorType: "none", phonemes: [{ phoneme: "t", accuracyScore: 91 }, { phoneme: "uː", accuracyScore: 91 }] },
              { word: "speak", accuracyScore: 88, errorType: "none", phonemes: [{ phoneme: "s", accuracyScore: 88 }, { phoneme: "piːk", accuracyScore: 88 }] },
              { word: "up", accuracyScore: 89, errorType: "none", phonemes: [{ phoneme: "ʌ", accuracyScore: 89 }, { phoneme: "p", accuracyScore: 89 }] },
            ],
          },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_04_01",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w4d1-read-mcq", sequence: 1, archetypeId: "READ_COMP_MCQ", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d1-listen-shadow", sequence: 2, archetypeId: "LISTEN_SHADOW", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d1-write-transform", sequence: 3, archetypeId: "WRITE_SENT_TRANS", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d1-speak-aloud", sequence: 4, archetypeId: "SPEAK_READ_ALOUD", label: "Speak", rawScore: 9.4, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w4d1-read-mcq", sequence: 1, archetypeId: "READ_COMP_MCQ", label: "Read", rawScore: 7.5, tier: "good", baseReward: 7 },
        { taskId: "w4d1-listen-shadow", sequence: 2, archetypeId: "LISTEN_SHADOW", label: "Listen", rawScore: 6.0, tier: "average", baseReward: 6 },
        { taskId: "w4d1-write-transform", sequence: 3, archetypeId: "WRITE_SENT_TRANS", label: "Write", rawScore: 6.7, tier: "good", baseReward: 6 },
        { taskId: "w4d1-speak-aloud", sequence: 4, archetypeId: "SPEAK_READ_ALOUD", label: "Speak", rawScore: 7.0, tier: "good", baseReward: 7 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 19,
        vocabulary: 9,
        pronunciation: 10,
        fluency: 9,
        expression: 10,
        comprehension: 20,
        tone: 0,
      },
      wrong: {
        grammar: 13,
        vocabulary: 6,
        pronunciation: 7,
        fluency: 7,
        expression: 6,
        comprehension: 14,
        tone: 0,
      },
    },
    skillLabels,
  },
};

const weekFourDayTwoEvaluation: EvaluationDayData = {
  dayId: "day_24_04_02",
  activityEvaluations: [
    {
      taskId: "w4d2-read-tone-id",
      evaluatorInput: {
        archetypeId: "READ_TONE_ID",
        widget: "read_tone_id",
        taskContentRef: "tasks.source.day_24_04_02.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "2 of 2 tones identified",
          rubricScores: { vocabulary: 10, tone: 10 },
          subSkillBreakdown: { vocabulary: 10, grammar: 8 },
        },
        wrong: {
          rawScore: 5,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "1 of 2 tones identified",
          rubricScores: { vocabulary: 5, tone: 5 },
          subSkillBreakdown: { vocabulary: 5, grammar: 5 },
        },
      },
    },
    {
      taskId: "w4d2-listen-mcq",
      evaluatorInput: {
        archetypeId: "LISTEN_MCQ",
        widget: "listen_mcq",
        taskContentRef: "tasks.source.day_24_04_02.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "1 of 1 questions correct",
          rubricScores: { comprehension: 10, accuracy: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 8 },
        },
        wrong: {
          rawScore: 0,
          percentage: 0,
          tier: "needs_work",
          attendedLabel: "0 of 1 questions correct",
          rubricScores: { comprehension: 0, accuracy: 0 },
          subSkillBreakdown: { comprehension: 0, vocabulary: 0 },
        },
      },
    },
    {
      taskId: "w4d2-write-timed",
      evaluatorInput: {
        archetypeId: "WRITE_TIMED",
        widget: "write_timed",
        taskContentRef: "tasks.source.day_24_04_02.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Timed paragraph clear and accurate",
          rubricScores: { expression: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { expression: 10, grammar: 10, vocabulary: 8 },
        },
        wrong: {
          rawScore: 5,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "Timed paragraph has grammar/filler slips",
          rubricScores: { expression: 5, grammatical_accuracy: 5 },
          subSkillBreakdown: { expression: 5, grammar: 5, vocabulary: 5 },
        },
      },
    },
    {
      taskId: "w4d2-speak-timed",
      evaluatorInput: {
        archetypeId: "SPEAK_TIMED",
        widget: "speak_timed",
        taskContentRef: "tasks.source.day_24_04_02.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.5,
          percentage: 95,
          tier: "excellent",
          attendedLabel: "Description clear and fluent",
          rubricScores: { fluency: 9.5, pronunciation: 9.5, grammatical_accuracy: 9.5 },
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          rawScore: 6.0,
          percentage: 60,
          tier: "average",
          attendedLabel: "Description lacks confident tone",
          rubricScores: { fluency: 6.0, pronunciation: 6.0, grammatical_accuracy: 6.0 },
          subSkillBreakdown: { fluency: 6, pronunciation: 6, grammar: 6, vocabulary: 6 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_04_02",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w4d2-read-tone-id", sequence: 1, archetypeId: "READ_TONE_ID", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d2-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d2-write-timed", sequence: 3, archetypeId: "WRITE_TIMED", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d2-speak-timed", sequence: 4, archetypeId: "SPEAK_TIMED", label: "Speak", rawScore: 9.5, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w4d2-read-tone-id", sequence: 1, archetypeId: "READ_TONE_ID", label: "Read", rawScore: 5, tier: "needs_work", baseReward: 5 },
        { taskId: "w4d2-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 0, tier: "needs_work", baseReward: 0 },
        { taskId: "w4d2-write-timed", sequence: 3, archetypeId: "WRITE_TIMED", label: "Write", rawScore: 5, tier: "needs_work", baseReward: 5 },
        { taskId: "w4d2-speak-timed", sequence: 4, archetypeId: "SPEAK_TIMED", label: "Speak", rawScore: 6, tier: "average", baseReward: 6 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 27,
        vocabulary: 26,
        pronunciation: 9,
        fluency: 10,
        expression: 10,
        comprehension: 10,
        tone: 10,
      },
      wrong: {
        grammar: 16,
        vocabulary: 16,
        pronunciation: 6,
        fluency: 6,
        expression: 5,
        comprehension: 0,
        tone: 5,
      },
    },
    skillLabels,
  },
};

const weekFourDayThreeEvaluation: EvaluationDayData = {
  dayId: "day_24_04_03",
  activityEvaluations: [
    {
      taskId: "w4d3-read-mcq",
      evaluatorInput: {
        archetypeId: "READ_COMP_MCQ",
        widget: "read_comp_mcq",
        taskContentRef: "tasks.source.day_24_04_03.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "4 of 4 questions correct",
          rubricScores: { accuracy: 10, comprehension: 10 },
          subSkillBreakdown: { comprehension: 10, grammar: 9 },
        },
        wrong: {
          rawScore: 7.5,
          percentage: 75,
          tier: "good",
          attendedLabel: "3 of 4 questions correct",
          rubricScores: { accuracy: 7.5, comprehension: 7.5 },
          subSkillBreakdown: { comprehension: 8, grammar: 7 },
        },
      },
    },
    {
      taskId: "w4d3-listen-tone",
      evaluatorInput: {
        archetypeId: "LISTEN_TONE",
        widget: "listen_tone",
        taskContentRef: "tasks.source.day_24_04_03.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "2 of 2 tones identified",
          rubricScores: { accuracy: 10, comprehension: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 9 },
        },
        wrong: {
          rawScore: 5.0,
          percentage: 50,
          tier: "average",
          attendedLabel: "1 of 2 tones identified",
          rubricScores: { accuracy: 5.0, comprehension: 5.0 },
          subSkillBreakdown: { comprehension: 5, vocabulary: 5 },
        },
      },
    },
    {
      taskId: "w4d3-write-transform",
      evaluatorInput: {
        archetypeId: "WRITE_SENT_TRANS",
        widget: "sentence_transform",
        taskContentRef: "tasks.source.day_24_04_03.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 sentences transformed",
          rubricScores: { grammatical_accuracy: 10, expression: 10 },
          subSkillBreakdown: { grammar: 10, expression: 10, vocabulary: 9 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "good",
          attendedLabel: "2 of 3 sentences transformed",
          rubricScores: { grammatical_accuracy: 6.7, expression: 6.7 },
          subSkillBreakdown: { grammar: 7, expression: 6, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w4d3-speak-pic-desc",
      evaluatorInput: {
        archetypeId: "SPEAK_PIC_DESC",
        widget: "speak_pic_desc",
        taskContentRef: "tasks.source.day_24_04_03.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.6,
          percentage: 96,
          tier: "excellent",
          attendedLabel: "Description highly fluent and descriptive",
          rubricScores: { fluency: 9.5, pronunciation: 9.6, grammatical_accuracy: 9.5 },
          subSkillBreakdown: { fluency: 10, pronunciation: 9.6, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          rawScore: 6.0,
          percentage: 60,
          tier: "average",
          attendedLabel: "Description missing key details",
          rubricScores: { fluency: 6.0, pronunciation: 6.0, grammatical_accuracy: 6.0 },
          subSkillBreakdown: { fluency: 6, pronunciation: 6, grammar: 6, vocabulary: 5 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_04_03",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w4d3-read-mcq", sequence: 1, archetypeId: "READ_COMP_MCQ", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d3-listen-tone", sequence: 2, archetypeId: "LISTEN_TONE", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d3-write-transform", sequence: 3, archetypeId: "WRITE_SENT_TRANS", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d3-speak-pic-desc", sequence: 4, archetypeId: "SPEAK_PIC_DESC", label: "Speak", rawScore: 9.6, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w4d3-read-mcq", sequence: 1, archetypeId: "READ_COMP_MCQ", label: "Read", rawScore: 7.5, tier: "good", baseReward: 7 },
        { taskId: "w4d3-listen-tone", sequence: 2, archetypeId: "LISTEN_TONE", label: "Listen", rawScore: 5, tier: "average", baseReward: 5 },
        { taskId: "w4d3-write-transform", sequence: 3, archetypeId: "WRITE_SENT_TRANS", label: "Write", rawScore: 6.7, tier: "good", baseReward: 6 },
        { taskId: "w4d3-speak-pic-desc", sequence: 4, archetypeId: "SPEAK_PIC_DESC", label: "Speak", rawScore: 6, tier: "average", baseReward: 6 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 19,
        vocabulary: 19,
        pronunciation: 9.6,
        fluency: 10,
        expression: 10,
        comprehension: 20,
        tone: 10,
      },
      wrong: {
        grammar: 13,
        vocabulary: 11,
        pronunciation: 6,
        fluency: 6,
        expression: 6,
        comprehension: 13,
        tone: 5,
      },
    },
    skillLabels,
  },
};

const weekFourDayFourEvaluation: EvaluationDayData = {
  dayId: "day_24_04_04",
  activityEvaluations: [
    {
      taskId: "w4d4-read-tone-id",
      evaluatorInput: {
        archetypeId: "READ_TONE_ID",
        widget: "read_tone_id",
        taskContentRef: "tasks.source.day_24_04_04.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "2 of 2 tones identified",
          rubricScores: { accuracy: 10, comprehension: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 10 },
        },
        wrong: {
          rawScore: 5.0,
          percentage: 50,
          tier: "average",
          attendedLabel: "1 of 2 tones identified",
          rubricScores: { accuracy: 5.0, comprehension: 5.0 },
          subSkillBreakdown: { comprehension: 5, vocabulary: 5 },
        },
      },
    },
    {
      taskId: "w4d4-listen-shadow",
      evaluatorInput: {
        archetypeId: "LISTEN_SHADOW",
        widget: "listen_shadow",
        taskContentRef: "tasks.source.day_24_04_04.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Shadowing exactly clear",
          rubricScores: { pronunciation: 10, fluency: 10 },
          subSkillBreakdown: { pronunciation: 10, fluency: 10 },
        },
        wrong: {
          rawScore: 5.0,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "Shadowing has errors",
          rubricScores: { pronunciation: 5.0, fluency: 5.0 },
          subSkillBreakdown: { pronunciation: 5, fluency: 5 },
        },
      },
    },
    {
      taskId: "w4d4-write-timed",
      evaluatorInput: {
        archetypeId: "WRITE_TIMED",
        widget: "write_timed",
        taskContentRef: "tasks.source.day_24_04_04.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Timed paragraph clear and accurate",
          rubricScores: { expression: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { expression: 10, grammar: 10, vocabulary: 10 },
        },
        wrong: {
          rawScore: 5,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "Timed paragraph has grammar/filler slips",
          rubricScores: { expression: 5, grammatical_accuracy: 5 },
          subSkillBreakdown: { expression: 5, grammar: 5, vocabulary: 5 },
        },
      },
    },
    {
      taskId: "w4d4-speak-smalltalk",
      evaluatorInput: {
        archetypeId: "SPEAK_SMALLTALK",
        widget: "speak_smalltalk",
        taskContentRef: "tasks.source.day_24_04_04.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Small talk responses highly natural",
          rubricScores: { fluency: 10, pronunciation: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { fluency: 10, pronunciation: 10, grammar: 10 },
        },
        wrong: {
          rawScore: 5.0,
          percentage: 50,
          tier: "average",
          attendedLabel: "Small talk had grammar errors",
          rubricScores: { fluency: 5.0, pronunciation: 5.0, grammatical_accuracy: 5.0 },
          subSkillBreakdown: { fluency: 5, pronunciation: 5, grammar: 5 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_04_04",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w4d4-read-tone-id", sequence: 1, archetypeId: "READ_TONE_ID", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d4-listen-shadow", sequence: 2, archetypeId: "LISTEN_SHADOW", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d4-write-timed", sequence: 3, archetypeId: "WRITE_TIMED", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d4-speak-smalltalk", sequence: 4, archetypeId: "SPEAK_SMALLTALK", label: "Speak", rawScore: 10, tier: "excellent", baseReward: 10 },
      ],
      wrong: [
        { taskId: "w4d4-read-tone-id", sequence: 1, archetypeId: "READ_TONE_ID", label: "Read", rawScore: 5, tier: "average", baseReward: 5 },
        { taskId: "w4d4-listen-shadow", sequence: 2, archetypeId: "LISTEN_SHADOW", label: "Listen", rawScore: 5, tier: "needs_work", baseReward: 5 },
        { taskId: "w4d4-write-timed", sequence: 3, archetypeId: "WRITE_TIMED", label: "Write", rawScore: 5, tier: "needs_work", baseReward: 5 },
        { taskId: "w4d4-speak-smalltalk", sequence: 4, archetypeId: "SPEAK_SMALLTALK", label: "Speak", rawScore: 5, tier: "average", baseReward: 5 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 20,
        vocabulary: 20,
        pronunciation: 20,
        fluency: 20,
        expression: 10,
        comprehension: 20,
        tone: 10,
      },
      wrong: {
        grammar: 10,
        vocabulary: 10,
        pronunciation: 10,
        fluency: 10,
        expression: 5,
        comprehension: 10,
        tone: 5,
      },
    },
    skillLabels,
  },
};

const weekFourDayFiveEvaluation: EvaluationDayData = {
  dayId: "day_24_04_05",
  activityEvaluations: [
    {
      taskId: "w4d5-read-mcq",
      evaluatorInput: {
        archetypeId: "READ_COMP_MCQ",
        widget: "read_comp_mcq",
        taskContentRef: "tasks.source.day_24_04_05.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "4 of 4 questions correct",
          rubricScores: { accuracy: 10, comprehension: 10 },
          subSkillBreakdown: { comprehension: 10, grammar: 9 },
        },
        wrong: {
          rawScore: 7.5,
          percentage: 75,
          tier: "good",
          attendedLabel: "3 of 4 questions correct",
          rubricScores: { accuracy: 7.5, comprehension: 7.5 },
          subSkillBreakdown: { comprehension: 8, grammar: 7 },
        },
      },
    },
    {
      taskId: "w4d5-listen-mcq",
      evaluatorInput: {
        archetypeId: "LISTEN_MCQ",
        widget: "listen_mcq",
        taskContentRef: "tasks.source.day_24_04_05.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 questions correct",
          rubricScores: { accuracy: 10, comprehension: 10 },
          subSkillBreakdown: { comprehension: 10, vocabulary: 9 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "good",
          attendedLabel: "2 of 3 questions correct",
          rubricScores: { accuracy: 6.7, comprehension: 6.7 },
          subSkillBreakdown: { comprehension: 7, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w4d5-write-transform",
      evaluatorInput: {
        archetypeId: "WRITE_SENT_TRANS",
        widget: "sentence_transform",
        taskContentRef: "tasks.source.day_24_04_05.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "3 of 3 sentences transformed",
          rubricScores: { grammatical_accuracy: 10, expression: 10 },
          subSkillBreakdown: { grammar: 10, expression: 10, vocabulary: 9 },
        },
        wrong: {
          rawScore: 6.7,
          percentage: 67,
          tier: "good",
          attendedLabel: "2 of 3 sentences transformed",
          rubricScores: { grammatical_accuracy: 6.7, expression: 6.7 },
          subSkillBreakdown: { grammar: 7, expression: 6, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w4d5-speak-pic-desc",
      evaluatorInput: {
        archetypeId: "SPEAK_PIC_DESC",
        widget: "speak_pic_desc",
        taskContentRef: "tasks.source.day_24_04_05.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.5,
          percentage: 95,
          tier: "excellent",
          attendedLabel: "Description highly fluent and descriptive",
          rubricScores: { fluency: 9.5, pronunciation: 9.5, grammatical_accuracy: 9.5 },
          subSkillBreakdown: { fluency: 10, pronunciation: 9.5, grammar: 9, vocabulary: 9 },
        },
        wrong: {
          rawScore: 6.0,
          percentage: 60,
          tier: "average",
          attendedLabel: "Description missing key details",
          rubricScores: { fluency: 6.0, pronunciation: 6.0, grammatical_accuracy: 6.0 },
          subSkillBreakdown: { fluency: 6, pronunciation: 6, grammar: 6, vocabulary: 5 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_04_05",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w4d5-read-mcq", sequence: 1, archetypeId: "READ_COMP_MCQ", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d5-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d5-write-transform", sequence: 3, archetypeId: "WRITE_SENT_TRANS", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d5-speak-pic-desc", sequence: 4, archetypeId: "SPEAK_PIC_DESC", label: "Speak", rawScore: 9.5, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w4d5-read-mcq", sequence: 1, archetypeId: "READ_COMP_MCQ", label: "Read", rawScore: 7.5, tier: "good", baseReward: 7 },
        { taskId: "w4d5-listen-mcq", sequence: 2, archetypeId: "LISTEN_MCQ", label: "Listen", rawScore: 6.7, tier: "good", baseReward: 6 },
        { taskId: "w4d5-write-transform", sequence: 3, archetypeId: "WRITE_SENT_TRANS", label: "Write", rawScore: 6.7, tier: "good", baseReward: 6 },
        { taskId: "w4d5-speak-pic-desc", sequence: 4, archetypeId: "SPEAK_PIC_DESC", label: "Speak", rawScore: 6.0, tier: "average", baseReward: 6 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 20,
        vocabulary: 20,
        pronunciation: 10,
        fluency: 10,
        expression: 10,
        comprehension: 20,
        tone: 0,
      },
      wrong: {
        grammar: 14,
        vocabulary: 14,
        pronunciation: 6,
        fluency: 6,
        expression: 6,
        comprehension: 14,
        tone: 0,
      },
    },
    skillLabels,
  },
};

const weekFourDaySixEvaluation: EvaluationDayData = {
  dayId: "day_24_04_06",
  activityEvaluations: [
    {
      taskId: "w4d6-read-tone-id",
      evaluatorInput: {
        archetypeId: "READ_TONE_ID",
        widget: "read_tone_id",
        taskContentRef: "tasks.source.day_24_04_06.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]"
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "2 of 2 tones correct",
          rubricScores: { accuracy: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { grammar: 10, comprehension: 10 }
        },
        wrong: {
          rawScore: 5,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "1 of 2 tones correct",
          rubricScores: { accuracy: 5, grammatical_accuracy: 5 },
          subSkillBreakdown: { grammar: 5, comprehension: 5 }
        }
      }
    },
    {
      taskId: "w4d6-listen-tone",
      evaluatorInput: {
        archetypeId: "LISTEN_TONE",
        widget: "listen_tone",
        taskContentRef: "tasks.source.day_24_04_06.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]"
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "2 of 2 tones correct",
          rubricScores: { accuracy: 10, comprehension: 10 },
          subSkillBreakdown: { grammar: 10, comprehension: 10 }
        },
        wrong: {
          rawScore: 5,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "1 of 2 tones correct",
          rubricScores: { accuracy: 5, comprehension: 5 },
          subSkillBreakdown: { grammar: 5, comprehension: 5 }
        }
      }
    },
    {
      taskId: "w4d6-write-timed",
      evaluatorInput: {
        archetypeId: "WRITE_TIMED",
        widget: "write_timed",
        taskContentRef: "tasks.source.day_24_04_06.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]"
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Polished self-introduction note accepted",
          rubricScores: { grammatical_accuracy: 10, expression: 10 },
          subSkillBreakdown: { grammar: 10, expression: 10, vocabulary: 10 }
        },
        wrong: {
          rawScore: 5.0,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "Self-introduction note is too short and lacks cues",
          rubricScores: { grammatical_accuracy: 5, expression: 5 },
          subSkillBreakdown: { grammar: 5, expression: 5, vocabulary: 5 }
        }
      }
    },
    {
      taskId: "w4d6-speak-present",
      evaluatorInput: {
        archetypeId: "SPEAK_PRESENT",
        widget: "speak_present",
        taskContentRef: "tasks.source.day_24_04_06.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]"
      },
      outputs: {
        correct: {
          rawScore: 9.6,
          percentage: 96,
          tier: "excellent",
          attendedLabel: "Poised self-introduction delivered beautifully",
          rubricScores: { fluency: 9.5, pronunciation: 9.5, grammatical_accuracy: 9.8 },
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 10, vocabulary: 9 }
        },
        wrong: {
          rawScore: 5.5,
          percentage: 55,
          tier: "needs_work",
          attendedLabel: "Introduction lacks structure and is hesitant",
          rubricScores: { fluency: 6, pronunciation: 6, grammatical_accuracy: 4.5 },
          subSkillBreakdown: { fluency: 6, pronunciation: 6, grammar: 5, vocabulary: 5 }
        }
      }
    }
  ],
  overallScorecard: {
    dayId: "day_24_04_06",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w4d6-read-tone-id", sequence: 1, archetypeId: "READ_TONE_ID", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d6-listen-tone", sequence: 2, archetypeId: "LISTEN_TONE", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d6-write-timed", sequence: 3, archetypeId: "WRITE_TIMED", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d6-speak-present", sequence: 4, archetypeId: "SPEAK_PRESENT", label: "Speak", rawScore: 9.6, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w4d6-read-tone-id", sequence: 1, archetypeId: "READ_TONE_ID", label: "Read", rawScore: 5, tier: "needs_work", baseReward: 5 },
        { taskId: "w4d6-listen-tone", sequence: 2, archetypeId: "LISTEN_TONE", label: "Listen", rawScore: 5, tier: "needs_work", baseReward: 5 },
        { taskId: "w4d6-write-timed", sequence: 3, archetypeId: "WRITE_TIMED", label: "Write", rawScore: 5, tier: "needs_work", baseReward: 5 },
        { taskId: "w4d6-speak-present", sequence: 4, archetypeId: "SPEAK_PRESENT", label: "Speak", rawScore: 5.5, tier: "needs_work", baseReward: 5 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 20,
        vocabulary: 20,
        pronunciation: 9,
        fluency: 10,
        expression: 10,
        comprehension: 20,
        tone: 10,
      },
      wrong: {
        grammar: 10,
        vocabulary: 10,
        pronunciation: 6,
        fluency: 6,
        expression: 5,
        comprehension: 10,
        tone: 5,
      },
    },
    skillLabels,
  },
};

const weekFourDaySevenEvaluation: EvaluationDayData = {
  dayId: "day_24_04_07",
  activityEvaluations: [
    {
      taskId: "w4d7-read-mcq",
      evaluatorInput: {
        archetypeId: "READ_COMP_MCQ",
        widget: "read_comp_mcq",
        taskContentRef: "tasks.source.day_24_04_07.tasks[0]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "4 of 4 questions correct",
          rubricScores: { accuracy: 10, comprehension: 10 },
          subSkillBreakdown: { comprehension: 10, grammar: 9 },
        },
        wrong: {
          rawScore: 7.5,
          percentage: 75,
          tier: "good",
          attendedLabel: "3 of 4 questions correct",
          rubricScores: { accuracy: 7.5, comprehension: 7.5 },
          subSkillBreakdown: { comprehension: 8, grammar: 7 },
        },
      },
    },
    {
      taskId: "w4d7-listen-shadow",
      evaluatorInput: {
        archetypeId: "LISTEN_SHADOW",
        widget: "listen_shadow",
        taskContentRef: "tasks.source.day_24_04_07.tasks[1]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Shadowing exactly clear",
          rubricScores: { pronunciation: 10, fluency: 10 },
          subSkillBreakdown: { pronunciation: 10, fluency: 10 },
        },
        wrong: {
          rawScore: 5.0,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "Shadowing has errors",
          rubricScores: { pronunciation: 5.0, fluency: 5.0 },
          subSkillBreakdown: { pronunciation: 5, fluency: 5 },
        },
      },
    },
    {
      taskId: "w4d7-write-timed",
      evaluatorInput: {
        archetypeId: "WRITE_TIMED",
        widget: "write_timed",
        taskContentRef: "tasks.source.day_24_04_07.tasks[2]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 10,
          percentage: 100,
          tier: "excellent",
          attendedLabel: "Timed paragraph clear and accurate",
          rubricScores: { expression: 10, grammatical_accuracy: 10 },
          subSkillBreakdown: { expression: 10, grammar: 10, vocabulary: 10 },
        },
        wrong: {
          rawScore: 5.0,
          percentage: 50,
          tier: "needs_work",
          attendedLabel: "Timed paragraph is too basic and lacks cues",
          rubricScores: { expression: 5.0, grammatical_accuracy: 5.0 },
          subSkillBreakdown: { expression: 5, grammar: 5, vocabulary: 5 },
        },
      },
    },
    {
      taskId: "w4d7-speak-debate",
      evaluatorInput: {
        archetypeId: "SPEAK_DEBATE",
        widget: "speak_debate",
        taskContentRef: "tasks.source.day_24_04_07.tasks[3]",
        userResponseRef: "tasks.source.answers[answerView]",
      },
      outputs: {
        correct: {
          rawScore: 9.8,
          percentage: 98,
          tier: "excellent",
          attendedLabel: "Polished counter-argument delivered beautifully",
          rubricScores: { fluency: 9.8, pronunciation: 9.8, grammatical_accuracy: 9.8 },
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 10, vocabulary: 10 },
        },
        wrong: {
          rawScore: 5.5,
          percentage: 55,
          tier: "needs_work",
          attendedLabel: "Counter-argument lacks structured cues and is hesitant",
          rubricScores: { fluency: 6.0, pronunciation: 6.0, grammatical_accuracy: 4.5 },
          subSkillBreakdown: { fluency: 6, pronunciation: 6, grammar: 5, vocabulary: 5 },
        },
      },
    },
  ],
  overallScorecard: {
    dayId: "day_24_04_07",
    pointsApplied: true,
    activities: {
      correct: [
        { taskId: "w4d7-read-mcq", sequence: 1, archetypeId: "READ_COMP_MCQ", label: "Read", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d7-listen-shadow", sequence: 2, archetypeId: "LISTEN_SHADOW", label: "Listen", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d7-write-timed", sequence: 3, archetypeId: "WRITE_TIMED", label: "Write", rawScore: 10, tier: "excellent", baseReward: 10 },
        { taskId: "w4d7-speak-debate", sequence: 4, archetypeId: "SPEAK_DEBATE", label: "Speak", rawScore: 9.8, tier: "excellent", baseReward: 9 },
      ],
      wrong: [
        { taskId: "w4d7-read-mcq", sequence: 1, archetypeId: "READ_COMP_MCQ", label: "Read", rawScore: 7.5, tier: "good", baseReward: 7 },
        { taskId: "w4d7-listen-shadow", sequence: 2, archetypeId: "LISTEN_SHADOW", label: "Listen", rawScore: 5, tier: "needs_work", baseReward: 5 },
        { taskId: "w4d7-write-timed", sequence: 3, archetypeId: "WRITE_TIMED", label: "Write", rawScore: 5, tier: "needs_work", baseReward: 5 },
        { taskId: "w4d7-speak-debate", sequence: 4, archetypeId: "SPEAK_DEBATE", label: "Speak", rawScore: 5.5, tier: "needs_work", baseReward: 5 },
      ],
    },
    pointsEarned: {
      correct: {
        grammar: 29,
        vocabulary: 20,
        pronunciation: 19,
        fluency: 20,
        expression: 10,
        comprehension: 20,
        tone: 0,
      },
      wrong: {
        grammar: 17,
        vocabulary: 10,
        pronunciation: 11,
        fluency: 11,
        expression: 5,
        comprehension: 13,
        tone: 0,
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
      4: weekOneDayFourEvaluation,
      5: weekOneDayFiveEvaluation,
      6: weekOneDaySixEvaluation,
      7: weekOneDaySevenEvaluation,
    },
    2: {
      1: weekTwoDayOneEvaluation,
      2: weekTwoDayTwoEvaluation,
      3: weekTwoDayThreeEvaluation,
      4: weekTwoDayFourEvaluation,
      5: weekTwoDayFiveEvaluation,
      6: weekTwoDaySixEvaluation,
      7: weekTwoDaySevenEvaluation,
    },
    3: {
      1: weekThreeDayOneEvaluation,
      3: weekThreeDayThreeEvaluation,
      2: weekThreeDayTwoEvaluation,
      4: weekThreeDayFourEvaluation,
      5: weekThreeDayFiveEvaluation,
      6: weekThreeDaySixEvaluation,
      7: weekThreeDaySevenEvaluation,
    },
    4: {
      1: weekFourDayOneEvaluation,
      2: weekFourDayTwoEvaluation,
      3: weekFourDayThreeEvaluation,
      4: weekFourDayFourEvaluation,
      5: weekFourDayFiveEvaluation,
      6: weekFourDaySixEvaluation,
      7: weekFourDaySevenEvaluation,
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
