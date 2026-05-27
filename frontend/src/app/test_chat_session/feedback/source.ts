import type { AnswerView, CourseTrack } from "../teaching/source";

export interface FeedbackInputSchema {
  taskId: string;
  evaluationRef: string;
  learnerResponseRef: string;
}

export interface FeedbackMistake {
  issue: string;
  userWrote?: string;
  correction?: string;
  rule?: string;
}

export interface ActivityFeedbackOutput {
  score: number;
  summary: string;
  didWell: string[];
  mistakes: FeedbackMistake[];
  nextTip: string;
  subSkillBreakdown: Record<string, number>;
}

export interface ActivityFeedback {
  taskId: string;
  feedbackInput: FeedbackInputSchema;
  outputs: Record<AnswerView, ActivityFeedbackOutput>;
}

export interface RagFeedback {
  dayId: string;
  memoryInput: {
    scorecardRef: string;
    activityFeedbackRefs: string[];
    learnerHistoryRef: string;
  };
  outputs: Record<AnswerView, string>;
}

export interface FeedbackDayData {
  dayId: string;
  activityFeedback: ActivityFeedback[];
  ragFeedback: RagFeedback;
}

const weekOneDayOneFeedback: FeedbackDayData = {
  dayId: "day_24_01_01",
  activityFeedback: [
    {
      taskId: "w1d1-read-cloze",
      feedbackInput: {
        taskId: "w1d1-read-cloze",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect control of simple present blanks.",
          didWell: [
            "You added -s for singular names and she.",
            "You kept the base verb after they.",
          ],
          mistakes: [],
          nextTip: "Keep checking the subject before choosing the verb form.",
          subSkillBreakdown: { grammar: 10, comprehension: 9 },
        },
        wrong: {
          score: 8,
          summary: "Strong work, with one third-person verb form to fix.",
          didWell: [
            "You handled she drinks and they study correctly.",
            "You understood the whole routine passage.",
          ],
          mistakes: [
            {
              issue: "Ravi is one person, so the verb needs -s.",
              userWrote: "take",
              correction: "takes",
              rule: "With he, she, it, or a singular name, add -s in the simple present.",
            },
          ],
          nextTip: "Before answering, ask: is the subject one person or many?",
          subSkillBreakdown: { grammar: 8, comprehension: 8 },
        },
      },
    },
    {
      taskId: "w1d1-listen-mcq",
      feedbackInput: {
        taskId: "w1d1-listen-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "You caught all routine details in the audio.",
          didWell: [
            "You identified the time, person, school activity, and night habit.",
          ],
          mistakes: [],
          nextTip: "For listening tasks, keep noting time words and frequency adverbs.",
          subSkillBreakdown: { comprehension: 10, grammar: 9 },
        },
        wrong: {
          score: 7.5,
          summary: "You understood most details, but one activity changed.",
          didWell: [
            "You caught the wake-up time and family detail.",
          ],
          mistakes: [
            {
              issue: "The audio says Omar studies English after school on Mondays.",
              userWrote: "Plays games",
              correction: "Studies English",
              rule: "Listen for the verb after the time phrase: On Mondays, he studies English.",
            },
          ],
          nextTip: "When you hear a day or time phrase, listen carefully for the next verb.",
          subSkillBreakdown: { comprehension: 8, grammar: 7 },
        },
      },
    },
    {
      taskId: "w1d1-write-open-sent",
      feedbackInput: {
        taskId: "w1d1-write-open-sent",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.5,
          summary: "Your routine sentences are accurate and natural.",
          didWell: [
            "You placed frequency adverbs naturally.",
            "You used he walks and she studies correctly.",
          ],
          mistakes: [],
          nextTip: "Try adding time phrases like in the morning or after dinner.",
          subSkillBreakdown: { grammar: 10, expression: 9, vocabulary: 9 },
        },
        wrong: {
          score: 7,
          summary: "Your meaning is clear, but one she sentence misses -s.",
          didWell: [
            "Your I and he sentences are correct.",
            "You used sometimes in the right position.",
          ],
          mistakes: [
            {
              issue: "She needs the third-person verb form.",
              userWrote: "She sometimes study English after dinner.",
              correction: "She sometimes studies English after dinner.",
              rule: "With she, add -s or -es: study becomes studies.",
            },
          ],
          nextTip: "For verbs ending in consonant + y, change y to ies after he or she.",
          subSkillBreakdown: { grammar: 7, expression: 8, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w1d1-speak-timed",
      feedbackInput: {
        taskId: "w1d1-speak-timed",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.2,
          summary: "Clear, controlled routine speaking.",
          didWell: [
            "Your sentences are short and easy to understand.",
            "You used frequency adverbs with natural rhythm.",
          ],
          mistakes: [],
          nextTip: "Next time, connect two routines with and or then.",
          subSkillBreakdown: { fluency: 9, pronunciation: 9, grammar: 9 },
        },
        wrong: {
          score: 7.2,
          summary: "Your speaking is understandable, with one grammar slip.",
          didWell: [
            "Your pronunciation is clear.",
            "Two of your three routine sentences use the target pattern well.",
          ],
          mistakes: [
            {
              issue: "He needs the third-person verb form in simple present.",
              userWrote: "He often play football on Sunday.",
              correction: "He often plays football on Sunday.",
              rule: "Use plays after he in the simple present.",
            },
          ],
          nextTip: "Pause after the subject and choose the verb form before speaking.",
          subSkillBreakdown: { fluency: 8, pronunciation: 8, grammar: 6 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_01_01",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.simple_present_foundation",
    },
    outputs: {
      correct:
        "You showed a strong first-day pattern: you can notice the subject, choose the right simple present verb, and carry that into writing and speaking. Your next useful step is to make the same sentences a little longer with time phrases, because your core grammar is ready for more natural daily-life detail.",
      wrong:
        "Your main pattern is clear: you understand simple present meaning, but third-person -s can disappear when you move quickly. That is normal at A1. For the next session, keep a small mental checkpoint before every he, she, or named-person sentence: subject first, then verb with -s or -es.",
    },
  },
};

const weekOneDayTwoFeedback: FeedbackDayData = {
  dayId: "day_24_01_02",
  activityFeedback: [
    {
      taskId: "w1d2-read-error-spot",
      feedbackInput: {
        taskId: "w1d2-read-error-spot",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent noticing of simple past errors.",
          didWell: [
            "You found irregular past mistakes and did + base verb mistakes.",
            "You noticed that last summer needs a past verb.",
          ],
          mistakes: [],
          nextTip: "Keep checking time markers first; they often tell you which tense is needed.",
          subSkillBreakdown: { grammar: 10, comprehension: 9 },
        },
        wrong: {
          score: 8,
          summary: "Strong reading work, with one past-time verb missed.",
          didWell: [
            "You found the irregular forms goed and finished after did.",
            "You also noticed the passive helper and advice mistake.",
          ],
          mistakes: [
            {
              issue: "Last summer is a past time marker, so the verb needs the past form.",
              userWrote: "we",
              correction: "visited",
              rule: "Use simple past with finished time phrases like yesterday, last night, or last summer.",
            },
          ],
          nextTip: "When a sentence starts with last, look for the verb and check if it is in past form.",
          subSkillBreakdown: { grammar: 8, comprehension: 8 },
        },
      },
    },
    {
      taskId: "w1d2-listen-cloze",
      feedbackInput: {
        taskId: "w1d2-listen-cloze",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "You caught every past verb in the listening notes.",
          didWell: [
            "You recognized irregular verbs like got, had, felt, and sent.",
            "You also heard the regular -ed verb prepared.",
          ],
          mistakes: [],
          nextTip: "Keep grouping past verbs into regular and irregular forms as you listen.",
          subSkillBreakdown: { comprehension: 10, grammar: 10 },
        },
        wrong: {
          score: 8,
          summary: "You understood the story, with one irregular verb to fix.",
          didWell: [
            "You caught got, had, prepared, and sent correctly.",
          ],
          mistakes: [
            {
              issue: "Feel is irregular in the past.",
              userWrote: "feeled",
              correction: "felt",
              rule: "Some verbs do not add -ed in the simple past: feel becomes felt.",
            },
          ],
          nextTip: "Build a small memory list for common irregular verbs: feel/felt, send/sent, have/had.",
          subSkillBreakdown: { comprehension: 8, grammar: 8 },
        },
      },
    },
    {
      taskId: "w1d2-write-error-corr",
      feedbackInput: {
        taskId: "w1d2-write-error-corr",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.4,
          summary: "Your corrected sentences are clear and natural.",
          didWell: [
            "You fixed did not plus base verb.",
            "You used went and bought correctly.",
          ],
          mistakes: [],
          nextTip: "Next, practise using irregular past verbs in your own short stories.",
          subSkillBreakdown: { grammar: 10, expression: 9, vocabulary: 8 },
        },
        wrong: {
          score: 7,
          summary: "Your corrections are mostly clear, but one irregular verb stayed wrong.",
          didWell: [
            "You fixed the first and third sentences well.",
            "Your meaning stayed easy to understand.",
          ],
          mistakes: [
            {
              issue: "Go has an irregular past form.",
              userWrote: "She goed to the store and bought some milk last night.",
              correction: "She went to the store and bought some milk last night.",
              rule: "Use went as the simple past form of go.",
            },
          ],
          nextTip: "When you see go in a past sentence, choose went instead of adding -ed.",
          subSkillBreakdown: { grammar: 7, expression: 8, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w1d2-speak-read-aloud",
      feedbackInput: {
        taskId: "w1d2-speak-read-aloud",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.1,
          summary: "Clear read-aloud delivery with strong past-tense pronunciation.",
          didWell: [
            "You pronounced regular -ed endings clearly.",
            "You read irregular verbs like ate, drank, and went accurately.",
          ],
          mistakes: [],
          nextTip: "Keep a steady pace and lightly stress past verbs when reading aloud.",
          subSkillBreakdown: { pronunciation: 9, fluency: 9, grammar: 9 },
        },
        wrong: {
          score: 7,
          summary: "Your read-aloud was understandable, with one past verb slip.",
          didWell: [
            "Your pacing was steady.",
            "Most regular -ed endings were clear.",
          ],
          mistakes: [
            {
              issue: "The passage uses the irregular past form ate.",
              userWrote: "eat",
              correction: "ate",
              rule: "When reading a past-tense story, keep irregular verbs in their past form.",
            },
          ],
          nextTip: "Before recording, scan the passage for irregular past verbs and say them once.",
          subSkillBreakdown: { pronunciation: 8, fluency: 8, grammar: 6 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_01_02",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.simple_past_foundation",
    },
    outputs: {
      correct:
        "You showed a strong simple-past pattern today: you can identify completed actions, choose irregular past forms, correct mistakes, and read a short past-tense story aloud clearly. Your next useful step is to use these verbs in your own 3-4 sentence story about yesterday.",
      wrong:
        "Your simple-past meaning is solid, and the main pattern to keep practising is irregular verbs. You caught most of the lesson, but forms like go/went, feel/felt, and eat/ate need a quick mental check before you write or speak.",
    },
  },
};

const weekOneDayThreeFeedback: FeedbackDayData = {
  dayId: "day_24_01_03",
  activityFeedback: [
    {
      taskId: "w1d3-read-comp-mcq",
      feedbackInput: {
        taskId: "w1d3-read-comp-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent reading of present continuous actions.",
          didWell: [
            "You matched each action to the correct person.",
            "You recognized is writing as the correct now-action pattern.",
          ],
          mistakes: [],
          nextTip: "Keep asking who is doing the action before choosing is or are.",
          subSkillBreakdown: { comprehension: 10, grammar: 10 },
        },
        wrong: {
          score: 7.5,
          summary: "You understood most of the scene, with one action detail missed.",
          didWell: [
            "You identified Mira, Arjun, and the teacher correctly.",
            "You chose the correct is writing pattern.",
          ],
          mistakes: [
            {
              issue: "The passage says the parents are talking near the door.",
              userWrote: "Reading",
              correction: "Talking",
              rule: "Use the action stated in the passage: two parents are talking.",
            },
          ],
          nextTip: "When a sentence has are plus verb-ing, check the plural subject and the action together.",
          subSkillBreakdown: { comprehension: 8, grammar: 7 },
        },
      },
    },
    {
      taskId: "w1d3-listen-dictation",
      feedbackInput: {
        taskId: "w1d3-listen-dictation",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "You caught every present continuous chunk exactly.",
          didWell: [
            "You heard am opening, are taking, is asking, and is writing.",
            "Your typed sentences kept the helper verbs and -ing forms together.",
          ],
          mistakes: [],
          nextTip: "Keep listening for the helper verb first, then the action word.",
          subSkillBreakdown: { comprehension: 10, grammar: 10, vocabulary: 8 },
        },
        wrong: {
          score: 7.5,
          summary: "Your dictation is strong, with one helper verb mismatch.",
          didWell: [
            "You typed three sentences exactly.",
            "You caught the -ing action words clearly.",
          ],
          mistakes: [
            {
              issue: "Students is plural, so it needs are.",
              userWrote: "The students is taking out their books.",
              correction: "The students are taking out their books.",
              rule: "Use are with plural subjects in the present continuous.",
            },
          ],
          nextTip: "After typing, scan each sentence for subject plus helper: I am, one person is, many people are.",
          subSkillBreakdown: { comprehension: 8, grammar: 7, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w1d3-write-sent-trans",
      feedbackInput: {
        taskId: "w1d3-write-sent-trans",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.5,
          summary: "Your sentence transformations are accurate and natural.",
          didWell: [
            "You changed the main verbs to -ing forms.",
            "You chose am, is, and are from the subject correctly.",
          ],
          mistakes: [],
          nextTip: "Next, add now or at the moment to make the time meaning even clearer.",
          subSkillBreakdown: { grammar: 10, expression: 9, vocabulary: 8 },
        },
        wrong: {
          score: 7,
          summary: "Your transformations are mostly clear, but one plural subject used the wrong helper.",
          didWell: [
            "You transformed she walks and I read correctly.",
            "Your -ing verb forms are clear.",
          ],
          mistakes: [
            {
              issue: "They needs are in present continuous.",
              userWrote: "They is playing football.",
              correction: "They are playing football.",
              rule: "Use are with they, we, you, and plural nouns.",
            },
          ],
          nextTip: "Before writing the -ing verb, choose the helper from the subject.",
          subSkillBreakdown: { grammar: 7, expression: 8, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w1d3-speak-timed",
      feedbackInput: {
        taskId: "w1d3-speak-timed",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.2,
          summary: "Clear speaking with strong present continuous control.",
          didWell: [
            "You used am, is, and are with the right subjects.",
            "Your now-action sentences were short and easy to follow.",
          ],
          mistakes: [],
          nextTip: "Try describing a whole scene next: one I sentence, one she sentence, and one they sentence.",
          subSkillBreakdown: { fluency: 9, pronunciation: 9, grammar: 9 },
        },
        wrong: {
          score: 7.2,
          summary: "Your speaking is understandable, with one helper verb slip.",
          didWell: [
            "You used I am and they are correctly.",
            "Your pronunciation and pacing stayed clear.",
          ],
          mistakes: [
            {
              issue: "She needs is, not are.",
              userWrote: "She are reading a book now.",
              correction: "She is reading a book now.",
              rule: "Use is with he, she, it, or one named person.",
            },
          ],
          nextTip: "Pause after the subject, choose am/is/are, then say the -ing action.",
          subSkillBreakdown: { fluency: 8, pronunciation: 8, grammar: 6 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_01_03",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.present_continuous_foundation",
    },
    outputs: {
      correct:
        "You showed a strong present-continuous pattern today: you can understand a scene, hear full am/is/are plus verb-ing chunks, rewrite simple present sentences, and speak about actions happening now. Your next useful step is to describe two or three actions in one scene using and.",
      wrong:
        "Your present-continuous meaning is clear, and the main pattern to keep practising is helper-verb choice. You are using -ing well, so focus your next checkpoint on the subject: I am, one person is, and two or more people are.",
    },
  },
};

const feedbackDays: Partial<Record<CourseTrack, Record<number, Record<number, FeedbackDayData>>>> = {
  "24w": {
    1: {
      1: weekOneDayOneFeedback,
      2: weekOneDayTwoFeedback,
      3: weekOneDayThreeFeedback,
    },
  },
  "48w": {},
};

export function getFeedbackDay(
  courseTrack: CourseTrack,
  week: number,
  day: number,
): FeedbackDayData | null {
  return feedbackDays[courseTrack]?.[week]?.[day] ?? null;
}

export function getActivityFeedback(
  dayData: FeedbackDayData | null,
  taskId: string,
): ActivityFeedback | null {
  return dayData?.activityFeedback.find((entry) => entry.taskId === taskId) ?? null;
}
