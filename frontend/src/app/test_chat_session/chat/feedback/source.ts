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


const weekOneDayFourFeedback: FeedbackDayData = {
  dayId: "day_24_01_04",
  activityFeedback: [
    {
      taskId: "w1d4-read-word-match",
      feedbackInput: {
        taskId: "w1d4-read-word-match",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect matching of articles.",
          didWell: ["You correctly matched a and an based on consonant and vowel sounds.", "You knew when to use the for a unique object."],
          mistakes: [],
          nextTip: "Try to apply this rule every time you encounter a noun.",
          subSkillBreakdown: { grammar: 10, vocabulary: 10 },
        },
        wrong: {
          score: 6.6,
          summary: "Good effort, but watch out for vowel vs. consonant sounds.",
          didWell: ["You got most of the articles right."],
          mistakes: [
            {
              issue: "Used 'a' instead of 'an' before a vowel sound.",
              userWrote: "a",
              correction: "an",
              rule: "Use 'an' before nouns starting with a vowel sound.",
            }
          ],
          nextTip: "Always check the first sound of the noun.",
          subSkillBreakdown: { grammar: 6.6, vocabulary: 6.6 },
        },
      },
    },
    {
      taskId: "w1d4-listen-mcq",
      feedbackInput: {
        taskId: "w1d4-listen-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent listening comprehension for articles.",
          didWell: ["You correctly identified how articles are used when introducing and referring back to nouns."],
          mistakes: [],
          nextTip: "Listen closely to articles as they indicate specificity in speech.",
          subSkillBreakdown: { comprehension: 10, grammar: 10 },
        },
        wrong: {
          score: 5,
          summary: "Needs work on hearing the difference between specific and non-specific.",
          didWell: ["You caught some details."],
          mistakes: [
            {
              issue: "Did not identify the correct article used for the first introduction of a noun.",
              userWrote: "The book",
              correction: "A book",
              rule: "Use 'a' or 'an' when a noun is mentioned for the first time.",
            }
          ],
          nextTip: "Pay attention to when a noun is mentioned for the first time vs. subsequent times.",
          subSkillBreakdown: { comprehension: 5, grammar: 5 },
        },
      },
    },
    {
      taskId: "w1d4-write-open-sent",
      feedbackInput: {
        taskId: "w1d4-write-open-sent",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Great job writing sentences with articles.",
          didWell: ["You correctly applied the rules for a, an, and the in your own sentences."],
          mistakes: [],
          nextTip: "Continue to use a mix of articles in your daily writing.",
          subSkillBreakdown: { grammar: 10, expression: 10 },
        },
        wrong: {
          score: 6.6,
          summary: "Good sentences, but one article mistake.",
          didWell: ["Your sentences were well-structured overall."],
          mistakes: [
            {
              issue: "Used 'a' before a vowel sound.",
              userWrote: "a umbrella",
              correction: "an umbrella",
              rule: "Use 'an' before nouns starting with a vowel sound like 'umbrella'.",
            }
          ],
          nextTip: "Read your sentences aloud to check if a/an sounds right.",
          subSkillBreakdown: { grammar: 6.6, expression: 6.6 },
        },
      },
    },
    {
      taskId: "w1d4-speak-pic-desc",
      feedbackInput: {
        taskId: "w1d4-speak-pic-desc",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent description using the correct articles naturally.",
          didWell: ["You fluently applied a, an, and the in context."],
          mistakes: [],
          nextTip: "Try describing more complex images with multiple objects.",
          subSkillBreakdown: { fluency: 10, grammar: 10 },
        },
        wrong: {
          score: 5,
          summary: "Good attempt, but you missed some articles and used 'a' instead of 'an'.",
          didWell: ["You described the main subject correctly."],
          mistakes: [
            {
              issue: "Missing or incorrect articles.",
              userWrote: "cat on sofa... a open book",
              correction: "a cat on the sofa... an open book",
              rule: "Use 'a'/'an' for non-specific items and 'the' for specific ones.",
            }
          ],
          nextTip: "Remember that singular nouns almost always need an article before them.",
          subSkillBreakdown: { fluency: 8, grammar: 2 },
        },
      },
    }
  ],
  ragFeedback: {
    dayId: "day_24_01_04",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.articles_foundation",
    },
    outputs: {
      correct: "Fantastic progress with articles today! You successfully matched them, heard them in context, and even described a picture fluently using a, an, and the correctly.",
      wrong: "You're getting the hang of articles, but there's still some confusion between 'a' and 'an', especially in speaking. We will keep practicing this to make it instinctual."
    },
  },
};

const weekOneDayFiveFeedback: FeedbackDayData = {
  dayId: "day_24_01_05",
  activityFeedback: [
    {
      taskId: "w1d5-read-cloze",
      feedbackInput: {
        taskId: "w1d5-read-cloze",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect control of pronoun blanks.",
          didWell: [
            "You used She as the subject.",
            "You correctly identified the possessive hers.",
            "You matched us as the receiver of the action.",
          ],
          mistakes: [],
          nextTip: "Always pay attention to gender and number when choosing pronouns.",
          subSkillBreakdown: { grammar: 10, comprehension: 10 },
        },
        wrong: {
          score: 7.5,
          summary: "Good reading work, but one pronoun choice went wrong.",
          didWell: [
            "You got the subject and possessive pronouns correct.",
            "You understood the plural pronoun us.",
          ],
          mistakes: [
            {
              issue: "Grandmother is female, so she requires female pronouns.",
              userWrote: "him",
              correction: "her",
              rule: "Use 'her' as the object pronoun representing a female singular person.",
            },
          ],
          nextTip: "Identify the gender of the noun being replaced before selecting the pronoun.",
          subSkillBreakdown: { grammar: 7.5, comprehension: 7.5 },
        },
      },
    },
    {
      taskId: "w1d5-listen-mcq",
      feedbackInput: {
        taskId: "w1d5-listen-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent job resolving pronoun references in natural speech.",
          didWell: [
            "You correctly identified Sophia as the subject who got the promotion.",
            "You knew that Sophia is the person buying dinner.",
          ],
          mistakes: [],
          nextTip: "Continue listening closely to subject-verb pairings in fast conversation.",
          subSkillBreakdown: { comprehension: 10, grammar: 10 },
        },
        wrong: {
          score: 5,
          summary: "Good listening effort, but you mixed up the promotion recipient.",
          didWell: [
            "You correctly identified that Sophia is the one promising dinner.",
          ],
          mistakes: [
            {
              issue: "Sophia called Lily to share her own promotion news, making Sophia the subject of the happy state.",
              userWrote: "Lily",
              correction: "Sophia",
              rule: "Listen to the direction of the conversation: Sophia called her sister to tell her she got a promotion.",
            },
          ],
          nextTip: "When a speaker introduces a scenario, note who initiates the call and what they say about themselves.",
          subSkillBreakdown: { comprehension: 5, grammar: 5 },
        },
      },
    },
    {
      taskId: "w1d5-write-paragraph",
      feedbackInput: {
        taskId: "w1d5-write-paragraph",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent paragraph writing. You used subject, object, and possessive pronouns flawlessly.",
          didWell: [
            "You correctly connected 'we' and 'us' to your friends.",
            "You used the possessive pronoun 'his' in the correct position.",
          ],
          mistakes: [],
          nextTip: "Try creating more complex scenarios with multiple friends of different genders to test pronoun agreement.",
          subSkillBreakdown: { grammar: 10, expression: 10 },
        },
        wrong: {
          score: 6.6,
          summary: "Your paragraph structure is nice, but there is one pronoun case error.",
          didWell: [
            "Your narrative is engaging and meets the word count.",
            "You used 'we' and 'his' correctly.",
          ],
          mistakes: [
            {
              issue: "Used a subject pronoun where an object pronoun is required.",
              userWrote: "Leo bought we ice cream",
              correction: "Leo bought us ice cream",
              rule: "Use object pronouns ('us') after verbs when they receive the action.",
            },
          ],
          nextTip: "Subject pronouns are for the doers of actions. Object pronouns are for the receivers.",
          subSkillBreakdown: { grammar: 6, expression: 7.2 },
        },
      },
    },
    {
      taskId: "w1d5-speak-roleplay",
      feedbackInput: {
        taskId: "w1d5-speak-roleplay",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Superb roleplay! Your pronunciation and pronoun use in conversation are top notch.",
          didWell: [
            "You correctly chose the possessive 'mine' to answer the question 'is it yours?'.",
            "You used the object pronoun 'him' and subject pronoun 'he' perfectly in context.",
          ],
          mistakes: [],
          nextTip: "Try acting out the scene again with different characters using 'her' and 'she'.",
          subSkillBreakdown: { fluency: 10, grammar: 10 },
        },
        wrong: {
          score: 5,
          summary: "Good conversational effort, but there is one pronoun agreement error.",
          didWell: [
            "Your pacing was natural and speaking was very clear.",
            "You used 'mine' correctly for ownership.",
          ],
          mistakes: [
            {
              issue: "Used a subject pronoun instead of an object pronoun after a preposition.",
              userWrote: "She lent it to he",
              correction: "She lent it to him",
              rule: "Always use object pronouns ('him') after prepositions like 'to'.",
            },
          ],
          nextTip: "Check your prepositions: 'to him', 'for her', 'with them' are the correct combinations.",
          subSkillBreakdown: { fluency: 8, grammar: 2 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_01_05",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.pronouns_foundation",
    },
    outputs: {
      correct: "Incredible pronoun mastery today! You navigated subject, object, and possessive pronouns seamlessly in reading, listening, writing, and speaking. You are ready to handle complex conversational dynamics!",
      wrong: "You have a solid foundation with pronouns, but you tend to mix up subject and object forms when speaking or writing quickly. Focus on checking the verb position: subject pronouns before the verb, and object pronouns after the verb or prepositions."
    },
  },
};

const weekOneDaySixFeedback: FeedbackDayData = {
  dayId: "day_24_01_06",
  activityFeedback: [
    {
      taskId: "w1d6-read-tfng",
      feedbackInput: {
        taskId: "w1d6-read-tfng",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect control of possessives in reading.",
          didWell: [
            "You correctly identified Emma's blue hat ownership.",
            "You solved Leo's sunglasses borrowing relationship.",
            "You matched Emma's friend as the red ball owner.",
          ],
          mistakes: [],
          nextTip: "Always map nouns to the correct possessive marker in the passage.",
          subSkillBreakdown: { grammar: 10, comprehension: 10 },
        },
        wrong: {
          score: 8,
          summary: "Good reading, but you mixed up one ownership statement.",
          didWell: [
            "You parsed Leo's borrowing relationship correctly.",
            "You noticed that the father's grill is old.",
          ],
          mistakes: [
            {
              issue: "Emma is wearing their mother's hat, not her own.",
              userWrote: "True",
              correction: "False",
              rule: "Emma is wearing a blue hat, but it is actually our mother's.",
            },
          ],
          nextTip: "Before marking a statement True or False, re-read the exact ownership sentence.",
          subSkillBreakdown: { grammar: 8, comprehension: 8 },
        },
      },
    },
    {
      taskId: "w1d6-listen-shadow",
      feedbackInput: {
        taskId: "w1d6-listen-shadow",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent shadowing pace and phonetic reproduction.",
          didWell: [
            "You reproduced the elided 's in 'it's hers' beautifully.",
            "Your link between 'actually his' was smooth and natural.",
          ],
          mistakes: [],
          nextTip: "Keep shadowing fast Monologues to build auditory rhythm.",
          subSkillBreakdown: { pronunciation: 10, fluency: 10 },
        },
        wrong: {
          score: 5,
          summary: "Your pace was good, but you missed some fast possessive endings.",
          didWell: [
            "You stayed in sync with the speaker's Monologue.",
          ],
          mistakes: [
            {
              issue: "Missed the possessive 's sound in fast speech.",
              userWrote: "it's her... actually him",
              correction: "it's hers... actually his",
              rule: "Pronounce the final possessive 's in hers and his clearly even in fast speech.",
            },
          ],
          nextTip: "Listen to the sharp sibilant /s/ or /z/ sound at the end of possessive pronouns.",
          subSkillBreakdown: { pronunciation: 6, fluency: 4 },
        },
      },
    },
    {
      taskId: "w1d6-write-email",
      feedbackInput: {
        taskId: "w1d6-write-email",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent email writing. Your possessive nouns and adjectives are fully accurate.",
          didWell: [
            "You used brother's and sister's with correct singular possessive 's.",
            "You paired Sam and Lily with correct possessive adjectives 'his' and 'her'.",
          ],
          mistakes: [],
          nextTip: "Try introducing plural family members (e.g., parents' house) to practice plural possessives.",
          subSkillBreakdown: { grammar: 10, expression: 10 },
        },
        wrong: {
          score: 6.6,
          summary: "Engaging email, but some possessives are missing singular 's or are using subject pronouns instead.",
          didWell: [
            "Your email layout is natural and friendly.",
            "You used 'her' and 'our' correctly.",
          ],
          mistakes: [
            {
              issue: "Missing possessive 's on the singular noun brother.",
              userWrote: "My brother name is Sam",
              correction: "My brother's name is Sam",
              rule: "Add 's to show that the name belongs to your brother.",
            },
            {
              issue: "Used a subject pronoun instead of a possessive adjective.",
              userWrote: "He favorite sport",
              correction: "His favorite sport",
              rule: "Use the possessive adjective 'his' before a noun like 'favorite sport'.",
            },
          ],
          nextTip: "Remember that singular nouns need 's for possession, and always check that adjectives (his, her) modify nouns.",
          subSkillBreakdown: { grammar: 6, expression: 7.2 },
        },
      },
    },
    {
      taskId: "w1d6-speak-smalltalk",
      feedbackInput: {
        taskId: "w1d6-speak-smalltalk",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Fabulous small talk performance! Your possessive pronouns sound smooth and clear.",
          didWell: [
            "You correctly selected 'mine' to describe your umbrella.",
            "You contrasted 'ours' and 'his' naturally in casual conversation.",
          ],
          mistakes: [],
          nextTip: "Try creating roleplay small talk about toys or books using yours/theirs.",
          subSkillBreakdown: { fluency: 10, grammar: 10 },
        },
        wrong: {
          score: 5,
          summary: "Your speaking flow was great, but you used object pronouns instead of possessive forms.",
          didWell: [
            "You responded to every prompt quickly and clearly.",
            "You contrasted 'ours' and 'his' perfectly in the second turn.",
          ],
          mistakes: [
            {
              issue: "Used object/subject pronouns instead of possessive pronouns.",
              userWrote: "it's me! She left her inside",
              correction: "it's mine! She left hers inside",
              rule: "Use possessive pronouns ('mine', 'hers') to replace nouns when describing ownership.",
            },
          ],
          nextTip: "When answering 'whose is this?', always use possessive pronouns (mine, hers, ours) rather than object pronouns (me, her, us).",
          subSkillBreakdown: { fluency: 8, grammar: 2 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_01_06",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.possessives_foundation",
    },
    outputs: {
      correct: "Superb possessive control today! You navigated possessive 's, possessive adjectives (his, her, our), and possessive pronouns (mine, hers, ours) with zero errors in both writing and speaking. Your small talk feels extremely natural!",
      wrong: "You have a clear understanding of possessives in reading, but you tend to drop possessive 's or swap possessives with object/subject pronouns under conversational pressure. Keep a small mental note: check that nouns have 's for ownership, and use mine/hers/theirs instead of me/her/them in small talk.",
    },
  },
};

const weekOneDaySevenFeedback: FeedbackDayData = {
  dayId: "day_24_01_07",
  activityFeedback: [
    {
      taskId: "w1d7-read-context-mcq",
      feedbackInput: {
        taskId: "w1d7-read-context-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]"
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Superb control of preposition MCQs.",
          didWell: [
            "You correctly chose 'on' for flat surfaces.",
            "You understood that an armchair is sat 'in' whereas flat surfaces are 'on'."
          ],
          mistakes: [],
          nextTip: "Keep practicing armchairs vs chairs to reinforce the 'in' vs 'on' distinction.",
          subSkillBreakdown: { grammar: 10, comprehension: 10 }
        },
        wrong: {
          score: 7.5,
          summary: "Great reading work, with one minor armchair preposition mistake.",
          didWell: [
            "You correctly chose 'on the counter' and 'on the wall'.",
            "You correctly located the café 'between' the bakery and library."
          ],
          mistakes: [
            {
              issue: "An armchair has arms and surrounds you, so you sit *in* it.",
              userWrote: "on",
              correction: "in",
              rule: "Use 'in' for armchairs and 'on' for hard, armless chairs."
            }
          ],
          nextTip: "Ask yourself if the chair has arms or surrounds you; if so, use 'in'.",
          subSkillBreakdown: { grammar: 8, comprehension: 7 }
        }
      }
    },
    {
      taskId: "w1d7-listen-retell",
      feedbackInput: {
        taskId: "w1d7-listen-retell",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]"
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect oral summarization with precise prepositions.",
          didWell: [
            "You spoke clearly and structured the summary well.",
            "You correctly recalled 'next to it' and 'between two trees'."
          ],
          mistakes: [],
          nextTip: "Try retelling slightly longer audio clips in your next practice session.",
          subSkillBreakdown: { comprehension: 10, fluency: 10 }
        },
        wrong: {
          score: 5,
          summary: "Your summary was clear, but you made a few preposition slips.",
          didWell: [
            "Your speech pacing was very steady.",
            "You correctly located the bakery next to the fountain."
          ],
          mistakes: [
            {
              issue: "A specific point in town needs 'at', and playing among two trees is 'between'.",
              userWrote: "In the center... play on two trees",
              correction: "At the center... play between two trees",
              rule: "Use 'at the center' for points, and 'between' for a position relative to exactly two objects."
            }
          ],
          nextTip: "Before speaking, verify the preposition by checking the quantity of objects: 'between' for two, 'among' for three or more.",
          subSkillBreakdown: { comprehension: 6, fluency: 8 }
        }
      }
    },
    {
      taskId: "w1d7-write-paraphrase",
      feedbackInput: {
        taskId: "w1d7-write-paraphrase",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]"
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect preposition corrections!",
          didWell: [
            "You used 'good at' correctly.",
            "You correctly matched 'depend on' and 'on Monday'."
          ],
          mistakes: [],
          nextTip: "Practice using these collocations in your own emails.",
          subSkillBreakdown: { grammar: 10, expression: 10 }
        },
        wrong: {
          score: 6.6,
          summary: "Good sentences, but you missed one preposition collocation.",
          didWell: [
            "You correctly matched 'depend on' and 'on Monday'."
          ],
          mistakes: [
            {
              issue: "Collocation for talent/ability uses 'at' instead of 'in'.",
              userWrote: "good in English",
              correction: "good at English",
              rule: "Use the preposition 'at' after 'good' to indicate an ability (e.g. good at math, good at English)."
            }
          ],
          nextTip: "Keep a small mental list of common prepositions following adjectives, like 'good at', 'interested in', 'afraid of'.",
          subSkillBreakdown: { grammar: 7, expression: 6 }
        }
      }
    },
    {
      taskId: "w1d7-speak-present",
      feedbackInput: {
        taskId: "w1d7-speak-present",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]"
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Outstanding presentation of the cozy room!",
          didWell: [
            "Your description of the coffee table and sofa was flawless.",
            "You contrasted 'next to' and 'between' very naturally."
          ],
          mistakes: [],
          nextTip: "Try writing down a description of your own bedroom using the same prepositions.",
          subSkillBreakdown: { fluency: 10, pronunciation: 10 }
        },
        wrong: {
          score: 5,
          summary: "Good attempt, but some prepositions described impossible room layouts.",
          didWell: [
            "Your pronunciation of the nouns was very clear.",
            "You correctly identified all key furniture objects."
          ],
          mistakes: [
            {
              issue: "The spatial description put items in impossible places (e.g. mug under table, plant inside sofa).",
              userWrote: "mug under table... plant inside sofa... picture on windows",
              correction: "mug on table... plant next to sofa... picture between windows",
              rule: "Verify the visual cues: mugs sit *on* tables, plants stand *next to* sofas, and pictures hang *between* windows."
            }
          ],
          nextTip: "Look closely at the visual prompt and double check the position of each item before recording.",
          subSkillBreakdown: { fluency: 8, pronunciation: 6 }
        }
      }
    }
  ],
  ragFeedback: {
    dayId: "day_24_01_07",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]"
      ],
      learnerHistoryRef: "mock.userMemory.prepositions_foundation"
    },
    outputs: {
      correct: "An absolute triumph to end the week! You have demonstrated A2-level mastery of spatial prepositions. Your room description presentation was beautifully structured and grammatically perfect. You should feel incredibly confident!",
      wrong: "A solid wrap-up to the week, showing a strong grasp of preposition meaning, though conversational speaking can lead to minor errors (like putting the plant *inside* the sofa!). Spend a little time scanning the scene before speaking to boost your confidence. Great effort this week!"
    }
  }
};

const weekTwoDayOneFeedback: FeedbackDayData = {
  dayId: "day_24_02_01",
  activityFeedback: [
    {
      taskId: "w2d1-read-intro-mcq",
      feedbackInput: {
        taskId: "w2d1-read-intro-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "You understood the greeting chat perfectly.",
          didWell: [
            "You noticed the introduction phrase and the polite reply.",
            "You understood that a follow-up question keeps the conversation moving.",
          ],
          mistakes: [],
          nextTip: "Keep watching for greeting phrases like 'by the way' and 'nice to meet you' in short chats.",
          subSkillBreakdown: { comprehension: 10, tone: 8 },
        },
        wrong: {
          score: 6.7,
          summary: "You followed most of the chat, but one polite response was missed.",
          didWell: [
            "You recognized how Arjun introduced himself.",
            "You understood why Emma asked a follow-up question.",
          ],
          mistakes: [
            {
              issue: "After hearing a person's name for the first time, the natural reply is a greeting such as 'Nice to meet you, Arjun.'",
              userWrote: "Where is your teacher?",
              correction: "Nice to meet you, Arjun.",
              rule: "Use a polite meeting phrase after someone introduces themselves.",
            },
          ],
          nextTip: "When you read a first-meeting chat, look for the line that responds warmly to the name introduction.",
          subSkillBreakdown: { comprehension: 7, tone: 6 },
        },
      },
    },
    {
      taskId: "w2d1-listen-greeting-mcq",
      feedbackInput: {
        taskId: "w2d1-listen-greeting-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Strong listening for greeting language.",
          didWell: [
            "You caught the reason the speakers started talking.",
            "You heard the polite reply and the final follow-up question clearly.",
          ],
          mistakes: [],
          nextTip: "In greeting dialogues, listen closely for the short response right after 'Nice to meet you.'",
          subSkillBreakdown: { comprehension: 10, tone: 8 },
        },
        wrong: {
          score: 6.7,
          summary: "You understood the main situation, but one response line changed.",
          didWell: [
            "You identified the class connection correctly.",
            "You heard the follow-up question at the end.",
          ],
          mistakes: [
            {
              issue: "Daniel answers the greeting politely before asking another question.",
              userWrote: "Thank you for calling.",
              correction: "Nice to meet you too.",
              rule: "A common spoken response to 'Nice to meet you' is 'Nice to meet you too.'",
            },
          ],
          nextTip: "When the first speaker says 'Nice to meet you,' expect a matching reply before the conversation continues.",
          subSkillBreakdown: { comprehension: 7, tone: 6 },
        },
      },
    },
    {
      taskId: "w2d1-write-intro-transform",
      feedbackInput: {
        taskId: "w2d1-write-intro-transform",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.6,
          summary: "Your introductions sound polite and natural.",
          didWell: [
            "You expanded the short lines into full, friendly sentences.",
            "You used 'my name is' and 'Nice to meet you' naturally.",
          ],
          mistakes: [],
          nextTip: "Try adding one extra detail after your introduction, like where you are from or what you study.",
          subSkillBreakdown: { grammar: 10, expression: 9, tone: 9 },
        },
        wrong: {
          score: 7.2,
          summary: "Your meaning is clear, but one introduction still needs an article.",
          didWell: [
            "Your first two introductions are smooth and polite.",
            "You kept the tone friendly and easy to understand.",
          ],
          mistakes: [
            {
              issue: "Singular job or study nouns usually need an article.",
              userWrote: "Hello, I'm design student.",
              correction: "Hello, I'm a design student.",
              rule: "Use 'a' before a singular countable noun like student, teacher, or designer.",
            },
          ],
          nextTip: "When you introduce your work or studies, pause and check whether the noun needs 'a' or 'an'.",
          subSkillBreakdown: { grammar: 7, expression: 8, tone: 7 },
        },
      },
    },
    {
      taskId: "w2d1-speak-intro-roleplay",
      feedbackInput: {
        taskId: "w2d1-speak-intro-roleplay",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.4,
          summary: "Confident, natural first-meeting speaking.",
          didWell: [
            "You introduced yourself clearly and sounded friendly.",
            "You added a simple follow-up question to keep the conversation going.",
          ],
          mistakes: [],
          nextTip: "Next time, add one extra personal detail after your name to make the introduction even warmer.",
          subSkillBreakdown: { fluency: 9, grammar: 9, tone: 10 },
        },
        wrong: {
          score: 5.5,
          summary: "Your conversation flow is friendly, but one introduction phrase is incomplete.",
          didWell: [
            "Your greeting and name introduction are clear.",
            "You remembered to ask a follow-up question.",
          ],
          mistakes: [
            {
              issue: "A singular study or job noun needs an article in spoken introductions too.",
              userWrote: "I'm design student.",
              correction: "I'm a design student.",
              rule: "Use 'a' before singular countable nouns when saying what you do or study.",
            },
          ],
          nextTip: "Practice one full chunk aloud: 'I'm a student.' 'I'm a designer.' 'I'm an engineer.'",
          subSkillBreakdown: { fluency: 8, grammar: 3, tone: 6 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_02_01",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.communication_greetings_foundation",
    },
    outputs: {
      correct:
        "You made a strong start to communication week. You can already greet someone politely, introduce yourself clearly, and keep the conversation alive with one simple follow-up question. That is exactly the foundation you need for natural first meetings.",
      wrong:
        "Your main communication skill is already there: you sound friendly and you know how to continue a first conversation. The biggest thing to polish is sentence shape inside introductions, especially short chunks like 'I'm a student.' Keep practicing these full patterns until they feel automatic.",
    },
  },
};

const weekTwoDayTwoFeedback: FeedbackDayData = {
  dayId: "day_24_02_02",
  activityFeedback: [
    {
      taskId: "w2d2-read-tfng",
      feedbackInput: {
        taskId: "w2d2-read-tfng",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent reading of the question-and-answer dialogue.",
          didWell: [
            "You separated directly stated facts from missing information.",
            "You noticed Ben agrees to practice and asks a follow-up question.",
          ],
          mistakes: [],
          nextTip: "For TFNG tasks, keep matching each statement to one exact sentence in the dialogue.",
          subSkillBreakdown: { comprehension: 10, grammar: 8 },
        },
        wrong: {
          score: 7.5,
          summary: "You understood most of the dialogue, with one agreement detail to fix.",
          didWell: [
            "You found the meeting place and recognized the Not Given statement.",
          ],
          mistakes: [
            {
              issue: "Ben agrees to practice, so the statement that he cannot practice is false.",
              userWrote: "True",
              correction: "False",
              rule: "If the statement disagrees with the dialogue, choose False.",
            },
          ],
          nextTip: "When a statement includes can or cannot, check the speaker's answer carefully.",
          subSkillBreakdown: { comprehension: 8, grammar: 7 },
        },
      },
    },
    {
      taskId: "w2d2-listen-infer",
      feedbackInput: {
        taskId: "w2d2-listen-infer",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Strong listening inference: you understood what the speakers meant.",
          didWell: [
            "You recognized the polite request opening.",
            "You caught that Leo agrees but limits his time.",
          ],
          mistakes: [],
          nextTip: "Keep listening for soft request phrases like 'Could you...' and 'Can I ask...'",
          subSkillBreakdown: { comprehension: 10, tone: 8 },
        },
        wrong: {
          score: 7.5,
          summary: "You understood the request, but one intent clue changed the meaning.",
          didWell: [
            "You correctly identified Mina's main request and her offer to bring markers.",
          ],
          mistakes: [
            {
              issue: "Leo does not refuse. He agrees, but only for ten minutes.",
              userWrote: "He is refusing to help.",
              correction: "He is limiting how long he can help.",
              rule: "A time limit after yes or I can usually means partial availability, not refusal.",
            },
          ],
          nextTip: "Listen for contrast between agreement words and limits like 'for ten minutes' or 'only today.'",
          subSkillBreakdown: { comprehension: 8, tone: 6 },
        },
      },
    },
    {
      taskId: "w2d2-write-email",
      feedbackInput: {
        taskId: "w2d2-write-email",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.4,
          summary: "Your message asks a clear, polite question.",
          didWell: [
            "You used a direct question with 'Can we...?'",
            "You included a useful time phrase and a polite close.",
          ],
          mistakes: [],
          nextTip: "Next time, add one optional follow-up question like 'What time is good for you?'",
          subSkillBreakdown: { expression: 9, grammar: 9, tone: 10, vocabulary: 8 },
        },
        wrong: {
          score: 7,
          summary: "Your message is understandable, with one question-form grammar issue.",
          didWell: [
            "Your greeting, purpose, and polite close are clear.",
          ],
          mistakes: [
            {
              issue: "After 'Can we', use the base verb.",
              userWrote: "Can we meeting after class today?",
              correction: "Can we meet after class today?",
              rule: "Modal verbs like can and could are followed by the base verb: can meet, could help.",
            },
          ],
          nextTip: "Practice the chunk 'Can we meet...?' until it feels automatic.",
          subSkillBreakdown: { expression: 8, grammar: 6, tone: 8, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w2d2-speak-interview",
      feedbackInput: {
        taskId: "w2d2-speak-interview",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.3,
          summary: "Clear interview answers with friendly A1 sentence control.",
          didWell: [
            "You answered each question directly.",
            "You used full chunks for name, study/work, and hobby.",
          ],
          mistakes: [],
          nextTip: "Try adding one extra detail after each answer, such as where you study or when you do your hobby.",
          subSkillBreakdown: { fluency: 9, pronunciation: 9, grammar: 9, tone: 9 },
        },
        wrong: {
          score: 7.1,
          summary: "Your interview flow is clear, with one missing article.",
          didWell: [
            "Your name and hobby answers are natural.",
            "Your pronunciation and response timing are easy to follow.",
          ],
          mistakes: [
            {
              issue: "A singular study or job noun needs an article.",
              userWrote: "I'm design student.",
              correction: "I'm a design student.",
              rule: "Use 'a' before singular countable roles: a student, a teacher, a designer.",
            },
          ],
          nextTip: "Practice the pattern 'I'm a...' before job and study words.",
          subSkillBreakdown: { fluency: 8, pronunciation: 8, grammar: 6, tone: 7 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_02_02",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.communication_questions_foundation",
    },
    outputs: {
      correct:
        "You are building a useful conversation habit: ask a clear question, answer directly, and add one follow-up question. You also showed good listening inference by noticing when a speaker is requesting help versus setting a time limit.",
      wrong:
        "Your conversation meaning is mostly clear. The main pattern to polish is question grammar after can or could, plus the article in 'I'm a student.' Keep practicing these short chunks: 'Can we meet?' and 'I'm a...'",
    },
  },
};

const weekTwoDayThreeFeedback: FeedbackDayData = {
  dayId: "day_24_02_03",
  activityFeedback: [
    {
      taskId: "w2d3-read-structure",
      feedbackInput: {
        taskId: "w2d3-read-structure",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "You identified the routine structure clearly.",
          didWell: [
            "You separated the main idea, ordered details, and closing thought.",
            "You noticed how sequence words support the body paragraph.",
          ],
          mistakes: [],
          nextTip: "When you write your own routine, use this same intro, body, and conclusion pattern.",
          subSkillBreakdown: { comprehension: 10, expression: 8 },
        },
        wrong: {
          score: 6.7,
          summary: "You understood the topic, but mixed up the details paragraph.",
          didWell: [
            "You correctly found the intro and the conclusion.",
            "You recognized that the passage is about a daily routine.",
          ],
          mistakes: [
            {
              issue: "The middle paragraph gives the ordered actions, so it is the body.",
              userWrote: "Conclusion",
              correction: "Body",
              rule: "The body of a routine passage gives the main details in order.",
            },
          ],
          nextTip: "Look for sequence words like first, then, and after that; they often mark the body.",
          subSkillBreakdown: { comprehension: 7, expression: 6 },
        },
      },
    },
    {
      taskId: "w2d3-listen-retell",
      feedbackInput: {
        taskId: "w2d3-listen-retell",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.4,
          summary: "Your retell kept the main actions in order.",
          didWell: [
            "You remembered the wake-up time, morning actions, commute, and evening routine.",
            "You used sequence words to make the retell easy to follow.",
          ],
          mistakes: [],
          nextTip: "Next time, add one more afternoon detail if you want a fuller retell.",
          subSkillBreakdown: { comprehension: 10, fluency: 9, vocabulary: 8 },
        },
        wrong: {
          score: 7.1,
          summary: "Your retell is understandable, with one changed routine detail.",
          didWell: [
            "You caught the wake-up time and several morning actions.",
            "Your sequence words made the response organized.",
          ],
          mistakes: [
            {
              issue: "The audio says the speaker cooks dinner after work, not lunch at work.",
              userWrote: "Then they cook lunch at work",
              correction: "After work, they cook dinner",
              rule: "When retelling, keep meals and time phrases matched to the original audio.",
            },
          ],
          nextTip: "Listen especially for time markers like in the afternoon and after work before retelling.",
          subSkillBreakdown: { comprehension: 7, fluency: 8, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w2d3-write-para",
      feedbackInput: {
        taskId: "w2d3-write-para",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.2,
          summary: "Your daily routine paragraph is clear and natural.",
          didWell: [
            "You used simple present verbs for routine actions.",
            "You connected the paragraph with first, then, after that, and finally.",
          ],
          mistakes: [],
          nextTip: "Try adding one feeling sentence, such as 'This routine helps me feel calm.'",
          subSkillBreakdown: { grammar: 9, expression: 9, fluency: 9, vocabulary: 8 },
        },
        wrong: {
          score: 7.2,
          summary: "Your paragraph is organized, with one simple present verb error.",
          didWell: [
            "Your sequence words make the routine easy to follow.",
            "Most verbs are accurate and natural.",
          ],
          mistakes: [
            {
              issue: "After I, use the base verb form.",
              userWrote: "I brushes my teeth",
              correction: "I brush my teeth",
              rule: "Use the base verb with I, you, we, and they in the simple present.",
            },
          ],
          nextTip: "After writing, scan every I sentence and check that the verb has no extra -s.",
          subSkillBreakdown: { grammar: 6, expression: 8, fluency: 8, vocabulary: 8 },
        },
      },
    },
    {
      taskId: "w2d3-speak-opinion",
      feedbackInput: {
        taskId: "w2d3-speak-opinion",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.1,
          summary: "Your spoken opinion is clear and complete.",
          didWell: [
            "You stated a preference directly.",
            "You gave a reason with because and sounded natural.",
          ],
          mistakes: [],
          nextTip: "To extend the answer, add one example of what you do in the morning or evening.",
          subSkillBreakdown: { fluency: 9, pronunciation: 9, grammar: 9, expression: 9 },
        },
        wrong: {
          score: 7,
          summary: "Your opinion is easy to understand, with one verb form to fix.",
          didWell: [
            "You gave a clear preference and reason.",
            "Your answer length is right for a short speaking task.",
          ],
          mistakes: [
            {
              issue: "After I, use feel instead of feeling in this sentence.",
              userWrote: "I feeling fresh",
              correction: "I feel fresh",
              rule: "Use subject plus simple present verb for states: I feel, I like, I prefer.",
            },
          ],
          nextTip: "Practice the chunk 'I prefer morning because I feel...' until it sounds automatic.",
          subSkillBreakdown: { fluency: 8, pronunciation: 8, grammar: 6, expression: 7 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_02_03",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.daily_life_routine_fluency",
    },
    outputs: {
      correct:
        "You are ready to talk about daily life with more flow. Your strongest pattern today was organization: you can notice a routine structure, retell actions in order, and use sequence words in writing and speaking.",
      wrong:
        "Your daily-life communication is understandable, and the main thing to polish is verb control when you speak or write quickly. Keep using sequence words, then slow down for I plus base verb patterns like I brush and I feel.",
    },
  },
};

const weekTwoDayFourFeedback: FeedbackDayData = {
  dayId: "day_24_02_04",
  activityFeedback: [
    {
      taskId: "w2d4-read-comp-mcq",
      feedbackInput: {
        taskId: "w2d4-read-comp-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect reading comprehension of the shopping dialogue.",
          didWell: [
            "You accurately matched specific details in the passage.",
            "You correctly identified the location of the honey and bakery items.",
          ],
          mistakes: [],
          nextTip: "Continue scanning dialogues for specific keywords when answering location-based questions.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 8 },
        },
        wrong: {
          score: 6.7,
          summary: "You got the main ideas, but one location detail was missed.",
          didWell: [
            "You correctly found the strawberries and bakery details.",
          ],
          mistakes: [
            {
              issue: "The honey is in aisle 4, not aisle 2.",
              userWrote: "In aisle 2",
              correction: "On the middle shelf in aisle 4",
              rule: "Always check which aisle corresponds to which item: aisle 2 was for strawberries.",
            },
          ],
          nextTip: "Cross-reference aisle numbers with the specific nouns mentioned right next to them.",
          subSkillBreakdown: { comprehension: 7, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w2d4-listen-mcq",
      feedbackInput: {
        taskId: "w2d4-listen-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent listening comprehension of the café order.",
          didWell: [
            "You heard the specific milk preference (oat milk) correctly.",
            "You captured the total price and food choice perfectly.",
          ],
          mistakes: [],
          nextTip: "In food-ordering contexts, keep listening for modifiers like sizes, temperature, and milk choices.",
          subSkillBreakdown: { comprehension: 10, tone: 8 },
        },
        wrong: {
          score: 6.7,
          summary: "You understood most of the order, but missed one specific food item.",
          didWell: [
            "You captured the milk preference and price successfully.",
          ],
          mistakes: [
            {
              issue: "The customer ordered a muffin, not a cookie.",
              userWrote: "Chocolate cookie",
              correction: "Warm blueberry muffin",
              rule: "Listen closely to the food noun following the main verb (e.g. 'take a warm blueberry muffin').",
            },
          ],
          nextTip: "Expect ordering phrases like 'I'll take a...' followed directly by the item name.",
          subSkillBreakdown: { comprehension: 7, tone: 6 },
        },
      },
    },
    {
      taskId: "w2d4-write-bullets-para",
      feedbackInput: {
        taskId: "w2d4-write-bullets-para",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.3,
          summary: "Your shopping list message is polite, clear, and perfectly formatted.",
          didWell: [
            "You successfully turned all 4 bullet points into full sentences.",
            "You naturally incorporated polite requests ('Could you please') and all target words.",
          ],
          mistakes: [],
          nextTip: "When translating lists to messages, always maintain this polite tone and clear list structure.",
          subSkillBreakdown: { expression: 9, grammar: 9, tone: 9, vocabulary: 8 },
        },
        wrong: {
          score: 7,
          summary: "Your message is clear, but needs better prepositional accuracy.",
          didWell: [
            "You mentioned the correct items and kept a friendly tone.",
          ],
          mistakes: [
            {
              issue: "Missing 'of' in count-measure phrases.",
              userWrote: "1 carton almond milk",
              correction: "1 carton of almond milk",
              rule: "Use 'of' after container/quantity nouns: carton of milk, pack of pasta, loaf of bread.",
            },
          ],
          nextTip: "Always review quantity structures: [number] + [unit] + 'of' + [noun].",
          subSkillBreakdown: { expression: 7, grammar: 6, tone: 7, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w2d4-speak-roleplay",
      feedbackInput: {
        taskId: "w2d4-speak-roleplay",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.4,
          summary: "Outstanding grocery shopping roleplay!",
          didWell: [
            "You stated your items politely using 'I'm looking for...'.",
            "You answered the shopkeeper's questions naturally.",
          ],
          mistakes: [],
          nextTip: "Keep practicing roleplay exercises to build real-world confidence in public interactions.",
          subSkillBreakdown: { fluency: 9, grammar: 9, tone: 10 },
        },
        wrong: {
          score: 5.5,
          summary: "Your response is mostly understandable, but has grammatical errors in item description.",
          didWell: [
            "You had a polite greeting and correct item nouns.",
          ],
          mistakes: [
            {
              issue: "Incomplete present continuous verb form.",
              userWrote: "I looking for tomatoes",
              correction: "I'm looking for tomatoes",
              rule: "Use subject pronoun + 'am/is/are' + verb-ing for active searching: 'I am looking for...'",
            },
          ],
          nextTip: "Slightly slow down when saying 'I'm looking for' to make sure the 'm' contraction is clearly pronounced.",
          subSkillBreakdown: { fluency: 8, grammar: 3, tone: 6 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_02_04",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.shopping_ordering_interactions",
    },
    outputs: {
      correct:
        "Fantastic progress today! You successfully handled real-world interactions for shopping and ordering. You have a solid grasp of polite request structures like 'Could I have' and descriptive grocery shopping roleplay.",
      wrong:
        "You did a great job following real-world dialogues. To polish your skills further, focus on full continuous forms (e.g. 'I'm looking for') and using prepositions like 'of' inside measurement phrases (e.g. 'carton of milk'). Keep practicing these core patterns!",
    },
  },
};

const weekTwoDayFiveFeedback: FeedbackDayData = {
  dayId: "day_24_02_05",
  activityFeedback: [
    {
      taskId: "w2d5-read-directions-tfng",
      feedbackInput: {
        taskId: "w2d5-read-directions-tfng",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "You read the direction text accurately.",
          didWell: [
            "You followed the starting point and turn direction.",
            "You separated stated directions from information that was not given.",
          ],
          mistakes: [],
          nextTip: "Keep underlining landmarks when you read directions: bus stop, bakery, pharmacy, station.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 8 },
        },
        wrong: {
          score: 7.5,
          summary: "You understood most directions, but mixed up left and right at the bakery.",
          didWell: [
            "You found the starting point and the station location.",
            "You correctly noticed that the bakery opening time was not given.",
          ],
          mistakes: [
            {
              issue: "The text says to turn left at the bakery.",
              userWrote: "True",
              correction: "False",
              rule: "For directions, left and right change the route, so check these words slowly.",
            },
          ],
          nextTip: "When reading directions, circle each movement word before answering.",
          subSkillBreakdown: { comprehension: 7, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w2d5-listen-help-infer",
      feedbackInput: {
        taskId: "w2d5-listen-help-infer",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "You understood the help request and the speaker's intent.",
          didWell: [
            "You identified that the traveler needed directions to the station.",
            "You caught the distance question and the pharmacy landmark.",
          ],
          mistakes: [],
          nextTip: "In real conversations, listen for the place name right after the help phrase.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 8 },
        },
        wrong: {
          score: 7.5,
          summary: "You understood the main request, but missed the distance meaning.",
          didWell: [
            "You recognized the polite help request.",
            "You identified the station and pharmacy details.",
          ],
          mistakes: [
            {
              issue: "Is it far from here? asks about distance, not time.",
              userWrote: "They are asking for the time.",
              correction: "They want to know the distance.",
              rule: "Far means distance. Use far, near, and about five minutes for location questions.",
            },
          ],
          nextTip: "When you hear far or near, think distance first.",
          subSkillBreakdown: { comprehension: 7, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w2d5-write-station-help",
      feedbackInput: {
        taskId: "w2d5-write-station-help",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.3,
          summary: "Your help request is polite, clear, and practical.",
          didWell: [
            "You opened with Excuse me and asked for help naturally.",
            "You named the station and added a useful follow-up question.",
          ],
          mistakes: [],
          nextTip: "Try adding one landmark question next time, like 'Is it near the pharmacy?'",
          subSkillBreakdown: { expression: 9, grammar: 9, vocabulary: 8, tone: 9 },
        },
        wrong: {
          score: 7,
          summary: "Your request is understandable, but two question patterns need cleaning up.",
          didWell: [
            "You used a polite opening and named the station.",
            "You included a thank-you, which makes the request sound friendly.",
          ],
          mistakes: [
            {
              issue: "The sentence needs am after I.",
              userWrote: "I trying to find the station.",
              correction: "I am trying to find the station.",
              rule: "Use am plus verb-ing after I for an action happening now.",
            },
            {
              issue: "In a direct question, put should before I.",
              userWrote: "Which way I should go from here?",
              correction: "Which way should I go from here?",
              rule: "Use question word + should + subject + base verb.",
            },
          ],
          nextTip: "Practise this full chunk: Which way should I go from here?",
          subSkillBreakdown: { expression: 8, grammar: 6, vocabulary: 7, tone: 8 },
        },
      },
    },
    {
      taskId: "w2d5-speak-map-desc",
      feedbackInput: {
        taskId: "w2d5-speak-map-desc",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.2,
          summary: "Your map description used clear place language.",
          didWell: [
            "You located the bus stop, bakery, pharmacy, and station.",
            "You used next to naturally for the station and pharmacy.",
          ],
          mistakes: [],
          nextTip: "Add route verbs next time: go straight, turn left, then walk past the pharmacy.",
          subSkillBreakdown: { fluency: 9, pronunciation: 9, expression: 9, vocabulary: 8 },
        },
        wrong: {
          score: 7,
          summary: "Your speaking was clear, but one map location was inaccurate.",
          didWell: [
            "You named the main places on the map.",
            "Your sentences were short and easy to follow.",
          ],
          mistakes: [
            {
              issue: "The map shows the station next to the pharmacy, not the cafe.",
              userWrote: "The station is next to the cafe.",
              correction: "The station is next to the pharmacy.",
              rule: "Use next to for two places that are side by side on the map.",
            },
          ],
          nextTip: "Before speaking, choose two landmarks and say their relationship: X is next to Y.",
          subSkillBreakdown: { fluency: 8, pronunciation: 8, expression: 7, vocabulary: 6 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_02_05",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.survival_directions",
    },
    outputs: {
      correct:
        "You handled survival communication very well today. You can ask for help politely, follow simple directions, understand what a traveler needs, and describe map locations with useful phrases like next to and on the right.",
      wrong:
        "You are close to solid survival-direction English. The main pattern to sharpen is location precision: left versus right, far versus time, and next to which landmark. Your polite help phrases are already working, so keep pairing them with one exact place word.",
    },
  },
};

const weekTwoDaySixFeedback: FeedbackDayData = {
  dayId: "day_24_02_06",
  activityFeedback: [
    {
      taskId: "w2d6-read-tone",
      feedbackInput: {
        taskId: "w2d6-read-tone",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "You identified both message tones clearly.",
          didWell: [
            "You noticed polite formal wording in the work message.",
            "You recognized casual chat clues like Hey and the smiley.",
          ],
          mistakes: [],
          nextTip: "When you read online messages, look for greeting style, contractions, and urgency words.",
          subSkillBreakdown: { tone: 10, comprehension: 9 },
        },
        wrong: {
          score: 5,
          summary: "You found the formal message, but the friend message was casual, not urgent.",
          didWell: [
            "You correctly identified the polite work message as formal.",
            "You understood the basic meaning of both messages.",
          ],
          mistakes: [
            {
              issue: "The friend message is friendly and relaxed, not urgent.",
              userWrote: "Urgent",
              correction: "Casual",
              rule: "Casual messages often use short forms, friendly greetings, and emojis.",
            },
          ],
          nextTip: "Urgent messages usually include time pressure, like now, immediately, or as soon as possible.",
          subSkillBreakdown: { tone: 5, comprehension: 6 },
        },
      },
    },
    {
      taskId: "w2d6-listen-tone",
      feedbackInput: {
        taskId: "w2d6-listen-tone",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "You caught the urgency in the phone call.",
          didWell: [
            "You noticed the time pressure in now and in the next five minutes.",
            "You separated polite language from the urgent situation.",
          ],
          mistakes: [],
          nextTip: "In calls, listen for both wording and timing; a polite request can still be urgent.",
          subSkillBreakdown: { comprehension: 10, tone: 10 },
        },
        wrong: {
          score: 6,
          summary: "You heard the friendly wording, but missed the time pressure.",
          didWell: [
            "You understood that the speaker was calling someone they know.",
            "You noticed polite request language.",
          ],
          mistakes: [
            {
              issue: "The speaker needs help in the next five minutes, so the tone is urgent.",
              userWrote: "Casual",
              correction: "Urgent",
              rule: "Urgency comes from immediate time markers like now and in the next five minutes.",
            },
          ],
          nextTip: "When listening for tone, write down any time words before choosing an answer.",
          subSkillBreakdown: { comprehension: 6, tone: 6 },
        },
      },
    },
    {
      taskId: "w2d6-write-paraphrase",
      feedbackInput: {
        taskId: "w2d6-write-paraphrase",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.4,
          summary: "Your rewrites keep the meaning and change the register well.",
          didWell: [
            "You made the first message casual without losing the request.",
            "You made the second message polite and complete for a formal reader.",
          ],
          mistakes: [],
          nextTip: "Keep matching the greeting and word choice to the relationship.",
          subSkillBreakdown: { expression: 9, tone: 10, vocabulary: 8 },
        },
        wrong: {
          score: 7,
          summary: "Your casual rewrite is strong, but the formal rewrite still sounds too casual.",
          didWell: [
            "You changed the first formal message into a natural chat text.",
            "You kept the main meaning of the second message.",
          ],
          mistakes: [
            {
              issue: "For a formal message, avoid can't and vague words like net.",
              userWrote: "Hey sir, I can't join today because net is bad.",
              correction:
                "Dear Sir, I am sorry, but I cannot join today because my internet connection is poor.",
              rule: "Formal messages use polite greetings, complete forms, and clearer nouns.",
            },
          ],
          nextTip: "For formal rewrites, expand short chat words: can't to cannot and net to internet connection.",
          subSkillBreakdown: { expression: 7, tone: 6, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w2d6-speak-smalltalk",
      feedbackInput: {
        taskId: "w2d6-speak-smalltalk",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.2,
          summary: "Your smalltalk answers sound friendly and natural.",
          didWell: [
            "You answered the weather and weekend prompt with a clear plan.",
            "You gave a simple Saturday routine with good rhythm.",
          ],
          mistakes: [],
          nextTip: "To keep smalltalk going, add one return question like 'What about you?'",
          subSkillBreakdown: { fluency: 9, pronunciation: 9, expression: 9, tone: 9 },
        },
        wrong: {
          score: 7.2,
          summary: "Your smalltalk is friendly, with one verb form to clean up.",
          didWell: [
            "Your first answer sounds casual and confident.",
            "You gave enough weekend detail for a natural short chat.",
          ],
          mistakes: [
            {
              issue: "After I usually, use the base verb relax.",
              userWrote: "I usually relaxing at home",
              correction: "I usually relax at home",
              rule: "Use usually plus the base verb for habits: I usually relax.",
            },
          ],
          nextTip: "Practice one smooth chunk: I usually relax at home on Saturdays.",
          subSkillBreakdown: { fluency: 8, pronunciation: 8, expression: 7, grammar: 6 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_02_06",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.modern_communication_tone",
    },
    outputs: {
      correct:
        "You handled modern communication with strong tone control today. You can read online tone, hear urgency in a phone call, shift a message between formal and casual, and still sound relaxed in smalltalk.",
      wrong:
        "You are getting comfortable with modern communication. The main pattern to sharpen is tone under time pressure: casual language can still be urgent when the speaker says now or in the next five minutes. Your writing and speaking stay understandable, so keep practicing the difference between friendly and immediate.",
    },
  },
};

const weekTwoDaySevenFeedback: FeedbackDayData = {
  dayId: "day_24_02_07",
  activityFeedback: [
    {
      taskId: "w2d7-read-structure",
      feedbackInput: {
        taskId: "w2d7-read-structure",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "You understood how the chat thread connects ideas.",
          didWell: [
            "You identified the greeting, shared weekly details, and reflective closing.",
            "You noticed the social flow of the conversation, not only the topic words.",
          ],
          mistakes: [],
          nextTip: "Use the same flow in your own small talk: open, share, reflect.",
          subSkillBreakdown: { comprehension: 10, expression: 8, tone: 8 },
        },
        wrong: {
          score: 6.7,
          summary: "You understood the chat, but mixed up the details section.",
          didWell: [
            "You correctly found the opening and closing reflection.",
            "You recognized that both speakers were talking about their week.",
          ],
          mistakes: [
            {
              issue: "The middle part gives examples from each person's week, so it is shared details.",
              userWrote: "Reflection",
              correction: "Shared Details",
              rule: "In a chat, examples and activities usually build the details section.",
            },
          ],
          nextTip: "Look for activity examples like studied, helped, went, or met; they usually signal details.",
          subSkillBreakdown: { comprehension: 7, expression: 6, tone: 6 },
        },
      },
    },
    {
      taskId: "w2d7-listen-retell",
      feedbackInput: {
        taskId: "w2d7-listen-retell",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.4,
          summary: "Your written retell captured the key points clearly.",
          didWell: [
            "You included both speakers and their main weekly activities.",
            "You kept the shared feeling and Sunday plan from the conversation.",
          ],
          mistakes: [],
          nextTip: "For an even stronger retell, add one connector such as meanwhile or after that.",
          subSkillBreakdown: { comprehension: 10, fluency: 9, vocabulary: 8 },
        },
        wrong: {
          score: 7.2,
          summary: "Your retell is organized, with one changed listening detail.",
          didWell: [
            "You remembered Leo's work project and family dinner.",
            "You included the quiet Sunday idea.",
          ],
          mistakes: [
            {
              issue: "The audio says Asha studied English every evening, not every morning.",
              userWrote: "studied English every morning",
              correction: "studied English every evening",
              rule: "Keep time words matched to the original audio when retelling.",
            },
          ],
          nextTip: "When you hear a time word, quickly note it with the activity it belongs to.",
          subSkillBreakdown: { comprehension: 7, fluency: 8, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w2d7-write-email",
      feedbackInput: {
        taskId: "w2d7-write-email",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.3,
          summary: "Your message sounds friendly, clear, and complete.",
          didWell: [
            "You opened and closed the message naturally.",
            "You used past forms for completed weekly activities.",
          ],
          mistakes: [],
          nextTip: "Next time, add one return question to invite your friend to reply.",
          subSkillBreakdown: { grammar: 9, expression: 9, fluency: 9, tone: 9 },
        },
        wrong: {
          score: 7.1,
          summary: "Your message is friendly, with one tense slip.",
          didWell: [
            "The message has a warm opening and closing.",
            "You included activities and a feeling sentence.",
          ],
          mistakes: [
            {
              issue: "The project is completed, so use simple past.",
              userWrote: "I finish a small project",
              correction: "I finished a small project",
              rule: "Use simple past for completed actions in your week: finished, studied, met.",
            },
          ],
          nextTip: "After writing about your week, scan action verbs and check whether they are completed past events.",
          subSkillBreakdown: { grammar: 6, expression: 8, fluency: 8, tone: 8 },
        },
      },
    },
    {
      taskId: "w2d7-speak-present",
      feedbackInput: {
        taskId: "w2d7-speak-present",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.2,
          summary: "Your spoken week summary is structured and easy to follow.",
          didWell: [
            "You opened with an overall feeling, then added clear details.",
            "You ended with a simple next-week plan.",
          ],
          mistakes: [],
          nextTip: "To sound even more natural, add one short pause after each idea group.",
          subSkillBreakdown: { fluency: 9, pronunciation: 9, expression: 9, grammar: 9 },
        },
        wrong: {
          score: 7.1,
          summary: "Your spoken summary is clear, with one past-tense slip.",
          didWell: [
            "Your structure is strong: feeling, details, and next plan.",
            "Your pronunciation and pace are understandable.",
          ],
          mistakes: [
            {
              issue: "Finished work from this week needs the past form.",
              userWrote: "I finish a work project",
              correction: "I finished a work project",
              rule: "Use simple past for completed weekly actions.",
            },
          ],
          nextTip: "Before speaking, choose two past verbs you will need, such as finished and met.",
          subSkillBreakdown: { fluency: 8, pronunciation: 8, expression: 8, grammar: 6 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_02_07",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.small_talk_social_interaction",
    },
    outputs: {
      correct:
        "You finished the small-talk week with strong natural fluency. You can follow how a chat develops, retell the main points from a casual conversation, write warmly to a friend, and speak about your week with a clear beginning, middle, and ending.",
      wrong:
        "Your social communication is friendly and understandable. The main pattern to polish is keeping past-time details accurate: listen carefully for time words, then use simple past when you write or speak about completed weekly activities.",
    },
  },
};

const weekThreeDayOneFeedback: FeedbackDayData = {
  dayId: "day_24_03_01",
  activityFeedback: [
    {
      taskId: "w3d1-read-word-match",
      feedbackInput: {
        taskId: "w3d1-read-word-match",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect vocabulary matching!",
          didWell: [
            "You correctly identified the difference between family roles (uncle) and workplace roles (colleague).",
            "You accurately matched community relationship terms like neighbour and classmate.",
          ],
          mistakes: [],
          nextTip: "Continue to practice using relationship vocabulary in your daily conversations.",
          subSkillBreakdown: { vocabulary: 10, grammar: 8 },
        },
        wrong: {
          score: 7.5,
          summary: "Good effort, but you mixed up one of the professional roles.",
          didWell: [
            "You correctly matched the definition for family roles (uncle) and community roles (neighbour).",
          ],
          mistakes: [
            {
              issue: "A colleague is someone you work with in a professional environment, while a classmate is someone you study with in a school environment.",
              userWrote: "classmate",
              correction: "colleague",
              rule: "Use 'colleague' for work relationships and 'classmate' for school or educational environments.",
            },
          ],
          nextTip: "Try scanning definitions for environment keywords like 'work/job' versus 'school/class'.",
          subSkillBreakdown: { vocabulary: 7, grammar: 7 },
        },
      },
    },
    {
      taskId: "w3d1-listen-mcq",
      feedbackInput: {
        taskId: "w3d1-listen-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect listening comprehension of the relationships dialogue.",
          didWell: [
            "You heard David's identity as the speaker's uncle visiting from London.",
            "You correctly matched Priya's workplace role and Mark's neighbor role.",
          ],
          mistakes: [],
          nextTip: "Listen for prepositions of place like 'from' or 'next door' to capture role details in the future.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 8 },
        },
        wrong: {
          score: 6.7,
          summary: "You got the main family detail, but missed one workplace location cue.",
          didWell: [
            "You correctly heard David's relationship and Mark's neighbor role.",
          ],
          mistakes: [
            {
              issue: "The speaker says Priya is 'from the office', so she works at the office, not at school.",
              userWrote: "At the same school",
              correction: "At the office",
              rule: "Listen closely to location nouns that follow relationship introductions to map the role correctly.",
            },
          ],
          nextTip: "Look out for place words like 'office' to immediately confirm the workplace connection.",
          subSkillBreakdown: { comprehension: 7, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w3d1-write-sent-trans",
      feedbackInput: {
        taskId: "w3d1-write-sent-trans",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent work on sentence transformations!",
          didWell: [
            "You used target nouns colleague and classmate perfectly in place of long phrases.",
            "You maintained correct singular grammatical agreement and possessive structures.",
          ],
          mistakes: [],
          nextTip: "Practice replacing descriptive clauses with precise single relationship nouns to make your writing concise.",
          subSkillBreakdown: { expression: 10, grammar: 10, vocabulary: 8 },
        },
        wrong: {
          score: 5,
          summary: "Your sentences are mostly clear, but has one pluralization slip.",
          didWell: [
            "You understood the first transformation to 'colleague' perfectly.",
          ],
          mistakes: [
            {
              issue: "Plural nouns are used for multiple people. For a single male student, use classmate instead of classmates.",
              userWrote: "He is my classmates.",
              correction: "He is my classmate.",
              rule: "Use singular form 'classmate' when referring to a single subject ('He').",
            },
          ],
          nextTip: "Always review subject-verb and subject-noun singular/plural agreement in your rewritten sentences.",
          subSkillBreakdown: { expression: 6, grammar: 4, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w3d1-speak-pic-desc",
      feedbackInput: {
        taskId: "w3d1-speak-pic-desc",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.5,
          summary: "Stunning family photo spoken description!",
          didWell: [
            "You described each person clearly using relationship terms.",
            "Your speech flow and timing were extremely natural.",
          ],
          mistakes: [],
          nextTip: "You can expand your response by adding one simple activity they might be doing together.",
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          score: 6,
          summary: "Clear spoken attempt, but you used one wrong role vocabulary.",
          didWell: [
            "Your pronunciation and pacing were steady.",
            "You identified David's and Priya's roles correctly.",
          ],
          mistakes: [
            {
              issue: "The image and context indicate Mark is a neighbour, not a classmate.",
              userWrote: "classmate",
              correction: "neighbour",
              rule: "Double check the visual labels or description prompts to match the correct community role.",
            },
          ],
          nextTip: "Focus on visual cues or text labels in the prompt before describing relationships.",
          subSkillBreakdown: { fluency: 8, pronunciation: 8, grammar: 6, vocabulary: 5 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_03_01",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.people_relationships_roles",
    },
    outputs: {
      correct:
        "Incredible start to Week 3! You showed an excellent grasp of people, family, and workplace roles. You naturally transitioned from descriptive phrases to precise nouns (colleague, classmate) and demonstrated excellent comprehension in listening and matching tasks.",
      wrong:
        "A promising start to relationship vocabulary! You have a good base, but need to be mindful of singular/plural agreement (classmate vs classmates) and double-check specific environmental context clues (workplace colleague vs school classmate). Keep practicing!",
    },
  },
};

const weekThreeDayTwoFeedback: FeedbackDayData = {
  dayId: "day_24_03_02",
  activityFeedback: [
    {
      taskId: "w3d2-read-context-mcq",
      feedbackInput: {
        taskId: "w3d2-read-context-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect context comprehension!",
          didWell: [
            "You correctly inferred that 'savoury' means salty/spicy by contrasting it with sweet desserts."
          ],
          mistakes: [],
          nextTip: "Keep scanning texts for contrastive words like 'sweet' or 'dessert' to infer word meaning.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 10 },
        },
        wrong: {
          score: 0,
          summary: "You missed the meaning of savoury.",
          didWell: [],
          mistakes: [
            {
              issue: "You selected 'Having a sweet taste'. In the menu, savoury is contrasted with 'strawberry chocolate cake' and lists 'cheese tarts', which are salty/spicy.",
              userWrote: "Having a sweet taste",
              correction: "Having a salty or spicy taste, not sweet",
              rule: "Savoury describes food that is salty or spicy rather than sweet.",
            },
          ],
          nextTip: "Try contrastive reading: when a text lists savoury vs sweet, they are opposites.",
          subSkillBreakdown: { comprehension: 0, vocabulary: 0 },
        },
      },
    },
    {
      taskId: "w3d2-listen-dictation",
      feedbackInput: {
        taskId: "w3d2-listen-dictation",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect dictation spelling and grammar!",
          didWell: [
            "You accurately caught every word in the café order including mineral water and olive oil."
          ],
          mistakes: [],
          nextTip: "Continue listening for fast noun-phrases.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 10 },
        },
        wrong: {
          score: 0,
          summary: "You had a few vocabulary misses in the dictation.",
          didWell: [],
          mistakes: [
            {
              issue: "You wrote 'salad dressing' instead of 'olive oil', and missed 'please' at the end of the order.",
              userWrote: "I would like to order a chicken salad with salad dressing, and a bottle of mineral water.",
              correction: "I would like to order a chicken salad with olive oil, and a bottle of mineral water, please.",
              rule: "Listen carefully for the specific ingredients and courtesy words at the end of orders.",
            },
          ],
          nextTip: "Focus on key details of food orders such as toppings and dressings.",
          subSkillBreakdown: { comprehension: 4, vocabulary: 4 },
        },
      },
    },
    {
      taskId: "w3d2-write-word-upgrade",
      feedbackInput: {
        taskId: "w3d2-write-word-upgrade",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent vocabulary upgrades!",
          didWell: [
            "You perfectly replaced simple words with advanced synonyms like 'delicious', 'bland', and 'flavourful'."
          ],
          mistakes: [],
          nextTip: "Try using these words when writing food reviews or messages.",
          subSkillBreakdown: { expression: 10, vocabulary: 10, grammar: 10 },
        },
        wrong: {
          score: 6.7,
          summary: "Almost correct, but you missed one upgrade.",
          didWell: [
            "You upgraded 'good' to 'delicious' and 'nice flavours' to 'flavourful' correctly."
          ],
          mistakes: [
            {
              issue: "For the second sentence, 'has no taste' should be upgraded to the adjective 'bland'.",
              userWrote: "The chicken soup has no taste.",
              correction: "The chicken soup is bland.",
              rule: "Use the target adjective 'bland' to describe food lacking taste.",
            },
          ],
          nextTip: "Review your vocabulary cards for taste descriptions.",
          subSkillBreakdown: { expression: 7, vocabulary: 7, grammar: 6 },
        },
      },
    },
    {
      taskId: "w3d2-speak-timed",
      feedbackInput: {
        taskId: "w3d2-speak-timed",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.5,
          summary: "Stunning speaking monologue!",
          didWell: [
            "You spoke fluently for 22 seconds using all four target words (delicious, ingredients, savoury, taste)."
          ],
          mistakes: [],
          nextTip: "Keep speaking under mild pressure to build your vocabulary recall speed.",
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          score: 6,
          summary: "Clear spoken attempt, but you used simple vocabulary.",
          didWell: [
            "You spoke with stable pacing and good pronunciation."
          ],
          mistakes: [
            {
              issue: "You missed the target words 'delicious' and 'savoury', using simple words like 'good' and 'nice' instead.",
              userWrote: "My favourite meal is spaghetti carbonara. It is a good dish made with simple ingredients like pasta, eggs, cheese, and black pepper. The taste is nice. I usually eat it on weekends with my family.",
              correction: "My favourite meal is spaghetti carbonara. It is a savoury dish made with simple ingredients like pasta, eggs, cheese, and black pepper. The taste is incredibly delicious and rich. I usually eat it on weekends with my family.",
              rule: "Actively recall and incorporate advanced target vocabulary when presenting without visual cues.",
            },
          ],
          nextTip: "Try writing down target vocabulary on a sticky note to prompt yourself during timing.",
          subSkillBreakdown: { fluency: 7, pronunciation: 7, grammar: 5, vocabulary: 5 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_03_02",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.food_eating_meals",
    },
    outputs: {
      correct:
        "Excellent work on the Food & Eating topic! You showed deep understanding of taste adjectives and ordering context. Your listening and dictation spelling were exact, your vocabulary upgrades were precise, and your spoken timed monologue was highly fluent. Keep up this premium work!",
      wrong:
        "Good effort on the Food & Eating curriculum! You have a solid grasp of basic ordering, but struggle with precise vocabulary recall under timing pressure. Focus on mastering the distinction between sweet/savoury, upgrading simple descriptions to 'bland' or 'flavourful', and actively practicing target vocabulary during spoken monologues.",
    },
  },
};

const weekThreeDayFourFeedback: FeedbackDayData = {
  dayId: "day_24_03_04",
  activityFeedback: [
    {
      taskId: "w3d4-read-context-mcq",
      feedbackInput: {
        taskId: "w3d4-read-context-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect context inference from the job ad!",
          didWell: [
            "You correctly inferred that 'responsible for' means 'in charge of' by reading the duties listed in the ad."
          ],
          mistakes: [],
          nextTip: "Keep scanning job ads for action phrases like 'responsible for', 'required to', and 'in charge of'.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 10 },
        },
        wrong: {
          score: 0,
          summary: "You missed the meaning of 'responsible for'.",
          didWell: [],
          mistakes: [
            {
              issue: "You selected 'Interested in doing something'. The ad lists specific duties after 'responsible for' — organising meetings, managing a team — which means 'in charge of'.",
              userWrote: "Interested in doing something",
              correction: "In charge of or must take care of",
              rule: "'Responsible for' in a job context means the person must handle those specific duties.",
            },
          ],
          nextTip: "Look at the tasks listed after 'responsible for' to understand it means 'in charge of'.",
          subSkillBreakdown: { comprehension: 0, vocabulary: 0 },
        },
      },
    },
    {
      taskId: "w3d4-listen-dictation",
      feedbackInput: {
        taskId: "w3d4-listen-dictation",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect dictation of the job description!",
          didWell: [
            "You accurately caught every word including 'receptionist', 'manages', and 'check-ins'."
          ],
          mistakes: [],
          nextTip: "Continue practising with longer workplace descriptions to build speed.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 10 },
        },
        wrong: {
          score: 4,
          summary: "Close, but you substituted a key verb.",
          didWell: [
            "You heard the job title and workplace correctly."
          ],
          mistakes: [
            {
              issue: "You wrote 'handles' instead of 'manages'. While similar, the audio clearly says 'manages'.",
              userWrote: "She works as a receptionist at a busy hotel and handles all guest check-ins every morning.",
              correction: "She works as a receptionist at a busy hotel and manages all guest check-ins every morning.",
              rule: "In dictation, type the exact word you hear, even if a synonym exists.",
            },
          ],
          nextTip: "Focus on the exact verbs in workplace descriptions: manages, organises, handles are different words.",
          subSkillBreakdown: { comprehension: 5, vocabulary: 4 },
        },
      },
    },
    {
      taskId: "w3d4-write-paraphrase",
      feedbackInput: {
        taskId: "w3d4-write-paraphrase",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.5,
          summary: "Excellent paraphrasing with job vocabulary!",
          didWell: [
            "You replaced simple phrases with precise job terms like 'employed' and 'manages'.",
            "Both rewrites keep the original meaning while sounding more professional.",
          ],
          mistakes: [],
          nextTip: "Try paraphrasing longer job descriptions to build your workplace vocabulary range.",
          subSkillBreakdown: { expression: 10, vocabulary: 9, grammar: 9 },
        },
        wrong: {
          score: 7,
          summary: "Your first rewrite is strong, but the second still uses simple language.",
          didWell: [
            "You successfully upgraded 'works in an office' to 'employed as an office assistant'.",
          ],
          mistakes: [
            {
              issue: "The goal was to replace 'tells people what to do' with a precise verb like 'manages'.",
              userWrote: "She tells the team what to do at the workplace.",
              correction: "She manages a team at the workplace.",
              rule: "Use workplace verbs like 'manages', 'leads', or 'supervises' instead of 'tells people what to do'.",
            },
          ],
          nextTip: "When paraphrasing, actively look for a single strong verb to replace a longer phrase.",
          subSkillBreakdown: { expression: 7, vocabulary: 7, grammar: 7 },
        },
      },
    },
    {
      taskId: "w3d4-speak-timed",
      feedbackInput: {
        taskId: "w3d4-speak-timed",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.5,
          summary: "Confident and fluent job description!",
          didWell: [
            "You spoke fluently for 24 seconds using all target words: manager, responsible for, works in, and team."
          ],
          mistakes: [],
          nextTip: "Try adding one extra detail about why the job matters to the community.",
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          score: 6,
          summary: "Clear spoken attempt, but you used simple vocabulary instead of target words.",
          didWell: [
            "You spoke with steady pacing and clear pronunciation."
          ],
          mistakes: [
            {
              issue: "You missed the target phrases 'responsible for' and 'team', using simpler words like 'does meetings' and 'leads people' instead.",
              userWrote: "My mother is a manager at a small company. She works in an office and she does meetings and leads people. The job is important because she helps everyone do their work.",
              correction: "My mother is a manager at a small company. She works in an office and is responsible for organising meetings and leading a team of ten people. The job is important because she helps everyone stay organised and finish their work on time.",
              rule: "Actively recall and incorporate target job vocabulary like 'responsible for' and 'team' during timed speech.",
            },
          ],
          nextTip: "Before speaking, mentally list 2-3 target words you want to use.",
          subSkillBreakdown: { fluency: 7, pronunciation: 7, grammar: 5, vocabulary: 5 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_03_04",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.work_jobs_roles",
    },
    outputs: {
      correct:
        "Excellent work on the Work & Jobs topic! You showed strong understanding of job vocabulary, accurately inferring 'responsible for' from context, perfectly dictating a workplace description, professionally paraphrasing with job terms, and fluently describing a job role under time pressure.",
      wrong:
        "Good effort on the Work & Jobs curriculum! You understand basic job concepts but need to sharpen precise vocabulary: use 'manages' instead of 'handles', 'responsible for' instead of 'does', and replace simple phrases with strong workplace verbs. Keep practising active recall of target words during timed tasks.",
    },
  },
};

const weekThreeDaySixFeedback: FeedbackDayData = {
  dayId: "day_24_03_06",
  activityFeedback: [
    {
      taskId: "w3d6-read-context-mcq",
      feedbackInput: {
        taskId: "w3d6-read-context-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect context comprehension!",
          didWell: [
            "You correctly inferred the meanings of content, disappointed, and devastated from the diary context."
          ],
          mistakes: [],
          nextTip: "Continue using surrounding sentences (context clues) to guess the meaning of new emotion words.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 10 },
        },
        wrong: {
          score: 6.7,
          summary: "Good attempt, but you missed one context clue.",
          didWell: [
            "You correctly identified the emotions in the morning and afternoon."
          ],
          mistakes: [
            {
              issue: "You selected 'Angry' instead of 'Devastated'. The diary says she lost her expensive phone and couldn't find it.",
              userWrote: "Angry",
              correction: "Because of losing the expensive phone",
              rule: "'Devastated' means extremely sad and shocked, which fits the context of losing something valuable.",
            },
          ],
          nextTip: "Pay attention to the specific event that triggers the emotion to distinguish between similar feelings.",
          subSkillBreakdown: { comprehension: 7, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w3d6-listen-dictation",
      feedbackInput: {
        taskId: "w3d6-listen-dictation",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect dictation spelling!",
          didWell: [
            "You accurately spelled complex abstract emotion words like overwhelmed and disheartened."
          ],
          mistakes: [],
          nextTip: "Keep practicing listening to advanced vocabulary to build your spelling confidence.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 10 },
        },
        wrong: {
          score: 5,
          summary: "You captured the meaning, but had spelling slips on the advanced words.",
          didWell: [
            "You successfully recognized the target words in the audio."
          ],
          mistakes: [
            {
              issue: "You misspelled 'overwhelmed' as 'overwelemed'.",
              userWrote: "overwelemed",
              correction: "overwhelmed",
              rule: "Remember the spelling of 'overwhelmed': over + whelm + ed.",
            },
          ],
          nextTip: "Break down long words into syllables when practicing spelling: dis-heart-en-ed.",
          subSkillBreakdown: { comprehension: 5, vocabulary: 5 },
        },
      },
    },
    {
      taskId: "w3d6-write-word-upgrade",
      feedbackInput: {
        taskId: "w3d6-write-word-upgrade",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent vocabulary upgrades!",
          didWell: [
            "You perfectly replaced simple words like 'sad' and 'stressed' with advanced synonyms like 'devastated', 'overwhelmed', and 'disappointed'."
          ],
          mistakes: [],
          nextTip: "Try using these words when writing diary entries or personal messages.",
          subSkillBreakdown: { expression: 10, vocabulary: 10, grammar: 10 },
        },
        wrong: {
          score: 6.7,
          summary: "Almost correct, but you missed one upgrade form.",
          didWell: [
            "You successfully upgraded 'sad' to 'devastated' and 'disappointed'."
          ],
          mistakes: [
            {
              issue: "You used the noun 'stress' instead of the adjective 'overwhelmed'.",
              userWrote: "She felt stress by all the homework.",
              correction: "She felt overwhelmed by all the homework.",
              rule: "Use the target adjective 'overwhelmed' to describe the feeling of having too much to deal with.",
            },
          ],
          nextTip: "Review the target vocabulary list and make sure to use the exact upgraded word.",
          subSkillBreakdown: { expression: 7, vocabulary: 7, grammar: 6 },
        },
      },
    },
    {
      taskId: "w3d6-speak-timed",
      feedbackInput: {
        taskId: "w3d6-speak-timed",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.5,
          summary: "Expressive and fluent spoken reflection!",
          didWell: [
            "You spoke fluently and naturally incorporated strong emotion words like overwhelmed and content."
          ],
          mistakes: [],
          nextTip: "Try connecting your feelings with more detailed reasons using 'because' or 'since'.",
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          score: 6,
          summary: "Clear spoken attempt, but you used simple vocabulary instead of target words.",
          didWell: [
            "You communicated your basic feelings and reasons clearly."
          ],
          mistakes: [
            {
              issue: "You missed the target words 'overwhelmed' and 'content', using simple words like 'bad' instead.",
              userWrote: "This week I feel bad because much work.",
              correction: "This week I felt quite overwhelmed because I had a lot of work to do. But today I feel very content.",
              rule: "Actively recall and incorporate advanced target vocabulary when describing your inner states.",
            },
          ],
          nextTip: "Before speaking, mentally list 2-3 advanced emotion words you want to use.",
          subSkillBreakdown: { fluency: 7, pronunciation: 7, grammar: 5, vocabulary: 5 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_03_06",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.feelings_emotions",
    },
    outputs: {
      correct:
        "Outstanding work on the Feelings & Emotions topic! You demonstrated a deep understanding of complex emotion vocabulary. Your ability to infer meaning from context, spell abstract words, upgrade simple emotions to precise adjectives, and fluently express your inner states under time pressure was excellent.",
      wrong:
        "Good effort on the Feelings & Emotions curriculum! You can clearly express basic feelings, but you need to practice using more precise and advanced vocabulary like 'overwhelmed' and 'devastated'. Keep practicing spelling these complex words and actively try to incorporate them into your daily reflections.",
    },
  },
};


const weekThreeDayThreeFeedback: FeedbackDayData = {
  dayId: "day_24_03_03",
  activityFeedback: [
    {
      taskId: "w3d3-read-word-match",
      feedbackInput: {
        taskId: "w3d3-read-word-match",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect vocabulary matching!",
          didWell: [
            "You correctly identified the difference between place words.",
          ],
          mistakes: [],
          nextTip: "Continue to practice using these words to describe your city.",
          subSkillBreakdown: { vocabulary: 10, grammar: 8 },
        },
        wrong: {
          score: 7.5,
          summary: "Good effort, but you mixed up one of the places.",
          didWell: [
            "You correctly matched the definition for market.",
          ],
          mistakes: [
            {
              issue: "A station is where you catch a train, not a city.",
              userWrote: "city",
              correction: "station",
              rule: "Use 'station' for transport locations.",
            },
          ],
          nextTip: "Try scanning definitions for transport keywords.",
          subSkillBreakdown: { vocabulary: 7, grammar: 7 },
        },
      },
    },
    {
      taskId: "w3d3-listen-mcq",
      feedbackInput: {
        taskId: "w3d3-listen-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect listening comprehension of the description.",
          didWell: [
            "You heard the speaker lives in a suburb.",
          ],
          mistakes: [],
          nextTip: "Keep listening for key locations in descriptions.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 8 },
        },
        wrong: {
          score: 6.7,
          summary: "You got the main detail, but missed the shopping cue.",
          didWell: [
            "You correctly heard the location.",
          ],
          mistakes: [
            {
              issue: "The speaker buys fruit and vegetables, not clothes.",
              userWrote: "Clothes and shoes",
              correction: "Fresh fruit and vegetables",
              rule: "Listen closely to the items purchased.",
            },
          ],
          nextTip: "Look out for food words like 'fruit' and 'vegetables'.",
          subSkillBreakdown: { comprehension: 7, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w3d3-write-para",
      feedbackInput: {
        taskId: "w3d3-write-para",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent work on the paragraph!",
          didWell: [
            "You used the target words naturally.",
          ],
          mistakes: [],
          nextTip: "Practice adding adjectives to describe the places.",
          subSkillBreakdown: { expression: 10, grammar: 10, vocabulary: 8 },
        },
        wrong: {
          score: 6,
          summary: "Your paragraph is mostly clear, but has some grammar slips.",
          didWell: [
            "You used the correct vocabulary words.",
          ],
          mistakes: [
            {
              issue: "Use 'a market' for a single market.",
              userWrote: "There are market near my house.",
              correction: "There is a market near my house.",
              rule: "Use 'There is' with singular nouns.",
            },
          ],
          nextTip: "Always review subject-verb agreement.",
          subSkillBreakdown: { expression: 7, grammar: 5, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w3d3-speak-pic-desc",
      feedbackInput: {
        taskId: "w3d3-speak-pic-desc",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.5,
          summary: "Great map description!",
          didWell: [
            "You described each place clearly.",
          ],
          mistakes: [],
          nextTip: "You can expand your response by adding prepositions like 'next to'.",
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          score: 6,
          summary: "Clear spoken attempt, but you missed some articles.",
          didWell: [
            "Your pronunciation and pacing were steady.",
          ],
          mistakes: [
            {
              issue: "Use 'the' before middle and right.",
              userWrote: "In middle, station.",
              correction: "In the middle, there is a station.",
              rule: "Use 'the' before position words.",
            },
          ],
          nextTip: "Focus on adding 'the' before 'middle', 'left', and 'right'.",
          subSkillBreakdown: { fluency: 8, pronunciation: 8, grammar: 6, vocabulary: 5 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_03_03",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.places_locations",
    },
    outputs: {
      correct:
        "Excellent progress in Week 3! You showed a solid understanding of city places and locations. You can effectively write a paragraph about your area and describe a city map.",
      wrong:
        "Good effort! You are getting familiar with place vocabulary. Keep practicing sentences with 'There is' and 'There are', and remember to include articles like 'a' and 'the' before nouns.",
    },
  },
};

const weekThreeDayFiveFeedback: FeedbackDayData = {
  dayId: "day_24_03_05",
  activityFeedback: [
    {
      taskId: "w3d5-read-word-match",
      feedbackInput: {
        taskId: "w3d5-read-word-match",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect time-word matching!",
          didWell: [
            "You correctly identified fortnightly as every two weeks and quarterly as four times a year.",
            "You matched deadline and occasionally with precision, showing strong schedule vocabulary.",
          ],
          mistakes: [],
          nextTip: "Try using these words in a sentence about your own routine this week.",
          subSkillBreakdown: { vocabulary: 10, grammar: 8 },
        },
        wrong: {
          score: 7.5,
          summary: "Good effort — you mixed up two frequency words.",
          didWell: [
            "You correctly matched deadline and occasionally.",
            "You understood that quarterly relates to a time period.",
          ],
          mistakes: [
            {
              issue: "Fortnightly means every two weeks, not every three months.",
              userWrote: "quarterly",
              correction: "fortnightly",
              rule: "Fortnightly comes from fortnight, which is two weeks. Quarterly comes from quarter, which is three months.",
            },
          ],
          nextTip: "Connect the word to its root: fortnight = 14 nights, quarter = one quarter of a year.",
          subSkillBreakdown: { vocabulary: 7, grammar: 7 },
        },
      },
    },
    {
      taskId: "w3d5-listen-mcq",
      feedbackInput: {
        taskId: "w3d5-listen-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "You followed the weekly plan with complete accuracy.",
          didWell: [
            "You caught the daily email-check, the Thursday deadline, and the occasional gym sessions.",
            "You distinguished between different frequency expressions in one short audio.",
          ],
          mistakes: [],
          nextTip: "Notice how the speaker used daily, fortnightly, and quarterly in the same short speech — try doing the same.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 9 },
        },
        wrong: {
          score: 6.7,
          summary: "You followed the routine well, but missed one scheduling detail.",
          didWell: [
            "You correctly identified daily emails and the occasional gym visits.",
            "You understood the structure of the weekly planning monologue.",
          ],
          mistakes: [
            {
              issue: "The speaker says the deadline is on Thursday, not Monday.",
              userWrote: "Monday",
              correction: "Thursday",
              rule: "Listen carefully for the day of the week when a deadline is mentioned.",
            },
          ],
          nextTip: "When you hear a deadline, quickly note the day word that follows it.",
          subSkillBreakdown: { comprehension: 7, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w3d5-write-sent-trans",
      feedbackInput: {
        taskId: "w3d5-write-sent-trans",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent sentence transformations using time adverbs!",
          didWell: [
            "You replaced all three informal phrases with precise time adverbs: daily, weekly, and occasionally.",
            "Your grammar and structure stayed natural in every rewritten sentence.",
          ],
          mistakes: [],
          nextTip: "Challenge yourself to use fortnightly or quarterly in a sentence about your own schedule.",
          subSkillBreakdown: { expression: 10, grammar: 10, vocabulary: 9 },
        },
        wrong: {
          score: 6.7,
          summary: "Two transformations were strong, but one was left unchanged.",
          didWell: [
            "You correctly transformed 'every day' to 'daily' and 'sometimes, not very often' to 'occasionally'.",
            "Your sentence structure stayed grammatically correct.",
          ],
          mistakes: [
            {
              issue: "'Every week' should be compressed to the single adverb 'weekly'.",
              userWrote: "We have a meeting every week.",
              correction: "We have a meeting weekly.",
              rule: "Replace 'every + time noun' with its adverb form: every week → weekly, every day → daily.",
            },
          ],
          nextTip: "Look for every + time noun patterns and swap them for their adverb equivalent.",
          subSkillBreakdown: { expression: 7, grammar: 6, vocabulary: 7 },
        },
      },
    },
    {
      taskId: "w3d5-speak-pic-desc",
      feedbackInput: {
        taskId: "w3d5-speak-pic-desc",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.3,
          summary: "Clear and confident planner description using time vocabulary!",
          didWell: [
            "You used daily and quarterly correctly to describe the planner events.",
            "Your sentence structure was natural and your pacing was clear.",
          ],
          mistakes: [],
          nextTip: "To expand your description, mention one specific event and say how often it happens.",
          subSkillBreakdown: { fluency: 9, pronunciation: 9, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          score: 6.5,
          summary: "Your description was understandable but had two time-word inaccuracies.",
          didWell: [
            "You identified that events happen in the morning and afternoon.",
            "Your pronunciation and pacing were steady throughout.",
          ],
          mistakes: [
            {
              issue: "The planner shows the deadline is on Thursday, not Friday, and the strategy meeting is quarterly, not weekly.",
              userWrote: "On Friday there is a deadline. The strategy meeting is weekly.",
              correction: "On Thursday there is a deadline. The strategy meeting happens quarterly.",
              rule: "Match your spoken description exactly to what is shown or labelled in the visual prompt.",
            },
          ],
          nextTip: "Before speaking, scan the image for time labels and key words to anchor your description.",
          subSkillBreakdown: { fluency: 8, pronunciation: 8, grammar: 6, vocabulary: 5 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_03_05",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.time_schedules_routines",
    },
    outputs: {
      correct:
        "Fantastic Friday session on Time and Schedules! You matched fortnightly, quarterly, deadline, and occasionally with precision, followed a spoken weekly plan with full accuracy, transformed sentences using time adverbs fluently, and described a weekly planner with clear and correct vocabulary. Your time-language is strong and practical.",
      wrong:
        "Good Friday work on time vocabulary! The main area to sharpen is distinguishing between similar frequency words — fortnightly versus quarterly — and listening carefully for specific day-of-week details when deadlines are mentioned. Your speaking is understandable; focus on checking visual or audio prompts for time labels before you respond.",
    },
  },
};

const weekThreeDaySevenFeedback: FeedbackDayData = {
  dayId: "day_24_03_07",
  activityFeedback: [
    {
      taskId: "w3d7-read-word-match",
      feedbackInput: {
        taskId: "w3d7-read-word-match",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect vocabulary matching!",
          didWell: [
            "You correctly identified the difference between the words.",
          ],
          mistakes: [],
          nextTip: "Continue to practice using these words to describe concepts.",
          subSkillBreakdown: { vocabulary: 10, grammar: 8 },
        },
        wrong: {
          score: 6.7,
          summary: "Good effort, but you mixed up some definitions.",
          didWell: [
            "You correctly matched most of the definitions.",
          ],
          mistakes: [
            {
              issue: "You mixed up some of the definitions.",
              userWrote: "Incorrect match",
              correction: "Correct match",
              rule: "Review the vocabulary definitions carefully.",
            },
          ],
          nextTip: "Try scanning definitions for keywords.",
          subSkillBreakdown: { vocabulary: 6, grammar: 6 },
        },
      },
    },
    {
      taskId: "w3d7-listen-mcq",
      feedbackInput: {
        taskId: "w3d7-listen-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect listening comprehension of the description.",
          didWell: [
            "You heard all the details correctly.",
          ],
          mistakes: [],
          nextTip: "Keep listening for key details in descriptions.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 8 },
        },
        wrong: {
          score: 6.7,
          summary: "You got the main detail, but missed a cue.",
          didWell: [
            "You correctly heard the main topic.",
          ],
          mistakes: [
            {
              issue: "You missed one of the specific details.",
              userWrote: "Incorrect detail",
              correction: "Correct detail",
              rule: "Listen closely to the specific details mentioned.",
            },
          ],
          nextTip: "Look out for specific keywords in the audio.",
          subSkillBreakdown: { comprehension: 7, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w3d7-write-para",
      feedbackInput: {
        taskId: "w3d7-write-para",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent work on the paragraph!",
          didWell: [
            "You used the target words naturally.",
          ],
          mistakes: [],
          nextTip: "Practice adding adjectives to describe your ideas.",
          subSkillBreakdown: { expression: 10, grammar: 10, vocabulary: 8 },
        },
        wrong: {
          score: 6,
          summary: "Your paragraph is mostly clear, but has some grammar slips.",
          didWell: [
            "You used the correct vocabulary words.",
          ],
          mistakes: [
            {
              issue: "You had a few grammatical errors.",
              userWrote: "Paragraph with errors",
              correction: "Corrected paragraph",
              rule: "Always review subject-verb agreement and sentence structure.",
            },
          ],
          nextTip: "Always review subject-verb agreement.",
          subSkillBreakdown: { expression: 7, grammar: 5, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w3d7-speak-timed",
      feedbackInput: {
        taskId: "w3d7-speak-timed",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.5,
          summary: "Great description!",
          didWell: [
            "You described the topic clearly.",
          ],
          mistakes: [],
          nextTip: "You can expand your response by adding more details.",
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          score: 6,
          summary: "Clear spoken attempt, but you missed some words.",
          didWell: [
            "Your pronunciation and pacing were steady.",
          ],
          mistakes: [
            {
              issue: "You missed some key vocabulary words.",
              userWrote: "Simple description",
              correction: "Detailed description",
              rule: "Try to incorporate the target vocabulary words.",
            },
          ],
          nextTip: "Focus on adding the target vocabulary words to your speech.",
          subSkillBreakdown: { fluency: 8, pronunciation: 8, grammar: 6, vocabulary: 5 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_03_07",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.general",
    },
    outputs: {
      correct:
        "Excellent progress in Week 3! You showed a solid understanding of the concepts.",
      wrong:
        "Good effort! You are getting familiar with the vocabulary. Keep practicing.",
    },
  },
};

const weekFourDayOneFeedback: FeedbackDayData = {
  dayId: "day_24_04_01",
  activityFeedback: [
    {
      taskId: "w4d1-read-mcq",
      feedbackInput: {
        taskId: "w4d1-read-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect reading comprehension!",
          didWell: [
            "You accurately understood Maya's transformation from fear to confidence.",
            "You correctly identified the key lesson: speaking is about being heard, not being perfect."
          ],
          mistakes: [],
          nextTip: "Try reading similar motivational stories to keep building positive framing.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 8 },
        },
        wrong: {
          score: 7.5,
          summary: "Good effort, but you missed one key story detail.",
          didWell: [
            "You correctly understood why Maya volunteered and her initial fear."
          ],
          mistakes: [
            {
              issue: "You selected a wrong option for Maya's voice. The story says her voice trembled at first but everyone was listening eagerly.",
              userWrote: "She forgot her words and sat down",
              correction: "Her voice trembled at first but everyone was listening eagerly",
              rule: "Always refer back to the exact passage details rather than guessing.",
            },
          ],
          nextTip: "Double-check key sentences in the story before choosing the option.",
          subSkillBreakdown: { comprehension: 7, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w4d1-listen-shadow",
      feedbackInput: {
        taskId: "w4d1-listen-shadow",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Outstanding shadowing practice!",
          didWell: [
            "You repeated the phrase exactly behind the speaker, capturing pacing and confidence.",
            "Your pronunciation of 'test', 'bridge', and 'voice' was exceptionally clear."
          ],
          mistakes: [],
          nextTip: "Try record-shadowing longer monologues to practice continuous speaking flow.",
          subSkillBreakdown: { comprehension: 10, fluency: 10, pronunciation: 9 },
        },
        wrong: {
          score: 6.0,
          summary: "Spoken shadowing attempted, but you had multiple grammatical omissions.",
          didWell: [
            "You maintained a good speaking pace."
          ],
          mistakes: [
            {
              issue: "You omitted key small grammar particles like 'a' and auxiliary verbs ('is', 'you').",
              userWrote: "Speaking is not test. It is bridge. When speak, you share unique voice.",
              correction: "Speaking is not a test. It is a bridge. When you speak, you share your unique voice with the world.",
              rule: "Shadowing requires close replication of functional grammar words, not just content keywords.",
            },
          ],
          nextTip: "Listen specifically to small structural words (is, a, the, when) and repeat them too.",
          subSkillBreakdown: { comprehension: 6, fluency: 6, pronunciation: 6 },
        },
      },
    },
    {
      taskId: "w4d1-write-transform",
      feedbackInput: {
        taskId: "w4d1-write-transform",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect growth mindset rewrites!",
          didWell: [
            "You beautifully reframed limiting self-talk into positive active growth statements.",
            "Your grammatical structures were flawless."
          ],
          mistakes: [],
          nextTip: "Start using these reframed phrases in your everyday reflections!",
          subSkillBreakdown: { expression: 10, grammar: 10, vocabulary: 9 },
        },
        wrong: {
          score: 6.7,
          summary: "Two strong rewrites, but one statement was still negative.",
          didWell: [
            "You successfully transformed 'I am shy' and 'I cannot speak English' into growth framing."
          ],
          mistakes: [
            {
              issue: "You kept a negative framing ('still hate') instead of a growth framing ('learn from').",
              userWrote: "I still hate making mistakes.",
              correction: "I learn from my mistakes.",
              rule: "Proactive growth transforms require replacing passive fear words with active learning verbs.",
            },
          ],
          nextTip: "Focus on swapping self-criticism ('hate') for positive learning actions ('learn', 'improve').",
          subSkillBreakdown: { expression: 7, grammar: 6, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w4d1-speak-aloud",
      feedbackInput: {
        taskId: "w4d1-speak-aloud",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.4,
          summary: "Fluent and positive read aloud!",
          didWell: [
            "You pronounced all target words like 'voice', 'confidence', and 'perfect' clearly.",
            "Your pacing was natural and you paused perfectly at punctuation."
          ],
          mistakes: [],
          nextTip: "Continue working on word stress in longer sentences.",
          subSkillBreakdown: { pronunciation: 10, fluency: 9, grammar: 9 },
        },
        wrong: {
          score: 7.0,
          summary: "Clear effort, but you had frequent hesitations and omissions.",
          didWell: [
            "You spoke clearly and used correct pronunciation on the words you said."
          ],
          mistakes: [
            {
              issue: "You had long gaps in your speech and omitted important words like 'practice' and 'perfect'.",
              userWrote: "My voice has... value. Every time... practice, build confidence. Not need to be perfect... just speak up.",
              correction: "My voice has value. Every time I practice, I build my confidence. I do not need to be perfect to start. I just need to speak up.",
              rule: "When reading aloud, try to scan the full sentence ahead to maintain a steady and continuous breath.",
            },
          ],
          nextTip: "Take a deep breath before you start reading and let your voice slide smoothly between words.",
          subSkillBreakdown: { pronunciation: 7, fluency: 7, grammar: 6 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_04_01",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.general",
    },
    outputs: {
      correct:
        "What a stellar start to Finding Your Voice week! You showed perfect comprehension of Maya's story, shadowed a confident speaker flawlessly, reframed limiting statements into proactive growth mindset sentences, and spoke with clear confidence in your read aloud. Keep this energy going!",
      wrong:
        "Good effort starting the Finding Your Voice week! You're making progress but focus on building continuous flow. Avoid grammatical omissions when shadowing, reframe self-criticism using active learning verbs in writing, and take deep breaths to reduce hesitations during aloud reading.",
    },
  },
};

const weekFourDayTwoFeedback: FeedbackDayData = {
  dayId: "day_24_04_02",
  activityFeedback: [
    {
      taskId: "w4d2-read-tone-id",
      feedbackInput: {
        taskId: "w4d2-read-tone-id",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect tone recognition!",
          didWell: [
            "You accurately distinguished the confident statement from the hesitant statement.",
          ],
          mistakes: [],
          nextTip: "Observe how confident tones avoid hedge words like 'guess' and use strong modals.",
          subSkillBreakdown: { vocabulary: 10, grammar: 8 },
        },
        wrong: {
          score: 5,
          summary: "You had some difficulty identifying Jamie's hesitant tone.",
          didWell: [
            "You correctly identified Alex's confident tone.",
          ],
          mistakes: [
            {
              issue: "You marked Jamie's hesitant statement as confident.",
              userWrote: "Confident / Sure",
              correction: "Hesitant / Uncertain",
              rule: "Filler words like 'well', 'guess', and 'maybe' indicate a hesitant and uncertain tone.",
            },
          ],
          nextTip: "Listen/look out for hedge phrases like 'I guess' or 'I don't know' as indicators of hesitation.",
          subSkillBreakdown: { vocabulary: 5, grammar: 5 },
        },
      },
    },
    {
      taskId: "w4d2-listen-mcq",
      feedbackInput: {
        taskId: "w4d2-listen-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect listening comprehension of confident speech!",
          didWell: [
            "You correctly selected Speaker B as the more confident speaker.",
          ],
          mistakes: [],
          nextTip: "Pay attention to pacing and vocal conviction in future listening tasks.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 8 },
        },
        wrong: {
          score: 0,
          summary: "Speaker A was highly hesitant, not confident.",
          didWell: [],
          mistakes: [
            {
              issue: "You selected Speaker A as the more confident speaker.",
              userWrote: "Speaker A",
              correction: "Speaker B",
              rule: "Speakers who speak without stuttering, stalling (e.g., 'Um'), or hedging sound much more confident.",
            },
          ],
          nextTip: "Focus on how the presence of fillers ('Um') instantly decreases the perceived confidence of a speaker.",
          subSkillBreakdown: { comprehension: 0, vocabulary: 0 },
        },
      },
    },
    {
      taskId: "w4d2-write-timed",
      feedbackInput: {
        taskId: "w4d2-write-timed",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Superb timed writing under pressure!",
          didWell: [
            "You wrote a very structured opinion on remote work using target words like 'productivity' and 'convinced' within the time limit.",
          ],
          mistakes: [],
          nextTip: "Continue using direct statements to state opinions without overthinking.",
          subSkillBreakdown: { expression: 10, grammar: 10, vocabulary: 8 },
        },
        wrong: {
          score: 5,
          summary: "Your timed paragraph lacked conviction and key target vocabulary.",
          didWell: [
            "You completed a response under timed pressure.",
          ],
          mistakes: [
            {
              issue: "You used filler phrases and missed target words like 'productivity' and 'convinced'.",
              userWrote: "I guess remote work is okay, but I am not convinced it is good. It has some problems maybe.",
              correction: "In my opinion, remote work is excellent because it increases productivity. I am convinced that working from home is the best setup, and I believe most companies should offer it.",
              rule: "Use active, strong assertions (e.g. 'is excellent', 'increases productivity') to build confidence in timed writing.",
            },
          ],
          nextTip: "Avoid starting sentences with hesitant markers like 'I guess' or ending with 'maybe'.",
          subSkillBreakdown: { expression: 5, grammar: 5, vocabulary: 5 },
        },
      },
    },
    {
      taskId: "w4d2-speak-timed",
      feedbackInput: {
        taskId: "w4d2-speak-timed",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.5,
          summary: "Stellar improvised timed speech!",
          didWell: [
            "You delivered a confident opinion on online learning within the 60-second limit and used target words beautifully.",
          ],
          mistakes: [],
          nextTip: "Add brief examples to support your reasons even further.",
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          score: 6,
          summary: "Clear spoken attempt, but hesitant and missed target cues.",
          didWell: [
            "You stayed speaking for the required duration.",
          ],
          mistakes: [
            {
              issue: "Your speech had multiple hesitation fillers ('Um', 'I don't know') and missed target cues.",
              userWrote: "Um, I think online class is good, but traditional is also good. I don't know which one is better.",
              correction: "In my opinion, online learning is very convenient, but I prefer traditional classroom learning. Traditional schools allow us to interact with teachers directly. I feel confident that face-to-face learning is much more effective.",
              rule: "State a clear preference directly instead of saying 'I don't know which one is better' to sound more confident.",
            },
          ],
          nextTip: "Take a deep breath and pick one side clearly instead of remaining in the middle.",
          subSkillBreakdown: { fluency: 6, pronunciation: 6, grammar: 6, vocabulary: 6 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_04_02",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.opinions_confidence",
    },
    outputs: {
      correct:
        "Incredible job sharing opinions confidently! You identified confident and hesitant statements with ease, distinguished speaker tones perfectly, wrote a beautiful opinion statement under extreme 3-minute time pressure, and capped it off with a stellar timed spoken monologue. Your voice is becoming extremely clear and convincing!",
      wrong:
        "Good attempt at sharing your opinions. The main focus is to keep practicing high-certainty opinion verbs and markers, eliminating hesitant expressions like 'maybe' and 'I guess' when you aim to speak or write with conviction. Timed pressure can be challenging; don't overthink, trust your initial thoughts and use direct statements.",
    },
  },
};

const weekFourDayThreeFeedback: FeedbackDayData = {
  dayId: "day_24_04_03",
  activityFeedback: [
    {
      taskId: "w4d3-read-mcq",
      feedbackInput: {
        taskId: "w4d3-read-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect comprehension of Elena's profile!",
          didWell: [
            "You correctly identified Elena's main profession.",
            "You understood her active relationship with nature."
          ],
          mistakes: [],
          nextTip: "Try creating a similar short bio about your own daily routine.",
          subSkillBreakdown: { comprehension: 10, grammar: 9 },
        },
        wrong: {
          score: 7.5,
          summary: "Good effort, but you missed Elena's primary motivation.",
          didWell: [
            "You correctly identified her daily work environment."
          ],
          mistakes: [
            {
              issue: "You selected that Elena's motivation is to sell photographs. The passage says her primary motivation is to inspire the conservation of ocean ecosystems.",
              userWrote: "To sell expensive wildlife photographs",
              correction: "To inspire the conservation of our fragile marine ecosystems",
              rule: "Look closely for key phrases like 'primary motivation' to extract the speaker's true intent.",
            },
          ],
          nextTip: "Reread the last two sentences of the bio carefully.",
          subSkillBreakdown: { comprehension: 8, grammar: 7 },
        },
      },
    },
    {
      taskId: "w4d3-listen-tone",
      feedbackInput: {
        taskId: "w4d3-listen-tone",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Outstanding tone recognition!",
          didWell: [
            "You perfectly distinguished between formal introductions and casual small talk.",
            "You recognized contractions and idioms as casual indicators."
          ],
          mistakes: [],
          nextTip: "Use Version A patterns for professional emails and Version B patterns for friendly chats.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 9 },
        },
        wrong: {
          score: 5.0,
          summary: "You had some trouble identifying Arthur's formal introduction register.",
          didWell: [
            "You correctly identified that Version B was casual."
          ],
          mistakes: [
            {
              issue: "You marked Version A as casual. Polite full sentences like 'It is a pleasure to meet you' indicate a formal/professional tone.",
              userWrote: "Casual / Informal",
              correction: "Formal / Professional",
              rule: "In formal registers, avoid casual greetings and use complete, structured sentences.",
            },
          ],
          nextTip: "Listen for formal greetings like 'Hello' and direct professional words to identify formal tone.",
          subSkillBreakdown: { comprehension: 5, vocabulary: 5 },
        },
      },
    },
    {
      taskId: "w4d3-write-transform",
      feedbackInput: {
        taskId: "w4d3-write-transform",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Superb growth transforms!",
          didWell: [
            "You successfully transformed all simple sentences into rich, expressive self-descriptions.",
            "Your spelling and grammar are spotless."
          ],
          mistakes: [],
          nextTip: "Keep using descriptive verbs like 'reside' and feelings like 'passionate' in your speaking too.",
          subSkillBreakdown: { grammar: 10, expression: 10, vocabulary: 9 },
        },
        wrong: {
          score: 6.7,
          summary: "Good effort, but one transformation was still basic.",
          didWell: [
            "You did an excellent job with the soccer and programmer transforms."
          ],
          mistakes: [
            {
              issue: "You left 'I live in Berlin' relatively basic instead of adding rich details.",
              userWrote: "I still live in Berlin.",
              correction: "I reside in the vibrant city of Berlin and enjoy exploring its culture.",
              rule: "Use expressive expansions (e.g. 'reside', 'vibrant city', 'enjoy exploring') instead of basic repetitions.",
            },
          ],
          nextTip: "Focus on adding at least one descriptive adjective and one active verb to your transformations.",
          subSkillBreakdown: { grammar: 7, expression: 6, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w4d3-speak-pic-desc",
      feedbackInput: {
        taskId: "w4d3-speak-pic-desc",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.6,
          summary: "Beautiful descriptive speaking!",
          didWell: [
            "You used excellent speculative expressions like 'seems to be'.",
            "Your pronunciation was crisp and pacing was completely steady."
          ],
          mistakes: [],
          nextTip: "Try adding a bit more detail about the lake view next time.",
          subSkillBreakdown: { fluency: 10, pronunciation: 9.6, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          score: 6.0,
          summary: "Spoken description was very brief and lacked detail.",
          didWell: [
            "You identified the core activity of painting."
          ],
          mistakes: [
            {
              issue: "Your speech had minimal details and lacked speculative vocabulary.",
              userWrote: "In this photo, there is a person painting. They paint mountains. I don't know who they are, maybe a student.",
              correction: "In this photo, there is a person painting outdoors next to a beautiful lake. They are painting scenic mountains and a setting sun on a canvas. They seem to be a very creative and peaceful person who loves nature.",
              rule: "When describing a picture, expand on the scenery, actions, and character projections using speculative markers.",
            },
          ],
          nextTip: "Try to speak for at least 20 seconds and describe at least three distinct visual details.",
          subSkillBreakdown: { fluency: 6, pronunciation: 6, grammar: 6, vocabulary: 5 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_04_03",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.general",
    },
    outputs: {
      correct:
        "Splendid Week 4 Day 3 session on Describing Yourself! You correctly analyzed Elena's bio, distinguished formal and casual introductions flawlessly, upgraded simple sentences to extremely rich and descriptive ones, and spoke beautifully about the outdoor painter activity. Your self-description and expression vocabulary are growing impressively.",
      wrong:
        "Good effort on today's Describing Yourself curriculum! Work on checking passage details before picking answers, and practice active listening to identify polite vs. casual registers. When transforming sentences and describing images, challenge yourself to use rich speculative vocabulary and descriptive adjectives rather than plain statements.",
    },
  },
};

const weekFourDayFourFeedback: FeedbackDayData = {
  dayId: "day_24_04_04",
  activityFeedback: [
    {
      taskId: "w4d4-read-tone-id",
      feedbackInput: {
        taskId: "w4d4-read-tone-id",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect tone recognition in self-correction dialogue!",
          didWell: [
            "You perfectly identified the tone shift from anxious/apologetic to calm/composed in Sarah's slip.",
            "You correctly recognized Mark's casual recovery tone."
          ],
          mistakes: [],
          nextTip: "Observe how native speakers use quick self-correction markers in business meetings to keep going.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 10 },
        },
        wrong: {
          score: 5.0,
          summary: "You had some difficulty identifying the tone shift in Mark's casual slip-up.",
          didWell: [
            "You correctly identified Sarah's apologetic-to-calm tone transition."
          ],
          mistakes: [
            {
              issue: "You marked Mark's tone as uncertain to completely confused. The dialogue shows him surprised ('Oh, wait!'), acknowledging the slip casually ('Oops!'), and quickly offering a helpful solution.",
              userWrote: "From uncertain to completely confused",
              correction: "From surprised/startled to helpful/reassured",
              rule: "Graceful recovery uses active problem-solving words ('Let me send...', 'Thanks for...') to reassuringly move past the slip.",
            },
          ],
          nextTip: "Listen for action-oriented recovery words like 'let me correct that' or 'let me send' to spot relaxed tones.",
          subSkillBreakdown: { comprehension: 5, vocabulary: 5 },
        },
      },
    },
    {
      taskId: "w4d4-listen-shadow",
      feedbackInput: {
        taskId: "w4d4-listen-shadow",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Beautifully shadowed the self-correction pattern!",
          didWell: [
            "You repeated the mid-sentence self-correction markers ('Oh, wait', 'I mean', 'Actually') with a natural, steady pacing.",
            "Your speech rhythm kept moving nicely without awkward pauses."
          ],
          mistakes: [],
          nextTip: "Keep practicing shadowing other speakers to internalize these natural filler transitions.",
          subSkillBreakdown: { pronunciation: 10, fluency: 10 },
        },
        wrong: {
          score: 5.0,
          summary: "Shadowed recording missed some of the core self-correction markers.",
          didWell: [
            "Your pronunciation of 'Tuesday' and 'schedule' was relatively clear."
          ],
          mistakes: [
            {
              issue: "You skipped the transition phrases 'Oh, wait' and 'I mean' in your recording.",
              userWrote: "We need to finish this by Tuesday... Oh Wednesday... Actually, let double check the schedule.",
              correction: "We need to finish this by Tuesday... Oh, wait, I mean Wednesday! Actually, let me double check the schedule.",
              rule: "Pronounce self-correction markers clearly so listeners can easily track your adjustments.",
            },
          ],
          nextTip: "Try slowing down slightly during the transition markers like 'Oh, wait' and 'I mean' to ensure they are fully spoken.",
          subSkillBreakdown: { pronunciation: 5, fluency: 5 },
        },
      },
    },
    {
      taskId: "w4d4-write-timed",
      feedbackInput: {
        taskId: "w4d4-write-timed",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Splendid timed personal reflection!",
          didWell: [
            "You wrote a very thoughtful personal reflection on handling speaking mistakes.",
            "You successfully integrated all target words ('Usually', 'Instead of', 'Simply') perfectly."
          ],
          mistakes: [],
          nextTip: "Continue using structured transitional words like 'Instead of' to organize your written thoughts under time limits.",
          subSkillBreakdown: { expression: 10, grammar: 10, vocabulary: 10 },
        },
        wrong: {
          score: 5.0,
          summary: "Timed writing was very brief and missed all target cues.",
          didWell: [
            "You expressed your genuine feeling of nervousness clearly."
          ],
          mistakes: [
            {
              issue: "Your reflection was too short and did not include any target transition words.",
              userWrote: "When I make a mistake I get very nervous. I don't know what to do and I stop speaking.",
              correction: "Usually, when I make a mistake while speaking, I try to stay calm. Instead of stressing, I simply take a deep breath, correct myself quickly, and keep going. Most people do not mind minor slips.",
              rule: "Use transition words (e.g. 'Usually', 'Instead of', 'Simply') to turn basic expressions of anxiety into proactive descriptions of graceful recovery.",
            },
          ],
          nextTip: "Focus on adding at least one transition word and expanding your idea into a two-sentence strategy next time.",
          subSkillBreakdown: { expression: 5, grammar: 5, vocabulary: 5 },
        },
      },
    },
    {
      taskId: "w4d4-speak-smalltalk",
      feedbackInput: {
        taskId: "w4d4-speak-smalltalk",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Outstanding small talk recovery dialogue!",
          didWell: [
            "You handled the unpredictable presentation slip question with excellent social grace.",
            "You naturally incorporated 'Actually', 'Simply', and 'Instead of' to create a relaxed flow."
          ],
          mistakes: [],
          nextTip: "Try asking a friendly follow-up question back to the partner next time, like 'Do you freeze up often?'",
          subSkillBreakdown: { fluency: 10, pronunciation: 10, grammar: 10 },
        },
        wrong: {
          score: 5.0,
          summary: "Your first small talk response was clear, but the second turn was hesitant and had grammar slips.",
          didWell: [
            "You responded very well in the first turn using 'Actually' and 'simply'."
          ],
          mistakes: [
            {
              issue: "Your second turn ('I freeze too, I don't know') lacked descriptive depth and missed target markers.",
              userWrote: "I freeze too, I don't know.",
              correction: "Instead of worrying, I just laugh it off. Awkward moments are totally normal!",
              rule: "Keep unpredictable small talk moving by substituting hesitant phrases with a positive or active strategy.",
            },
          ],
          nextTip: "Use the phrase 'Instead of' to start your answers when asked for a secret or tip, as it immediately structures a recovery strategy.",
          subSkillBreakdown: { fluency: 5, pronunciation: 5, grammar: 5 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_04_04",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.general",
    },
    outputs: {
      correct:
        "Stellar Week 4 Day 4 session! You demonstrated outstanding confidence and fluency in handling awkward moments. You perfectly identified tone shifts in Sarah and Mark's corrections, beautifully shadowed the mid-sentence self-correction pattern, wrote a rich personal reflection under 3-minute timed pressure, and aced the unpredictable small talk challenge. Your ability to recover gracefully is a major milestone in your B1 English journey!",
      wrong:
        "Great effort on today's 'Handling awkward moments' lesson. Recovering from speaking mistakes is a major confidence booster. Focus on practicing self-correction transition markers like 'Oh, wait' and 'Actually' to keep your speech moving smoothly. When writing and talking, try to replace expressions of fear or freezing with structured transition words ('Usually', 'Instead of', 'Simply') to sound more proactive and assured.",
    },
  },
};

const weekFourDayFiveFeedback: FeedbackDayData = {
  dayId: "day_24_04_05",
  activityFeedback: [
    {
      taskId: "w4d5-read-mcq",
      feedbackInput: {
        taskId: "w4d5-read-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect reading comprehension of 'Chasing the Stars'!",
          didWell: [
            "You correctly identified that a gift of binoculars from the grandfather sparked the passion.",
            "You understood the calming effect stargazing has on the narrator's worries."
          ],
          mistakes: [],
          nextTip: "Try explaining your own favorite hobbies in a similar narrative structure.",
          subSkillBreakdown: { comprehension: 10, grammar: 9 },
        },
        wrong: {
          score: 7.5,
          summary: "Good effort, but you missed one key details of the stargazing passage.",
          didWell: [
            "You correctly identified the grandfather's gift and Saturn's rings."
          ],
          mistakes: [
            {
              issue: "You selected that stargazing makes the narrator feel small and isolated. The passage says it is a calming ritual that puts worries into perspective.",
              userWrote: "It makes them feel small and isolated",
              correction: "It gives them a calming perspective on daily problems",
              rule: "Analyze the tone of narrator's modifiers ('calming', 'adjust to infinite beauty') to identify their true feeling.",
            },
          ],
          nextTip: "Double-check emotional and state-of-mind descriptions directly in the text.",
          subSkillBreakdown: { comprehension: 8, grammar: 7 },
        },
      },
    },
    {
      taskId: "w4d5-listen-mcq",
      feedbackInput: {
        taskId: "w4d5-listen-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect listening comprehension of the enthusiastic indoor gardening talk!",
          didWell: [
            "You correctly recognized Monstera deliciosa as the favorite plant.",
            "You accurately noted the three-year duration."
          ],
          mistakes: [],
          nextTip: "Observe how positive modals like 'absolute favorite' are emphasized by native speakers.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 9 },
        },
        wrong: {
          score: 6.7,
          summary: "You got two details right, but missed the duration detail.",
          didWell: [
            "You correctly identified the Monstera deliciosa and the misting routine."
          ],
          mistakes: [
            {
              issue: "You marked the speaker's gardening duration as six months. The audio script explicitly says about three years.",
              userWrote: "Just six months",
              correction: "About three years",
              rule: "Listen closely to numeric keywords and time expressions early in the speech.",
            },
          ],
          nextTip: "Try to listen for time markers like 'for... now' or 'since' to quickly identify duration.",
          subSkillBreakdown: { comprehension: 7, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w4d5-write-transform",
      feedbackInput: {
        taskId: "w4d5-write-transform",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Excellent passion-oriented sentence transformations!",
          didWell: [
            "You successfully transformed basic descriptions into premium, highly expressive sentences.",
            "You beautifully integrated 'huge film fan', 'passionate about', and 'absolute favorite'."
          ],
          mistakes: [],
          nextTip: "Try incorporating these upgraded descriptive expressions in your spontaneous conversations.",
          subSkillBreakdown: { grammar: 10, expression: 10, vocabulary: 9 },
        },
        wrong: {
          score: 6.7,
          summary: "Two outstanding transformations, but one sentence remained quite plain.",
          didWell: [
            "Your transformations for playing guitar and cooking dinner were wonderfully descriptive."
          ],
          mistakes: [
            {
              issue: "Your transform for 'I watch movies' missed expressive passion verbs and hints.",
              userWrote: "I just watch movies when I am bored and have nothing to do.",
              correction: "I am a huge film fan and watch at least two movies a week.",
              rule: "Swap out simple passive descriptions ('watch when bored') for high-energy nouns ('huge film fan') and frequency indicators ('at least twice a week').",
            },
          ],
          nextTip: "Focus on replacing plain passive clauses with active modifiers and strong interest markers.",
          subSkillBreakdown: { grammar: 7, expression: 6, vocabulary: 6 },
        },
      },
    },
    {
      taskId: "w4d5-speak-pic-desc",
      feedbackInput: {
        taskId: "w4d5-speak-pic-desc",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.5,
          summary: "Lovely, fluent, and highly expressive hobby description!",
          didWell: [
            "You correctly identified the gardening scene with the terracotta pots and classic red watering can.",
            "You used beautiful speculative phrases and linked the visual to your own relaxing garden routine smoothly."
          ],
          mistakes: [],
          nextTip: "Add even more visual details like the colors of the blooming flowers next time.",
          subSkillBreakdown: { fluency: 10, pronunciation: 9.5, grammar: 9, vocabulary: 9 },
        },
        wrong: {
          score: 6.0,
          summary: "Spoken description was very plain and missed personal interest connections.",
          didWell: [
            "You identified the red watering can and potted plants correctly."
          ],
          mistakes: [
            {
              issue: "Your transcript lacked speculative language and expressed a blunt negative opinion instead of active hobby description.",
              userWrote: "This is a plant and watering pot. It is red. I do not like plants because they are boring.",
              correction: "In this picture, I can see a beautiful gardening scene with healthy potted plants and a red watering can. It seems like a peaceful garden. I really enjoy gardening myself because connecting with nature is extremely relaxing for me.",
              rule: "Build descriptive speak confidence by replacing short, blunt rejections with speculative projections ('seems like', 'appears to') and positive vocabulary expansions.",
            },
          ],
          nextTip: "Use speculative indicators ('seems like') and describe what the scene feels like or represents to add length.",
          subSkillBreakdown: { fluency: 6, pronunciation: 6, grammar: 6, vocabulary: 5 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_04_05",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.general",
    },
    outputs: {
      correct:
        "Spectacular Week 4 Day 5 session! You demonstrated outstanding confidence and natural warmth in expressing your hobbies and passions. You fully understood the backyard stargazing and indoor gardening passages, upgraded basic sentences into rich, voice-building statements, and spoke with excellent descriptive detail about the outdoor gardening corner. This is a brilliant end to our confidence-building week!",
      wrong:
        "Great effort on today's Talking about Interests lesson! Hobbies and passions are comfortable confidence topics. Work on reading/listening closely for time and modifier clues in text, and when writing or speaking, avoid plain, basic statements. Instead, challenge yourself to use rich speculative vocabulary ('seems like') and active growth modifiers to let your passion shine through.",
    },
  },
};

const weekFourDaySixFeedback: FeedbackDayData = {
  dayId: "day_24_04_06",
  activityFeedback: [
    {
      taskId: "w4d6-read-tone-id",
      feedbackInput: {
        taskId: "w4d6-read-tone-id",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect tone recognition in self-introductions!",
          didWell: [
            "You accurately identified David's polished and structured tone.",
            "You correctly recognized Emma's hesitant and uncertain tone."
          ],
          mistakes: [],
          nextTip: "Notice how polished introductions state the role and focus directly without using qualifiers.",
          subSkillBreakdown: { comprehension: 10, grammar: 10 },
        },
        wrong: {
          score: 5,
          summary: "You had some difficulty identifying the tone differences.",
          didWell: [
            "You correctly identified David's polished tone."
          ],
          mistakes: [
            {
              issue: "You marked Emma's hesitant introduction as polished and confident.",
              userWrote: "Confident / Polished",
              correction: "Hesitant / Uncertain",
              rule: "Fillers ('Um', 'well') and hedges ('I guess', 'hopefully') indicate hesitation.",
            },
          ],
          nextTip: "Look for qualifier words like 'maybe' or 'just' to spot hesitant tones.",
          subSkillBreakdown: { comprehension: 5, grammar: 5 },
        },
      },
    },
    {
      taskId: "w4d6-listen-tone",
      feedbackInput: {
        taskId: "w4d6-listen-tone",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Perfect tone ear training!",
          didWell: [
            "You correctly identified that Speaker A is poised and structured.",
            "You accurately spotted Speaker B's hesitation markers."
          ],
          mistakes: [],
          nextTip: "Pacing your words evenly and speaking continuously instantly increases perceived confidence.",
          subSkillBreakdown: { comprehension: 10, vocabulary: 10 },
        },
        wrong: {
          score: 5,
          summary: "You missed some indicators of vocal confidence.",
          didWell: [
            "You correctly noticed that Speaker A has a polished register."
          ],
          mistakes: [
            {
              issue: "You selected Speaker B (Emma) as more poised than Speaker A (David).",
              userWrote: "Speaker B (Emma)",
              correction: "Speaker A (David)",
              rule: "Steady voice pacing and complete absence of fillers sound much more poised.",
            },
          ],
          nextTip: "Listen to the timing between sentences; confident speakers don't stall.",
          subSkillBreakdown: { comprehension: 5, vocabulary: 5 },
        },
      },
    },
    {
      taskId: "w4d6-write-timed",
      feedbackInput: {
        taskId: "w4d6-write-timed",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Superb timed self-introduction draft!",
          didWell: [
            "You successfully wrote a polished 3-sentence introduction.",
            "You integrated the target words 'thrilled', 'passion', and 'focus' perfectly."
          ],
          mistakes: [],
          nextTip: "Use this written draft directly as notes for your spoken self-introduction.",
          subSkillBreakdown: { expression: 10, grammar: 10, vocabulary: 10 },
        },
        wrong: {
          score: 5,
          summary: "Your timed note was too short and lacked structured details.",
          didWell: [
            "You managed to write your name and role within the time limit."
          ],
          mistakes: [
            {
              issue: "Your writing lacked passion and missed all three target words: 'thrilled', 'passion', 'focus'.",
              userWrote: "I am a new worker here. I don't have a passion, but I just hope to focus on doing my job okay.",
              correction: "I am thrilled to join the team as a software engineer. Solving complex algorithms has always been my core passion. My primary focus is to build clean, efficient, and scalable web platforms.",
              rule: "Use strong assertions ('thrilled', 'core passion', 'primary focus') to build a strong personal projection.",
            },
          ],
          nextTip: "Follow the 3-sentence structure: Role, Passion, Focus, to make drafting easy.",
          subSkillBreakdown: { expression: 5, grammar: 5, vocabulary: 5 },
        },
      },
    },
    {
      taskId: "w4d6-speak-present",
      feedbackInput: {
        taskId: "w4d6-speak-present",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.6,
          summary: "poised, highly structured and professional presentation!",
          didWell: [
            "You presented your background, passion, and focus in three logical steps.",
            "Your vocal projection was clear, and you paced your sentences with excellent poise."
          ],
          mistakes: [],
          nextTip: "Practice this exact presentation multiple times to make it completely natural for actual job interviews.",
          subSkillBreakdown: { fluency: 10, pronunciation: 9.6, grammar: 9, vocabulary: 10 },
        },
        wrong: {
          score: 5.5,
          summary: "Spoken presentation was hesitant and lacked clear structure.",
          didWell: [
            "You spoke clearly and stayed within the 90-second time limit."
          ],
          mistakes: [
            {
              issue: "Your presentation had many hesitation fillers ('Um', 'don't know') and failed to state a clear passion or focus.",
              userWrote: "Um, hi... I am a new engineer here. I don't know, I just... write code. I don't really have a big passion or focus yet.",
              correction: "Hello everyone, I am thrilled to join the team as a new engineer. Writing efficient code is my lifelong passion. My primary focus is to build robust systems. I look forward to working together with you all.",
              rule: "Deliver a presentation with structure and poise by avoiding hedges like 'don't know' and replacing them with direct passion statements.",
            },
          ],
          nextTip: "Take a deep breath and use your written draft notes to guide your speech steadily.",
          subSkillBreakdown: { fluency: 6, pronunciation: 6, grammar: 5, vocabulary: 5 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_04_06",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.general",
    },
    outputs: {
      correct:
        "Exceptional work on Week 4 Day 6! You've mastered presenting yourself with poise and structure. You correctly identified confident and hesitant self-introductions, successfully trained your ear for vocal tone, drafted a beautiful 3-sentence notes scaffold, and delivered a highly poised and structured 90-second self-introduction. You are sounding extremely professional and confident!",
      wrong:
        "Good effort today on presenting yourself. While you completed the practice tasks, focus on keeping your introductions structured and free of filler words. Try to avoid hedge words like 'maybe' and 'just' when writing and speaking, and utilize a simple three-sentence outline (Role, Passion, Focus) to ensure your message is clear and confident.",
    },
  },
};

const weekFourDaySevenFeedback: FeedbackDayData = {
  dayId: "day_24_04_07",
  activityFeedback: [
    {
      taskId: "w4d7-read-mcq",
      feedbackInput: {
        taskId: "w4d7-read-mcq",
        evaluationRef: "evaluation.source.activityEvaluations[0]",
        learnerResponseRef: "tasks.source.tasks[0].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Masterful reading comprehension of 'Finding My Voice'!",
          didWell: [
            "You correctly identified that a fear of making mistakes kept the narrator silent.",
            "You understood that fluency is about connection, not perfection."
          ],
          mistakes: [],
          nextTip: "Write down a few keywords that reflect your own connection-focused mindset.",
          subSkillBreakdown: { comprehension: 10, grammar: 9 },
        },
        wrong: {
          score: 7.5,
          summary: "Good effort, but you missed one key detail of the narrator's journey.",
          didWell: [
            "You correctly understood the narrator's fear and their mentor's core message."
          ],
          mistakes: [
            {
              issue: "You marked taking a written exam as the narrator's first step. The passage explicitly states they started by shadowing short audio clips and recording their voice.",
              userWrote: "Taking a difficult written grammar exam",
              correction: "Shadowing short audio clips and recording their own voice",
              rule: "Read chronologically to track the narrator's starting action steps.",
            },
          ],
          nextTip: "Focus on locating starting words like 'I started by' to accurately identify the first action.",
          subSkillBreakdown: { comprehension: 8, grammar: 7 },
        },
      },
    },
    {
      taskId: "w4d7-listen-shadow",
      feedbackInput: {
        taskId: "w4d7-listen-shadow",
        evaluationRef: "evaluation.source.activityEvaluations[1]",
        learnerResponseRef: "tasks.source.tasks[1].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Crisp and energetic shadowing!",
          didWell: [
            "You shadowed the growth affirmation with exceptional speed, rhythm, and clarity.",
            "You pronounced 'proud of', 'progress', and 'confidence' beautifully."
          ],
          mistakes: [],
          nextTip: "Repeat this exact growth statement to yourself in the morning to start your day with energy!",
          subSkillBreakdown: { pronunciation: 10, fluency: 10 },
        },
        wrong: {
          score: 5.0,
          summary: "Your shadowing was slightly hesitant and missed key target words.",
          didWell: [
            "Your pronunciation of 'unique' and 'voice' was excellent."
          ],
          mistakes: [
            {
              issue: "You missed the target words 'proud of' and 'confidence' in your recording.",
              userWrote: "My voice is unique, and I am proud of progress. Every single day, I speak with confidence.",
              correction: "My voice is unique, and I am proud of my progress. Every single day, I am speaking with more confidence and energy!",
              rule: "Make sure to pronounce every word in the target sentence, especially key nouns and adjectives.",
            },
          ],
          nextTip: "Listen to the recording twice and speak along in unison to build natural timing.",
          subSkillBreakdown: { pronunciation: 5, fluency: 5 },
        },
      },
    },
    {
      taskId: "w4d7-write-timed",
      feedbackInput: {
        taskId: "w4d7-write-timed",
        evaluationRef: "evaluation.source.activityEvaluations[2]",
        learnerResponseRef: "tasks.source.tasks[2].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 10,
          summary: "Highly reflective and beautiful Cycle 1 wrap-up!",
          didWell: [
            "You wrote a wonderfully personal, forward-looking paragraph showing great resilience.",
            "You integrated the target adverbs 'discovered', 'moreover', and 'in the future' flawlessly."
          ],
          mistakes: [],
          nextTip: "Keep writing regular short reflections to cement your vocabulary gains.",
          subSkillBreakdown: { expression: 10, grammar: 10, vocabulary: 10 },
        },
        wrong: {
          score: 5.0,
          summary: "Your paragraph was too brief and did not address the target prompts.",
          didWell: [
            "You expressed your main learning that you speak better now."
          ],
          mistakes: [
            {
              issue: "Your timed response was very short and missed all three target words.",
              userWrote: "I learned that I speak better. I don't know what else.",
              correction: "This week, I discovered that I am much more resilient than I thought. Moreover, I realized that making mistakes is simply part of learning, not a failure. In the future, I will continue speaking up without fear.",
              rule: "Structure your response into at least three sentences: one for discovery, one for support, and one for future planning.",
            },
          ],
          nextTip: "Spend the first 30 seconds listing your target words as visual anchors before writing.",
          subSkillBreakdown: { expression: 5, grammar: 5, vocabulary: 5 },
        },
      },
    },
    {
      taskId: "w4d7-speak-debate",
      feedbackInput: {
        taskId: "w4d7-speak-debate",
        evaluationRef: "evaluation.source.activityEvaluations[3]",
        learnerResponseRef: "tasks.source.tasks[3].answers[answerView]",
      },
      outputs: {
        correct: {
          score: 9.8,
          summary: "Outstanding performance in the Debate Arena!",
          didWell: [
            "You successfully defended learning with others with strong opinion structures.",
            "You used the debate markers 'strongly believe', 'however', and 'on the other hand' perfectly."
          ],
          mistakes: [],
          nextTip: "Try to debate more complex topics using the same outline of stating a preference and listing counters.",
          subSkillBreakdown: { fluency: 10, pronunciation: 9, grammar: 10, vocabulary: 10 },
        },
        wrong: {
          score: 5.5,
          summary: "Your argument was hesitant and failed to defend your side clearly.",
          didWell: [
            "You spoke clearly and remained friendly throughout the debate."
          ],
          mistakes: [
            {
              issue: "Your speech was very brief, neutral, and missed all target debate markers.",
              userWrote: "I think learning alone is okay but learning with others is nice. I don't know.",
              correction: "While learning alone has benefits, I strongly believe learning with others is better. On the other hand, you can practice speaking with partners. However, group work makes learning much more fun!",
              rule: "In a debate, pick one side clearly and argue for it using transition words instead of remaining in the middle.",
            },
          ],
          nextTip: "Start your response directly with a high-conviction phrase like 'I strongly believe' to set a solid direction.",
          subSkillBreakdown: { fluency: 6, pronunciation: 6, grammar: 5, vocabulary: 5 },
        },
      },
    },
  ],
  ragFeedback: {
    dayId: "day_24_04_07",
    memoryInput: {
      scorecardRef: "evaluation.source.overallScorecard",
      activityFeedbackRefs: [
        "feedback.source.activityFeedback[0]",
        "feedback.source.activityFeedback[1]",
        "feedback.source.activityFeedback[2]",
        "feedback.source.activityFeedback[3]",
      ],
      learnerHistoryRef: "mock.userMemory.general",
    },
    outputs: {
      correct:
        "Sensational Cycle 1 wrap-up! Today, you achieved absolute excellence in our Full Confidence Showcase. You demonstrated flawless reading comprehension on overcoming speaker dread, delivered a crisp and highly energetic shadow session, crafted a deeply thoughtful timed growth reflection, and successfully won a friendly debate with the AI Opponent on group learning. Your growth from Day 1 to Day 28 is spectacular. Congratulations on completing Cycle 1!",
      wrong:
        "Congratulations on completing Cycle 1! Today's Showcase featured great effort. To continue growing your speaking confidence, focus on precision reading comprehension and double-checking textual cues. For shadowing, practice speaking along in unison to build rhythmic energy. Finally, when debating or reflecting, avoid passive or neutral statements; instead, challenge yourself to use high-certainty debate markers ('strongly believe', 'however', 'on the other hand') to voice your opinions with poise.",
    },
  },
};

const feedbackDays: Partial<Record<CourseTrack, Record<number, Record<number, FeedbackDayData>>>> = {
  "24w": {
    1: {
      1: weekOneDayOneFeedback,
      2: weekOneDayTwoFeedback,
      3: weekOneDayThreeFeedback,
      4: weekOneDayFourFeedback,
      5: weekOneDayFiveFeedback,
      6: weekOneDaySixFeedback,
      7: weekOneDaySevenFeedback,
    },
    2: {
      1: weekTwoDayOneFeedback,
      2: weekTwoDayTwoFeedback,
      3: weekTwoDayThreeFeedback,
      4: weekTwoDayFourFeedback,
      5: weekTwoDayFiveFeedback,
      6: weekTwoDaySixFeedback,
      7: weekTwoDaySevenFeedback,
    },
    3: {
      1: weekThreeDayOneFeedback,
      2: weekThreeDayTwoFeedback,
      3: weekThreeDayThreeFeedback,
      4: weekThreeDayFourFeedback,
      5: weekThreeDayFiveFeedback,
      6: weekThreeDaySixFeedback,
      7: weekThreeDaySevenFeedback,
    },
    4: {
      1: weekFourDayOneFeedback,
      2: weekFourDayTwoFeedback,
      3: weekFourDayThreeFeedback,
      4: weekFourDayFourFeedback,
      5: weekFourDayFiveFeedback,
      6: weekFourDaySixFeedback,
      7: weekFourDaySevenFeedback,
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
