import type { AnswerView, CourseTrack } from "../teaching/source";

export type TaskWidgetKind =
  | "error_spotting"
  | "fill_blanks"
  | "read_structure"
  | "listen_cloze"
  | "listen_mcq"
  | "listen_infer"
  | "read_comp_mcq"
  | "listen_dictation"
  | "error_correction"
  | "sentence_transform"
  | "open_text"
  | "read_aloud"
  | "speak_record"
  | "read_word_match"
  | "speak_pic_desc"
  | "write_paragraph"
  | "speak_roleplay"
  | "speak_interview"
  | "read_tfng"
  | "listen_shadow"
  | "write_email"
  | "speak_smalltalk"
  | "listen_retell"
  | "write_paraphrase"
  | "read_tone_id"
  | "speak_present"
  | "write_bullets_to_para"
  | "write_word_upgrade"
  | "speak_timed"
  | "write_timed"
  | "read_context_mcq"
  | "listen_tone"
  | "speak_debate";

interface BaseTask {
  id: string;
  sequence: number;
  archetypeId: string;
  widget: TaskWidgetKind;
  sectionLabel: string;
  topic: string;
  taskIntro: string;
  instructions: string;
  subSkill: string;
  activity: string;
  estimatedMinutes: number;
}

export interface BlankItem {
  itemId: string;
  sentenceWithBlank: string;
  baseVerb: string;
  correctAnswer: string;
  explanation: string;
}

export interface FillBlanksTask extends BaseTask {
  widget: "fill_blanks";
  passageTitle: string;
  passage: string;
  grammarRule: string;
  items: BlankItem[];
  answers: Record<AnswerView, Record<string, string>>;
}

export interface ErrorSpottingToken {
  tokenId: string;
  text: string;
  isError: boolean;
}

export interface ErrorSpottingError {
  tokenId: string;
  incorrectPhrase: string;
  correction: string;
  rule: string;
  explanation: string;
}

export interface ErrorSpottingSentence {
  sentenceId: string;
  tokens: ErrorSpottingToken[];
  error: ErrorSpottingError;
}

export interface ErrorSpottingTask extends BaseTask {
  widget: "error_spotting";
  passageTitle: string;
  grammarRule: string;
  sentences: ErrorSpottingSentence[];
  answers: Record<AnswerView, string[]>;
}

export interface McqItem {
  itemId: string;
  prompt: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

export interface ListenMcqTask extends BaseTask {
  widget: "listen_mcq";
  audioGenre: string;
  audioScript: string;
  audioDurationSeconds: number;
  innerWidget: "mcq";
  items: McqItem[];
  answers: Record<AnswerView, Record<string, number>>;
}

export interface ListenInferTask extends BaseTask {
  widget: "listen_infer";
  audioGenre: string;
  audioScript: string;
  audioDurationSeconds: number;
  intentFocus: string;
  items: McqItem[];
  answers: Record<AnswerView, Record<string, number>>;
}

export interface ListenToneIntroItem {
  id: string;
  label: string;
  speaker: string;
  audioScript: string;
  audioDurationSeconds: number;
}

export interface ListenToneTask extends BaseTask {
  widget: "listen_tone";
  grammarRule: string;
  intros: ListenToneIntroItem[];
  items: McqItem[];
  answers: Record<AnswerView, Record<string, number>>;
}


export interface ReadCompMcqTask extends BaseTask {
  widget: "read_comp_mcq";
  passageTitle: string;
  passage: string;
  grammarRule: string;
  items: McqItem[];
  answers: Record<AnswerView, Record<string, number>>;
}

export interface ToneIdItem {
  itemId: string;
  sender: string;
  message: string;
  prompt: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

export interface ReadToneIdTask extends BaseTask {
  widget: "read_tone_id";
  passageTitle: string;
  grammarRule: string;
  items: ToneIdItem[];
  answers: Record<AnswerView, Record<string, number>>;
}

export interface ReadContextMcqTask extends BaseTask {
  widget: "read_context_mcq";
  passageTitle: string;
  passage: string;
  grammarRule: string;
  items: McqItem[];
  answers: Record<AnswerView, Record<string, number>>;
}

export interface ListenClozeTask extends BaseTask {
  widget: "listen_cloze";
  audioGenre: string;
  audioScript: string;
  audioDurationSeconds: number;
  passageTitle: string;
  passage: string;
  grammarRule: string;
  targetWords: string[];
  items: BlankItem[];
  answers: Record<AnswerView, Record<string, string>>;
}

export interface DictationItem {
  itemId: string;
  prompt: string;
  correctAnswer: string;
  explanation: string;
}

export interface ListenDictationTask extends BaseTask {
  widget: "listen_dictation";
  audioGenre: string;
  audioScript: string;
  audioDurationSeconds: number;
  grammarRule: string;
  targetWords: string[];
  items: DictationItem[];
  answers: Record<AnswerView, Record<string, string>>;
}

export interface OpenTextItem {
  itemId: string;
  prompt: string;
  sampleAnswer: string;
  answerHints: string[];
}

export interface OpenTextAnswer {
  itemId: string;
  text: string;
  isCorrect: boolean;
}

export interface OpenTextTask extends BaseTask {
  widget: "open_text";
  grammarRule: string;
  targetWords: string[];
  commonMistakes: string[];
  items: OpenTextItem[];
  answers: Record<AnswerView, OpenTextAnswer[]>;
}

export interface ErrorCorrectionItem {
  itemId: string;
  incorrectSentence: string;
  sampleAnswer: string;
  watchHints: string[];
}

export interface ErrorCorrectionTask extends BaseTask {
  widget: "error_correction";
  grammarRule: string;
  items: ErrorCorrectionItem[];
  answers: Record<AnswerView, OpenTextAnswer[]>;
}

export interface SentenceTransformItem {
  itemId: string;
  sourceSentence: string;
  sampleAnswer: string;
  watchHints: string[];
}

export interface SentenceTransformTask extends BaseTask {
  widget: "sentence_transform";
  grammarRule: string;
  items: SentenceTransformItem[];
  answers: Record<AnswerView, OpenTextAnswer[]>;
}

export interface SpeakingAnswer {
  itemId: string;
  transcript: string;
  durationSeconds: number;
  isCorrect: boolean;
}

export interface SpeakRecordTask extends BaseTask {
  widget: "speak_record";
  mode: "timed" | "read_aloud";
  speakingDurationSeconds: number;
  grammarRule: string;
  targetWords: string[];
  prompts: string[];
  sampleResponses: string[];
  answers: Record<AnswerView, SpeakingAnswer[]>;
}

export interface ReadAloudTask extends BaseTask {
  widget: "read_aloud";
  textToReadAloud: string;
  grammarRule: string;
  targetWords: string[];
  speakingDurationSeconds: number;
  answers: Record<AnswerView, SpeakingAnswer[]>;
}


export interface WordMatchItem {
  itemId: string;
  prompt: string;
  correctAnswer: string;
  explanation: string;
}

export interface ReadWordMatchTask extends BaseTask {
  widget: "read_word_match";
  grammarRule: string;
  items: WordMatchItem[];
  options: string[];
  answers: Record<AnswerView, Record<string, string>>;
}

export interface StructureLabelItem {
  itemId: string;
  label?: string;
  paragraph: string;
  correctAnswer: string;
  explanation: string;
}

export interface ReadStructureTask extends BaseTask {
  widget: "read_structure";
  passageTitle: string;
  grammarRule: string;
  structureLabels: string[];
  items: StructureLabelItem[];
  answers: Record<AnswerView, Record<string, string>>;
}

export interface SpeakPicDescTask extends BaseTask {
  widget: "speak_pic_desc";
  imageUrl: string;
  imageAlt: string;
  grammarRule: string;
  speakingDurationSeconds: number;
  answers: Record<AnswerView, SpeakingAnswer[]>;
}

export interface WriteParagraphTask extends BaseTask {
  widget: "write_paragraph";
  prompt: string;
  grammarRule: string;
  targetWords: string[];
  minimumWords: number;
  sampleAnswer: string;
  answerHints: string[];
  answers: Record<AnswerView, OpenTextAnswer[]>;
}

export interface WriteBulletsToParaTask extends BaseTask {
  widget: "write_bullets_to_para";
  bullets: string[];
  prompt: string;
  grammarRule: string;
  targetWords: string[];
  minimumWords: number;
  sampleAnswer: string;
  answerHints: string[];
  answers: Record<AnswerView, OpenTextAnswer[]>;
}

export interface SpeakRoleplayTask extends BaseTask {
  widget: "speak_roleplay";
  dialogueContext: {
    role: string;
    text: string;
    speaker: "partner" | "learner";
  }[];
  grammarRule: string;
  targetWords: string[];
  speakingDurationSeconds: number;
  answers: Record<AnswerView, SpeakingAnswer[]>;
}

export interface InterviewQuestion {
  itemId: string;
  interviewerPrompt: string;
  sampleAnswer: string;
  answerHint: string;
}

export interface SpeakInterviewTask extends BaseTask {
  widget: "speak_interview";
  interviewContext: string;
  grammarRule: string;
  targetWords: string[];
  speakingDurationSeconds: number;
  questions: InterviewQuestion[];
  answers: Record<AnswerView, SpeakingAnswer[]>;
}

export interface TfngItem {
  itemId: string;
  prompt: string;
  correctAnswer: "True" | "False" | "Not Given";
  explanation: string;
}

export interface ReadTfngTask extends BaseTask {
  widget: "read_tfng";
  passageTitle: string;
  passage: string;
  grammarRule: string;
  items: TfngItem[];
  answers: Record<AnswerView, Record<string, "True" | "False" | "Not Given">>;
}

export interface ListenShadowTask extends BaseTask {
  widget: "listen_shadow";
  audioGenre: string;
  audioScript: string;
  audioDurationSeconds: number;
  grammarRule: string;
  targetWords: string[];
  textToShadow: string;
  answers: Record<AnswerView, SpeakingAnswer[]>;
}

export interface WriteEmailTask extends BaseTask {
  widget: "write_email";
  prompt: string;
  grammarRule: string;
  targetWords: string[];
  minimumWords: number;
  sampleAnswer: string;
  answerHints: string[];
  answers: Record<AnswerView, OpenTextAnswer[]>;
}

export interface SpeakSmalltalkTask extends BaseTask {
  widget: "speak_smalltalk";
  dialogueContext: {
    role: string;
    text: string;
    speaker: "partner" | "learner";
  }[];
  grammarRule: string;
  targetWords: string[];
  speakingDurationSeconds: number;
  answers: Record<AnswerView, SpeakingAnswer[]>;
}

export interface RetellAnswer {
  itemId: string;
  text?: string;
  transcript?: string;
  durationSeconds?: number;
  isCorrect: boolean;
}

export interface ListenRetellTask extends BaseTask {
  widget: "listen_retell";
  responseMode?: "spoken" | "written";
  audioGenre: string;
  audioScript: string;
  audioDurationSeconds: number;
  grammarRule: string;
  targetWords: string[];
  passageToRetell: string;
  answers: Record<AnswerView, RetellAnswer[]>;
}

export interface ParaphraseItem {
  itemId: string;
  incorrectSentence: string;
  sampleAnswer: string;
  watchHints: string[];
}

export interface WriteParaphraseTask extends BaseTask {
  widget: "write_paraphrase";
  grammarRule: string;
  items: ParaphraseItem[];
  answers: Record<AnswerView, OpenTextAnswer[]>;
}

export interface SpeakPresentTask extends BaseTask {
  widget: "speak_present";
  grammarRule: string;
  targetWords: string[];
  speakingDurationSeconds: number;
  visualPromptDescription: string;
  modelPresentation?: string;
  answers: Record<AnswerView, SpeakingAnswer[]>;
}

export interface WordUpgradeItem {
  itemId: string;
  sourceSentence: string;
  targetUpgradeWord: string;
  sampleAnswer: string;
  watchHints: string[];
}

export interface WriteWordUpgradeTask extends BaseTask {
  widget: "write_word_upgrade";
  grammarRule: string;
  items: WordUpgradeItem[];
  answers: Record<AnswerView, OpenTextAnswer[]>;
}

export interface SpeakTimedTask extends BaseTask {
  widget: "speak_timed";
  grammarRule: string;
  targetWords: string[];
  speakingDurationSeconds: number;
  prompt: string;
  sampleResponse: string;
  answers: Record<AnswerView, SpeakingAnswer[]>;
}

export interface WriteTimedTask extends BaseTask {
  widget: "write_timed";
  grammarRule: string;
  targetWords: string[];
  writingDurationSeconds: number;
  prompt: string;
  sampleAnswer: string;
  answers: Record<AnswerView, Array<{ itemId: string; text: string; isCorrect: boolean }>>;
  answerHints: string[];
}

export interface SpeakDebateDialogueTurn {
  role: string;
  text: string;
  speaker: "ai" | "learner";
}

export interface SpeakDebateTask extends BaseTask {
  widget: "speak_debate";
  grammarRule: string;
  targetWords: string[];
  speakingDurationSeconds: number;
  debateContext: SpeakDebateDialogueTurn[];
  answers: Record<AnswerView, SpeakingAnswer[]>;
}

export type SessionTask =
  | ErrorSpottingTask
  | FillBlanksTask
  | ListenClozeTask
  | ListenMcqTask
  | ListenInferTask
  | ReadCompMcqTask
  | ReadToneIdTask
  | ListenDictationTask
  | ErrorCorrectionTask
  | SentenceTransformTask
  | OpenTextTask
  | ReadAloudTask
  | SpeakRecordTask
  | ReadWordMatchTask
  | ReadStructureTask
  | SpeakPicDescTask
  | WriteParagraphTask
  | WriteBulletsToParaTask
  | SpeakRoleplayTask
  | SpeakInterviewTask
  | ReadTfngTask
  | ListenShadowTask
  | WriteEmailTask
  | SpeakSmalltalkTask
  | ListenRetellTask
  | WriteParaphraseTask
  | SpeakPresentTask
  | WriteWordUpgradeTask
  | SpeakTimedTask
  | WriteTimedTask
  | ReadContextMcqTask
  | ListenToneTask
  | SpeakDebateTask;

export interface TaskDayData {
  dayId: string;
  tasks: SessionTask[];
}

const weekOneDayOneTasks: TaskDayData = {
  dayId: "day_24_01_01",
  tasks: [
    {
      id: "w1d1-read-cloze",
      sequence: 1,
      archetypeId: "READ_CLOZE",
      widget: "fill_blanks",
      sectionLabel: "Reading cloze",
      topic: "Simple present routines",
      taskIntro: "Complete the routine passage",
      instructions:
        "Fill each blank with the correct simple present verb form.",
      subSkill: "Grammar",
      activity: "Read",
      estimatedMinutes: 3,
      passageTitle: "Lina's Morning",
      passage:
        "Every morning, Lina ___ at 6:30. She ___ tea before class. Her brother Ravi ___ the bus at 7:15. They ___ English after dinner, and Lina usually ___ music before bed.",
      grammarRule:
        "Use the base verb with I, you, we, and they. Add -s or -es with he, she, and singular names.",
      items: [
        {
          itemId: "b1",
          sentenceWithBlank: "Every morning, Lina ___ at 6:30.",
          baseVerb: "wake",
          correctAnswer: "wakes",
          explanation: "Lina is one person, so wake becomes wakes.",
        },
        {
          itemId: "b2",
          sentenceWithBlank: "She ___ tea before class.",
          baseVerb: "drink",
          correctAnswer: "drinks",
          explanation: "She takes the third-person -s form: drinks.",
        },
        {
          itemId: "b3",
          sentenceWithBlank: "Her brother Ravi ___ the bus at 7:15.",
          baseVerb: "take",
          correctAnswer: "takes",
          explanation: "Ravi is one person, so take becomes takes.",
        },
        {
          itemId: "b4",
          sentenceWithBlank: "They ___ English after dinner.",
          baseVerb: "study",
          correctAnswer: "study",
          explanation: "They uses the base verb: study.",
        },
        {
          itemId: "b5",
          sentenceWithBlank: "Lina usually ___ music before bed.",
          baseVerb: "play",
          correctAnswer: "plays",
          explanation: "Lina is one person, so play becomes plays.",
        },
      ],
      answers: {
        correct: {
          b1: "wakes",
          b2: "drinks",
          b3: "takes",
          b4: "study",
          b5: "plays",
        },
        wrong: {
          b1: "wakes",
          b2: "drinks",
          b3: "take",
          b4: "study",
          b5: "plays",
        },
      },
    },
    {
      id: "w1d1-listen-mcq",
      sequence: 2,
      archetypeId: "LISTEN_MCQ",
      widget: "listen_mcq",
      sectionLabel: "Listening MCQ",
      topic: "Listening for daily routines",
      taskIntro: "Listen to Omar's weekday routine",
      instructions:
        "Review the completed listening answers and the explanation for each question.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 4,
      audioGenre: "Short routine monologue",
      audioDurationSeconds: 48,
      audioScript:
        "Omar usually wakes up at six thirty. He eats breakfast with his sister, and then he walks to the bus stop. On Mondays, he studies English after school. He never plays games before homework, but he often listens to music at night.",
      innerWidget: "mcq",
      items: [
        {
          itemId: "q1",
          prompt: "What time does Omar usually wake up?",
          options: ["Six o'clock", "Six thirty", "Seven fifteen", "Eight o'clock"],
          correctIndex: 1,
          explanation: "The audio says Omar usually wakes up at six thirty.",
        },
        {
          itemId: "q2",
          prompt: "Who does Omar eat breakfast with?",
          options: ["His brother", "His sister", "His friend", "His teacher"],
          correctIndex: 1,
          explanation: "The audio says he eats breakfast with his sister.",
        },
        {
          itemId: "q3",
          prompt: "What does Omar do after school on Mondays?",
          options: ["Studies English", "Plays games", "Visits a park", "Reads comics"],
          correctIndex: 0,
          explanation: "The audio says he studies English after school on Mondays.",
        },
        {
          itemId: "q4",
          prompt: "What does Omar often do at night?",
          options: ["Cooks dinner", "Runs outside", "Listens to music", "Calls his teacher"],
          correctIndex: 2,
          explanation: "The audio says he often listens to music at night.",
        },
      ],
      answers: {
        correct: { q1: 1, q2: 1, q3: 0, q4: 2 },
        wrong: { q1: 1, q2: 1, q3: 1, q4: 2 },
      },
    },
    {
      id: "w1d1-write-open-sent",
      sequence: 3,
      archetypeId: "WRITE_OPEN_SENT",
      widget: "open_text",
      sectionLabel: "Writing task",
      topic: "Write simple present routine sentences",
      taskIntro: "Write three routine sentences",
      instructions:
        "Use I, he, and she with frequency adverbs and the correct simple present verb form.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 5,
      grammarRule:
        "I uses the base verb. He and she use the third-person -s form.",
      targetWords: ["always", "usually", "often", "sometimes", "never"],
      commonMistakes: [
        "Do not add -s after I.",
        "Do add -s after he or she.",
        "Put the frequency adverb before the main verb.",
      ],
      items: [
        {
          itemId: "w1",
          prompt: "Write one affirmative routine sentence with I and a frequency adverb.",
          sampleAnswer: "I usually drink tea in the morning.",
          answerHints: ["Start with I.", "Use the base verb.", "Add one frequency adverb."],
        },
        {
          itemId: "w2",
          prompt: "Write one routine sentence with he and a frequency adverb.",
          sampleAnswer: "He often walks to school.",
          answerHints: ["Start with He.", "Add -s to the main verb."],
        },
        {
          itemId: "w3",
          prompt: "Write one routine sentence with she and a frequency adverb.",
          sampleAnswer: "She sometimes studies English after dinner.",
          answerHints: ["Start with She.", "Use a frequency adverb.", "Add -s or -es when needed."],
        },
      ],
      answers: {
        correct: [
          { itemId: "w1", text: "I usually drink tea in the morning.", isCorrect: true },
          { itemId: "w2", text: "He often walks to school.", isCorrect: true },
          { itemId: "w3", text: "She sometimes studies English after dinner.", isCorrect: true },
        ],
        wrong: [
          { itemId: "w1", text: "I usually drink tea in the morning.", isCorrect: true },
          { itemId: "w2", text: "He often walks to school.", isCorrect: true },
          { itemId: "w3", text: "She sometimes study English after dinner.", isCorrect: false },
        ],
      },
    },
    {
      id: "w1d1-speak-timed",
      sequence: 4,
      archetypeId: "SPEAK_TIMED",
      widget: "speak_record",
      sectionLabel: "Speaking task",
      topic: "Say simple present routines",
      taskIntro: "Record your routine sentences",
      instructions:
        "Say one short routine sentence for each prompt. Use a frequency adverb and the correct verb form.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      mode: "timed",
      speakingDurationSeconds: 45,
      grammarRule:
        "Use base verbs with I. Use third-person -s with he and she.",
      targetWords: ["always", "usually", "often", "sometimes", "never"],
      prompts: [
        "Say one routine sentence with I and a frequency adverb.",
        "Say one routine sentence with he and a frequency adverb.",
        "Say one routine sentence with she and a frequency adverb.",
      ],
      sampleResponses: [
        "I usually read after dinner.",
        "He often plays football on Sunday.",
        "She never drinks coffee at night.",
      ],
      answers: {
        correct: [
          { itemId: "prompt_1", transcript: "I usually read after dinner.", durationSeconds: 7, isCorrect: true },
          { itemId: "prompt_2", transcript: "He often plays football on Sunday.", durationSeconds: 8, isCorrect: true },
          { itemId: "prompt_3", transcript: "She never drinks coffee at night.", durationSeconds: 7, isCorrect: true },
        ],
        wrong: [
          { itemId: "prompt_1", transcript: "I usually read after dinner.", durationSeconds: 7, isCorrect: true },
          { itemId: "prompt_2", transcript: "He often play football on Sunday.", durationSeconds: 8, isCorrect: false },
          { itemId: "prompt_3", transcript: "She never drinks coffee at night.", durationSeconds: 7, isCorrect: true },
        ],
      },
    },
  ],
};

const weekOneDayTwoTasks: TaskDayData = {
  dayId: "day_24_01_02",
  tasks: [
    {
      id: "w1d2-read-error-spot",
      sequence: 1,
      archetypeId: "READ_ERROR_SPOT",
      widget: "error_spotting",
      sectionLabel: "Reading task",
      topic: "Spot past tense errors",
      taskIntro: "Tap each word with a grammar mistake",
      instructions:
        "Read the passage and find the one incorrect word in each sentence.",
      subSkill: "Grammar",
      activity: "Read",
      estimatedMinutes: 3,
      passageTitle: "Yesterday's Events",
      grammarRule:
        "Use simple past for finished actions. Some verbs are irregular, and after did the main verb stays in base form.",
      sentences: [
        {
          sentenceId: "s1",
          tokens: [
            { tokenId: "s1_t1", text: "Yesterday", isError: false },
            { tokenId: "s1_t2", text: "I", isError: false },
            { tokenId: "s1_t3", text: "goed", isError: true },
            { tokenId: "s1_t4", text: "to", isError: false },
            { tokenId: "s1_t5", text: "the", isError: false },
            { tokenId: "s1_t6", text: "market.", isError: false },
          ],
          error: {
            tokenId: "s1_t3",
            incorrectPhrase: "goed",
            correction: "went",
            rule: "Use the irregular past form of go: went.",
            explanation: "Go does not become goed in the past.",
          },
        },
        {
          sentenceId: "s2",
          tokens: [
            { tokenId: "s2_t1", text: "She", isError: false },
            { tokenId: "s2_t2", text: "did", isError: false },
            { tokenId: "s2_t3", text: "finished", isError: true },
            { tokenId: "s2_t4", text: "her", isError: false },
            { tokenId: "s2_t5", text: "homework", isError: false },
            { tokenId: "s2_t6", text: "last", isError: false },
            { tokenId: "s2_t7", text: "night.", isError: false },
          ],
          error: {
            tokenId: "s2_t3",
            incorrectPhrase: "finished",
            correction: "finish",
            rule: "After did, use the base verb.",
            explanation: "Did already marks past time, so finished becomes finish.",
          },
        },
        {
          sentenceId: "s3",
          tokens: [
            { tokenId: "s3_t1", text: "The", isError: false },
            { tokenId: "s3_t2", text: "new", isError: false },
            { tokenId: "s3_t3", text: "manager", isError: false },
            { tokenId: "s3_t4", text: "hired", isError: true },
            { tokenId: "s3_t5", text: "last", isError: false },
            { tokenId: "s3_t6", text: "week.", isError: false },
          ],
          error: {
            tokenId: "s3_t4",
            incorrectPhrase: "hired",
            correction: "was hired",
            rule: "Use was or were + past participle when the subject receives the action.",
            explanation: "The manager received the hiring action, so was is needed.",
          },
        },
        {
          sentenceId: "s4",
          tokens: [
            { tokenId: "s4_t1", text: "Last", isError: false },
            { tokenId: "s4_t2", text: "summer", isError: false },
            { tokenId: "s4_t3", text: "we", isError: false },
            { tokenId: "s4_t4", text: "visit", isError: true },
            { tokenId: "s4_t5", text: "our", isError: false },
            { tokenId: "s4_t6", text: "grandparents.", isError: false },
          ],
          error: {
            tokenId: "s4_t4",
            incorrectPhrase: "visit",
            correction: "visited",
            rule: "Use a past verb with past time markers like last summer.",
            explanation: "Last summer tells us the action is finished.",
          },
        },
        {
          sentenceId: "s5",
          tokens: [
            { tokenId: "s5_t1", text: "They", isError: false },
            { tokenId: "s5_t2", text: "had", isError: false },
            { tokenId: "s5_t3", text: "a", isError: false },
            { tokenId: "s5_t4", text: "good", isError: false },
            { tokenId: "s5_t5", text: "advices", isError: true },
            { tokenId: "s5_t6", text: "after", isError: false },
            { tokenId: "s5_t7", text: "the", isError: false },
            { tokenId: "s5_t8", text: "meeting.", isError: false },
          ],
          error: {
            tokenId: "s5_t5",
            incorrectPhrase: "advices",
            correction: "advice",
            rule: "Advice is uncountable, so do not add -s.",
            explanation: "The past verb had is correct, but advice should stay singular.",
          },
        },
      ],
      answers: {
        correct: ["s1_t3", "s2_t3", "s3_t4", "s4_t4", "s5_t5"],
        wrong: ["s1_t3", "s2_t3", "s3_t4", "s4_t3", "s5_t5"],
      },
    },
    {
      id: "w1d2-listen-cloze",
      sequence: 2,
      archetypeId: "LISTEN_CLOZE",
      widget: "listen_cloze",
      sectionLabel: "Listening task",
      topic: "Listen and fill past verb forms",
      taskIntro: "Listen, then complete the past-tense notes",
      instructions:
        "Play the audio once, then type the missing past-tense verbs in the paraphrased notes.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 3,
      audioGenre: "Office stand-up",
      audioDurationSeconds: 44,
      audioScript:
        "Yesterday, Priya got up early because she had a job interview at nine in the morning. The night before, she prepared her answers carefully, so she felt confident. After the interview, she sent a short thank-you email to the manager.",
      passageTitle: "Interview Day Notes",
      passage:
        "Last Monday, Priya ___ up early. She ___ a job interview at 9 AM. She ___ her answers the night before, so she ___ confident. After the interview, she ___ a thank-you email.",
      grammarRule:
        "Use simple past verbs for finished actions: got, had, prepared, felt, and sent.",
      targetWords: ["got", "had", "prepared", "felt", "sent"],
      items: [
        {
          itemId: "b1",
          sentenceWithBlank: "Last Monday, Priya ___ up early.",
          baseVerb: "get",
          correctAnswer: "got",
          explanation: "Get is irregular in the past: get becomes got.",
        },
        {
          itemId: "b2",
          sentenceWithBlank: "She ___ a job interview at 9 AM.",
          baseVerb: "have",
          correctAnswer: "had",
          explanation: "Have is irregular in the past: have becomes had.",
        },
        {
          itemId: "b3",
          sentenceWithBlank: "She ___ her answers the night before.",
          baseVerb: "prepare",
          correctAnswer: "prepared",
          explanation: "Prepare is regular, so the past form is prepared.",
        },
        {
          itemId: "b4",
          sentenceWithBlank: "She ___ confident.",
          baseVerb: "feel",
          correctAnswer: "felt",
          explanation: "Feel is irregular in the past: feel becomes felt.",
        },
        {
          itemId: "b5",
          sentenceWithBlank: "After the interview, she ___ a thank-you email.",
          baseVerb: "send",
          correctAnswer: "sent",
          explanation: "Send is irregular in the past: send becomes sent.",
        },
      ],
      answers: {
        correct: {
          b1: "got",
          b2: "had",
          b3: "prepared",
          b4: "felt",
          b5: "sent",
        },
        wrong: {
          b1: "got",
          b2: "had",
          b3: "prepared",
          b4: "feeled",
          b5: "sent",
        },
      },
    },
    {
      id: "w1d2-write-error-corr",
      sequence: 3,
      archetypeId: "WRITE_ERROR_CORR",
      widget: "error_correction",
      sectionLabel: "Writing task",
      topic: "Correct past tense mistakes",
      taskIntro: "Rewrite each sentence correctly",
      instructions:
        "Rewrite each incorrect sentence so it is grammatically correct and natural.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 5,
      grammarRule:
        "Use irregular past forms, use the base verb after did, and keep the sentence natural.",
      items: [
        {
          itemId: "ec1",
          incorrectSentence: "He don't have no time to attending the meeting yesterday.",
          sampleAnswer: "He didn't have any time to attend the meeting yesterday.",
          watchHints: ["didn't + base verb", "avoid double negatives", "to + base verb"],
        },
        {
          itemId: "ec2",
          incorrectSentence: "She goed to the store and buyed some milk last night.",
          sampleAnswer: "She went to the store and bought some milk last night.",
          watchHints: ["go -> went", "buy -> bought"],
        },
        {
          itemId: "ec3",
          incorrectSentence: "We didn't walked to the park because it was rained.",
          sampleAnswer: "We didn't walk to the park because it rained.",
          watchHints: ["did + base verb", "avoid unnecessary was"],
        },
      ],
      answers: {
        correct: [
          { itemId: "ec1", text: "He didn't have any time to attend the meeting yesterday.", isCorrect: true },
          { itemId: "ec2", text: "She went to the store and bought some milk last night.", isCorrect: true },
          { itemId: "ec3", text: "We didn't walk to the park because it rained.", isCorrect: true },
        ],
        wrong: [
          { itemId: "ec1", text: "He didn't have any time to attend the meeting yesterday.", isCorrect: true },
          { itemId: "ec2", text: "She goed to the store and bought some milk last night.", isCorrect: false },
          { itemId: "ec3", text: "We didn't walk to the park because it rained.", isCorrect: true },
        ],
      },
    },
    {
      id: "w1d2-speak-read-aloud",
      sequence: 4,
      archetypeId: "SPEAK_READ_ALOUD",
      widget: "read_aloud",
      sectionLabel: "Speaking task",
      topic: "Read past simple passage aloud",
      taskIntro: "Read the passage above out loud",
      instructions:
        "Read the connected passage aloud clearly. Focus on past -ed endings and common irregular verbs.",
      subSkill: "Pronunciation",
      activity: "Speak",
      estimatedMinutes: 3,
      textToReadAloud:
        "Yesterday, Liam walked to the old park near his house. He played a fun game on his phone and then listened to some relaxing music. Later, he ate a quick lunch and drank fresh water. He wanted to stay longer, but it started to rain. So, he grabbed his bag and went home.",
      grammarRule:
        "Pronounce regular past -ed endings clearly: walked /t/, played /d/, wanted /id/. Use correct irregular forms like ate, drank, and went.",
      targetWords: ["walked", "played", "listened", "wanted", "started", "grabbed", "ate", "drank", "went"],
      speakingDurationSeconds: 45,
      answers: {
        correct: [
          {
            itemId: "read_aloud",
            transcript:
              "Yesterday, Liam walked to the old park near his house. He played a fun game on his phone and then listened to some relaxing music. Later, he ate a quick lunch and drank fresh water. He wanted to stay longer, but it started to rain. So, he grabbed his bag and went home.",
            durationSeconds: 42,
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "read_aloud",
            transcript:
              "Yesterday, Liam walked to the old park near his house. He played a fun game on his phone and then listened to some relaxing music. Later, he eat a quick lunch and drank fresh water. He wanted to stay longer, but it started to rain. So, he grabbed his bag and went home.",
            durationSeconds: 43,
            isCorrect: false,
          },
        ],
      },
    },
  ],
};

const weekOneDayThreeTasks: TaskDayData = {
  dayId: "day_24_01_03",
  tasks: [
    {
      id: "w1d3-read-comp-mcq",
      sequence: 1,
      archetypeId: "READ_COMP_MCQ",
      widget: "read_comp_mcq",
      sectionLabel: "Reading task",
      topic: "Understand actions happening now",
      taskIntro: "Read the scene and answer questions",
      instructions:
        "Read the short passage. Choose the answer that matches what is happening right now.",
      subSkill: "Comprehension",
      activity: "Read",
      estimatedMinutes: 4,
      passageTitle: "At the Community Center",
      passage:
        "It is four o'clock at the community center. Mira is helping two children with their homework. Her brother Arjun is setting up chairs for a music class. Two parents are talking near the door, and the teacher is writing today's words on the board. Everyone is getting ready for the evening lesson.",
      grammarRule:
        "Use am, is, or are plus verb-ing to describe actions happening now.",
      items: [
        {
          itemId: "q1",
          prompt: "What is Mira doing now?",
          options: ["Cooking dinner", "Helping children", "Playing music", "Writing on the board"],
          correctIndex: 1,
          explanation: "The passage says Mira is helping two children with their homework.",
        },
        {
          itemId: "q2",
          prompt: "Who is setting up chairs?",
          options: ["The teacher", "Two parents", "Arjun", "Mira"],
          correctIndex: 2,
          explanation: "The passage says Arjun is setting up chairs for a music class.",
        },
        {
          itemId: "q3",
          prompt: "What are two parents doing near the door?",
          options: ["Talking", "Reading", "Singing", "Cleaning"],
          correctIndex: 0,
          explanation: "The passage says two parents are talking near the door.",
        },
        {
          itemId: "q4",
          prompt: "Which sentence uses present continuous correctly?",
          options: [
            "The teacher writes today's words now.",
            "The teacher is writing today's words now.",
            "The teacher are writing today's words now.",
            "The teacher writing today's words now.",
          ],
          correctIndex: 1,
          explanation: "One teacher needs is plus the -ing verb: is writing.",
        },
      ],
      answers: {
        correct: { q1: 1, q2: 2, q3: 0, q4: 1 },
        wrong: { q1: 1, q2: 2, q3: 1, q4: 1 },
      },
    },
    {
      id: "w1d3-listen-dictation",
      sequence: 2,
      archetypeId: "LISTEN_DICTATION",
      widget: "listen_dictation",
      sectionLabel: "Listening task",
      topic: "Hear present continuous chunks",
      taskIntro: "Listen and type the exact sentences",
      instructions:
        "Play the audio and type each present continuous sentence exactly as you hear it.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 4,
      audioGenre: "Live classroom update",
      audioDurationSeconds: 36,
      audioScript:
        "I am opening the classroom door. The students are taking out their books. Riya is asking a question. The teacher is writing examples on the board.",
      grammarRule:
        "Listen for the full chunk: subject plus am, is, or are plus verb-ing.",
      targetWords: ["am opening", "are taking", "is asking", "is writing"],
      items: [
        {
          itemId: "d1",
          prompt: "Sentence 1",
          correctAnswer: "I am opening the classroom door.",
          explanation: "The subject I uses am, followed by opening.",
        },
        {
          itemId: "d2",
          prompt: "Sentence 2",
          correctAnswer: "The students are taking out their books.",
          explanation: "The plural subject students uses are, followed by taking.",
        },
        {
          itemId: "d3",
          prompt: "Sentence 3",
          correctAnswer: "Riya is asking a question.",
          explanation: "Riya is one person, so use is asking.",
        },
        {
          itemId: "d4",
          prompt: "Sentence 4",
          correctAnswer: "The teacher is writing examples on the board.",
          explanation: "The teacher is one person, so use is writing.",
        },
      ],
      answers: {
        correct: {
          d1: "I am opening the classroom door.",
          d2: "The students are taking out their books.",
          d3: "Riya is asking a question.",
          d4: "The teacher is writing examples on the board.",
        },
        wrong: {
          d1: "I am opening the classroom door.",
          d2: "The students is taking out their books.",
          d3: "Riya is asking a question.",
          d4: "The teacher is writing examples on the board.",
        },
      },
    },
    {
      id: "w1d3-write-sent-trans",
      sequence: 3,
      archetypeId: "WRITE_SENT_TRANS",
      widget: "sentence_transform",
      sectionLabel: "Writing task",
      topic: "Rewrite into present continuous",
      taskIntro: "Change routine sentences into now sentences",
      instructions:
        "Rewrite each simple present sentence as a present continuous sentence about what is happening now.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 5,
      grammarRule:
        "Change the verb to am, is, or are plus verb-ing. Choose the helper from the subject.",
      items: [
        {
          itemId: "st1",
          sourceSentence: "She walks to school.",
          sampleAnswer: "She is walking to school.",
          watchHints: ["she -> is", "walk -> walking"],
        },
        {
          itemId: "st2",
          sourceSentence: "They play football.",
          sampleAnswer: "They are playing football.",
          watchHints: ["they -> are", "play -> playing"],
        },
        {
          itemId: "st3",
          sourceSentence: "I read my book.",
          sampleAnswer: "I am reading my book.",
          watchHints: ["I -> am", "read -> reading"],
        },
      ],
      answers: {
        correct: [
          { itemId: "st1", text: "She is walking to school.", isCorrect: true },
          { itemId: "st2", text: "They are playing football.", isCorrect: true },
          { itemId: "st3", text: "I am reading my book.", isCorrect: true },
        ],
        wrong: [
          { itemId: "st1", text: "She is walking to school.", isCorrect: true },
          { itemId: "st2", text: "They is playing football.", isCorrect: false },
          { itemId: "st3", text: "I am reading my book.", isCorrect: true },
        ],
      },
    },
    {
      id: "w1d3-speak-timed",
      sequence: 4,
      archetypeId: "SPEAK_TIMED",
      widget: "speak_record",
      sectionLabel: "Speaking task",
      topic: "Describe what people are doing now",
      taskIntro: "Record present continuous sentences",
      instructions:
        "Say one sentence for each prompt. Describe what the person or people are doing right now.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      mode: "timed",
      speakingDurationSeconds: 45,
      grammarRule:
        "Use am with I, is with he, she, or one name, and are with they, we, or plural nouns.",
      targetWords: ["am", "is", "are", "working", "studying", "playing", "reading"],
      prompts: [
        "Say one sentence about what you are doing now.",
        "Say one sentence about what one person is doing now.",
        "Say one sentence about what two or more people are doing now.",
      ],
      sampleResponses: [
        "I am studying English now.",
        "She is reading a book now.",
        "They are playing football now.",
      ],
      answers: {
        correct: [
          { itemId: "prompt_1", transcript: "I am studying English now.", durationSeconds: 6, isCorrect: true },
          { itemId: "prompt_2", transcript: "She is reading a book now.", durationSeconds: 7, isCorrect: true },
          { itemId: "prompt_3", transcript: "They are playing football now.", durationSeconds: 7, isCorrect: true },
        ],
        wrong: [
          { itemId: "prompt_1", transcript: "I am studying English now.", durationSeconds: 6, isCorrect: true },
          { itemId: "prompt_2", transcript: "She are reading a book now.", durationSeconds: 7, isCorrect: false },
          { itemId: "prompt_3", transcript: "They are playing football now.", durationSeconds: 7, isCorrect: true },
        ],
      },
    },
  ],
};


const weekOneDayFourTasks: TaskDayData = {
  dayId: "day_24_01_04",
  tasks: [
    {
      id: "w1d4-read-word-match",
      sequence: 1,
      archetypeId: "READ_WORD_MATCH",
      widget: "read_word_match",
      sectionLabel: "Reading task",
      topic: "Match articles to nouns",
      taskIntro: "Choose the correct article for each noun",
      instructions: "Match a, an, or the with the noun based on the rules for articles.",
      subSkill: "Grammar",
      activity: "Read",
      estimatedMinutes: 3,
      grammarRule: "Use a before consonant sounds, an before vowel sounds, and the for specific things.",
      items: [
        {
          itemId: "wm1",
          prompt: "apple",
          correctAnswer: "an",
          explanation: "Apple starts with a vowel sound, so use an."
        },
        {
          itemId: "wm2",
          prompt: "car",
          correctAnswer: "a",
          explanation: "Car starts with a consonant sound, so use a."
        },
        {
          itemId: "wm3",
          prompt: "sun",
          correctAnswer: "the",
          explanation: "There is only one sun, so use the."
        }
      ],
      options: ["a", "an", "the"],
      answers: {
        correct: { wm1: "an", wm2: "a", wm3: "the" },
        wrong: { wm1: "a", wm2: "a", wm3: "the" }
      }
    },
    {
      id: "w1d4-listen-mcq",
      sequence: 2,
      archetypeId: "LISTEN_MCQ",
      widget: "listen_mcq",
      sectionLabel: "Listening task",
      topic: "Hearing articles in natural speech",
      taskIntro: "Listen and choose the correct option",
      instructions: "Listen to the short audio and answer the questions.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 4,
      audioGenre: "Short dialogue",
      audioDurationSeconds: 30,
      audioScript: "I bought a new book yesterday. The book is about animals. It has an interesting story about an elephant.",
      innerWidget: "mcq",
      items: [
        {
          itemId: "q1",
          prompt: "What did the person buy?",
          options: ["A book", "The book", "An elephant", "A car"],
          correctIndex: 0,
          explanation: "The person says 'I bought a new book', introducing it for the first time."
        },
        {
          itemId: "q2",
          prompt: "Which article is used before 'interesting story'?",
          options: ["a", "an", "the", "no article"],
          correctIndex: 1,
          explanation: "Interesting starts with a vowel sound, so 'an' is used."
        }
      ],
      answers: {
        correct: { q1: 0, q2: 1 },
        wrong: { q1: 1, q2: 1 }
      }
    },
    {
      id: "w1d4-write-open-sent",
      sequence: 3,
      archetypeId: "WRITE_OPEN_SENT",
      widget: "open_text",
      sectionLabel: "Writing task",
      topic: "Write sentences using a, an, and the",
      taskIntro: "Write your own sentences using articles",
      instructions: "Write three short sentences. Use 'a', 'an', and 'the' correctly.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 5,
      grammarRule: "Use a/an for non-specific singular nouns, and the for specific or already mentioned nouns.",
      targetWords: ["a", "an", "the"],
      commonMistakes: [
        "Using a before a vowel sound.",
        "Using an before a consonant sound.",
        "Forgetting the for unique nouns like the sun or the moon."
      ],
      items: [
        {
          itemId: "w1",
          prompt: "Write a sentence using 'a'.",
          sampleAnswer: "I have a cat.",
          answerHints: ["Use a singular noun.", "It should start with a consonant sound."]
        },
        {
          itemId: "w2",
          prompt: "Write a sentence using 'an'.",
          sampleAnswer: "She ate an apple.",
          answerHints: ["Use a singular noun.", "It should start with a vowel sound."]
        },
        {
          itemId: "w3",
          prompt: "Write a sentence using 'the'.",
          sampleAnswer: "The sky is blue today.",
          answerHints: ["Use a specific noun or something unique."]
        }
      ],
      answers: {
        correct: [
          { itemId: "w1", text: "I saw a dog.", isCorrect: true },
          { itemId: "w2", text: "He bought an umbrella.", isCorrect: true },
          { itemId: "w3", text: "The moon is bright.", isCorrect: true }
        ],
        wrong: [
          { itemId: "w1", text: "I saw a dog.", isCorrect: true },
          { itemId: "w2", text: "He bought a umbrella.", isCorrect: false },
          { itemId: "w3", text: "The moon is bright.", isCorrect: true }
        ]
      }
    },
    {
      id: "w1d4-speak-pic-desc",
      sequence: 4,
      archetypeId: "SPEAK_PIC_DESC",
      widget: "speak_pic_desc",
      sectionLabel: "Speaking task",
      topic: "Describe a picture using articles",
      taskIntro: "Look at the picture and describe it",
      instructions: "Describe the image aloud. Try to use 'a', 'an', and 'the' naturally.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      imageUrl: "",
      imageAlt: "A cat sleeping on the sofa next to an open book.",
      grammarRule: "Use a/an when mentioning something for the first time. Use the when something is obvious or specific.",
      speakingDurationSeconds: 45,
      answers: {
        correct: [
          { itemId: "prompt_1", transcript: "There is a cat on the sofa. The cat is sleeping next to an open book.", durationSeconds: 8, isCorrect: true }
        ],
        wrong: [
          { itemId: "prompt_1", transcript: "There is cat on sofa. A cat is sleeping next to a open book.", durationSeconds: 9, isCorrect: false }
        ]
      }
    }
  ]
};

const weekOneDayFiveTasks: TaskDayData = {
  dayId: "day_24_01_05",
  tasks: [
    {
      id: "w1d5-read-cloze",
      sequence: 1,
      archetypeId: "READ_CLOZE",
      widget: "fill_blanks",
      sectionLabel: "Reading cloze",
      topic: "Fill pronoun blanks",
      taskIntro: "Complete the pronoun passage",
      instructions: "Fill each blank with the correct pronoun.",
      subSkill: "Grammar",
      activity: "Read",
      estimatedMinutes: 3,
      passageTitle: "Ravi's Family Visit",
      passage: "Yesterday, Ravi and I visited my grandmother. ___ was very happy to see us. We helped ___ clean her garden. She made ___ a delicious lunch. Later, Ravi said that the red umbrella on the table was ___.",
      grammarRule: "Use subject pronouns for the actor, object pronouns for the receiver, and possessive pronouns for ownership.",
      items: [
        {
          itemId: "b1",
          sentenceWithBlank: "___ was very happy to see us.",
          baseVerb: "she",
          correctAnswer: "She",
          explanation: "Use the subject pronoun 'She' because it is performing the action 'was'."
        },
        {
          itemId: "b2",
          sentenceWithBlank: "We helped ___ clean her garden.",
          baseVerb: "she",
          correctAnswer: "her",
          explanation: "Use the object pronoun 'her' as the receiver of the helping action."
        },
        {
          itemId: "b3",
          sentenceWithBlank: "She made ___ a delicious lunch.",
          baseVerb: "we",
          correctAnswer: "us",
          explanation: "Use the object pronoun 'us' because it is receiving the lunch she made."
        },
        {
          itemId: "b4",
          sentenceWithBlank: "...was ___.",
          baseVerb: "she",
          correctAnswer: "hers",
          explanation: "Use the possessive pronoun 'hers' to show ownership of the umbrella."
        }
      ],
      answers: {
        correct: {
          b1: "She",
          b2: "her",
          b3: "us",
          b4: "hers"
        },
        wrong: {
          b1: "She",
          b2: "him",
          b3: "us",
          b4: "hers"
        }
      }
    },
    {
      id: "w1d5-listen-mcq",
      sequence: 2,
      archetypeId: "LISTEN_INFER",
      widget: "listen_mcq",
      sectionLabel: "Listening task",
      topic: "Implied meaning of pronouns",
      taskIntro: "Listen and resolve pronoun ambiguity",
      instructions: "Listen to the dialogue where pronouns are ambiguous and resolve who they refer to.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 4,
      audioGenre: "Conversation explanation",
      audioDurationSeconds: 30,
      audioScript: "Sophia called her sister Lily yesterday. She told her that she was really happy because she got a promotion at work. She promised to buy her dinner tonight.",
      innerWidget: "mcq",
      items: [
        {
          itemId: "q1",
          prompt: "In the sentence 'She told her that she was really happy...', who got the promotion?",
          options: ["Sophia", "Lily", "Both of them", "Neither of them"],
          correctIndex: 0,
          explanation: "Sophia initiated the call to share her own happy news about getting a promotion."
        },
        {
          itemId: "q2",
          prompt: "In the sentence 'She promised to buy her dinner...', who will buy dinner?",
          options: ["Lily", "Sophia", "Their boss", "No one"],
          correctIndex: 1,
          explanation: "Sophia is the subject performing the promise to buy dinner for Lily."
        }
      ],
      answers: {
        correct: { q1: 0, q2: 1 },
        wrong: { q1: 1, q2: 1 }
      }
    },
    {
      id: "w1d5-write-paragraph",
      sequence: 3,
      archetypeId: "WRITE_PARA",
      widget: "write_paragraph",
      sectionLabel: "Writing task",
      topic: "Write a paragraph with pronouns",
      taskIntro: "Write a short pronoun story",
      instructions: "Write a paragraph about a day out. Use at least one subject pronoun, one object pronoun, and one possessive pronoun correctly.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 5,
      prompt: "Write a paragraph (3-4 sentences) describing a day out with a friend. Be sure to use pronouns like 'we', 'us', and 'his' or 'hers'.",
      grammarRule: "Use subject pronouns (e.g. we), object pronouns (e.g. us, him, her), and possessive pronouns (e.g. his, hers) correctly.",
      targetWords: ["we", "us", "our", "me", "him", "her", "his", "hers"],
      minimumWords: 20,
      sampleAnswer: "My friend Leo and I went to the park. We played soccer together for two hours. Leo bought us ice cream afterwards. The red ball we played with was his.",
      answerHints: [
        "Include a subject pronoun (e.g. 'we').",
        "Include an object pronoun (e.g. 'us', 'him', 'her').",
        "Include a possessive pronoun (e.g. 'his', 'hers').",
        "Write at least 20 words in total."
      ],
      answers: {
        correct: [
          {
            itemId: "wp1",
            text: "My friend Leo and I went to the park. We played soccer together. Leo bought us ice cream afterwards. The red ball was his.",
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "wp1",
            text: "My friend Leo and I went to the park. We played soccer together. Leo bought we ice cream afterwards. The red ball was his.",
            isCorrect: false
          }
        ]
      }
    },
    {
      id: "w1d5-speak-roleplay",
      sequence: 4,
      archetypeId: "SPEAK_ROLEPLAY",
      widget: "speak_roleplay",
      sectionLabel: "Speaking task",
      topic: "Pronoun roleplay scenario",
      taskIntro: "Act out the scenario with pronouns",
      instructions: "Listen to your partner's prompt in the conversation and record your responses using correct pronouns.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      dialogueContext: [
        { role: "Partner", text: "Hi! Did you see the new book on the table? Is it yours?", speaker: "partner" },
        { role: "You", text: "No, it is not mine. I think it belongs to Emily.", speaker: "learner" },
        { role: "Partner", text: "Oh, really? I thought she gave it to you.", speaker: "partner" },
        { role: "You", text: "She lent it to him, but he forgot to return it.", speaker: "learner" }
      ],
      grammarRule: "Use possessive pronouns like 'mine' and object pronouns like 'him' to talk about ownership and people.",
      targetWords: ["mine", "yours", "she", "him", "he"],
      speakingDurationSeconds: 30,
      answers: {
        correct: [
          { itemId: "sr1", transcript: "No, it is not mine. I think it belongs to Emily.", durationSeconds: 7, isCorrect: true },
          { itemId: "sr2", transcript: "She lent it to him, but he forgot to return it.", durationSeconds: 8, isCorrect: true }
        ],
        wrong: [
          { itemId: "sr1", transcript: "No, it is not mine. I think it belongs to Emily.", durationSeconds: 7, isCorrect: true },
          { itemId: "sr2", transcript: "She lent it to he, but he forgot to return it.", durationSeconds: 8, isCorrect: false }
        ]
      }
    }
  ]
};

const weekOneDaySixTasks: TaskDayData = {
  dayId: "day_24_01_06",
  tasks: [
    {
      id: "w1d6-read-tfng",
      sequence: 1,
      archetypeId: "READ_TFNG",
      widget: "read_tfng",
      sectionLabel: "Reading TFNG",
      topic: "Possessives in text",
      taskIntro: "Read and judge statements",
      instructions: "Read the family description and decide if the possessive statements are True, False, or Not Given.",
      subSkill: "Grammar",
      activity: "Read",
      estimatedMinutes: 3,
      passageTitle: "Alex's Family Picnic",
      passage: "My name is Alex. Today, our family is having a picnic. My sister's name is Emma. She is wearing a blue hat, but it is actually our mother's. My brother Leo forgot his sunglasses, so he is borrowing mine. Our father is cooking dinner. His barbecue grill is very old, but it works perfectly. Our dog is playing with its favorite red ball, which belongs to Emma's friend.",
      grammarRule: "Use possessive 's for singular nouns (Emma's hat) and possessive adjectives/pronouns (his sunglasses, borrowing mine) to show relationship or ownership.",
      items: [
        {
          itemId: "q1",
          prompt: "The blue hat Emma is wearing belongs to Emma.",
          correctAnswer: "False",
          explanation: "The passage states that the hat is actually their mother's, so it does not belong to Emma."
        },
        {
          itemId: "q2",
          prompt: "Leo is wearing Alex's sunglasses.",
          correctAnswer: "True",
          explanation: "Leo forgot his sunglasses and is borrowing 'mine' (Alex's), so he is wearing Alex's sunglasses."
        },
        {
          itemId: "q3",
          prompt: "Their father's barbecue grill is brand new.",
          correctAnswer: "False",
          explanation: "The passage says 'His barbecue grill is very old'."
        },
        {
          itemId: "q4",
          prompt: "The dog's favorite ball is blue.",
          correctAnswer: "False",
          explanation: "The dog is playing with its favorite 'red' ball."
        },
        {
          itemId: "q5",
          prompt: "Emma's friend owns the red ball.",
          correctAnswer: "True",
          explanation: "The passage says the red ball 'belongs to Emma's friend'."
        }
      ],
      answers: {
        correct: {
          q1: "False",
          q2: "True",
          q3: "False",
          q4: "False",
          q5: "True"
        },
        wrong: {
          q1: "True",
          q2: "True",
          q3: "False",
          q4: "False",
          q5: "True"
        }
      }
    },
    {
      id: "w1d6-listen-shadow",
      sequence: 2,
      archetypeId: "LISTEN_SHADOW",
      widget: "listen_shadow",
      sectionLabel: "Listening shadow",
      topic: "Repeat possessives in fast speech",
      taskIntro: "Shadow the speaker's possessives",
      instructions: "Listen to the audio clip where possessive pronouns are swallowed in fast speech, and repeat after the speaker to train your shadowing.",
      subSkill: "Fluency",
      activity: "Listen",
      estimatedMinutes: 3,
      audioGenre: "Fast Monologue",
      audioScript: "That's not my phone, I think it's hers. Oh wait, it's actually his! Mine is in the bag.",
      audioDurationSeconds: 20,
      grammarRule: "In fast speech, possessives like 'hers', 'his', and 'mine' are often reduced or blended with neighboring words. Practice saying them smoothly.",
      targetWords: ["it's hers", "actually his", "Mine is"],
      textToShadow: "That's not my phone, I think it's hers. Oh wait, it's actually his! Mine is in the bag.",
      answers: {
        correct: [
          {
            itemId: "shadow",
            transcript: "That's not my phone, I think it's hers. Oh wait, it's actually his! Mine is in the bag.",
            durationSeconds: 15,
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "shadow",
            transcript: "That's not my phone, I think it's her. Oh wait, it's actually him! Mine is in the bag.",
            durationSeconds: 16,
            isCorrect: false
          }
        ]
      }
    },
    {
      id: "w1d6-write-email",
      sequence: 3,
      archetypeId: "WRITE_EMAIL",
      widget: "write_email",
      sectionLabel: "Writing email",
      topic: "Introduce your family in an email",
      taskIntro: "Draft a family introduction email",
      instructions: "Write a short email introducing your family using possessive adjectives and nouns correctly.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 5,
      prompt: "Write a short email introducing your family. Use possessive adjectives (my, his, her, our) and possessive nouns (e.g. brother's, sister's) to introduce family members Sam and Lily.",
      grammarRule: "Use possessive adjectives (my, his, her, our, their) and possessive nouns (e.g. brother's, sister's) to clearly introduce family members and their belongings.",
      targetWords: ["my", "his", "her", "brother's", "sister's", "our", "their"],
      minimumWords: 20,
      sampleAnswer: "To: friend@example.com\nSubject: Meet my family\n\nHi! I want to introduce my family. My brother's name is Sam. His favorite sport is tennis. My sister's name is Lily. Her hobby is drawing. We love our family time together!",
      answerHints: [
        "Use at least two possessive adjectives (e.g., 'my', 'his', 'her').",
        "Use at least one possessive noun (e.g., 'brother's', 'sister's').",
        "Write at least 20 words introducing your family."
      ],
      answers: {
        correct: [
          {
            itemId: "we1",
            text: "To: friend@example.com\nSubject: Meet my family\n\nHi! I want to introduce my family. My brother's name is Sam. His favorite sport is tennis. My sister's name is Lily. Her hobby is drawing. We love our family time together!",
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "we1",
            text: "To: friend@example.com\nSubject: Meet my family\n\nHi! I want to introduce my family. My brother name is Sam. He favorite sport is tennis. My sister name is Lily. Her hobby is drawing. We love our family time together!",
            isCorrect: false
          }
        ]
      }
    },
    {
      id: "w1d6-speak-smalltalk",
      sequence: 4,
      archetypeId: "SPEAK_SMALLTALK",
      widget: "speak_smalltalk",
      sectionLabel: "Speaking smalltalk",
      topic: "Casual conversation with possessives",
      taskIntro: "Casual possessive small talk",
      instructions: "Respond to your partner's questions during casual small talk using possessive pronouns naturally.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      dialogueContext: [
        { role: "Partner", text: "Hey! Is this black umbrella yours or hers?", speaker: "partner" },
        { role: "You", text: "Actually, it's mine! She left hers inside the office.", speaker: "learner" },
        { role: "Partner", text: "Ah, got it. And what about these keys? Are they his?", speaker: "partner" },
        { role: "You", text: "No, they are ours. His keys are on the kitchen table.", speaker: "learner" }
      ],
      grammarRule: "Use possessive pronouns (mine, yours, hers, ours, theirs) in small talk to avoid repeating the noun.",
      targetWords: ["yours", "mine", "hers", "his", "ours"],
      speakingDurationSeconds: 30,
      answers: {
        correct: [
          { itemId: "st1", transcript: "Actually, it's mine! She left hers inside the office.", durationSeconds: 6, isCorrect: true },
          { itemId: "st2", transcript: "No, they are ours. His keys are on the kitchen table.", durationSeconds: 7, isCorrect: true }
        ],
        wrong: [
          { itemId: "st1", transcript: "Actually, it's me! She left her inside the office.", durationSeconds: 6, isCorrect: false },
          { itemId: "st2", transcript: "No, they are ours. His keys are on the kitchen table.", durationSeconds: 7, isCorrect: true }
        ]
      }
    }
  ]
};

const weekOneDaySevenTasks: TaskDayData = {
  dayId: "day_24_01_07",
  tasks: [
    {
      id: "w1d7-read-context-mcq",
      sequence: 1,
      archetypeId: "READ_CONTEXT_MCQ",
      widget: "read_comp_mcq",
      sectionLabel: "Contextual vocabulary MCQ",
      topic: "Prepositions in context",
      taskIntro: "Preposition Context MCQ",
      instructions: "Select the correct preposition for each sentence based on the context.",
      subSkill: "Grammar",
      activity: "Read",
      estimatedMinutes: 3,
      passageTitle: "A Morning at the Busy Café",
      passage: "Every morning, residents gather at Café Nero. The barista puts cups ___ the counter. Sarah sits ___ a comfortable armchair next to the fireplace. A huge clock hangs ___ the wall. The café is situated ___ the bakery and the library, making it the perfect meeting spot.",
      grammarRule: "Use 'on' for surfaces (on the counter, on the wall), 'in' for armchairs or rooms (in an armchair), and 'between' for a position in the middle of two things.",
      items: [
        {
          itemId: "q1",
          prompt: "The barista puts cups ___ the counter.",
          options: ["in", "on", "at", "between"],
          correctIndex: 1,
          explanation: "The counter is a flat surface, so the correct preposition is 'on'."
        },
        {
          itemId: "q2",
          prompt: "Sarah sits ___ a comfortable armchair.",
          options: ["in", "on", "at", "between"],
          correctIndex: 0,
          explanation: "An armchair is an enclosed seat that you sit 'in', whereas a hard chair without arms is sat 'on'."
        },
        {
          itemId: "q3",
          prompt: "A huge clock hangs ___ the wall.",
          options: ["in", "on", "at", "between"],
          correctIndex: 1,
          explanation: "Objects attached to a wall are resting on that vertical surface, so we say 'on the wall'."
        },
        {
          itemId: "q4",
          prompt: "The café is situated ___ the bakery and the library.",
          options: ["in", "on", "at", "between"],
          correctIndex: 3,
          explanation: "The café is in the middle of two locations, which requires 'between'."
        }
      ],
      answers: {
        correct: { q1: 1, q2: 0, q3: 1, q4: 3 },
        wrong: { q1: 1, q2: 1, q3: 1, q4: 3 }
      }
    },
    {
      id: "w1d7-listen-retell",
      sequence: 2,
      archetypeId: "LISTEN_RETELL",
      widget: "listen_retell",
      sectionLabel: "Listening retell",
      topic: "Listen and summarize",
      taskIntro: "Summarize the audio description",
      instructions: "Listen to the description of a historic town and then retell the main ideas in your own words.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 4,
      audioGenre: "Travel Monologue",
      audioDurationSeconds: 35,
      audioScript: "At the center of our historic town, there is a beautiful stone fountain. Next to it, you can find a small local bakery that smells of fresh bread. In the park nearby, children love playing between the two giant oak trees. It is a peaceful place to live.",
      grammarRule: "Listen for prepositions of place: 'at the center', 'next to it', 'in the park', 'between the two trees'.",
      targetWords: ["at the center", "next to it", "in the park", "between the two trees"],
      passageToRetell: "At the center of our historic town, there is a beautiful stone fountain. Next to it, you can find a small local bakery that smells of fresh bread. In the park nearby, children love playing between the two giant oak trees. It is a peaceful place to live.",
      answers: {
        correct: [
          {
            itemId: "retell",
            transcript: "At the center of the town is a fountain. Next to it is a bakery. In the park nearby, children play between two trees.",
            durationSeconds: 18,
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "retell",
            transcript: "In the center of the town is a fountain. Next to it is a bakery. In the park nearby, children play on two trees.",
            durationSeconds: 20,
            isCorrect: false
          }
        ]
      }
    },
    {
      id: "w1d7-write-paraphrase",
      sequence: 3,
      archetypeId: "WRITE_PARAPHRASE",
      widget: "write_paraphrase",
      sectionLabel: "Writing paraphrase",
      topic: "Correcting preposition mistakes",
      taskIntro: "Paraphrase sentences correctly",
      instructions: "Rewrite the sentences, swapping the incorrect prepositions with the correct ones.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 5,
      grammarRule: "Swap incorrect prepositions with correct ones. Pay attention to common collocations like 'good at', 'depend on', and 'interested in'.",
      items: [
        {
          itemId: "wp1",
          incorrectSentence: "I am extremely good in English.",
          sampleAnswer: "I am extremely good at English.",
          watchHints: ["good at"]
        },
        {
          itemId: "wp2",
          incorrectSentence: "Our plans depend from the weather.",
          sampleAnswer: "Our plans depend on the weather.",
          watchHints: ["depend on"]
        },
        {
          itemId: "wp3",
          incorrectSentence: "We arrived at Monday morning.",
          sampleAnswer: "We arrived on Monday morning.",
          watchHints: ["on Monday"]
        }
      ],
      answers: {
        correct: [
          { itemId: "wp1", text: "I am extremely good at English.", isCorrect: true },
          { itemId: "wp2", text: "Our plans depend on the weather.", isCorrect: true },
          { itemId: "wp3", text: "We arrived on Monday morning.", isCorrect: true }
        ],
        wrong: [
          { itemId: "wp1", text: "I am extremely good in English.", isCorrect: false },
          { itemId: "wp2", text: "Our plans depend on the weather.", isCorrect: true },
          { itemId: "wp3", text: "We arrived on Monday morning.", isCorrect: true }
        ]
      }
    },
    {
      id: "w1d7-speak-present",
      sequence: 4,
      archetypeId: "SPEAK_PRESENT",
      widget: "speak_present",
      sectionLabel: "Speaking presentation",
      topic: "Room layout presentation",
      taskIntro: "Describe the cozy room",
      instructions: "Describe the objects and their positions in the cozy room, using at least three prepositions.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      grammarRule: "Describe using spatial prepositions: 'on the table', 'next to the sofa', 'between the window and the door'.",
      targetWords: ["on the table", "next to the sofa", "between"],
      speakingDurationSeconds: 45,
      visualPromptDescription: "A cozy room with a sofa, a coffee table in front of it with a mug on top, a plant next to the sofa, and a picture between two windows.",
      answers: {
        correct: [
          {
            itemId: "present",
            transcript: "There is a coffee table in the room. A coffee mug is sitting on the table. A green plant is standing next to the sofa. A lovely picture hangs between the two windows.",
            durationSeconds: 24,
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "present",
            transcript: "There is a coffee table. A coffee mug is under the table. A green plant is inside the sofa. A lovely picture is on the windows.",
            durationSeconds: 22,
            isCorrect: false
          }
        ]
      }
    }
  ]
};

const weekTwoDayOneTasks: TaskDayData = {
  dayId: "day_24_02_01",
  tasks: [
    {
      id: "w2d1-read-intro-mcq",
      sequence: 1,
      archetypeId: "READ_COMP_MCQ",
      widget: "read_comp_mcq",
      sectionLabel: "Reading",
      topic: "Greetings and introductions",
      taskIntro: "Read the first-meeting chat",
      instructions:
        "Read the short conversation and choose the best answer for each question.",
      subSkill: "Comprehension",
      activity: "Read",
      estimatedMinutes: 3,
      passageTitle: "At the Workshop Entrance",
      passage:
        "Emma smiled at the person next to her. 'Hi, is this seat free?' she asked. 'Yes, it is,' he said. 'I'm Arjun, by the way.' Emma replied, 'Nice to meet you, Arjun. I'm Emma.' A moment later, she asked, 'Are you new here?' Arjun nodded and said it was his first workshop.",
      grammarRule:
        "Notice how people greet each other, share their names, and ask one simple follow-up question to keep the conversation going.",
      items: [
        {
          itemId: "q1",
          prompt: "How does Arjun introduce himself?",
          options: [
            "I'm Arjun, by the way.",
            "This is Arjun speaking.",
            "Call me later.",
            "You know my name.",
          ],
          correctIndex: 0,
          explanation: "Arjun uses a simple, natural introduction: 'I'm Arjun, by the way.'",
        },
        {
          itemId: "q2",
          prompt: "What does Emma say after hearing Arjun's name?",
          options: [
            "See you tomorrow.",
            "Nice to meet you, Arjun.",
            "Where is your teacher?",
            "Please sit over there.",
          ],
          correctIndex: 1,
          explanation: "A polite first response is 'Nice to meet you, Arjun.'",
        },
        {
          itemId: "q3",
          prompt: "Why does Emma ask, 'Are you new here?'",
          options: [
            "She wants to end the conversation.",
            "She is checking his ticket.",
            "She is starting a friendly follow-up question.",
            "She forgot his name already.",
          ],
          correctIndex: 2,
          explanation: "The question helps continue the conversation in a natural, friendly way.",
        },
      ],
      answers: {
        correct: { q1: 0, q2: 1, q3: 2 },
        wrong: { q1: 0, q2: 2, q3: 2 },
      },
    },
    {
      id: "w2d1-listen-greeting-mcq",
      sequence: 2,
      archetypeId: "LISTEN_MCQ",
      widget: "listen_mcq",
      sectionLabel: "Listening",
      topic: "Listening to a first conversation",
      taskIntro: "Listen to the greeting exchange",
      instructions:
        "Play the audio and choose the answer that matches what the speakers say.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 3,
      audioGenre: "Short greeting dialogue",
      audioDurationSeconds: 34,
      audioScript:
        "Hello, I'm Sofia. I think we're in the same English class. Hi Sofia, I'm Daniel. Yes, I started last week. Nice to meet you, Daniel. Nice to meet you too. Do you live nearby?",
      innerWidget: "mcq",
      items: [
        {
          itemId: "q1",
          prompt: "Why does Sofia speak to Daniel?",
          options: [
            "They are in the same English class.",
            "She wants to borrow a phone.",
            "They work in the same office.",
            "She lost her notebook.",
          ],
          correctIndex: 0,
          explanation: "Sofia says she thinks they are in the same English class.",
        },
        {
          itemId: "q2",
          prompt: "What does Daniel say after Sofia says, 'Nice to meet you'?",
          options: [
            "I live far away.",
            "Nice to meet you too.",
            "See you next week.",
            "Thank you for calling.",
          ],
          correctIndex: 1,
          explanation: "Daniel replies politely with 'Nice to meet you too.'",
        },
        {
          itemId: "q3",
          prompt: "What follow-up question does Daniel ask?",
          options: [
            "What time is class?",
            "Are you from Chennai?",
            "Do you live nearby?",
            "Can you help me study?",
          ],
          correctIndex: 2,
          explanation: "Daniel keeps the conversation going by asking, 'Do you live nearby?'",
        },
      ],
      answers: {
        correct: { q1: 0, q2: 1, q3: 2 },
        wrong: { q1: 0, q2: 3, q3: 2 },
      },
    },
    {
      id: "w2d1-write-intro-transform",
      sequence: 3,
      archetypeId: "WRITE_SENT_TRANS",
      widget: "sentence_transform",
      sectionLabel: "Writing",
      topic: "Polite self-introductions",
      taskIntro: "Rewrite the introductions naturally",
      instructions:
        "Turn each short line into a more natural introduction sentence.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 4,
      grammarRule:
        "Expand short chat lines into polite introductions with forms like 'Hello, my name is...', 'I'm...', and 'Nice to meet you.'",
      items: [
        {
          itemId: "st1",
          sourceSentence: "Hi, I am John.",
          sampleAnswer: "Hello, my name is John. Nice to meet you.",
          watchHints: ["Use a polite greeting.", "Add your name clearly."],
        },
        {
          itemId: "st2",
          sourceSentence: "Hey, I am Sara from Delhi.",
          sampleAnswer: "Hello, my name is Sara, and I'm from Delhi.",
          watchHints: ["Use 'my name is'.", "Connect the second idea with 'and'."],
        },
        {
          itemId: "st3",
          sourceSentence: "Hi, I study design.",
          sampleAnswer: "Hello, I'm a design student.",
          watchHints: ["Use 'I'm a...'.", "Add the article 'a' before the job or study noun."],
        },
      ],
      answers: {
        correct: [
          { itemId: "st1", text: "Hello, my name is John. Nice to meet you.", isCorrect: true },
          { itemId: "st2", text: "Hello, my name is Sara, and I'm from Delhi.", isCorrect: true },
          { itemId: "st3", text: "Hello, I'm a design student.", isCorrect: true },
        ],
        wrong: [
          { itemId: "st1", text: "Hello, my name is John. Nice to meet you.", isCorrect: true },
          { itemId: "st2", text: "Hello, my name is Sara, and I'm from Delhi.", isCorrect: true },
          { itemId: "st3", text: "Hello, I'm design student.", isCorrect: false },
        ],
      },
    },
    {
      id: "w2d1-speak-intro-roleplay",
      sequence: 4,
      archetypeId: "SPEAK_ROLEPLAY",
      widget: "speak_roleplay",
      sectionLabel: "Speaking",
      topic: "Introduce yourself in a new conversation",
      taskIntro: "Introduce yourself naturally",
      instructions:
        "Respond to the new person in the chat. Introduce yourself clearly and ask one friendly follow-up question.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      dialogueContext: [
        {
          role: "Maya",
          text: "Hi there, I don't think we've met before. I'm Maya.",
          speaker: "partner",
        },
        {
          role: "You",
          text: "Hi Maya, I'm Aarav. Nice to meet you.",
          speaker: "learner",
        },
        {
          role: "Maya",
          text: "Nice to meet you too, Aarav. What do you do?",
          speaker: "partner",
        },
        {
          role: "You",
          text: "I'm a design student. What about you?",
          speaker: "learner",
        },
      ],
      grammarRule:
        "Use a greeting, say your name clearly, and add one short follow-up question to keep the conversation natural.",
      targetWords: ["Hi", "I'm", "Nice to meet you", "What do you do?"],
      speakingDurationSeconds: 30,
      answers: {
        correct: [
          {
            itemId: "sr1",
            transcript: "Hi Maya, I'm Aarav. Nice to meet you.",
            durationSeconds: 6,
            isCorrect: true,
          },
          {
            itemId: "sr2",
            transcript: "I'm a design student. What about you?",
            durationSeconds: 6,
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "sr1",
            transcript: "Hi Maya, I'm Aarav. Nice to meet you.",
            durationSeconds: 6,
            isCorrect: true,
          },
          {
            itemId: "sr2",
            transcript: "I'm design student. What about you?",
            durationSeconds: 6,
            isCorrect: false,
          },
        ],
      },
    },
  ],
};

const weekTwoDayTwoTasks: TaskDayData = {
  dayId: "day_24_02_02",
  tasks: [
    {
      id: "w2d2-read-tfng",
      sequence: 1,
      archetypeId: "READ_TFNG",
      widget: "read_tfng",
      sectionLabel: "Reading",
      topic: "Questions in a short dialogue",
      taskIntro: "Read the study-plan chat",
      instructions:
        "Decide if each statement is True, False, or Not Given from the conversation.",
      subSkill: "Comprehension",
      activity: "Read",
      estimatedMinutes: 3,
      passageTitle: "After Class",
      passage:
        "Asha: Hi Ben, are you free after class? Ben: I think so. Why? Asha: Can we practice English for fifteen minutes? Ben: Sure. Where should we meet? Asha: At the library entrance. Ben: Good idea. Do we need our notebooks? Asha: Yes, please bring your notebook.",
      grammarRule:
        "Use the exact words in the dialogue. True is directly supported, False disagrees with the dialogue, and Not Given is not stated.",
      items: [
        {
          itemId: "s1",
          prompt: "Asha asks if Ben is free after class.",
          correctAnswer: "True",
          explanation: "Asha asks, 'Are you free after class?'",
        },
        {
          itemId: "s2",
          prompt: "Ben says he cannot practice English.",
          correctAnswer: "False",
          explanation: "Ben says, 'Sure,' so he agrees to practice.",
        },
        {
          itemId: "s3",
          prompt: "They plan to meet at the library entrance.",
          correctAnswer: "True",
          explanation: "Asha says they should meet at the library entrance.",
        },
        {
          itemId: "s4",
          prompt: "Ben tells Asha about his favorite hobby.",
          correctAnswer: "Not Given",
          explanation: "The dialogue talks about practice and notebooks, but not Ben's hobby.",
        },
      ],
      answers: {
        correct: { s1: "True", s2: "False", s3: "True", s4: "Not Given" },
        wrong: { s1: "True", s2: "True", s3: "True", s4: "Not Given" },
      },
    },
    {
      id: "w2d2-listen-infer",
      sequence: 2,
      archetypeId: "LISTEN_INFER",
      widget: "listen_infer",
      sectionLabel: "Listening",
      topic: "Inferring intent in a request",
      taskIntro: "Listen for what the speakers mean",
      instructions:
        "Play the short conversation and choose the best intent for each line.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 4,
      audioGenre: "Polite request dialogue",
      audioDurationSeconds: 42,
      audioScript:
        "Mina: Hi Leo, can I ask you something? Leo: Sure. Mina: Could you help me with the poster after lunch? Leo: I can help for ten minutes. Mina: Great, thank you. Do you want me to bring the markers? Leo: Yes, please.",
      intentFocus:
        "Listen beyond the literal words. Notice when a speaker is starting a request, asking for help, limiting time, or offering to prepare something.",
      items: [
        {
          itemId: "q1",
          prompt: "Why does Mina say, 'Can I ask you something?'",
          options: [
            "To politely start a request",
            "To end the conversation",
            "To ask Leo's name",
            "To say she is busy",
          ],
          correctIndex: 0,
          explanation: "Mina uses this question to politely prepare Leo for a request.",
        },
        {
          itemId: "q2",
          prompt: "What is Mina's main intent?",
          options: [
            "She wants to invite Leo to dinner.",
            "She wants help with the poster.",
            "She wants to borrow Leo's notebook.",
            "She wants to cancel lunch.",
          ],
          correctIndex: 1,
          explanation: "Mina asks, 'Could you help me with the poster after lunch?'",
        },
        {
          itemId: "q3",
          prompt: "Why does Leo say, 'for ten minutes'?",
          options: [
            "He is asking for the time.",
            "He is saying the poster is finished.",
            "He is limiting how long he can help.",
            "He is refusing to help.",
          ],
          correctIndex: 2,
          explanation: "Leo agrees to help, but he gives a time limit.",
        },
        {
          itemId: "q4",
          prompt: "Why does Mina ask about bringing markers?",
          options: [
            "She is offering to prepare materials.",
            "She is asking for Leo's hobby.",
            "She is changing the meeting place.",
            "She is ending the project.",
          ],
          correctIndex: 0,
          explanation: "Mina offers to bring the markers they may need for the poster.",
        },
      ],
      answers: {
        correct: { q1: 0, q2: 1, q3: 2, q4: 0 },
        wrong: { q1: 0, q2: 1, q3: 3, q4: 0 },
      },
    },
    {
      id: "w2d2-write-email",
      sequence: 3,
      archetypeId: "WRITE_EMAIL",
      widget: "write_email",
      sectionLabel: "Writing",
      topic: "Ask a simple question by message",
      taskIntro: "Write a short question message",
      instructions:
        "Write a simple message asking someone if they can meet. Include a greeting, one clear question, and a polite close.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 5,
      prompt: "Write a short message to a classmate asking: Can we meet after class?",
      grammarRule:
        "Use a polite greeting, one clear question with 'Can we...?' or 'Could you...?', and a short closing line.",
      targetWords: ["Hi", "Can we", "after class", "thank you"],
      minimumWords: 20,
      sampleAnswer:
        "To: ben@example.com\nSubject: Quick question\nHi Ben,\nCan we meet after class today? I want to practice the English dialogue for fifteen minutes. Please tell me if you are free. Thank you!",
      answerHints: [
        "Start with a greeting.",
        "Ask one direct question.",
        "Add a time phrase like after class.",
        "Close politely.",
      ],
      answers: {
        correct: [
          {
            itemId: "email",
            text: "To: ben@example.com\nSubject: Quick question\nHi Ben,\nCan we meet after class today? I want to practice the English dialogue for fifteen minutes. Please tell me if you are free. Thank you!",
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "email",
            text: "To: ben@example.com\nSubject: Quick question\nHi Ben,\nCan we meeting after class today? I want practice the English dialogue for fifteen minutes. Please tell me if you are free. Thank you!",
            isCorrect: false,
          },
        ],
      },
    },
    {
      id: "w2d2-speak-interview",
      sequence: 4,
      archetypeId: "SPEAK_INTERVIEW",
      widget: "speak_interview",
      sectionLabel: "Speaking",
      topic: "Answer simple interview questions",
      taskIntro: "Answer three live questions",
      instructions:
        "Answer each question in one short sentence. Keep your answer clear and friendly.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      interviewContext: "Mini interview",
      grammarRule:
        "Use full short answers: 'My name is...', 'I'm a...', and 'I like...'.",
      targetWords: ["My name is", "I'm a", "I like"],
      speakingDurationSeconds: 30,
      questions: [
        {
          itemId: "i1",
          interviewerPrompt: "What is your name?",
          sampleAnswer: "My name is Aarav.",
          answerHint: "Say your name in one full sentence.",
        },
        {
          itemId: "i2",
          interviewerPrompt: "What do you do?",
          sampleAnswer: "I'm a design student.",
          answerHint: "Use I'm a plus your work or study role.",
        },
        {
          itemId: "i3",
          interviewerPrompt: "What is your hobby?",
          sampleAnswer: "I like drawing in my free time.",
          answerHint: "Use I like plus a hobby.",
        },
      ],
      answers: {
        correct: [
          { itemId: "i1", transcript: "My name is Aarav.", durationSeconds: 4, isCorrect: true },
          { itemId: "i2", transcript: "I'm a design student.", durationSeconds: 5, isCorrect: true },
          { itemId: "i3", transcript: "I like drawing in my free time.", durationSeconds: 6, isCorrect: true },
        ],
        wrong: [
          { itemId: "i1", transcript: "My name is Aarav.", durationSeconds: 4, isCorrect: true },
          { itemId: "i2", transcript: "I'm design student.", durationSeconds: 5, isCorrect: false },
          { itemId: "i3", transcript: "I like drawing in my free time.", durationSeconds: 6, isCorrect: true },
        ],
      },
    },
  ],
};

const weekTwoDayThreeTasks: TaskDayData = {
  dayId: "day_24_02_03",
  tasks: [
    {
      id: "w2d3-read-structure",
      sequence: 1,
      archetypeId: "READ_STRUCTURE_ID",
      widget: "read_structure",
      sectionLabel: "Reading",
      topic: "Identify parts of a morning routine",
      taskIntro: "Label the routine passage structure",
      instructions:
        "Read the short passage and choose whether each paragraph is the intro, body, or conclusion.",
      subSkill: "Comprehension",
      activity: "Read",
      estimatedMinutes: 4,
      passageTitle: "My Morning Routine",
      grammarRule:
        "A clear routine paragraph starts with a main idea, gives ordered details, and ends with a closing thought.",
      structureLabels: ["Intro", "Body", "Conclusion"],
      items: [
        {
          itemId: "p1",
          paragraph:
            "Every morning, I follow a simple routine before work. It helps me feel calm and ready for the day.",
          correctAnswer: "Intro",
          explanation:
            "This paragraph introduces the topic and gives the main idea of the routine.",
        },
        {
          itemId: "p2",
          paragraph:
            "First, I wake up at six thirty and drink a glass of water. Then I brush my teeth, take a shower, and make tea. After that, I read the news for ten minutes.",
          correctAnswer: "Body",
          explanation:
            "This paragraph gives the ordered routine details with sequence words.",
        },
        {
          itemId: "p3",
          paragraph:
            "Finally, I pack my bag and leave home at eight. This routine is not special, but it makes my mornings easier.",
          correctAnswer: "Conclusion",
          explanation:
            "This paragraph closes the routine and adds a final thought about it.",
        },
      ],
      answers: {
        correct: {
          p1: "Intro",
          p2: "Body",
          p3: "Conclusion",
        },
        wrong: {
          p1: "Intro",
          p2: "Conclusion",
          p3: "Conclusion",
        },
      },
    },
    {
      id: "w2d3-listen-retell",
      sequence: 2,
      archetypeId: "LISTEN_RETELL",
      widget: "listen_retell",
      sectionLabel: "Listening",
      topic: "Retell a daily routine",
      taskIntro: "Listen and retell the person's day",
      instructions:
        "Listen to the routine once, then retell the main actions in your own words.",
      subSkill: "Active recall",
      activity: "Listen",
      estimatedMinutes: 4,
      audioGenre: "Daily routine monologue",
      audioScript:
        "I usually wake up at six forty-five. First, I feed my dog and make coffee. Then I take the bus to work at eight. In the afternoon, I answer emails and talk to customers. After work, I cook dinner and call my mother. I go to bed around ten thirty.",
      audioDurationSeconds: 52,
      grammarRule:
        "Retell the key actions in order. Use sequence words like first, then, after work, and finally.",
      targetWords: ["first", "then", "after work", "finally"],
      passageToRetell:
        "The speaker wakes up at six forty-five, feeds the dog, makes coffee, and takes the bus to work. In the afternoon, the speaker answers emails and talks to customers. After work, the speaker cooks dinner, calls their mother, and goes to bed around ten thirty.",
      answers: {
        correct: [
          {
            itemId: "retell",
            transcript:
              "The speaker wakes up at six forty-five. First, they feed the dog and make coffee. Then they take the bus to work. After work, they cook dinner, call their mother, and go to bed around ten thirty.",
            durationSeconds: 34,
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "retell",
            transcript:
              "The speaker wakes up at six forty-five. First, they make coffee and take the bus. Then they cook lunch at work and call their mother in the morning.",
            durationSeconds: 29,
            isCorrect: false,
          },
        ],
      },
    },
    {
      id: "w2d3-write-para",
      sequence: 3,
      archetypeId: "WRITE_PARA",
      widget: "write_paragraph",
      sectionLabel: "Writing",
      topic: "Write your daily routine",
      taskIntro: "Write a short routine paragraph",
      instructions:
        "Write one short paragraph about your own daily routine. Use sequence words and simple present verbs.",
      subSkill: "Fluency",
      activity: "Write",
      estimatedMinutes: 6,
      prompt: "Describe your daily routine in 5 to 7 sentences.",
      grammarRule:
        "Use simple present for routines and sequence words to connect the actions naturally.",
      targetWords: ["first", "then", "after that", "usually", "finally"],
      minimumWords: 45,
      sampleAnswer:
        "I usually wake up at seven and drink water. First, I brush my teeth and take a shower. Then I make breakfast and check my messages. After that, I travel to work by bus. In the evening, I cook dinner and study English. Finally, I relax for a short time before bed.",
      answerHints: [
        "Start with the time you wake up.",
        "Use at least three sequence words.",
        "Keep the verbs in simple present.",
        "End with one final evening or night activity.",
      ],
      answers: {
        correct: [
          {
            itemId: "paragraph",
            text:
              "I usually wake up at seven and drink water. First, I brush my teeth and take a shower. Then I make breakfast and read my messages. After that, I go to work by bus. In the evening, I cook dinner and study English. Finally, I listen to music before bed.",
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "paragraph",
            text:
              "I usually wake up at seven and drink water. First, I brushes my teeth and take a shower. Then I make breakfast and read my messages. After that, I go to work by bus. In the evening, I cook dinner and study English. Finally, I listen to music before bed.",
            isCorrect: false,
          },
        ],
      },
    },
    {
      id: "w2d3-speak-opinion",
      sequence: 4,
      archetypeId: "SPEAK_OPINION",
      widget: "speak_record",
      sectionLabel: "Speaking",
      topic: "Share a short daily-life opinion",
      taskIntro: "Give a short spoken opinion",
      instructions:
        "Answer the prompt in two or three sentences. Give your preference and one reason.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 3,
      mode: "timed",
      speakingDurationSeconds: 40,
      grammarRule:
        "Use I prefer morning or I prefer evening, then add because plus a simple reason.",
      targetWords: ["I prefer", "because", "morning", "evening"],
      prompts: ["Do you prefer morning or evening? Give one short reason."],
      sampleResponses: [
        "I prefer morning because I feel fresh and focused. I can finish my important work early.",
      ],
      answers: {
        correct: [
          {
            itemId: "opinion",
            transcript:
              "I prefer morning because I feel fresh and focused. I can finish my important work early.",
            durationSeconds: 12,
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "opinion",
            transcript:
              "I prefer morning because I feeling fresh and focused. I can finish my important work early.",
            durationSeconds: 12,
            isCorrect: false,
          },
        ],
      },
    },
  ],
};

const stationDirectionsMapImageUrl = `data:image/svg+xml;utf8,${encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 360" role="img" aria-label="Simple map showing bus stop, bakery, pharmacy, station, park, cafe, and roads">
  <rect width="720" height="360" fill="#eef7fb"/>
  <rect x="0" y="0" width="720" height="120" fill="#d9f2da"/>
  <text x="32" y="64" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#287446">City Park</text>
  <rect x="0" y="154" width="720" height="54" fill="#f7f3df"/>
  <rect x="318" y="0" width="56" height="360" fill="#f7f3df"/>
  <path d="M0 181H720M346 0V360" stroke="#c9b978" stroke-width="5" stroke-dasharray="18 12"/>
  <text x="404" y="174" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#796924">Park Road</text>
  <text x="258" y="40" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#796924" transform="rotate(90 258 40)">Station Street</text>
  <rect x="92" y="225" width="132" height="80" rx="14" fill="#ffffff" stroke="#8eb5d8" stroke-width="3"/>
  <text x="118" y="272" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#1d4f77">Bus Stop</text>
  <rect x="252" y="220" width="112" height="80" rx="14" fill="#fff1d8" stroke="#d49a46" stroke-width="3"/>
  <text x="274" y="254" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="#86520f">Bakery</text>
  <text x="292" y="280" font-family="Arial, sans-serif" font-size="30" fill="#86520f">&#8592;</text>
  <rect x="402" y="72" width="124" height="78" rx="14" fill="#e7fff1" stroke="#53a674" stroke-width="3"/>
  <text x="420" y="120" font-family="Arial, sans-serif" font-size="21" font-weight="700" fill="#217044">Pharmacy</text>
  <rect x="548" y="72" width="120" height="78" rx="14" fill="#e7edff" stroke="#637fd5" stroke-width="3"/>
  <text x="570" y="120" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#2944a2">Station</text>
  <rect x="450" y="244" width="114" height="70" rx="14" fill="#ffffff" stroke="#b98ac9" stroke-width="3"/>
  <text x="482" y="287" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#754387">Cafe</text>
  <path d="M158 214C210 190 256 181 318 181M346 181V116M374 111H402" fill="none" stroke="#0070c4" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M386 96l24 15-24 15" fill="none" stroke="#0070c4" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="158" cy="214" r="12" fill="#0070c4"/>
  <text x="28" y="336" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#1d4f77">Route: go straight on Park Road, turn left at the bakery, then the station is next to the pharmacy.</text>
</svg>
`)}`;

const weekTwoDayFiveTasks: TaskDayData = {
  dayId: "day_24_02_05",
  tasks: [
    {
      id: "w2d5-read-directions-tfng",
      sequence: 1,
      archetypeId: "READ_TFNG",
      widget: "read_tfng",
      sectionLabel: "Reading",
      topic: "Simple street directions",
      taskIntro: "Read the directions to the station",
      instructions:
        "Decide if each statement is True, False, or Not Given from the directions.",
      subSkill: "Practical reading",
      activity: "Read",
      estimatedMinutes: 3,
      passageTitle: "From the Bus Stop to the Station",
      passage:
        "You are at the bus stop on Park Road. Go straight for two minutes. Turn left at the bakery. Walk past the pharmacy. The station is next to the pharmacy, on your right. The cafe is behind you, so do not go back.",
      grammarRule:
        "Use direction words and landmarks carefully: go straight, turn left, past, next to, on your right, and behind.",
      items: [
        {
          itemId: "s1",
          prompt: "You start at the bus stop on Park Road.",
          correctAnswer: "True",
          explanation: "The first sentence says you are at the bus stop on Park Road.",
        },
        {
          itemId: "s2",
          prompt: "You should turn right at the bakery.",
          correctAnswer: "False",
          explanation: "The directions say to turn left at the bakery, not right.",
        },
        {
          itemId: "s3",
          prompt: "The station is next to the pharmacy.",
          correctAnswer: "True",
          explanation: "The text says the station is next to the pharmacy.",
        },
        {
          itemId: "s4",
          prompt: "The bakery opens at 8 a.m.",
          correctAnswer: "Not Given",
          explanation: "The directions mention the bakery as a landmark, but they do not give opening times.",
        },
      ],
      answers: {
        correct: { s1: "True", s2: "False", s3: "True", s4: "Not Given" },
        wrong: { s1: "True", s2: "True", s3: "True", s4: "Not Given" },
      },
    },
    {
      id: "w2d5-listen-help-infer",
      sequence: 2,
      archetypeId: "LISTEN_INFER",
      widget: "listen_infer",
      sectionLabel: "Listening",
      topic: "Infer what help someone needs",
      taskIntro: "Listen to a help request",
      instructions:
        "Play the short conversation and choose what the speaker needs or means.",
      subSkill: "Listening for intent",
      activity: "Listen",
      estimatedMinutes: 4,
      audioGenre: "Help request dialogue",
      audioScript:
        "Traveler: Excuse me, could you help me? I am trying to find the station. Person: Of course. Go straight on this road and turn left at the bakery. Traveler: Thank you. Is it far from here? Person: No, it is about five minutes. The station is next to the pharmacy.",
      audioDurationSeconds: 38,
      intentFocus:
        "Listen for the problem, the place needed, distance words, and landmarks that solve the problem.",
      items: [
        {
          itemId: "q1",
          prompt: "Why does the traveler say, 'Could you help me?'",
          options: [
            "To politely ask for assistance",
            "To buy something at the bakery",
            "To end the conversation",
            "To invite the person for coffee",
          ],
          correctIndex: 0,
          explanation: "The traveler uses a polite question before explaining the problem.",
        },
        {
          itemId: "q2",
          prompt: "What does the traveler need?",
          options: [
            "A ticket price",
            "Directions to the station",
            "A phone number",
            "A cafe table",
          ],
          correctIndex: 1,
          explanation: "The traveler says, 'I am trying to find the station.'",
        },
        {
          itemId: "q3",
          prompt: "What does the traveler mean by, 'Is it far from here?'",
          options: [
            "They want to know the distance.",
            "They want to change the topic.",
            "They cannot hear the speaker.",
            "They are asking for the time.",
          ],
          correctIndex: 0,
          explanation: "The traveler asks whether the station is far, so they want distance information.",
        },
        {
          itemId: "q4",
          prompt: "Which landmark helps the traveler find the station?",
          options: ["The pharmacy", "The post office", "The school", "The hospital"],
          correctIndex: 0,
          explanation: "The helper says the station is next to the pharmacy.",
        },
      ],
      answers: {
        correct: { q1: 0, q2: 1, q3: 0, q4: 0 },
        wrong: { q1: 0, q2: 1, q3: 3, q4: 0 },
      },
    },
    {
      id: "w2d5-write-station-help",
      sequence: 3,
      archetypeId: "WRITE_IDEA_PARA",
      widget: "write_paragraph",
      sectionLabel: "Writing",
      topic: "Ask for directions in writing",
      taskIntro: "Write what you would say",
      instructions:
        "Write a short polite request for directions to the station. Include the place, one help phrase, and a thank-you.",
      subSkill: "Generative thinking",
      activity: "Write",
      estimatedMinutes: 5,
      prompt: "You need directions to the station. Write what you would say.",
      grammarRule:
        "Start politely, ask for the place clearly, and add a simple follow-up question if needed.",
      targetWords: ["Excuse me", "could you help me", "station", "thank you"],
      minimumWords: 24,
      sampleAnswer:
        "Excuse me, could you help me? I am trying to find the station. Which way should I go from here? Is it far? Thank you for your help.",
      answerHints: [
        "Start with Excuse me.",
        "Say the exact place you need.",
        "Ask one clear directions question.",
        "End politely.",
      ],
      answers: {
        correct: [
          {
            itemId: "paragraph",
            text:
              "Excuse me, could you help me? I am trying to find the station. Which way should I go from here? Is it far? Thank you for your help.",
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "paragraph",
            text:
              "Excuse me, could you help me? I trying to find the station. Which way I should go from here? Is it far? Thank you for your help.",
            isCorrect: false,
          },
        ],
      },
    },
    {
      id: "w2d5-speak-map-desc",
      sequence: 4,
      archetypeId: "SPEAK_PIC_DESC",
      widget: "speak_pic_desc",
      sectionLabel: "Speaking",
      topic: "Describe places on a map",
      taskIntro: "Describe the map location",
      instructions:
        "Look at the map and describe what you see. Say where the station, pharmacy, bakery, and bus stop are.",
      subSkill: "Visual description",
      activity: "Speak",
      estimatedMinutes: 4,
      imageUrl: stationDirectionsMapImageUrl,
      imageAlt:
        "Map with a bus stop on Park Road, a bakery at the turn, a pharmacy, a station next to the pharmacy, a cafe, and a route arrow.",
      grammarRule:
        "Use place phrases like next to, on the right, at the bakery, and go straight.",
      speakingDurationSeconds: 40,
      answers: {
        correct: [
          {
            itemId: "map",
            transcript:
              "I can see a bus stop on Park Road. The bakery is near the turn. The pharmacy is on the right, and the station is next to the pharmacy.",
            durationSeconds: 21,
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "map",
            transcript:
              "I can see a bus stop on Park Road. The bakery is near the turn. The station is next to the cafe, and the pharmacy is behind me.",
            durationSeconds: 20,
            isCorrect: false,
          },
        ],
      },
    },
  ],
};

const weekTwoDayFourTasks: TaskDayData = {
  dayId: "day_24_02_04",
  tasks: [
    {
      id: "w2d4-read-comp-mcq",
      sequence: 1,
      archetypeId: "READ_COMP_MCQ",
      widget: "read_comp_mcq",
      sectionLabel: "Reading",
      topic: "Shopping Dialogue",
      taskIntro: "Read the shopping conversation",
      instructions: "Read the dialogue between a customer and a shopkeeper, then answer the questions.",
      subSkill: "Comprehension",
      activity: "Read",
      estimatedMinutes: 3,
      passageTitle: "Finding Items",
      passage:
        "Shopkeeper: Hello! Can I help you find something?\nCustomer: Yes, please. I'm looking for fresh strawberries and organic honey.\nShopkeeper: Strawberries are in aisle 2, next to the apples. The honey is on the middle shelf in aisle 4.\nCustomer: Perfect, thank you. I also need a loaf of sourdough bread.\nShopkeeper: The bakery section is right at the back. Fresh bread is delivered every morning at eight.\nCustomer: Great, I'll head there now. Thanks for your help!",
      grammarRule:
        "Identify specific details about what the customer is buying and where they are located in the shop.",
      items: [
        {
          itemId: "q1",
          prompt: "What is the customer looking for first?",
          options: ["Sourdough bread", "Strawberries and honey", "Apples and milk", "Chocolate cake"],
          correctIndex: 1,
          explanation: "The customer says, 'I'm looking for fresh strawberries and organic honey.'",
        },
        {
          itemId: "q2",
          prompt: "Where can the customer find the organic honey?",
          options: ["In aisle 2", "In the bakery section", "On the middle shelf in aisle 4", "Next to the entrance"],
          correctIndex: 2,
          explanation: "The shopkeeper says, 'The honey is on the middle shelf in aisle 4.'",
        },
        {
          itemId: "q3",
          prompt: "When is fresh sourdough bread delivered?",
          options: ["At eight in the morning", "Every evening", "In the afternoon", "At noon"],
          correctIndex: 0,
          explanation: "The shopkeeper says, 'Fresh bread is delivered every morning at eight.'",
        },
      ],
      answers: {
        correct: { q1: 1, q2: 2, q3: 0 },
        wrong: { q1: 1, q2: 0, q3: 0 },
      },
    },
    {
      id: "w2d4-listen-mcq",
      sequence: 2,
      archetypeId: "LISTEN_MCQ",
      widget: "listen_mcq",
      sectionLabel: "Listening",
      topic: "Café Order details",
      taskIntro: "Listen to the café order",
      instructions: "Listen to the café order conversation and choose the correct option.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 3,
      audioGenre: "Café order conversation",
      audioScript:
        "Server: Welcome to Green Bean Café. What can I get for you today?\nCustomer: Hi. Could I have a medium iced latte with oat milk, please?\nServer: Sure, a medium iced latte with oat milk. Anything to eat?\nCustomer: Yes, I'll also take a warm blueberry muffin, please.\nServer: Perfect. That's one iced latte and a blueberry muffin. That will be seven fifty.",
      audioDurationSeconds: 38,
      innerWidget: "mcq",
      items: [
        {
          itemId: "l1",
          prompt: "What drink did the customer order?",
          options: ["Hot espresso", "Iced latte with oat milk", "Iced americano", "Hot latte with almond milk"],
          correctIndex: 1,
          explanation: "The customer asks for a 'medium iced latte with oat milk'.",
        },
        {
          itemId: "l2",
          prompt: "What food item did the customer select?",
          options: ["Chocolate cookie", "Warm blueberry muffin", "Croissant", "Apple pie"],
          correctIndex: 1,
          explanation: "The customer says, 'I'll also take a warm blueberry muffin, please.'",
        },
        {
          itemId: "l3",
          prompt: "What is the total price of the order?",
          options: ["Six dollars", "Eight fifty", "Seven fifty", "Five fifty"],
          correctIndex: 2,
          explanation: "The server says, 'That will be seven fifty.'",
        },
      ],
      answers: {
        correct: { l1: 1, l2: 1, l3: 2 },
        wrong: { l1: 1, l2: 0, l3: 2 },
      },
    },
    {
      id: "w2d4-write-bullets-para",
      sequence: 3,
      archetypeId: "WRITE_BULLETS_TO_PARA",
      widget: "write_bullets_to_para",
      sectionLabel: "Writing",
      topic: "Write a message from a shopping list",
      taskIntro: "Write a clear message for your partner",
      instructions:
        "You have a shopping list with bullet points. Write a natural message to your roommate asking them if they can pick them up.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 5,
      prompt: "Turn these shopping items into a polite chat message to your roommate: bananas, almond milk, pasta, and fresh basil.",
      bullets: ["3 ripe bananas", "1 carton of almond milk", "2 packs of whole wheat pasta", "Some fresh basil"],
      grammarRule:
        "Translate bullet points into complete, natural sentences using polite request structures like 'Could you please...?'",
      targetWords: ["Hi", "could you please", "also", "thank you"],
      minimumWords: 25,
      sampleAnswer:
        "Hi! Could you please pick up a few things from the store? We need 3 ripe bananas and 1 carton of almond milk. Also, please get 2 packs of whole wheat pasta and some fresh basil. Thank you so much!",
      answerHints: [
        "Start with a friendly greeting.",
        "Mention all 4 items from the list.",
        "Use polite request phrasing.",
        "End with a thank you.",
      ],
      answers: {
        correct: [
          {
            itemId: "bullets_para",
            text:
              "Hi! Could you please pick up a few things from the grocery store? We need 3 ripe bananas and 1 carton of almond milk. Also, please get 2 packs of whole wheat pasta and some fresh basil. Thank you!",
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "bullets_para",
            text:
              "Hi, could you please pick up 3 ripe bananas and 1 carton almond milk? Also get 2 packs whole wheat pasta. Thank you.",
            isCorrect: false,
          },
        ],
      },
    },
    {
      id: "w2d4-speak-roleplay",
      sequence: 4,
      archetypeId: "SPEAK_ROLEPLAY",
      widget: "speak_roleplay",
      sectionLabel: "Speaking",
      topic: "Order items at a grocery shop",
      taskIntro: "Roleplay with the shopkeeper",
      instructions: "Respond to the shopkeeper. Order the items you need politely and answer their questions.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      dialogueContext: [
        {
          role: "Shopkeeper",
          text: "Hello! Welcome to Fresh Foods Market. How can I help you today?",
          speaker: "partner",
        },
        {
          role: "You",
          text: "Hi! I'm looking for some fresh tomatoes and a bottle of olive oil, please.",
          speaker: "learner",
        },
        {
          role: "Shopkeeper",
          text: "Sure, the tomatoes are in aisle 1, and olive oil is in aisle 3. Would you like a paper bag for these?",
          speaker: "partner",
        },
        {
          role: "You",
          text: "Yes, please. I'd like a paper bag, and also a bottle of mineral water.",
          speaker: "learner",
        },
      ],
      grammarRule:
        "Use a polite greeting, say what you are looking for clearly using 'I'm looking for...', and answer questions directly.",
      targetWords: ["looking for", "olive oil", "Yes, please", "also"],
      speakingDurationSeconds: 30,
      answers: {
        correct: [
          {
            itemId: "sr1",
            transcript: "Hi! I'm looking for some fresh tomatoes and a bottle of olive oil, please.",
            durationSeconds: 7,
            isCorrect: true,
          },
          {
            itemId: "sr2",
            transcript: "Yes, please. I'd like a paper bag, and also a bottle of mineral water.",
            durationSeconds: 6,
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "sr1",
            transcript: "Hi! I looking for some fresh tomatoes and bottle of olive oil, please.",
            durationSeconds: 7,
            isCorrect: false,
          },
          {
            itemId: "sr2",
            transcript: "Yes, please. I'd like a paper bag, and also a bottle of mineral water.",
            durationSeconds: 6,
            isCorrect: true,
          },
        ],
      },
    },
  ],
};

const weekTwoDaySixTasks: TaskDayData = {
  dayId: "day_24_02_06",
  tasks: [
    {
      id: "w2d6-read-tone",
      sequence: 1,
      archetypeId: "READ_TONE_ID",
      widget: "read_tone_id",
      sectionLabel: "Reading",
      topic: "Tone in text messages",
      taskIntro: "Compare two online messages",
      instructions:
        "Read each message and choose whether the tone is formal, casual, or urgent.",
      subSkill: "Tone awareness",
      activity: "Read",
      estimatedMinutes: 4,
      passageTitle: "Two Online Messages",
      grammarRule:
        "Formal messages use polite complete sentences. Casual messages use friendly short forms. Urgent messages often ask for immediate action.",
      items: [
        {
          itemId: "tone1",
          sender: "Work group",
          message:
            "Dear Ms. Rao, could we please reschedule our online meeting to 3 p.m.? Thank you for your understanding.",
          prompt: "What is the tone of this message?",
          options: ["Formal", "Casual", "Urgent"],
          correctIndex: 0,
          explanation:
            "Dear, could we please, and thank you make the message formal and polite.",
        },
        {
          itemId: "tone2",
          sender: "Friend chat",
          message: "Hey! Running five mins late. Grab a table? See you soon :)",
          prompt: "What is the tone of this message?",
          options: ["Formal", "Casual", "Urgent"],
          correctIndex: 1,
          explanation:
            "Hey, mins, and the smiley make the message casual and friendly.",
        },
      ],
      answers: {
        correct: { tone1: 0, tone2: 1 },
        wrong: { tone1: 0, tone2: 2 },
      },
    },
    {
      id: "w2d6-listen-tone",
      sequence: 2,
      archetypeId: "LISTEN_TONE",
      widget: "listen_mcq",
      sectionLabel: "Listening",
      topic: "Tone in a phone call",
      taskIntro: "Listen for the speaker's tone",
      instructions:
        "Play the phone call preview and choose the tone that best matches the speaker.",
      subSkill: "Listening for tone",
      activity: "Listen",
      estimatedMinutes: 3,
      audioGenre: "Short phone call",
      audioScript:
        "Hi Neha, sorry to call suddenly. The delivery is at the gate now, but I am in a meeting. Could you please pick it up in the next five minutes?",
      audioDurationSeconds: 28,
      innerWidget: "mcq",
      items: [
        {
          itemId: "call-tone",
          prompt: "What is the speaker's tone?",
          options: ["Formal", "Casual", "Urgent"],
          correctIndex: 2,
          explanation:
            "The speaker says suddenly, now, and in the next five minutes, so the tone is urgent.",
        },
      ],
      answers: {
        correct: { "call-tone": 2 },
        wrong: { "call-tone": 1 },
      },
    },
    {
      id: "w2d6-write-paraphrase",
      sequence: 3,
      archetypeId: "WRITE_PARAPHRASE",
      widget: "write_paraphrase",
      sectionLabel: "Writing",
      topic: "Change message register",
      taskIntro: "Rewrite messages for a new reader",
      instructions:
        "Rewrite one formal message as a casual text and one casual text as a polite formal message.",
      subSkill: "Register flexibility",
      activity: "Write",
      estimatedMinutes: 6,
      grammarRule:
        "Keep the meaning the same, but change the level of formality for the person receiving the message.",
      items: [
        {
          itemId: "rewrite1",
          incorrectSentence:
            "Dear Anika, I hope you are well. Could you please call me when you are available?",
          sampleAnswer: "Hey Anika, hope you're good. Can you call me when you're free?",
          watchHints: ["Hey", "you're", "when you're free"],
        },
        {
          itemId: "rewrite2",
          incorrectSentence: "Hey sir, can't join today. Net is bad.",
          sampleAnswer:
            "Dear Sir, I am sorry, but I cannot join today because my internet connection is poor.",
          watchHints: ["Dear Sir", "I am sorry", "cannot", "because"],
        },
      ],
      answers: {
        correct: [
          {
            itemId: "rewrite1",
            text: "Hey Anika, hope you're good. Can you call me when you're free?",
            isCorrect: true,
          },
          {
            itemId: "rewrite2",
            text:
              "Dear Sir, I am sorry, but I cannot join today because my internet connection is poor.",
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "rewrite1",
            text: "Hey Anika, hope you're good. Can you call me when you're free?",
            isCorrect: true,
          },
          {
            itemId: "rewrite2",
            text: "Hey sir, I can't join today because net is bad.",
            isCorrect: false,
          },
        ],
      },
    },
    {
      id: "w2d6-speak-smalltalk",
      sequence: 4,
      archetypeId: "SPEAK_SMALLTALK",
      widget: "speak_smalltalk",
      sectionLabel: "Speaking",
      topic: "Casual weekend chat",
      taskIntro: "Chat casually with the AI",
      instructions:
        "Answer two smalltalk turns about weather and weekend plans in a friendly casual tone.",
      subSkill: "Confidence",
      activity: "Speak",
      estimatedMinutes: 4,
      dialogueContext: [
        {
          role: "AI",
          text: "The weather is so nice today. Do you have any weekend plans?",
          speaker: "partner",
        },
        {
          role: "You",
          text: "Yes, I might meet my friends for coffee if the weather stays good.",
          speaker: "learner",
        },
        {
          role: "AI",
          text: "That sounds fun. What do you usually like to do on Saturdays?",
          speaker: "partner",
        },
        {
          role: "You",
          text: "I usually relax at home, watch something, and call my cousins.",
          speaker: "learner",
        },
      ],
      grammarRule:
        "Use short friendly answers, ask or answer naturally, and mention one simple weekend detail.",
      targetWords: ["That sounds fun", "I might", "usually", "weekend"],
      speakingDurationSeconds: 35,
      answers: {
        correct: [
          {
            itemId: "smalltalk1",
            transcript: "Yes, I might meet my friends for coffee if the weather stays good.",
            durationSeconds: 8,
            isCorrect: true,
          },
          {
            itemId: "smalltalk2",
            transcript: "I usually relax at home, watch something, and call my cousins.",
            durationSeconds: 8,
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "smalltalk1",
            transcript: "Yes, I might meet my friends for coffee if the weather stays good.",
            durationSeconds: 8,
            isCorrect: true,
          },
          {
            itemId: "smalltalk2",
            transcript: "I usually relaxing at home, watch something, and call my cousins.",
            durationSeconds: 8,
            isCorrect: false,
          },
        ],
      },
    },
  ],
};

const weekTwoDaySevenTasks: TaskDayData = {
  dayId: "day_24_02_07",
  tasks: [
    {
      id: "w2d7-read-structure",
      sequence: 1,
      archetypeId: "READ_STRUCTURE_ID",
      widget: "read_structure",
      sectionLabel: "Reading",
      topic: "Small-talk chat structure",
      taskIntro: "Identify how the chat connects ideas",
      instructions:
        "Read the short social chat and label each part by its role in the conversation.",
      subSkill: "Comprehension",
      activity: "Read",
      estimatedMinutes: 4,
      passageTitle: "Weekend Chat Thread",
      grammarRule:
        "Notice how friendly chats move from greeting, to shared details, to a reflective closing.",
      structureLabels: ["Opening", "Shared Details", "Reflection"],
      items: [
        {
          itemId: "c1",
          label: "Chat part 1",
          paragraph:
            "Maya: Hey Sam! How was your week? Sam: Pretty good, thanks. A little busy, but good.",
          correctAnswer: "Opening",
          explanation:
            "This part starts the social exchange with a greeting and a simple week check-in.",
        },
        {
          itemId: "c2",
          label: "Chat part 2",
          paragraph:
            "Maya: Same here. I had two classes and helped my brother with homework. Sam: Nice. I went to the gym twice and met my cousin on Friday.",
          correctAnswer: "Shared Details",
          explanation:
            "This part adds connected details about each person's week.",
        },
        {
          itemId: "c3",
          label: "Chat part 3",
          paragraph:
            "Maya: Sounds like a full week. I feel tired, but happy. Sam: Me too. Let's keep Sunday quiet and start fresh tomorrow.",
          correctAnswer: "Reflection",
          explanation:
            "This part closes the chat by reflecting on feelings and the next step.",
        },
      ],
      answers: {
        correct: {
          c1: "Opening",
          c2: "Shared Details",
          c3: "Reflection",
        },
        wrong: {
          c1: "Opening",
          c2: "Reflection",
          c3: "Reflection",
        },
      },
    },
    {
      id: "w2d7-listen-retell",
      sequence: 2,
      archetypeId: "LISTEN_RETELL",
      widget: "listen_retell",
      responseMode: "written",
      sectionLabel: "Listening",
      topic: "Retell a casual conversation",
      taskIntro: "Retell the key points in writing",
      instructions:
        "Listen to the casual conversation, then write the key points in your own words.",
      subSkill: "Active listening",
      activity: "Listen",
      estimatedMinutes: 5,
      audioGenre: "Casual conversation",
      audioScript:
        "Asha: Hi Leo, how was your week? Leo: It was good but busy. I finished a work project and cooked dinner for my family. Asha: Nice. I studied English every evening and met my friend on Saturday. Leo: That sounds good. I think we both had a full week, so Sunday should be quiet.",
      audioDurationSeconds: 58,
      grammarRule:
        "Retell the main points, not every word. Include who spoke, key activities, and the shared feeling.",
      targetWords: ["busy week", "finished", "studied", "quiet Sunday"],
      passageToRetell:
        "Leo had a good but busy week. He finished a work project and cooked dinner for his family. Asha studied English every evening and met a friend on Saturday. They both felt it was a full week and wanted a quiet Sunday.",
      answers: {
        correct: [
          {
            itemId: "retell",
            text:
              "Leo had a good but busy week. He finished a work project and cooked for his family. Asha studied English every evening and met her friend on Saturday. They both felt the week was full and wanted a quiet Sunday.",
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "retell",
            text:
              "Leo had a good but busy week. He finished a work project and cooked for his family. Asha studied English every morning and met her friend on Saturday. They both wanted a quiet Sunday.",
            isCorrect: false,
          },
        ],
      },
    },
    {
      id: "w2d7-write-email",
      sequence: 3,
      archetypeId: "WRITE_EMAIL",
      widget: "write_email",
      sectionLabel: "Writing",
      topic: "Message a friend about your week",
      taskIntro: "Write a short friendly message",
      instructions:
        "Write a short message to a friend about your week. Include two activities and one feeling.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 6,
      prompt: "Write 45 to 60 words to a friend about your week.",
      grammarRule:
        "Use friendly opening and closing phrases, simple past for completed activities, and one feeling sentence.",
      targetWords: ["How are you?", "this week", "I felt", "talk soon"],
      minimumWords: 45,
      sampleAnswer:
        "To: friend@example.com\nSubject: My week\nHi Riya,\nHow are you? This week was busy but good. I finished a small project at work, studied English after dinner, and met my cousin on Saturday. I felt tired on Friday, but I feel happy now. Hope your week was nice too. Talk soon!",
      answerHints: [
        "Open with a friendly greeting.",
        "Mention two real activities from the week.",
        "Add one feeling sentence.",
        "Close naturally with a friendly line.",
      ],
      answers: {
        correct: [
          {
            itemId: "email",
            text:
              "To: friend@example.com\nSubject: My week\nHi Riya,\nHow are you? This week was busy but good. I finished a small project at work, studied English after dinner, and met my cousin on Saturday. I felt tired on Friday, but I feel happy now. Hope your week was nice too. Talk soon!",
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "email",
            text:
              "To: friend@example.com\nSubject: My week\nHi Riya,\nHow are you? This week was busy but good. I finish a small project at work, studied English after dinner, and met my cousin on Saturday. I felt tired on Friday, but I feel happy now. Hope your week was nice too. Talk soon!",
            isCorrect: false,
          },
        ],
      },
    },
    {
      id: "w2d7-speak-present",
      sequence: 4,
      archetypeId: "SPEAK_PRESENT",
      widget: "speak_present",
      sectionLabel: "Speaking",
      topic: "This is my week",
      taskIntro: "Give a 60-second spoken summary",
      instructions:
        "Speak for up to 60 seconds about your week. Start with a general feeling, mention two activities, and end with one plan.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 5,
      grammarRule:
        "Use a simple structure: overall feeling, two weekly details, one closing thought or plan.",
      targetWords: ["This week", "I finished", "I also", "Next week"],
      speakingDurationSeconds: 60,
      visualPromptDescription:
        "This is my week: one opening feeling, two clear activities, and one simple plan for next week.",
      modelPresentation:
        "This week was busy but good. I finished a work project and studied English after dinner. I also met my cousin on Saturday, so I felt happy. Next week, I want to keep studying and sleep a little earlier.",
      answers: {
        correct: [
          {
            itemId: "present",
            transcript:
              "This week was busy but good. I finished a work project and studied English after dinner. I also met my cousin on Saturday, so I felt happy. Next week, I want to keep studying and sleep a little earlier.",
            durationSeconds: 44,
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "present",
            transcript:
              "This week was busy but good. I finish a work project and studied English after dinner. I also met my cousin on Saturday, so I felt happy. Next week, I want to keep studying.",
            durationSeconds: 38,
            isCorrect: false,
          },
        ],
      },
    },
  ],
};

const familyPhotoImageUrl = `data:image/svg+xml;utf8,${encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 360" role="img" aria-label="Family and friends gathering in a backyard photo">
  <rect width="720" height="360" fill="#fdfcf7"/>
  <rect x="0" y="240" width="720" height="120" fill="#e2f0d9"/>
  <circle cx="360" cy="0" r="280" fill="#eef7fb" opacity="0.6"/>
  <text x="360" y="50" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="#2c5e3b" text-anchor="middle">Family &amp; Friends Gathering</text>
  
  <g transform="translate(180, 180)">
    <circle cx="0" cy="-40" r="32" fill="#d9ebd3" stroke="#2e7d32" stroke-width="3"/>
    <path d="M-40 40 C-40 0 -20 -10 0 -10 C20 -10 40 0 40 40 Z" fill="#d9ebd3" stroke="#2e7d32" stroke-width="3"/>
    <text x="0" y="-35" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#1b5e20" text-anchor="middle">David</text>
    <text x="0" y="20" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#1b5e20" text-anchor="middle">Uncle</text>
  </g>

  <g transform="translate(360, 180)">
    <circle cx="0" cy="-40" r="32" fill="#fce4d6" stroke="#c65911" stroke-width="3"/>
    <path d="M-40 40 C-40 0 -20 -10 0 -10 C20 -10 40 0 40 40 Z" fill="#fce4d6" stroke="#c65911" stroke-width="3"/>
    <text x="0" y="-35" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#833c0c" text-anchor="middle">Priya</text>
    <text x="0" y="20" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#833c0c" text-anchor="middle">Colleague</text>
  </g>

  <g transform="translate(540, 180)">
    <circle cx="0" cy="-40" r="32" fill="#fff2cc" stroke="#bf9000" stroke-width="3"/>
    <path d="M-40 40 C-40 0 -20 -10 0 -10 C20 -10 40 0 40 40 Z" fill="#fff2cc" stroke="#bf9000" stroke-width="3"/>
    <text x="0" y="-35" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#7f6000" text-anchor="middle">Mark</text>
    <text x="0" y="20" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#7f6000" text-anchor="middle">Neighbour</text>
  </g>
</svg>
`)}`;

const weekThreeDayOneTasks: TaskDayData = {
  dayId: "day_24_03_01",
  tasks: [
    {
      id: "w3d1-read-word-match",
      sequence: 1,
      archetypeId: "READ_WORD_MATCH",
      widget: "read_word_match",
      sectionLabel: "Reading",
      topic: "Family, Friends & Roles",
      taskIntro: "Match vocabulary to their definitions",
      instructions: "Match each word (uncle, colleague, neighbour, classmate) with its correct definition.",
      subSkill: "Vocabulary",
      activity: "Read",
      estimatedMinutes: 3,
      grammarRule: "Learn family, work, and community relationship words: uncle, colleague, neighbour, classmate.",
      options: ["uncle", "colleague", "neighbour", "classmate"],
      items: [
        {
          itemId: "wm1",
          prompt: "The brother of your mother or father.",
          correctAnswer: "uncle",
          explanation: "An uncle is a family role referring to your parent's brother.",
        },
        {
          itemId: "wm2",
          prompt: "A person you work with, especially in a professional job.",
          correctAnswer: "colleague",
          explanation: "A colleague is a work role referring to someone in your workplace.",
        },
        {
          itemId: "wm3",
          prompt: "Someone who lives near you or next door to you.",
          correctAnswer: "neighbour",
          explanation: "A neighbour is a community role referring to someone living nearby.",
        },
        {
          itemId: "wm4",
          prompt: "A member of the same class at school or university.",
          correctAnswer: "classmate",
          explanation: "A classmate is a school role referring to someone you study with.",
        },
      ],
      answers: {
        correct: { wm1: "uncle", wm2: "colleague", wm3: "neighbour", wm4: "classmate" },
        wrong: { wm1: "uncle", wm2: "classmate", wm3: "neighbour", wm4: "classmate" },
      },
    },
    {
      id: "w3d1-listen-mcq",
      sequence: 2,
      archetypeId: "LISTEN_MCQ",
      widget: "listen_mcq",
      sectionLabel: "Listening",
      topic: "Identifying People in a Dialogue",
      taskIntro: "Listen to a scenario introducing people",
      instructions: "Listen to the short scenario and answer the questions about the relationships.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 3,
      audioGenre: "People introductions conversation",
      audioScript: "Hi Sarah! Come in and meet everyone. This is my uncle, David, who is visiting from London. And over there by the window is my colleague, Priya, from the office. Oh, and you already know my neighbour, Mark, who lives next door.",
      audioDurationSeconds: 32,
      innerWidget: "mcq",
      items: [
        {
          itemId: "l1",
          prompt: "Who is David to the speaker?",
          options: ["His colleague", "His neighbour", "His uncle", "His classmate"],
          correctIndex: 2,
          explanation: "The speaker says, 'This is my uncle, David'.",
        },
        {
          itemId: "l2",
          prompt: "Where does Priya work with the speaker?",
          options: ["At the same school", "At the office", "Next door", "At the hospital"],
          correctIndex: 1,
          explanation: "The speaker says, 'my colleague, Priya, from the office'.",
        },
        {
          itemId: "l3",
          prompt: "Who is Mark?",
          options: ["David's uncle", "The speaker's classmate", "Priya's brother", "The speaker's neighbour"],
          correctIndex: 3,
          explanation: "The speaker says, 'my neighbour, Mark, who lives next door'.",
        },
      ],
      answers: {
        correct: { l1: 2, l2: 1, l3: 3 },
        wrong: { l1: 2, l2: 0, l3: 3 },
      },
    },
    {
      id: "w3d1-write-sent-trans",
      sequence: 3,
      archetypeId: "WRITE_SENT_TRANS",
      widget: "sentence_transform",
      sectionLabel: "Writing",
      topic: "Vocabulary sentence transformation",
      taskIntro: "Transform the sentence using target vocabulary",
      instructions: "Rewrite the sentence to include the correct vocabulary word from the options.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 4,
      grammarRule: "Change simple phrases like 'person at work' or 'friend in my class' to 'colleague' or 'classmate'.",
      items: [
        {
          itemId: "trans1",
          sourceSentence: "She is a person I work with at the office.",
          sampleAnswer: "She is my colleague.",
          watchHints: ["colleague", "my"],
        },
        {
          itemId: "trans2",
          sourceSentence: "He is a student in the same school class as me.",
          sampleAnswer: "He is my classmate.",
          watchHints: ["classmate", "my"],
        },
      ],
      answers: {
        correct: [
          { itemId: "trans1", text: "She is my colleague.", isCorrect: true },
          { itemId: "trans2", text: "He is my classmate.", isCorrect: true },
        ],
        wrong: [
          { itemId: "trans1", text: "She is my colleague.", isCorrect: true },
          { itemId: "trans2", text: "He is my classmates.", isCorrect: false },
        ],
      },
    },
    {
      id: "w3d1-speak-pic-desc",
      sequence: 4,
      archetypeId: "SPEAK_PIC_DESC",
      widget: "speak_pic_desc",
      sectionLabel: "Speaking",
      topic: "Describe a family photo",
      taskIntro: "Describe who is in the family photo",
      instructions: "Look at the picture and describe who is who using your new vocabulary: uncle, neighbour, colleague.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      imageUrl: familyPhotoImageUrl,
      imageAlt: "A family photo showing Uncle David, Colleague Priya, and Neighbour Mark.",
      grammarRule: "Use relationship words like uncle, neighbour, and colleague to describe people and their roles.",
      speakingDurationSeconds: 45,
      answers: {
        correct: [
          {
            itemId: "picdesc",
            transcript: "In this photo, I can see my uncle David on the left. In the middle is Priya, who is my colleague from work. On the right, I can see my neighbour Mark.",
            durationSeconds: 15,
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "picdesc",
            transcript: "In this photo, I can see my uncle David on the left. In the middle is Priya, who is my colleague from work. On the right, I can see my classmate Mark.",
            durationSeconds: 15,
            isCorrect: false,
          },
        ],
      },
    },
  ],
};

const weekThreeDayTwoTasks: TaskDayData = {
  dayId: "day_24_03_02",
  tasks: [
    {
      id: "w3d2-read-context-mcq",
      sequence: 1,
      archetypeId: "READ_CONTEXT_MCQ",
      widget: "read_comp_mcq",
      sectionLabel: "Reading",
      topic: "Food & Eating",
      taskIntro: "Infer word meaning from context",
      instructions: "Read the menu passage and answer the question below.",
      subSkill: "Vocabulary",
      activity: "Read",
      estimatedMinutes: 3,
      passageTitle: "La Bistro Menu",
      passage: "Our lunch menu features several delicious savoury dishes, including warm goat cheese tarts and slow-roasted herb vegetables. For those with a sweet tooth, we also offer our famous strawberry chocolate cake.",
      grammarRule: "Infer word meanings like 'savoury' (salty or spicy food, not sweet) by contrasting them with 'sweet' or 'dessert' cues.",
      items: [
        {
          itemId: "rc1",
          prompt: "What does 'savoury' mean in the context of this menu?",
          options: [
            "Having a sweet taste",
            "Having a salty or spicy taste, not sweet",
            "Extremely hot and spicy",
            "Cold or frozen"
          ],
          correctIndex: 1,
          explanation: "Savoury describes food that is salty or spicy rather than sweet, which fits the cheese tarts and roasted vegetables mentioned."
        }
      ],
      answers: {
        correct: { rc1: 1 },
        wrong: { rc1: 0 }
      }
    },
    {
      id: "w3d2-listen-dictation",
      sequence: 2,
      archetypeId: "LISTEN_DICTATION",
      widget: "listen_dictation",
      sectionLabel: "Listening",
      topic: "Ordering Food",
      taskIntro: "Type the café order you hear",
      instructions: "Listen to the food order and type the exact sentence.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 4,
      audioGenre: "Café order monologue",
      audioScript: "I would like to order a chicken salad with olive oil, and a bottle of mineral water, please.",
      audioDurationSeconds: 12,
      grammarRule: "Listen closely for polite food ordering phrases and precise ingredient vocabulary.",
      targetWords: ["chicken salad", "olive oil", "mineral water"],
      items: [
        {
          itemId: "ld1",
          prompt: "Type the exact café order you hear.",
          correctAnswer: "I would like to order a chicken salad with olive oil, and a bottle of mineral water, please.",
          explanation: "The speaker politely orders: 'I would like to order a chicken salad with olive oil, and a bottle of mineral water, please.'"
        }
      ],
      answers: {
        correct: {
          ld1: "I would like to order a chicken salad with olive oil, and a bottle of mineral water, please."
        },
        wrong: {
          ld1: "I would like to order a chicken salad with salad dressing, and a bottle of mineral water."
        }
      }
    },
    {
      id: "w3d2-write-word-upgrade",
      sequence: 3,
      archetypeId: "WRITE_WORD_UPGRADE",
      widget: "write_word_upgrade",
      sectionLabel: "Writing",
      topic: "Vocabulary Word Upgrade",
      taskIntro: "Upgrade simple food vocabulary",
      instructions: "Rewrite the sentence using the correct target taste word to upgrade simple words like 'good' or 'no taste'.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 4,
      grammarRule: "Replace simple words (like 'good') with premium vocabulary (like 'delicious', 'flavourful', 'bland').",
      items: [
        {
          itemId: "wu1",
          sourceSentence: "The food is good.",
          targetUpgradeWord: "delicious",
          sampleAnswer: "The food is delicious.",
          watchHints: ["delicious", "food"]
        },
        {
          itemId: "wu2",
          sourceSentence: "The chicken soup has no taste.",
          targetUpgradeWord: "bland",
          sampleAnswer: "The chicken soup is bland.",
          watchHints: ["bland", "soup"]
        },
        {
          itemId: "wu3",
          sourceSentence: "This sauce has a lot of nice flavours.",
          targetUpgradeWord: "flavourful",
          sampleAnswer: "This sauce is flavourful.",
          watchHints: ["flavourful", "sauce"]
        }
      ],
      answers: {
        correct: [
          { itemId: "wu1", text: "The food is delicious.", isCorrect: true },
          { itemId: "wu2", text: "The chicken soup is bland.", isCorrect: true },
          { itemId: "wu3", text: "This sauce is flavourful.", isCorrect: true }
        ],
        wrong: [
          { itemId: "wu1", text: "The food is delicious.", isCorrect: true },
          { itemId: "wu2", text: "The chicken soup has no taste.", isCorrect: false },
          { itemId: "wu3", text: "This sauce is flavourful.", isCorrect: true }
        ]
      }
    },
    {
      id: "w3d2-speak-timed",
      sequence: 4,
      archetypeId: "SPEAK_TIMED",
      widget: "speak_timed",
      sectionLabel: "Speaking",
      topic: "Timed Monologue Speech",
      taskIntro: "Describe your favourite meal under time pressure",
      instructions: "Describe your favourite meal in 60 seconds. Talk about its ingredients, its taste, and when you eat it.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      grammarRule: "Describe a meal confidently, using taste words (delicious, savoury) and ingredient vocabulary.",
      targetWords: ["delicious", "ingredients", "savoury", "taste"],
      speakingDurationSeconds: 60,
      prompt: "Describe your favourite meal. Talk about its ingredients, how it tastes, and when you usually eat it.",
      sampleResponse: "My favourite meal is spaghetti carbonara. It is a savoury dish made with simple ingredients like pasta, eggs, cheese, and black pepper. The taste is incredibly delicious and rich. I usually eat it on weekends with my family.",
      answers: {
        correct: [
          {
            itemId: "timed1",
            transcript: "My favourite meal is spaghetti carbonara. It is a savoury dish made with simple ingredients like pasta, eggs, cheese, and black pepper. The taste is incredibly delicious and rich. I usually eat it on weekends with my family.",
            durationSeconds: 22,
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "timed1",
            transcript: "My favourite meal is spaghetti carbonara. It is a good dish made with simple ingredients like pasta, eggs, cheese, and black pepper. The taste is nice. I usually eat it on weekends with my family.",
            durationSeconds: 18,
            isCorrect: false
          }
        ]
      }
    }
  ]
};

const weeklyPlannerImageUrl = `data:image/svg+xml;utf8,${encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 360" role="img" aria-label="Weekly planner calendar showing daily tasks and schedules">
  <rect width="720" height="360" fill="#f8f9fe"/>
  <rect x="0" y="0" width="720" height="52" fill="#4a6cf7" rx="0"/>
  <text x="360" y="32" font-family="Arial, sans-serif" font-size="20" font-weight="800" fill="white" text-anchor="middle">My Weekly Planner</text>
  <text x="360" y="48" font-family="Arial, sans-serif" font-size="11" fill="rgba(255,255,255,0.8)" text-anchor="middle">Mon – Fri schedule</text>

  <!-- Column headers -->
  <rect x="10" y="58" width="138" height="30" fill="#dce3ff" rx="4"/>
  <text x="79" y="78" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#2c3e7c" text-anchor="middle">Monday</text>
  <rect x="154" y="58" width="138" height="30" fill="#dce3ff" rx="4"/>
  <text x="223" y="78" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#2c3e7c" text-anchor="middle">Tuesday</text>
  <rect x="298" y="58" width="138" height="30" fill="#dce3ff" rx="4"/>
  <text x="367" y="78" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#2c3e7c" text-anchor="middle">Wednesday</text>
  <rect x="442" y="58" width="138" height="30" fill="#dce3ff" rx="4"/>
  <text x="511" y="78" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#2c3e7c" text-anchor="middle">Thursday</text>
  <rect x="586" y="58" width="124" height="30" fill="#ffdce3" rx="4"/>
  <text x="648" y="78" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#7c2c3e" text-anchor="middle">Friday</text>

  <!-- Row 1: Morning -->
  <text x="10" y="110" font-family="Arial, sans-serif" font-size="10" font-weight="700" fill="#6b7280">08:00</text>
  <rect x="36" y="96" width="112" height="28" fill="#e0f2fe" rx="6"/>
  <text x="92" y="115" font-family="Arial, sans-serif" font-size="11" fill="#0369a1" text-anchor="middle">Team standup</text>
  <rect x="180" y="96" width="112" height="28" fill="#fef9c3" rx="6"/>
  <text x="236" y="115" font-family="Arial, sans-serif" font-size="11" fill="#854d0e" text-anchor="middle">English class</text>
  <rect x="324" y="96" width="112" height="28" fill="#e0f2fe" rx="6"/>
  <text x="380" y="115" font-family="Arial, sans-serif" font-size="11" fill="#0369a1" text-anchor="middle">Team standup</text>
  <rect x="468" y="96" width="112" height="28" fill="#fef9c3" rx="6"/>
  <text x="524" y="115" font-family="Arial, sans-serif" font-size="11" fill="#854d0e" text-anchor="middle">English class</text>
  <rect x="598" y="96" width="110" height="28" fill="#fce7f3" rx="6"/>
  <text x="653" y="115" font-family="Arial, sans-serif" font-size="11" fill="#9d174d" text-anchor="middle">Weekly review</text>

  <!-- Row 2: Midday -->
  <text x="10" y="152" font-family="Arial, sans-serif" font-size="10" font-weight="700" fill="#6b7280">12:00</text>
  <rect x="36" y="138" width="112" height="28" fill="#f3f4f6" rx="6"/>
  <text x="92" y="157" font-family="Arial, sans-serif" font-size="11" fill="#374151" text-anchor="middle">Lunch break</text>
  <rect x="180" y="138" width="112" height="28" fill="#f3f4f6" rx="6"/>
  <text x="236" y="157" font-family="Arial, sans-serif" font-size="11" fill="#374151" text-anchor="middle">Lunch break</text>
  <rect x="324" y="138" width="112" height="28" fill="#f3f4f6" rx="6"/>
  <text x="380" y="157" font-family="Arial, sans-serif" font-size="11" fill="#374151" text-anchor="middle">Lunch break</text>
  <rect x="468" y="138" width="112" height="28" fill="#f3f4f6" rx="6"/>
  <text x="524" y="157" font-family="Arial, sans-serif" font-size="11" fill="#374151" text-anchor="middle">Lunch break</text>
  <rect x="598" y="138" width="110" height="28" fill="#f3f4f6" rx="6"/>
  <text x="653" y="157" font-family="Arial, sans-serif" font-size="11" fill="#374151" text-anchor="middle">Lunch break</text>

  <!-- Row 3: Afternoon -->
  <text x="10" y="194" font-family="Arial, sans-serif" font-size="10" font-weight="700" fill="#6b7280">14:00</text>
  <rect x="36" y="180" width="112" height="28" fill="#dcfce7" rx="6"/>
  <text x="92" y="199" font-family="Arial, sans-serif" font-size="11" fill="#166534" text-anchor="middle">Project work</text>
  <rect x="180" y="180" width="112" height="28" fill="#dcfce7" rx="6"/>
  <text x="236" y="199" font-family="Arial, sans-serif" font-size="11" fill="#166534" text-anchor="middle">Report writing</text>
  <rect x="324" y="180" width="112" height="28" fill="#dcfce7" rx="6"/>
  <text x="380" y="199" font-family="Arial, sans-serif" font-size="11" fill="#166534" text-anchor="middle">Client meeting</text>
  <rect x="468" y="180" width="112" height="28" fill="#dcfce7" rx="6"/>
  <text x="524" y="199" font-family="Arial, sans-serif" font-size="11" fill="#166534" text-anchor="middle">Quarterly report</text>
  <rect x="598" y="180" width="110" height="28" fill="#fce7f3" rx="6"/>
  <text x="653" y="199" font-family="Arial, sans-serif" font-size="11" fill="#9d174d" text-anchor="middle">Early finish</text>

  <!-- Row 4: Labels -->
  <text x="10" y="236" font-family="Arial, sans-serif" font-size="10" font-weight="700" fill="#6b7280">17:00</text>
  <rect x="36" y="222" width="112" height="28" fill="#fef3c7" rx="6"/>
  <text x="92" y="241" font-family="Arial, sans-serif" font-size="11" fill="#92400e" text-anchor="middle">Daily wrap-up</text>
  <rect x="180" y="222" width="112" height="28" fill="#fef3c7" rx="6"/>
  <text x="236" y="241" font-family="Arial, sans-serif" font-size="11" fill="#92400e" text-anchor="middle">Daily wrap-up</text>
  <rect x="324" y="222" width="112" height="28" fill="#fef3c7" rx="6"/>
  <text x="380" y="241" font-family="Arial, sans-serif" font-size="11" fill="#92400e" text-anchor="middle">Daily wrap-up</text>
  <rect x="468" y="222" width="112" height="28" fill="#fef3c7" rx="6"/>
  <text x="524" y="241" font-family="Arial, sans-serif" font-size="11" fill="#92400e" text-anchor="middle">Deadline review</text>
  <rect x="598" y="222" width="110" height="28" fill="#fce7f3" rx="6"/>
  <text x="653" y="241" font-family="Arial, sans-serif" font-size="11" fill="#9d174d" text-anchor="middle">Weekend plans</text>

  <!-- Legend -->
  <rect x="10" y="270" width="700" height="1" fill="#e5e7eb"/>
  <text x="10" y="292" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="#6b7280">Key words to describe this planner:</text>
  <rect x="10" y="302" width="90" height="22" fill="#4a6cf7" rx="11"/>
  <text x="55" y="317" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="white" text-anchor="middle">daily</text>
  <rect x="110" y="302" width="90" height="22" fill="#4a6cf7" rx="11"/>
  <text x="155" y="317" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="white" text-anchor="middle">weekly</text>
  <rect x="210" y="302" width="110" height="22" fill="#4a6cf7" rx="11"/>
  <text x="265" y="317" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="white" text-anchor="middle">fortnightly</text>
  <rect x="330" y="302" width="110" height="22" fill="#4a6cf7" rx="11"/>
  <text x="385" y="317" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="white" text-anchor="middle">quarterly</text>
  <rect x="450" y="302" width="110" height="22" fill="#e74c3c" rx="11"/>
  <text x="505" y="317" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="white" text-anchor="middle">deadline</text>
  <rect x="570" y="302" width="140" height="22" fill="#4a6cf7" rx="11"/>
  <text x="640" y="317" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="white" text-anchor="middle">occasionally</text>

  <rect x="10" y="336" width="700" height="14" fill="#f3f4f6" rx="4"/>
  <text x="360" y="347" font-family="Arial, sans-serif" font-size="10" fill="#9ca3af" text-anchor="middle">Describe what you see using time vocabulary</text>
</svg>
`)}`;                    

const weekThreeDayFiveTasks: TaskDayData = {
  dayId: "day_24_03_05",
  tasks: [
    {
      id: "w3d5-read-word-match",
      sequence: 1,
      archetypeId: "READ_WORD_MATCH",
      widget: "read_word_match",
      sectionLabel: "Reading",
      topic: "Time & Schedule Vocabulary",
      taskIntro: "Match time words to their meanings",
      instructions: "Match each time word (fortnightly, quarterly, deadline, occasionally) to its correct meaning.",
      subSkill: "Vocabulary",
      activity: "Read",
      estimatedMinutes: 3,
      grammarRule: "Learn precise time-frequency words: fortnightly (every 2 weeks), quarterly (4 times a year), deadline (the latest time to finish), occasionally (sometimes, not often).",
      options: ["fortnightly", "quarterly", "deadline", "occasionally"],
      items: [
        {
          itemId: "twm1",
          prompt: "Happening every two weeks.",
          correctAnswer: "fortnightly",
          explanation: "Fortnightly means once every two weeks, or every fortnight.",
        },
        {
          itemId: "twm2",
          prompt: "Happening four times a year, every three months.",
          correctAnswer: "quarterly",
          explanation: "Quarterly means once every quarter, which is every three months.",
        },
        {
          itemId: "twm3",
          prompt: "The latest time by which something must be completed.",
          correctAnswer: "deadline",
          explanation: "A deadline is the fixed time or date by which a task must be done.",
        },
        {
          itemId: "twm4",
          prompt: "Sometimes, but not very often or regularly.",
          correctAnswer: "occasionally",
          explanation: "Occasionally means from time to time, but not on a fixed schedule.",
        },
      ],
      answers: {
        correct: { twm1: "fortnightly", twm2: "quarterly", twm3: "deadline", twm4: "occasionally" },
        wrong: { twm1: "quarterly", twm2: "quarterly", twm3: "deadline", twm4: "occasionally" },
      },
    },
    {
      id: "w3d5-listen-mcq",
      sequence: 2,
      archetypeId: "LISTEN_MCQ",
      widget: "listen_mcq",
      sectionLabel: "Listening",
      topic: "Planning the Week",
      taskIntro: "Listen to someone plan their week",
      instructions: "Listen to the audio of someone planning their week and answer the questions below.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 3,
      audioGenre: "Weekly planning monologue",
      audioScript: "Right, let me go through my week. I check my emails daily, every single morning. My team meets fortnightly, so our next one is in two weeks. I have a project deadline on Thursday, so I need to finish the report by then. I only go to the gym occasionally — maybe once or twice a month. And we have our quarterly strategy meeting next Monday to review the last three months.",
      audioDurationSeconds: 42,
      innerWidget: "mcq",
      items: [
        {
          itemId: "pm1",
          prompt: "How often does the speaker check emails?",
          options: ["Weekly", "Daily", "Fortnightly", "Occasionally"],
          correctIndex: 1,
          explanation: "The speaker says 'I check my emails daily, every single morning'.",
        },
        {
          itemId: "pm2",
          prompt: "When is the project deadline?",
          options: ["Monday", "Wednesday", "Thursday", "Friday"],
          correctIndex: 2,
          explanation: "The speaker says 'I have a project deadline on Thursday'.",
        },
        {
          itemId: "pm3",
          prompt: "How often does the speaker go to the gym?",
          options: ["Daily", "Weekly", "Fortnightly", "Occasionally"],
          correctIndex: 3,
          explanation: "The speaker says 'I only go to the gym occasionally — maybe once or twice a month'.",
        },
      ],
      answers: {
        correct: { pm1: 1, pm2: 2, pm3: 3 },
        wrong: { pm1: 1, pm2: 0, pm3: 3 },
      },
    },
    {
      id: "w3d5-write-sent-trans",
      sequence: 3,
      archetypeId: "WRITE_SENT_TRANS",
      widget: "sentence_transform",
      sectionLabel: "Writing",
      topic: "Time expression sentence transformation",
      taskIntro: "Transform sentences using precise time vocabulary",
      instructions: "Rewrite the sentence using the correct time word from the options given.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 4,
      grammarRule: "Replace informal phrases like 'I do this every day' or 'sometimes' with precise adverbs: daily, weekly, occasionally.",
      items: [
        {
          itemId: "st1",
          sourceSentence: "I do this every day.",
          sampleAnswer: "I do this daily.",
          watchHints: ["daily"],
        },
        {
          itemId: "st2",
          sourceSentence: "We have a meeting every week.",
          sampleAnswer: "We have a meeting weekly.",
          watchHints: ["weekly"],
        },
        {
          itemId: "st3",
          sourceSentence: "She goes to the cinema sometimes, not very often.",
          sampleAnswer: "She goes to the cinema occasionally.",
          watchHints: ["occasionally"],
        },
      ],
      answers: {
        correct: [
          { itemId: "st1", text: "I do this daily.", isCorrect: true },
          { itemId: "st2", text: "We have a meeting weekly.", isCorrect: true },
          { itemId: "st3", text: "She goes to the cinema occasionally.", isCorrect: true },
        ],
        wrong: [
          { itemId: "st1", text: "I do this daily.", isCorrect: true },
          { itemId: "st2", text: "We have a meeting every week.", isCorrect: false },
          { itemId: "st3", text: "She goes to the cinema occasionally.", isCorrect: true },
        ],
      },
    },
    {
      id: "w3d5-speak-pic-desc",
      sequence: 4,
      archetypeId: "SPEAK_PIC_DESC",
      widget: "speak_pic_desc",
      sectionLabel: "Speaking",
      topic: "Describe a weekly planner",
      taskIntro: "Describe what you see using time vocabulary",
      instructions: "Look at the weekly planner and describe what you see using time vocabulary: daily, weekly, fortnightly, quarterly, deadline, occasionally.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      imageUrl: weeklyPlannerImageUrl,
      imageAlt: "A weekly planner showing Monday to Friday with daily standup meetings, a Thursday deadline, quarterly strategy review, and occasional gym sessions.",
      grammarRule: "Use time-frequency words to describe how often events appear in the planner: daily, weekly, occasionally.",
      speakingDurationSeconds: 45,
      answers: {
        correct: [
          {
            itemId: "wkpic",
            transcript: "I can see a weekly planner for Monday to Friday. There is a daily team standup in the morning. On Thursday there is a deadline for a project report. The strategy meeting happens quarterly. The daily wrap-up appears every afternoon.",
            durationSeconds: 20,
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "wkpic",
            transcript: "I can see a weekly planner for Monday to Friday. There is a team standup every morning. On Friday there is a deadline. The strategy meeting is weekly. The wrap-up appears every day.",
            durationSeconds: 16,
            isCorrect: false,
          },
        ],
      },
    },
  ],
};

const weekThreeDayFourTasks: TaskDayData = {
  dayId: "day_24_03_04",
  tasks: [
    {
      id: "w3d4-read-context-mcq",
      sequence: 1,
      archetypeId: "READ_CONTEXT_MCQ",
      widget: "read_comp_mcq",
      sectionLabel: "Reading",
      topic: "Job Advertisements",
      taskIntro: "Infer word meaning from a job ad",
      instructions: "Read the short job advertisement and answer the question below.",
      subSkill: "Vocabulary",
      activity: "Read",
      estimatedMinutes: 3,
      passageTitle: "Job Opening: Office Manager",
      passage: "We are looking for an experienced office manager. The successful candidate will be responsible for organising meetings, managing a small team of five, and ensuring the office runs smoothly every day.",
      grammarRule: "Infer meaning from context: 'responsible for' means 'in charge of' or 'must take care of'.",
      items: [
        {
          itemId: "rc1",
          prompt: "What does 'responsible for' mean in this job ad?",
          options: [
            "Interested in doing something",
            "In charge of or must take care of",
            "Allowed to do something",
            "Finished with a task"
          ],
          correctIndex: 1,
          explanation: "'Responsible for' means the person must take care of those duties: organising meetings, managing a team, and keeping the office running."
        }
      ],
      answers: {
        correct: { rc1: 1 },
        wrong: { rc1: 0 }
      }
    },
    {
      id: "w3d4-listen-dictation",
      sequence: 2,
      archetypeId: "LISTEN_DICTATION",
      widget: "listen_dictation",
      sectionLabel: "Listening",
      topic: "Job Description",
      taskIntro: "Type the job description you hear",
      instructions: "Listen to the short job description and type the exact sentence.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 4,
      audioGenre: "Short job description",
      audioScript: "She works as a receptionist at a busy hotel and manages all guest check-ins every morning.",
      audioDurationSeconds: 14,
      grammarRule: "Listen closely for job title nouns and workplace action verbs like 'works as' and 'manages'.",
      targetWords: ["receptionist", "hotel", "manages", "check-ins"],
      items: [
        {
          itemId: "ld1",
          prompt: "Type the exact job description you hear.",
          correctAnswer: "She works as a receptionist at a busy hotel and manages all guest check-ins every morning.",
          explanation: "The speaker describes a receptionist who 'works as' and 'manages' guest check-ins at a hotel."
        }
      ],
      answers: {
        correct: {
          ld1: "She works as a receptionist at a busy hotel and manages all guest check-ins every morning."
        },
        wrong: {
          ld1: "She works as a receptionist at a busy hotel and handles all guest check-ins every morning."
        }
      }
    },
    {
      id: "w3d4-write-paraphrase",
      sequence: 3,
      archetypeId: "WRITE_PARAPHRASE",
      widget: "write_paraphrase",
      sectionLabel: "Writing",
      topic: "Rewrite with job vocabulary",
      taskIntro: "Rewrite sentences using new work words",
      instructions: "Rewrite each sentence using job-related vocabulary to make it more precise and professional.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 5,
      grammarRule: "Keep the meaning the same, but use more precise job-related vocabulary and varied sentence structures.",
      items: [
        {
          itemId: "rewrite1",
          incorrectSentence: "He works in an office.",
          sampleAnswer: "He is employed as an office assistant.",
          watchHints: ["employed", "office assistant"],
        },
        {
          itemId: "rewrite2",
          incorrectSentence: "She tells people what to do at work.",
          sampleAnswer: "She manages a team at the workplace.",
          watchHints: ["manages", "team", "workplace"],
        },
      ],
      answers: {
        correct: [
          {
            itemId: "rewrite1",
            text: "He is employed as an office assistant.",
            isCorrect: true,
          },
          {
            itemId: "rewrite2",
            text: "She manages a team at the workplace.",
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "rewrite1",
            text: "He is employed as an office assistant.",
            isCorrect: true,
          },
          {
            itemId: "rewrite2",
            text: "She tells the team what to do at the workplace.",
            isCorrect: false,
          },
        ],
      },
    },
    {
      id: "w3d4-speak-timed",
      sequence: 4,
      archetypeId: "SPEAK_TIMED",
      widget: "speak_timed",
      sectionLabel: "Speaking",
      topic: "Timed Job Description Speech",
      taskIntro: "Talk about a job you know for 60 seconds",
      instructions: "Describe a job you know well. Talk about what the person does, where they work, and why the job is important.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      grammarRule: "Describe a job confidently using workplace vocabulary like manager, responsible for, and works in.",
      targetWords: ["manager", "responsible for", "works in", "team"],
      speakingDurationSeconds: 60,
      prompt: "Talk about a job you know. Describe what the person does, where they work, and why the job is important.",
      sampleResponse: "My mother is a manager at a small company. She works in an office and is responsible for organising meetings and leading a team of ten people. The job is important because she helps everyone stay organised and finish their work on time.",
      answers: {
        correct: [
          {
            itemId: "timed1",
            transcript: "My mother is a manager at a small company. She works in an office and is responsible for organising meetings and leading a team of ten people. The job is important because she helps everyone stay organised and finish their work on time.",
            durationSeconds: 24,
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "timed1",
            transcript: "My mother is a manager at a small company. She works in an office and she does meetings and leads people. The job is important because she helps everyone do their work.",
            durationSeconds: 18,
            isCorrect: false
          }
        ]
      }
    }
  ]
};

const weekThreeDaySixTasks: TaskDayData = {
  dayId: "day_24_03_06",
  tasks: [
    {
      id: "w3d6-read-context-mcq",
      sequence: 1,
      archetypeId: "READ_CONTEXT_MCQ",
      widget: "read_context_mcq",
      sectionLabel: "Reading task",
      topic: "Infer emotions from context",
      taskIntro: "Read the diary entry and infer the emotions",
      instructions: "Choose the correct emotion based on the context in the passage.",
      subSkill: "Vocabulary",
      activity: "Read",
      estimatedMinutes: 3,
      passageTitle: "A Saturday to Remember",
      passage: "It was a strange Saturday. In the morning, I finally finished my big project after weeks of stress, and sitting on the balcony with my tea, I felt completely content. But by afternoon, my friend called to say she couldn't make it to our concert because she was sick. We had been planning this for months, and I was so looking forward to it. I sat on my bed, feeling quite disappointed. To make matters worse, I later realized I had lost my expensive phone on the train. I searched everywhere but couldn't find it. The day ended with me feeling utterly devastated.",
      grammarRule: "Use context clues to understand the exact emotion a person is feeling. 'Content' means peaceful and satisfied. 'Disappointed' means sad because something didn't happen. 'Devastated' means extremely sad and shocked.",
      items: [
        {
          itemId: "q1",
          prompt: "How did the writer feel in the morning?",
          options: ["Overwhelmed", "Content", "Devastated", "Angry"],
          correctIndex: 1,
          explanation: "The writer says 'sitting on the balcony with my tea, I felt completely content' after finishing a stressful project.",
        },
        {
          itemId: "q2",
          prompt: "What does 'disappointed' mean in the context of the afternoon?",
          options: ["Excited for the future", "Scared of being alone", "Sad that the concert plan was cancelled", "Happy to stay home"],
          correctIndex: 2,
          explanation: "The writer was disappointed because her friend couldn't make it to the concert they planned for months.",
        },
        {
          itemId: "q3",
          prompt: "Why did the writer feel 'devastated' at the end of the day?",
          options: ["Because of the project", "Because of the concert", "Because it was raining", "Because of losing the expensive phone"],
          correctIndex: 3,
          explanation: "The writer felt devastated after realizing she lost her expensive phone and couldn't find it.",
        }
      ],
      answers: {
        correct: { q1: 1, q2: 2, q3: 3 },
        wrong: { q1: 1, q2: 1, q3: 3 },
      },
    },
    {
      id: "w3d6-listen-dictation",
      sequence: 2,
      archetypeId: "LISTEN_DICTATION",
      widget: "listen_dictation",
      sectionLabel: "Listening task",
      topic: "Dictate emotion words",
      taskIntro: "Listen and write the emotion words",
      instructions: "Listen to the descriptions and write the exact emotion word you hear.",
      subSkill: "Vocabulary",
      activity: "Listen",
      estimatedMinutes: 4,
      audioGenre: "Short personal description",
      audioDurationSeconds: 45,
      audioScript: "When I saw the amount of work I had to do by tomorrow, I felt completely overwhelmed. I just didn't know where to start. Then, when I tried to get help and nobody answered my calls, I felt quite disheartened. But finally, I managed to finish one small task, and that made me feel a bit better.",
      grammarRule: "Listen carefully for the spelling of abstract emotion words like overwhelmed and disheartened.",
      targetWords: ["overwhelmed", "disheartened"],
      items: [
        {
          itemId: "d1",
          prompt: "When I saw the amount of work, I felt completely ___.",
          correctAnswer: "overwhelmed",
          explanation: "The speaker says 'I felt completely overwhelmed'.",
        },
        {
          itemId: "d2",
          prompt: "When nobody answered my calls, I felt quite ___.",
          correctAnswer: "disheartened",
          explanation: "The speaker says 'I felt quite disheartened'.",
        }
      ],
      answers: {
        correct: { d1: "overwhelmed", d2: "disheartened" },
        wrong: { d1: "overwelemed", d2: "disheartened" },
      },
    },
    {
      id: "w3d6-write-word-upgrade",
      sequence: 3,
      archetypeId: "WRITE_WORD_UPGRADE",
      widget: "write_word_upgrade",
      sectionLabel: "Writing task",
      topic: "Upgrade emotion vocabulary",
      taskIntro: "Upgrade simple emotions to stronger words",
      instructions: "Rewrite the sentence by replacing the simple emotion word with the target upgrade word.",
      subSkill: "Vocabulary",
      activity: "Write",
      estimatedMinutes: 5,
      grammarRule: "Use advanced vocabulary to express inner states more precisely. Replace 'sad' with 'devastated', 'disappointed', or 'disheartened'. Replace 'stressed' with 'overwhelmed'.",
      items: [
        {
          itemId: "w1",
          sourceSentence: "I was very sad when I lost my job.",
          targetUpgradeWord: "devastated",
          sampleAnswer: "I was devastated when I lost my job.",
          watchHints: ["Replace 'very sad' with 'devastated'."],
        },
        {
          itemId: "w2",
          sourceSentence: "She felt stressed by all the homework.",
          targetUpgradeWord: "overwhelmed",
          sampleAnswer: "She felt overwhelmed by all the homework.",
          watchHints: ["Replace 'stressed' with 'overwhelmed'."],
        },
        {
          itemId: "w3",
          sourceSentence: "We were sad that the park was closed.",
          targetUpgradeWord: "disappointed",
          sampleAnswer: "We were disappointed that the park was closed.",
          watchHints: ["Replace 'sad' with 'disappointed'."],
        }
      ],
      answers: {
        correct: [
          { itemId: "w1", text: "I was devastated when I lost my job.", isCorrect: true },
          { itemId: "w2", text: "She felt overwhelmed by all the homework.", isCorrect: true },
          { itemId: "w3", text: "We were disappointed that the park was closed.", isCorrect: true },
        ],
        wrong: [
          { itemId: "w1", text: "I was devastated when I lost my job.", isCorrect: true },
          { itemId: "w2", text: "She felt stress by all the homework.", isCorrect: false },
          { itemId: "w3", text: "We were disappointed that the park was closed.", isCorrect: true },
        ],
      },
    },
    {
      id: "w3d6-speak-timed",
      sequence: 4,
      archetypeId: "SPEAK_TIMED",
      widget: "speak_timed",
      sectionLabel: "Speaking task",
      topic: "Talk about your feelings",
      taskIntro: "Reflect on your week",
      instructions: "Talk about how you felt today or this week. Use at least one strong emotion word like content, overwhelmed, or disappointed.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      grammarRule: "Express inner states naturally and explain why you felt that way.",
      targetWords: ["content", "overwhelmed", "disappointed", "devastated", "disheartened"],
      speakingDurationSeconds: 45,
      prompt: "Talk about how you felt today or this week.",
      sampleResponse: "This week I felt quite overwhelmed because I had a lot of work to do. But today is Saturday, and I am relaxing at home, so I feel very content.",
      answers: {
        correct: [
          { itemId: "prompt_1", transcript: "This week I felt quite overwhelmed because I had a lot of work to do. But today is Saturday, and I am relaxing at home, so I feel very content.", durationSeconds: 12, isCorrect: true },
        ],
        wrong: [
          { itemId: "prompt_1", transcript: "This week I feel bad because much work.", durationSeconds: 5, isCorrect: false },
        ],
      },
    },
  ],
};


const cityStreetImageUrl = `data:image/svg+xml;utf8,${encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 360" role="img" aria-label="A city street map with a market and a station">
  <rect width="720" height="360" fill="#fdfcf7"/>
  <rect x="0" y="240" width="720" height="120" fill="#e2f0d9"/>
  <rect x="100" y="220" width="520" height="40" fill="#d0d0d0"/>
  <text x="360" y="50" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="#2c5e3b" text-anchor="middle">My Neighbourhood</text>
  
  <g transform="translate(180, 160)">
    <rect x="-40" y="-40" width="80" height="60" fill="#fff2cc" stroke="#bf9000" stroke-width="3"/>
    <text x="0" y="-10" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#7f6000" text-anchor="middle">Market</text>
  </g>

  <g transform="translate(360, 160)">
    <rect x="-40" y="-50" width="80" height="70" fill="#fce4d6" stroke="#c65911" stroke-width="3"/>
    <text x="0" y="-10" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#833c0c" text-anchor="middle">Station</text>
  </g>

  <g transform="translate(540, 160)">
    <rect x="-40" y="-40" width="80" height="60" fill="#d9ebd3" stroke="#2e7d32" stroke-width="3"/>
    <text x="0" y="-10" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#1b5e20" text-anchor="middle">Suburb</text>
  </g>
</svg>
`)}`;


const weekThreeDayThreeTasks: TaskDayData = {
  dayId: "day_24_03_03",
  tasks: [
    {
      id: "w3d3-read-word-match",
      sequence: 1,
      archetypeId: "READ_WORD_MATCH",
      widget: "read_word_match",
      sectionLabel: "Reading",
      topic: "Places & Locations",
      taskIntro: "Match vocabulary to their definitions",
      instructions: "Match each place word (market, station, suburb, city) with its correct definition.",
      subSkill: "Vocabulary",
      activity: "Read",
      estimatedMinutes: 3,
      grammarRule: "Learn words for places and locations: market, station, suburb, city.",
      options: ["market", "station", "suburb", "city"],
      items: [
        {
          itemId: "wm1",
          prompt: "A place where you can buy fresh food and vegetables.",
          correctAnswer: "market",
          explanation: "A market is an open area or building where people buy and sell goods.",
        },
        {
          itemId: "wm2",
          prompt: "A place where you go to catch a train or bus.",
          correctAnswer: "station",
          explanation: "A station is a place where trains or buses stop for passengers.",
        },
        {
          itemId: "wm3",
          prompt: "A quiet residential area outside the centre of a city.",
          correctAnswer: "suburb",
          explanation: "A suburb is an area on the edge of a city where people live.",
        },
        {
          itemId: "wm4",
          prompt: "A large and busy place where many people live and work.",
          correctAnswer: "city",
          explanation: "A city is a large, important town.",
        },
      ],
      answers: {
        correct: { wm1: "market", wm2: "station", wm3: "suburb", wm4: "city" },
        wrong: { wm1: "market", wm2: "city", wm3: "suburb", wm4: "city" },
      },
    },
    {
      id: "w3d3-listen-mcq",
      sequence: 2,
      archetypeId: "LISTEN_MCQ",
      widget: "listen_mcq",
      sectionLabel: "Listening",
      topic: "Neighbourhood description",
      taskIntro: "Listen to a description of a neighbourhood",
      instructions: "Listen to the audio and answer the questions about the location.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 3,
      audioGenre: "Neighbourhood description",
      audioScript: "I live in a quiet suburb just outside the city. It's very convenient because there is a large market where I buy fresh fruit and vegetables. To get to work, I just walk to the station, which is only five minutes away.",
      audioDurationSeconds: 24,
      innerWidget: "mcq",
      items: [
        {
          itemId: "l1",
          prompt: "Where does the speaker live?",
          options: ["In the city centre", "In a quiet suburb", "Near a farm", "Next to the office"],
          correctIndex: 1,
          explanation: "The speaker says, 'I live in a quiet suburb just outside the city.'",
        },
        {
          itemId: "l2",
          prompt: "What does the speaker buy at the market?",
          options: ["Clothes and shoes", "Fresh fruit and vegetables", "Books and magazines", "Tickets"],
          correctIndex: 1,
          explanation: "The speaker says, 'there is a large market where I buy fresh fruit and vegetables.'",
        },
        {
          itemId: "l3",
          prompt: "How does the speaker travel to work?",
          options: ["By driving a car", "By walking to the station", "By taking a taxi", "By riding a bicycle"],
          correctIndex: 1,
          explanation: "The speaker says, 'To get to work, I just walk to the station'.",
        },
      ],
      answers: {
        correct: { l1: 1, l2: 1, l3: 1 },
        wrong: { l1: 1, l2: 0, l3: 1 },
      },
    },
    {
      id: "w3d3-write-para",
      sequence: 3,
      archetypeId: "WRITE_PARA",
      widget: "write_paragraph",
      sectionLabel: "Writing",
      topic: "Describe your area",
      taskIntro: "Write about your neighbourhood",
      instructions: "Write 3-4 sentences about the area where you live. Use the words 'market' and 'station'.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 5,
      prompt: "Describe your neighbourhood in 3 to 4 sentences. Include the words 'market' and 'station'.",
      grammarRule: "Use simple present tense to describe places that exist now. E.g., 'There is a market near my house.'",
      targetWords: ["market", "station", "live", "near"],
      minimumWords: 20,
      sampleAnswer: "I live in a nice area. There is a large market near my home. I go to the station every day to take the train to work.",
      answerHints: [
        "Say where you live.",
        "Mention the market.",
        "Mention the station.",
        "Use simple sentences.",
      ],
      answers: {
        correct: [
          {
            itemId: "para",
            text: "I live in a very beautiful suburb. There is a market near my house where we buy food. I walk to the station every morning.",
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "para",
            text: "I live in a very beautiful suburb. There are market near my house. I walk to station morning.",
            isCorrect: false,
          },
        ],
      },
    },
    {
      id: "w3d3-speak-pic-desc",
      sequence: 4,
      archetypeId: "SPEAK_PIC_DESC",
      widget: "speak_pic_desc",
      sectionLabel: "Speaking",
      topic: "Describe a city map",
      taskIntro: "Describe the places on the map",
      instructions: "Look at the map and describe what you see. Use words like market, station, and suburb.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      imageUrl: cityStreetImageUrl,
      imageAlt: "A city map showing a market, a station, and a suburb.",
      grammarRule: "Use 'There is' or 'I can see' to describe what is in the picture.",
      speakingDurationSeconds: 45,
      answers: {
        correct: [
          {
            itemId: "picdesc",
            transcript: "In this map, I can see a market on the left. In the middle, there is a station. On the right, there is a suburb area.",
            durationSeconds: 12,
            isCorrect: true,
          },
        ],
        wrong: [
          {
            itemId: "picdesc",
            transcript: "In this map, I can see a market on the left. In middle, station. On right, suburb area.",
            durationSeconds: 10,
            isCorrect: false,
          },
        ],
      },
    },
  ],
};

const weekThreeDaySevenTasks: TaskDayData = {
  dayId: "day_24_03_07",
  tasks: [
    {
      id: "w3d7-read-word-match",
      sequence: 1,
      archetypeId: "READ_WORD_MATCH",
      widget: "read_word_match",
      sectionLabel: "Reading",
      topic: "Weekly Review Match",
      taskIntro: "Consolidate the week's vocabulary",
      instructions: "Match each word from this week (colleague, savoury, suburb, manager, deadline, content) to its correct definition.",
      subSkill: "Vocabulary",
      activity: "Read",
      estimatedMinutes: 4,
      grammarRule: "Review vocabulary across all 6 topic areas covered this week.",
      options: ["colleague", "savoury", "suburb", "manager", "deadline", "content"],
      items: [
        {
          itemId: "rm1",
          prompt: "Someone you work with in a profession or business.",
          correctAnswer: "colleague",
          explanation: "A colleague is a person you work with.",
        },
        {
          itemId: "rm2",
          prompt: "Food that is salty or spicy, not sweet.",
          correctAnswer: "savoury",
          explanation: "Savoury describes food that has a salty or spicy flavour.",
        },
        {
          itemId: "rm3",
          prompt: "A residential area on the edge of a city.",
          correctAnswer: "suburb",
          explanation: "A suburb is a quiet area outside the city centre.",
        },
        {
          itemId: "rm4",
          prompt: "A person responsible for controlling or administering a company or team.",
          correctAnswer: "manager",
          explanation: "A manager leads a team or department.",
        },
        {
          itemId: "rm5",
          prompt: "The latest time or date by which something should be completed.",
          correctAnswer: "deadline",
          explanation: "A deadline is the time when a task must be finished.",
        },
        {
          itemId: "rm6",
          prompt: "In a state of peaceful happiness and satisfaction.",
          correctAnswer: "content",
          explanation: "Being content means feeling satisfied and at peace.",
        }
      ],
      answers: {
        correct: { rm1: "colleague", rm2: "savoury", rm3: "suburb", rm4: "manager", rm5: "deadline", rm6: "content" },
        wrong: { rm1: "manager", rm2: "savoury", rm3: "suburb", rm4: "colleague", rm5: "deadline", rm6: "content" },
      },
    },
    {
      id: "w3d7-listen-mcq",
      sequence: 2,
      archetypeId: "LISTEN_MCQ",
      widget: "listen_mcq",
      sectionLabel: "Listening",
      topic: "Weekend consolidation story",
      taskIntro: "Listen to a short story using week's vocabulary",
      instructions: "Listen to the short story that uses vocabulary from all 6 topics, then answer the questions.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 4,
      audioGenre: "Short personal story",
      audioScript: "My colleague invited me to a savoury dinner at a new restaurant in the suburb. Our manager had just given us a tight deadline for a big project, so we were feeling quite overwhelmed. But after the delicious meal and good conversation, we both felt very content.",
      audioDurationSeconds: 28,
      innerWidget: "mcq",
      items: [
        {
          itemId: "lm1",
          prompt: "Where did the speaker and their colleague go for dinner?",
          options: ["In the city centre", "In the suburb", "At the office", "At a market"],
          correctIndex: 1,
          explanation: "The speaker says they went to a new restaurant 'in the suburb'.",
        },
        {
          itemId: "lm2",
          prompt: "Why were they feeling overwhelmed before the dinner?",
          options: ["Because of a tight deadline", "Because the food was bad", "Because they lost their phone", "Because they were sick"],
          correctIndex: 0,
          explanation: "The manager had just given them a 'tight deadline' for a big project.",
        },
        {
          itemId: "lm3",
          prompt: "How did they feel after the meal?",
          options: ["Devastated", "Disappointed", "Content", "Overwhelmed"],
          correctIndex: 2,
          explanation: "The speaker says 'we both felt very content'.",
        },
      ],
      answers: {
        correct: { lm1: 1, lm2: 0, lm3: 2 },
        wrong: { lm1: 1, lm2: 1, lm3: 2 },
      },
    },
    {
      id: "w3d7-write-para",
      sequence: 3,
      archetypeId: "WRITE_PARA",
      widget: "write_paragraph",
      sectionLabel: "Writing",
      topic: "Free recall writing",
      taskIntro: "Write a short paragraph using this week's words",
      instructions: "Write a short paragraph (3-5 sentences) on any topic you like. Try to use at least 5 words you learned this week (e.g. colleague, manager, suburb, content, deadline).",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 6,
      prompt: "Write a short paragraph on any topic. Use at least 5 new words from this week.",
      grammarRule: "Open creative recall. Focus on integrating new vocabulary smoothly into sentences.",
      targetWords: ["colleague", "manager", "suburb", "content", "deadline", "overwhelmed", "savoury", "market"],
      minimumWords: 25,
      sampleAnswer: "My colleague and I live in the same suburb. Yesterday, our manager gave us a new deadline. We felt a bit overwhelmed, but we are content now.",
      answerHints: [
        "Choose any topic (e.g. work, a weekend).",
        "Include 5 words from the week.",
        "Write 3-5 sentences.",
      ],
      answers: {
        correct: [
          {
            itemId: "wp1",
            text: "My colleague and I work hard. Our manager is very strict about every deadline. However, since I live in a quiet suburb, I feel content when I go home.",
            isCorrect: true,
          }
        ],
        wrong: [
          {
            itemId: "wp1",
            text: "My colleague is good.",
            isCorrect: false,
          }
        ]
      }
    },
    {
      id: "w3d7-speak-timed",
      sequence: 4,
      archetypeId: "SPEAK_TIMED",
      widget: "speak_timed",
      sectionLabel: "Speaking",
      topic: "Playful end-of-week recall challenge",
      taskIntro: "Use as many new words as you can in 90 seconds",
      instructions: "Talk for up to 90 seconds on any topic. Try to use as many vocabulary words from this week as you can.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 5,
      grammarRule: "Fluency challenge: recall and use new vocabulary in spontaneous speech.",
      targetWords: ["colleague", "manager", "suburb", "content", "deadline", "overwhelmed", "savoury", "market", "station", "devastated"],
      speakingDurationSeconds: 90,
      prompt: "Use as many new words as you can in 90 seconds on any topic.",
      sampleResponse: "This week at work, my manager gave me a strict deadline. I felt a bit overwhelmed. But my colleague helped me finish. After work, I walked to the station and took a train to the suburb where I live. I cooked a savoury meal and felt very content.",
      answers: {
        correct: [
          {
            itemId: "st1",
            transcript: "This week at work, my manager gave me a strict deadline. I felt a bit overwhelmed. But my colleague helped me finish. After work, I walked to the station and took a train to the suburb where I live. I cooked a savoury meal and felt very content.",
            durationSeconds: 30,
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "st1",
            transcript: "I work with my manager. The deadline is tomorrow.",
            durationSeconds: 15,
            isCorrect: false
          }
        ]
      }
    }
  ]
};

const weekFourDayOneTasks: TaskDayData = {
  dayId: "day_24_04_01",
  tasks: [
    {
      id: "w4d1-read-mcq",
      sequence: 1,
      archetypeId: "READ_COMP_MCQ",
      widget: "read_comp_mcq",
      sectionLabel: "Reading",
      topic: "Overcoming fear story",
      taskIntro: "Read about Maya's step forward",
      instructions: "Read the story of Maya finding her courage, then answer the questions.",
      subSkill: "Comprehension",
      activity: "Read",
      estimatedMinutes: 4,
      passageTitle: "Maya's Step Forward",
      passage: "Maya always sat at the back of the classroom. Her heart would race whenever the teacher asked a question. She was terrified of making a mistake in front of everyone. One day, the teacher asked for a volunteer to share a short story. Maya felt the familiar panic, but she took a deep breath and raised her hand. When she stood up and began speaking, her voice trembled at first. But as she continued, she realized that everyone was listening eagerly. Nobody laughed. That single moment of courage showed her that speaking up is not about being perfect, but about being heard.",
      grammarRule: "Read for comprehension and tone. Identify the turning point in Maya's motivation.",
      items: [
        {
          itemId: "q1",
          prompt: "Why did Maya always sit at the back of the classroom?",
          options: [
            "She wanted to sleep",
            "She was terrified of making a mistake and speaking up",
            "She liked the view",
            "She was late every day"
          ],
          correctIndex: 1,
          explanation: "Maya sat at the back because her heart would race and she was terrified of making a mistake."
        },
        {
          itemId: "q2",
          prompt: "What did Maya do when the teacher asked for a volunteer?",
          options: [
            "She ran out of the room",
            "She ignored the teacher",
            "She took a deep breath and raised her hand",
            "She asked her friend to volunteer"
          ],
          correctIndex: 2,
          explanation: "Even though she felt panic, she took a deep breath and raised her hand to volunteer."
        },
        {
          itemId: "q3",
          prompt: "What happened when Maya started speaking?",
          options: [
            "Her voice trembled at first but everyone was listening eagerly",
            "Everyone laughed at her",
            "She forgot her words and sat down",
            "The teacher stopped her"
          ],
          correctIndex: 0,
          explanation: "Her voice trembled at first, but everyone was listening eagerly and nobody laughed."
        },
        {
          itemId: "q4",
          prompt: "What did that single moment of courage teach Maya?",
          options: [
            "She should never volunteer again",
            "Speaking up is not about being perfect, but about being heard",
            "She needs to speak louder",
            "She should only speak when she is 100% perfect"
          ],
          correctIndex: 1,
          explanation: "The passage states that she realized speaking up is not about being perfect, but about being heard."
        }
      ],
      answers: {
        correct: { q1: 1, q2: 2, q3: 0, q4: 1 },
        wrong: { q1: 1, q2: 2, q3: 2, q4: 1 }
      }
    },
    {
      id: "w4d1-listen-shadow",
      sequence: 2,
      archetypeId: "LISTEN_SHADOW",
      widget: "listen_shadow",
      sectionLabel: "Listening",
      topic: "Confidence Shadowing",
      taskIntro: "Shadow a confident motivational speaker",
      instructions: "Listen to the confident speaker, then repeat immediately after. Shadowing builds natural speaking habit.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 4,
      audioGenre: "Motivational monologue",
      audioScript: "Speaking is not a test. It is a bridge. When you speak, you share your unique voice with the world. Do not worry about mistakes. Just focus on connecting with others. You can do this!",
      audioDurationSeconds: 15,
      grammarRule: "Imitate natural speaking pacing, word stress, and confidence.",
      targetWords: ["test", "bridge", "voice", "connecting"],
      textToShadow: "Speaking is not a test. It is a bridge. When you speak, you share your unique voice with the world.",
      answers: {
        correct: [
          {
            itemId: "shadow1",
            transcript: "Speaking is not a test. It is a bridge. When you speak, you share your unique voice with the world.",
            durationSeconds: 8,
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "shadow1",
            transcript: "Speaking is not test. It is bridge. When speak, you share unique voice.",
            durationSeconds: 6,
            isCorrect: false
          }
        ]
      }
    },
    {
      id: "w4d1-write-transform",
      sequence: 3,
      archetypeId: "WRITE_SENT_TRANS",
      widget: "sentence_transform",
      sectionLabel: "Writing",
      topic: "Low-stakes self-expression reframe",
      taskIntro: "Transform negative phrasing into growth framing",
      instructions: "Rewrite the self-limiting statements to build a positive growth framing about learning English.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 4,
      grammarRule: "Reframe negative words (shy, fear, mistakes) using proactive growth verbs (working on, learn, building).",
      items: [
        {
          itemId: "st1",
          sourceSentence: "I am shy.",
          sampleAnswer: "I am working on speaking more.",
          watchHints: ["positive framing", "focus on action"]
        },
        {
          itemId: "st2",
          sourceSentence: "I always make mistakes.",
          sampleAnswer: "I learn from my mistakes.",
          watchHints: ["growth mindset", "reframe mistakes"]
        },
        {
          itemId: "st3",
          sourceSentence: "I cannot speak English.",
          sampleAnswer: "I am building my English speaking habit.",
          watchHints: ["active growth", "focus on building habit"]
        }
      ],
      answers: {
        correct: [
          { itemId: "st1", text: "I am working on speaking more.", isCorrect: true },
          { itemId: "st2", text: "I learn from my mistakes.", isCorrect: true },
          { itemId: "st3", text: "I am building my English speaking habit.", isCorrect: true }
        ],
        wrong: [
          { itemId: "st1", text: "I am working on speaking more.", isCorrect: true },
          { itemId: "st2", text: "I still hate making mistakes.", isCorrect: false },
          { itemId: "st3", text: "I am building my English speaking habit.", isCorrect: true }
        ]
      }
    },
    {
      id: "w4d1-speak-aloud",
      sequence: 4,
      archetypeId: "SPEAK_READ_ALOUD",
      widget: "read_aloud",
      sectionLabel: "Speaking",
      topic: "Motivational paragraph read aloud",
      taskIntro: "Read the motivational speech aloud",
      instructions: "Read the connected paragraph aloud clearly. Perfect low-stakes practice to build speaking habit without improvising.",
      subSkill: "Pronunciation",
      activity: "Speak",
      estimatedMinutes: 3,
      textToReadAloud: "My voice has value. Every time I practice, I build my confidence. I do not need to be perfect to start. I just need to speak up.",
      grammarRule: "Focus on clear pronunciation, steady pacing, and breathing pauses between sentences.",
      targetWords: ["voice", "value", "confidence", "perfect", "speak"],
      speakingDurationSeconds: 30,
      answers: {
        correct: [
          {
            itemId: "read_aloud",
            transcript: "My voice has value. Every time I practice, I build my confidence. I do not need to be perfect to start. I just need to speak up.",
            durationSeconds: 15,
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "read_aloud",
            transcript: "My voice has... value. Every time... practice, build confidence. Not need to be perfect... just speak up.",
            durationSeconds: 22,
            isCorrect: false
          }
        ]
      }
    }
  ]
};

const weekFourDayTwoTasks: TaskDayData = {
  dayId: "day_24_04_02",
  tasks: [
    {
      id: "w4d2-read-tone-id",
      sequence: 1,
      archetypeId: "READ_TONE_ID",
      widget: "read_tone_id",
      sectionLabel: "Reading",
      topic: "Tone awareness in opinions",
      taskIntro: "Identify confident vs hesitant opinions",
      instructions: "Read each short opinion and choose whether it sounds confident or hesitant.",
      subSkill: "Vocabulary",
      activity: "Read",
      estimatedMinutes: 3,
      passageTitle: "Opinions on remote work",
      grammarRule: "Confident tone uses strong words (absolutely, convinced, certainly) and direct verbs. Hesitant/uncertain tone uses fillers and hedges (guess, maybe, not sure, probably).",
      items: [
        {
          itemId: "tone1",
          sender: "Alex",
          message: "I am absolutely convinced that remote work is exceptionally beneficial because it saves time and boosts overall productivity.",
          prompt: "What is the tone of this message?",
          options: ["Hesitant / Uncertain", "Confident / Sure"],
          correctIndex: 1,
          explanation: "Alex uses 'absolutely convinced' and strong direct verbs, expressing high certainty."
        },
        {
          itemId: "tone2",
          sender: "Jamie",
          message: "Well, I guess remote work is okay, but I'm not really sure if it actually works for everyone, maybe it's fine.",
          prompt: "What is the tone of this message?",
          options: ["Hesitant / Uncertain", "Confident / Sure"],
          correctIndex: 0,
          explanation: "Jamie uses hedging terms like 'guess', 'not really sure', and 'maybe', indicating uncertainty."
        }
      ],
      answers: {
        correct: { tone1: 1, tone2: 0 },
        wrong: { tone1: 1, tone2: 1 }
      }
    },
    {
      id: "w4d2-listen-mcq",
      sequence: 2,
      archetypeId: "LISTEN_MCQ",
      widget: "listen_mcq",
      sectionLabel: "Listening",
      topic: "Confident Speech Patterns",
      taskIntro: "Who sounds more confident?",
      instructions: "Listen to Speaker A and Speaker B sharing their opinions on working from home. Select the speaker who sounds more confident.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 3,
      audioGenre: "Two opinions on remote work",
      audioScript: "Speaker A: Um, I think working from home is probably good, I guess... But maybe it's hard to focus sometimes? I don't know, it's just my opinion. Speaker B: In my experience, remote work is exceptionally beneficial. It allows us to manage our time efficiently and delivers much better work-life balance.",
      audioDurationSeconds: 22,
      innerWidget: "mcq",
      items: [
        {
          itemId: "lmcq1",
          prompt: "Who sounds more confident about their opinion?",
          options: ["Speaker A", "Speaker B"],
          correctIndex: 1,
          explanation: "Speaker B speaks clearly, uses no filler words or hedges, and expresses ideas with structured conviction."
        }
      ],
      answers: {
        correct: { lmcq1: 1 },
        wrong: { lmcq1: 0 }
      }
    },
    {
      id: "w4d2-write-timed",
      sequence: 3,
      archetypeId: "WRITE_TIMED",
      widget: "write_timed",
      sectionLabel: "Writing",
      topic: "Timed Opinion Write",
      taskIntro: "Write your opinion on remote work in 3 minutes",
      instructions: "State your opinion on remote work clearly. Do not overthink — timed pressure helps train writing confidence. Write at least 25 words.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 4,
      writingDurationSeconds: 180,
      prompt: "What is your opinion on working from home (remote work)?",
      targetWords: ["opinion", "remote", "productivity", "convinced", "believe"],
      grammarRule: "Share your opinion using strong opinion verbs and markers. Focus on keeping your writing clear and fluent under pressure.",
      sampleAnswer: "In my opinion, remote work is excellent because it increases productivity. I am convinced that working from home is the best setup, and I believe most companies should offer it.",
      answerHints: [
        "State your opinion clearly.",
        "Use at least two target words.",
        "Write at least 25 words.",
        "Do not overthink under pressure!"
      ],
      answers: {
        correct: [
          {
            itemId: "write1",
            text: "In my opinion, remote work is excellent because it increases productivity. I am convinced that working from home is the best setup, and I believe most companies should offer it.",
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "write1",
            text: "I guess remote work is okay, but I am not convinced it is good. It has some problems maybe.",
            isCorrect: false
          }
        ]
      }
    },
    {
      id: "w4d2-speak-timed",
      sequence: 4,
      archetypeId: "SPEAK_TIMED",
      widget: "speak_timed",
      sectionLabel: "Speaking",
      topic: "Timed Improvised Opinion Speech",
      taskIntro: "Speak on online classes for 60 seconds",
      instructions: "State your opinion on whether online classes are better than traditional learning. Speak for 60 seconds with confidence.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      speakingDurationSeconds: 60,
      prompt: "Share your opinion on whether online classes are better than traditional classroom learning.",
      targetWords: ["opinion", "online", "traditional", "confident", "prefer"],
      grammarRule: "Structure your improvised opinion: state your view clearly, give one reason, and conclude with conviction.",
      sampleResponse: "In my opinion, online learning is very convenient, but I prefer traditional classroom learning. Traditional schools allow us to interact with teachers directly. I feel confident that face-to-face learning is much more effective.",
      answers: {
        correct: [
          {
            itemId: "speak1",
            transcript: "In my opinion, online learning is very convenient, but I prefer traditional classroom learning. Traditional schools allow us to interact with teachers directly. I feel confident that face-to-face learning is much more effective.",
            durationSeconds: 25,
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "speak1",
            transcript: "Um, I think online class is good, but traditional is also good. I don't know which one is better.",
            durationSeconds: 15,
            isCorrect: false
          }
        ]
      }
    }
  ]
};

const paintingArtImageUrl = `data:image/svg+xml;utf8,${encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 360" role="img" aria-label="A person painting a scenic mountain landscape on a canvas outdoors">
  <defs>
    <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#a5c4f7" />
      <stop offset="100%" stop-color="#e2ecfc" />
    </linearGradient>
    <linearGradient id="mntGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#4f46e5" />
      <stop offset="100%" stop-color="#818cf8" />
    </linearGradient>
    <linearGradient id="sunGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#fb7185" />
      <stop offset="100%" stop-color="#f43f5e" />
    </linearGradient>
  </defs>
  <rect width="720" height="360" fill="url(#skyGrad)" />
  <circle cx="360" cy="180" r="100" fill="url(#sunGrad)" opacity="0.85" />
  <path d="M 0 360 L 0 240 Q 180 180 360 260 Q 540 320 720 220 L 720 360 Z" fill="#1e1b4b" opacity="0.9" />
  <path d="M 120 360 L 300 210 L 480 360 Z" fill="url(#mntGrad)" opacity="0.6" />
  <path d="M 0 360 Q 240 280 480 360 Z" fill="#312e81" />
  <rect x="180" y="80" width="10" height="240" fill="#78350f" transform="rotate(-15, 185, 200)" />
  <rect x="230" y="80" width="10" height="240" fill="#78350f" transform="rotate(15, 235, 200)" />
  <rect x="210" y="60" width="10" height="260" fill="#451a03" />
  <rect x="150" y="100" width="120" height="90" fill="#fafafa" stroke="#451a03" stroke-width="4" rx="4" />
  <circle cx="210" cy="140" r="20" fill="#fda4af" />
  <path d="M 152 188 L 190 150 L 220 170 L 268 135 L 268 188 Z" fill="#818cf8" />
  <path d="M 450 260 C 420 240, 390 280, 420 300 C 450 320, 480 280, 450 260 Z" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2" />
  <circle cx="420" cy="275" r="8" fill="#f43f5e" />
  <circle cx="435" cy="285" r="8" fill="#3b82f6" />
  <circle cx="450" cy="270" r="8" fill="#10b981" />
  <text x="360" y="45" font-family="sans-serif" font-size="22" font-weight="800" fill="#1e1b4b" text-anchor="middle" letter-spacing="1">Describe the Activity</text>
</svg>
`)}`;

const weekFourDayThreeTasks: TaskDayData = {
  dayId: "day_24_04_03",
  tasks: [
    {
      id: "w4d3-read-mcq",
      sequence: 1,
      archetypeId: "READ_COMP_MCQ",
      widget: "read_comp_mcq",
      sectionLabel: "Reading",
      topic: "Elena's Bio",
      taskIntro: "Elena Rostova's Self-Description",
      instructions: "Read Elena's short bio and answer the multiple choice questions.",
      subSkill: "Comprehension",
      activity: "Read",
      estimatedMinutes: 4,
      passageTitle: "Meet Elena Rostova",
      passage: "My name is Elena Rostova. I describe myself as a curious observer of nature. For the past ten years, I have worked as a marine biologist and wildlife photographer. Most of my days are spent either in research labs analyzing water samples or diving underwater to capture the beautiful details of ocean life. My primary motivation is to inspire the conservation of our fragile marine ecosystems. Through my photography, I hope to show the world that every creature plays an essential role in keeping our planet alive.",
      grammarRule: "Look for how Elena connects her professional titles with personal motivation to build a complete self-description.",
      items: [
        {
          itemId: "q1",
          prompt: "What does Elena do for a living?",
          options: [
            "She is a full-time university teacher",
            "She works as a marine biologist and wildlife photographer",
            "She is a forest ranger and gardener",
            "She is an artist painting underwater landscapes"
          ],
          correctIndex: 1,
          explanation: "Elena states she has worked as a marine biologist and wildlife photographer for the past ten years."
        },
        {
          itemId: "q2",
          prompt: "How does Elena describe herself in her own words?",
          options: [
            "An adventurous deep-sea traveler",
            "A strict lab researcher",
            "A curious observer of nature",
            "A popular social media creator"
          ],
          correctIndex: 2,
          explanation: "Elena explicitly says, 'I describe myself as a curious observer of nature.'"
        },
        {
          itemId: "q3",
          prompt: "What is Elena's primary motivation?",
          options: [
            "To inspire the conservation of our fragile marine ecosystems",
            "To sell expensive wildlife photographs",
            "To discover new species of deep-sea fish",
            "To travel to exotic islands around the world"
          ],
          correctIndex: 0,
          explanation: "Elena states, 'My primary motivation is to inspire the conservation of our fragile marine ecosystems.'"
        },
        {
          itemId: "q4",
          prompt: "Where does Elena spend most of her time working?",
          options: [
            "In classrooms teaching high school students",
            "Writing research books at a quiet library",
            "Climbing mountains to take bird photographs",
            "In research labs analyzing water samples or diving underwater"
          ],
          correctIndex: 3,
          explanation: "Elena explains most of her days are spent either in research labs analyzing water samples or diving underwater."
        }
      ],
      answers: {
        correct: { q1: 1, q2: 2, q3: 0, q4: 3 },
        wrong: { q1: 1, q2: 2, q3: 1, q4: 3 }
      }
    },
    {
      id: "w4d3-listen-tone",
      sequence: 2,
      archetypeId: "LISTEN_TONE",
      widget: "listen_tone",
      sectionLabel: "Listening",
      topic: "Formal vs. Casual self-description",
      taskIntro: "Listen to formal and casual introductions",
      instructions: "Listen to Arthur introducing himself in two different ways, then choose which is formal and which is casual.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 3,
      grammarRule: "Learn to identify formal vocabulary (e.g. 'It is a pleasure', 'specialize in') vs. casual phrases (e.g. 'Hey there', 'huge bookworm').",
      intros: [
        {
          id: "intro_a",
          label: "Version A",
          speaker: "Arthur (Formal)",
          audioScript: "Hello, my name is Arthur. It is a pleasure to meet you. I am currently working as a software developer, where I specialize in building user interfaces. In my free time, I enjoy reading classical literature.",
          audioDurationSeconds: 16
        },
        {
          id: "intro_b",
          label: "Version B",
          speaker: "Arthur (Casual)",
          audioScript: "Hey there! I'm Art. Great meeting you! I develop software and mostly work on frontends. Outside of work, I'm a huge bookworm and love reading classics.",
          audioDurationSeconds: 12
        }
      ],
      items: [
        {
          itemId: "l1",
          prompt: "What is the tone of Version A?",
          options: ["Formal / Professional", "Casual / Informal"],
          correctIndex: 0,
          explanation: "Version A uses polite vocabulary like 'It is a pleasure to meet you', complete sentences, and formal phrases like 'specialize in'."
        },
        {
          itemId: "l2",
          prompt: "What is the tone of Version B?",
          options: ["Formal / Professional", "Casual / Informal"],
          correctIndex: 1,
          explanation: "Version B uses contractions ('I'm'), casual expressions ('Hey there', 'Great meeting you'), and idiomatic slang ('huge bookworm')."
        }
      ],
      answers: {
        correct: { l1: 0, l2: 1 },
        wrong: { l1: 0, l2: 0 }
      }
    },
    {
      id: "w4d3-write-transform",
      sequence: 3,
      archetypeId: "WRITE_SENT_TRANS",
      widget: "sentence_transform",
      sectionLabel: "Writing",
      topic: "Richer self-description transforms",
      taskIntro: "Transform simple statements into rich descriptions",
      instructions: "Rewrite each simple statement to make it a richer, more expressive self-description.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 4,
      grammarRule: "Expand simple statements by adding active feelings (e.g., 'passionate about') or professional details (e.g., 'reside in').",
      items: [
        {
          itemId: "st1",
          sourceSentence: "I like soccer.",
          sampleAnswer: "I am passionate about soccer and play every weekend.",
          watchHints: ["passionate about", "play every weekend"]
        },
        {
          itemId: "st2",
          sourceSentence: "I am a programmer.",
          sampleAnswer: "I work as a software engineer and love building creative apps.",
          watchHints: ["work as", "love building"]
        },
        {
          itemId: "st3",
          sourceSentence: "I live in Berlin.",
          sampleAnswer: "I reside in the vibrant city of Berlin and enjoy exploring its culture.",
          watchHints: ["reside in", "vibrant city", "enjoy exploring"]
        }
      ],
      answers: {
        correct: [
          { itemId: "st1", text: "I am passionate about soccer and play every weekend.", isCorrect: true },
          { itemId: "st2", text: "I work as a software engineer and love building creative apps.", isCorrect: true },
          { itemId: "st3", text: "I reside in the vibrant city of Berlin and enjoy exploring its culture.", isCorrect: true }
        ],
        wrong: [
          { itemId: "st1", text: "I am passionate about soccer and play every weekend.", isCorrect: true },
          { itemId: "st2", text: "I work as a software engineer and love building creative apps.", isCorrect: true },
          { itemId: "st3", text: "I still live in Berlin.", isCorrect: false }
        ]
      }
    },
    {
      id: "w4d3-speak-pic-desc",
      sequence: 4,
      archetypeId: "SPEAK_PIC_DESC",
      widget: "speak_pic_desc",
      sectionLabel: "Speaking",
      topic: "Describe an activity outdoors",
      taskIntro: "Describe the person and what they might be doing",
      instructions: "Look at the picture. Describe the person, what they are doing, and what kind of person they might be based on this activity.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      imageUrl: paintingArtImageUrl,
      imageAlt: "A person painting a scenic mountain landscape on a canvas outdoors next to a lake.",
      grammarRule: "Use speculative phrases like 'looks like', 'seems to be', and 'might be' to project details and express ideas.",
      speakingDurationSeconds: 45,
      answers: {
        correct: [
          {
            itemId: "picdesc",
            transcript: "In this photo, there is a person painting outdoors next to a beautiful lake. They are painting scenic mountains and a setting sun on a canvas. They seem to be a very creative and peaceful person who loves nature.",
            durationSeconds: 18,
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "picdesc",
            transcript: "In this photo, there is a person painting. They paint mountains. I don't know who they are, maybe a student.",
            durationSeconds: 12,
            isCorrect: false
          }
        ]
      }
    }
  ]
};

const weekFourDayFourTasks: TaskDayData = {
  dayId: "day_24_04_04",
  tasks: [
    {
      id: "w4d4-read-tone-id",
      sequence: 1,
      archetypeId: "READ_TONE_ID",
      widget: "read_tone_id",
      sectionLabel: "Reading",
      topic: "Awkward moment tone shift",
      taskIntro: "Identify tone shift in self-correction",
      instructions: "Read the short dialogue where someone makes a mistake and choose the option that describes the tone shift.",
      subSkill: "Vocabulary",
      activity: "Read",
      estimatedMinutes: 3,
      passageTitle: "The presentation slip",
      grammarRule: "Recognize how speaker tone transitions from tense/anxious when making a mistake to relaxed/relieved when recovering gracefully.",
      items: [
        {
          itemId: "tone1",
          sender: "Sarah",
          message: "Sorry, I... I meant to say we grew by fifteen percent, not fifty. My bad, let me correct that!",
          prompt: "How does Sarah's tone shift in this message?",
          options: [
            "From anxious/apologetic to calm/composed",
            "From aggressive to defensive",
            "From formal to highly informal"
          ],
          correctIndex: 0,
          explanation: "Sarah starts with a slight stammer and apology ('Sorry, I...'), showing temporary anxiety, then immediately corrects herself smoothly ('let me correct that!'), showing calm recovery."
        },
        {
          itemId: "tone2",
          sender: "Mark",
          message: "Oh, wait! I just realized I sent you the wrong draft. Oops! Let me send the updated version right away. Thanks for your patience!",
          prompt: "How does Mark's tone shift here?",
          options: [
            "From angry to polite",
            "From surprised/startled to helpful/reassured",
            "From uncertain to completely confused"
          ],
          correctIndex: 1,
          explanation: "Mark starts with surprise ('Oh, wait!'), acknowledges the mistake casually ('Oops!'), and quickly moves to solve the problem while showing appreciation, showing a graceful recovery."
        }
      ],
      answers: {
        correct: { tone1: 0, tone2: 1 },
        wrong: { tone1: 0, tone2: 2 }
      }
    },
    {
      id: "w4d4-listen-shadow",
      sequence: 2,
      archetypeId: "LISTEN_SHADOW",
      widget: "listen_shadow",
      sectionLabel: "Listening",
      topic: "Graceful self-correction",
      taskIntro: "Shadow natural self-correction",
      instructions: "Listen to the speaker self-correct mid-sentence, then record yourself repeating the same natural flow.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 3,
      audioGenre: "Self-correction speech",
      audioDurationSeconds: 20,
      audioScript: "We need to finish this by Tuesday... Oh, wait, I mean Wednesday! Actually, let me double check the schedule.",
      grammarRule: "Use brief self-correction markers like 'Oh, wait', 'I mean', or 'Actually' to adjust your speech mid-sentence without pausing for too long.",
      targetWords: ["Oh, wait", "I mean", "Actually"],
      textToShadow: "We need to finish this by Tuesday... Oh, wait, I mean Wednesday! Actually, let me double check the schedule.",
      answers: {
        correct: [
          {
            itemId: "shadow",
            transcript: "We need to finish this by Tuesday... Oh, wait, I mean Wednesday! Actually, let me double check the schedule.",
            durationSeconds: 10,
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "shadow",
            transcript: "We need to finish this by Tuesday... Oh Wednesday... Actually, let double check the schedule.",
            durationSeconds: 8,
            isCorrect: false
          }
        ]
      }
    },
    {
      id: "w4d4-write-timed",
      sequence: 3,
      archetypeId: "WRITE_TIMED",
      widget: "write_timed",
      sectionLabel: "Writing",
      topic: "Reflecting on mistakes",
      taskIntro: "Reflect on speaking slips",
      instructions: "Take 3 minutes to reflect on this question: 'What do you do when you make a mistake while speaking?' Write a short, personal reflection.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 3,
      grammarRule: "Focus on personal reflection and continuous flow. Use transition words like 'Usually', 'Instead of', or 'Simply' to organize your thoughts.",
      targetWords: ["Usually", "Instead of", "Simply"],
      writingDurationSeconds: 180,
      prompt: "What do you do when you make a mistake while speaking?",
      sampleAnswer: "Usually, when I make a mistake while speaking, I try to stay calm. Instead of stressing, I simply take a deep breath, correct myself quickly, and keep going. Most people do not mind minor slips.",
      answers: {
        correct: [
          {
            itemId: "reflection",
            text: "Usually, when I make a mistake while speaking, I try to stay calm. Instead of stressing, I simply take a deep breath, correct myself quickly, and keep going. Most people do not mind minor slips.",
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "reflection",
            text: "When I make a mistake I get very nervous. I don't know what to do and I stop speaking.",
            isCorrect: false
          }
        ]
      },
      answerHints: [
        "Answer the question directly.",
        "Use at least one target word.",
        "Write at least two sentences."
      ]
    },
    {
      id: "w4d4-speak-smalltalk",
      sequence: 4,
      archetypeId: "SPEAK_SMALLTALK",
      widget: "speak_smalltalk",
      sectionLabel: "Speaking",
      topic: "Unpredictable small talk",
      taskIntro: "Casual small talk challenge",
      instructions: "Respond naturally to the partner's casual questions in this unpredictable small talk challenge.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      dialogueContext: [
        { role: "Partner", text: "Hi there! I heard your presentation went well, but did I hear you made a slight slip at the start?", speaker: "partner" },
        { role: "You", text: "Actually, yes! I said the wrong year, but I simply corrected it and moved on.", speaker: "learner" },
        { role: "Partner", text: "That's awesome. I usually freeze up when that happens. What's your secret?", speaker: "partner" },
        { role: "You", text: "Instead of worrying, I just laugh it off. Awkward moments are totally normal!", speaker: "learner" }
      ],
      grammarRule: "Handle conversational surprises gracefully. Use transition words like 'Actually', 'Simply', and 'Instead of' to keep your small talk flowing.",
      targetWords: ["Actually", "Simply", "Instead of"],
      speakingDurationSeconds: 30,
      answers: {
        correct: [
          {
            itemId: "st1",
            transcript: "Actually, yes! I said the wrong year, but I simply corrected it and moved on.",
            durationSeconds: 7,
            isCorrect: true
          },
          {
            itemId: "st2",
            transcript: "Instead of worrying, I just laugh it off. Awkward moments are totally normal!",
            durationSeconds: 7,
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "st1",
            transcript: "Actually, yes! I said the wrong year, but I simply corrected it and moved on.",
            durationSeconds: 7,
            isCorrect: true
          },
          {
            itemId: "st2",
            transcript: "I freeze too, I don't know.",
            durationSeconds: 4,
            isCorrect: false
          }
        ]
      }
    }
  ]
};

const gardeningHobbyImageUrl = `data:image/svg+xml;utf8,${encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 360" role="img" aria-label="A vibrant backyard garden corner with potted green plants, colorful blooming flowers, and a classic red watering can">
  <defs>
    <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#bae6fd" />
      <stop offset="100%" stop-color="#f0f9ff" />
    </linearGradient>
    <linearGradient id="wallGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#cbd5e1" />
      <stop offset="100%" stop-color="#94a3b8" />
    </linearGradient>
    <linearGradient id="potGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#b45309" />
      <stop offset="100%" stop-color="#d97706" />
    </linearGradient>
  </defs>
  <rect width="720" height="360" fill="url(#skyGrad)" />
  <rect y="180" width="720" height="180" fill="url(#wallGrad)" />
  
  <line x1="120" y1="180" x2="120" y2="360" stroke="#78350f" stroke-width="6" />
  <line x1="280" y1="180" x2="280" y2="360" stroke="#78350f" stroke-width="6" />
  <line x1="440" y1="180" x2="440" y2="360" stroke="#78350f" stroke-width="6" />
  <line x1="600" y1="180" x2="600" y2="360" stroke="#78350f" stroke-width="6" />
  <rect y="220" width="720" height="20" fill="#a16207" opacity="0.8" />
  <rect y="300" width="720" height="20" fill="#a16207" opacity="0.8" />

  <rect y="320" width="720" height="40" fill="#15803d" />
  
  <path d="M 80 340 L 95 270 L 155 270 L 170 340 Z" fill="url(#potGrad)" />
  <rect x="90" y="265" width="70" height="8" rx="2" fill="#92400e" />
  <path d="M 125 265 Q 125 150 70 140 Q 110 180 100 210 Q 130 190 125 265 Z" fill="#166534" />
  <path d="M 125 265 Q 140 130 200 130 Q 160 170 170 200 Q 135 195 125 265 Z" fill="#15803d" />
  <path d="M 125 265 Q 90 170 40 200 Q 80 215 85 240 Q 110 240 125 265 Z" fill="#14532d" />
  <path d="M 125 265 Q 170 180 210 220 Q 175 230 170 250 Q 145 250 125 265 Z" fill="#166534" />

  <path d="M 300 345 L 310 295 L 360 295 L 370 345 Z" fill="#475569" />
  <rect x="306" y="290" width="58" height="6" rx="2" fill="#334155" />
  <path d="M 320 290 Q 300 240 310 220" stroke="#16a34a" stroke-width="3" fill="none" />
  <circle cx="310" cy="220" r="12" fill="#e11d48" />
  <circle cx="310" cy="220" r="4" fill="#facc15" />
  
  <path d="M 350 290 Q 370 230 355 210" stroke="#16a34a" stroke-width="3" fill="none" />
  <circle cx="355" cy="210" r="14" fill="#db2777" />
  <circle cx="355" cy="210" r="5" fill="#facc15" />

  <path d="M 335 290 Q 335 220 335 195" stroke="#16a34a" stroke-width="3" fill="none" />
  <circle cx="335" cy="195" r="16" fill="#ea580c" />
  <circle cx="335" cy="195" r="6" fill="#facc15" />

  <rect x="490" y="270" width="90" height="70" rx="10" fill="#dc2626" />
  <path d="M 490 285 C 450 285, 450 325, 490 325" stroke="#dc2626" stroke-width="8" fill="none" />
  <path d="M 580 310 L 630 270" stroke="#dc2626" stroke-width="10" stroke-linecap="round" fill="none" />
  <path d="M 625 265 L 635 275" stroke="#94a3b8" stroke-width="12" stroke-linecap="round" fill="none" />
  <circle cx="650" cy="285" r="3" fill="#38bdf8" />
  <circle cx="665" cy="300" r="3" fill="#38bdf8" />
  <circle cx="655" cy="315" r="3" fill="#38bdf8" />
</svg>
`)}`;

const weekFourDayFiveTasks: TaskDayData = {
  dayId: "day_24_04_05",
  tasks: [
    {
      id: "w4d5-read-mcq",
      sequence: 1,
      archetypeId: "READ_COMP_MCQ",
      widget: "read_comp_mcq",
      sectionLabel: "Reading",
      topic: "Passionate about stargazing",
      taskIntro: "Read about a relaxing stargazing passion",
      instructions: "Read the personal passage about stargazing and answer the four multiple-choice questions.",
      subSkill: "Comprehension",
      activity: "Read",
      estimatedMinutes: 4,
      passageTitle: "Chasing the Stars",
      grammarRule: "Identify descriptive expressions and narrative flow in personal interest stories.",
      passage: "My fascination with astronomy began with a simple gift: a pair of binoculars from my grandfather. One clear autumn night, he guided me to our backyard and pointed them toward the moon. Looking through those lenses, I was awestruck by the crisp detail of the lunar craters. That single moment sparked a lifelong passion for stargazing. Years later, I invested in a proper telescope, and I still remember the absolute thrill of locating Saturn's rings for the first time. For me, standing in the quiet dark and gazing at distant galaxies isn't just a hobby. It is a calming ritual that puts all of my daily, small worries into perspective. To anyone wanting to start, my advice is simple: don't rush to buy expensive gear. Simply grab a free star map, step outside on a clear night, and let your eyes adjust to the infinite beauty above.",
      items: [
        {
          itemId: "q1",
          prompt: "What first sparked the narrator's passion for stargazing?",
          options: [
            "A childhood book about space",
            "A gift of binoculars from their grandfather",
            "A school trip to a massive planetarium",
            "A bright meteor shower they saw on TV"
          ],
          correctIndex: 1,
          explanation: "The passage states that the narrator's fascination with astronomy 'began with a simple gift: a pair of binoculars from my grandfather.'"
        },
        {
          itemId: "q2",
          prompt: "What major achievement is recalled in the second paragraph?",
          options: [
            "Spotting a new comet passing by",
            "Taking a photo of a lunar eclipse",
            "Locating Saturn's rings for the first time",
            "Charting all eighty-eight constellations"
          ],
          correctIndex: 2,
          explanation: "The narrator explicitly notes: 'I still remember the absolute thrill of locating Saturn's rings for the first time.'"
        },
        {
          itemId: "q3",
          prompt: "How does stargazing affect the narrator's state of mind?",
          options: [
            "It makes them feel small and isolated",
            "It gives them a calming perspective on daily problems",
            "It makes them excited about space travel",
            "It leaves them feeling extremely tired"
          ],
          correctIndex: 1,
          explanation: "The passage describes stargazing as 'a calming ritual that puts all of my daily, small worries into perspective.'"
        },
        {
          itemId: "q4",
          prompt: "What is the narrator's primary advice for beginners?",
          options: [
            "Buy the most expensive telescope available",
            "Join a professional astronomical society",
            "Travel to a high mountain or desert",
            "Start simply with a free star map and your naked eyes"
          ],
          correctIndex: 3,
          explanation: "The narrator advises beginners not to rush to buy expensive gear, but to 'simply grab a free star map, step outside on a clear night, and let your eyes adjust.'"
        }
      ],
      answers: {
        correct: { q1: 1, q2: 2, q3: 1, q4: 3 },
        wrong: { q1: 1, q2: 2, q3: 0, q4: 3 }
      }
    },
    {
      id: "w4d5-listen-mcq",
      sequence: 2,
      archetypeId: "LISTEN_MCQ",
      widget: "listen_mcq",
      sectionLabel: "Listening",
      topic: "Enthusiasm for gardening",
      taskIntro: "Listen to an enthusiastic plant lover",
      instructions: "Listen to the speaker talk enthusiastically about their indoor gardening hobby, then answer the questions.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 3,
      audioGenre: "Enthusiastic monologue",
      audioDurationSeconds: 25,
      audioScript: "I've been into indoor gardening for about three years now. Honestly, there is nothing quite like the feeling of seeing a fresh, new leaf unfurl on a plant you've cared for. My absolute favorite is my Monstera deliciosa—it is huge! I make sure to mist its leaves every morning, and I've even started propagating cuttings to share with my friends. It is incredibly therapeutic and contagious!",
      innerWidget: "mcq",
      items: [
        {
          itemId: "l1",
          prompt: "What is the speaker's absolute favorite plant in their collection?",
          options: [
            "A fiddle-leaf fig",
            "A gold-lined snake plant",
            "A Monstera deliciosa",
            "A classic golden pothos"
          ],
          correctIndex: 2,
          explanation: "The speaker explicitly states: 'My absolute favorite is my Monstera deliciosa—it is huge!'"
        },
        {
          itemId: "l2",
          prompt: "How long has the speaker been practicing indoor gardening?",
          options: [
            "One full year",
            "About three years",
            "Over five years",
            "Just six months"
          ],
          correctIndex: 1,
          explanation: "The speaker starts by saying: 'I've been into indoor gardening for about three years now.'"
        },
        {
          itemId: "l3",
          prompt: "What morning routine does the speaker mention?",
          options: [
            "Misting the plant's leaves",
            "Measuring the soil moisture",
            "Adding rich fertilizer",
            "Taking the plant outside for sunlight"
          ],
          correctIndex: 0,
          explanation: "The speaker explains: 'I make sure to mist its leaves every morning.'"
        }
      ],
      answers: {
        correct: { l1: 2, l2: 1, l3: 0 },
        wrong: { l1: 2, l2: 3, l3: 0 }
      }
    },
    {
      id: "w4d5-write-transform",
      sequence: 3,
      archetypeId: "WRITE_SENT_TRANS",
      widget: "sentence_transform",
      sectionLabel: "Writing",
      topic: "Hobby vocabulary upgrade",
      taskIntro: "Express passions with premium voice",
      instructions: "Transform basic hobby statements into expressive, confident descriptions using advanced verbs and modifiers.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 3,
      grammarRule: "Avoid basic phrases like 'I watch' or 'I play'. Upgrade your style by using high-enthusiasm patterns ('huge fan', 'passionate about', 'favorite way to unwind').",
      items: [
        {
          itemId: "wt1",
          sourceSentence: "I watch movies.",
          sampleAnswer: "I am a huge film fan and watch at least two movies a week.",
          watchHints: ["huge film fan", "at least"]
        },
        {
          itemId: "wt2",
          sourceSentence: "I play guitar in my free time.",
          sampleAnswer: "I am passionate about playing the guitar and dedicate time to practicing it every single day.",
          watchHints: ["passionate about", "dedicate time"]
        },
        {
          itemId: "wt3",
          sourceSentence: "I like cooking dinner.",
          sampleAnswer: "Cooking delicious meals for my family is my absolute favorite way to unwind after a busy day.",
          watchHints: ["absolute favorite", "unwind"]
        }
      ],
      answers: {
        correct: [
          { itemId: "wt1", text: "I am a huge film fan and watch at least two movies a week.", isCorrect: true },
          { itemId: "wt2", text: "I am passionate about playing the guitar and dedicate time to practicing it every single day.", isCorrect: true },
          { itemId: "wt3", text: "Cooking delicious meals for my family is my absolute favorite way to unwind after a busy day.", isCorrect: true }
        ],
        wrong: [
          { itemId: "wt1", text: "I just watch movies when I am bored and have nothing to do.", isCorrect: false },
          { itemId: "wt2", text: "I am passionate about playing the guitar and dedicate time to practicing it every single day.", isCorrect: true },
          { itemId: "wt3", text: "Cooking delicious meals for my family is my absolute favorite way to unwind after a busy day.", isCorrect: true }
        ]
      }
    },
    {
      id: "w4d5-speak-pic-desc",
      sequence: 4,
      archetypeId: "SPEAK_PIC_DESC",
      widget: "speak_pic_desc",
      sectionLabel: "Speaking",
      topic: "Gardening scene description",
      taskIntro: "Describe the hobby scene and share your preference",
      instructions: "Look at the picture. Describe the scene, the hobby shown, and share whether you enjoy gardening or a similar hobby.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 4,
      imageUrl: gardeningHobbyImageUrl,
      imageAlt: "A vibrant backyard garden corner with potted green plants, colorful blooming flowers, and a classic red watering can.",
      grammarRule: "Use speculative language ('seems like', 'appears to') and descriptive details. Connect it to your own personal interests smoothly.",
      speakingDurationSeconds: 45,
      answers: {
        correct: [
          {
            itemId: "picdesc",
            transcript: "In this picture, I can see a beautiful gardening scene with healthy potted plants and a red watering can. It seems like a peaceful garden. I really enjoy gardening myself because connecting with nature is extremely relaxing for me.",
            durationSeconds: 19,
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "picdesc",
            transcript: "This is a plant and watering pot. It is red. I do not like plants because they are boring.",
            durationSeconds: 10,
            isCorrect: false
          }
        ]
      }
    }
  ]
};

const weekFourDaySixTasks: TaskDayData = {
  dayId: "day_24_04_06",
  tasks: [
    {
      id: "w4d6-read-tone-id",
      sequence: 1,
      archetypeId: "READ_TONE_ID",
      widget: "read_tone_id",
      sectionLabel: "Reading",
      topic: "Tone identification in introductions",
      taskIntro: "Identify differences in self-introductions",
      instructions: "Compare these two self-introductions and choose the tone that matches best.",
      subSkill: "Comprehension",
      activity: "Read",
      estimatedMinutes: 3,
      passageTitle: "Two Self-Introductions",
      grammarRule: "Polished introductions use proactive, direct verbs, whereas hesitant ones contain qualifiers like 'maybe' and 'just'.",
      items: [
        {
          itemId: "t1",
          sender: "David",
          message: "Good morning, everyone. I am thrilled to join the marketing team today. Over the past five years, my main passion has been driving growth through creative social campaigns. In this role, my absolute focus is to expand our digital footprint, and I look forward to collaborating with all of you.",
          prompt: "Identify the tone of David's introduction:",
          options: ["Hesitant and uncertain", "Confident and polished", "Aggressive and demanding"],
          correctIndex: 1,
          explanation: "David's speech uses proactive verbs ('thrilled to join', 'expansion of footprint') and strong nouns without hesitation words."
        },
        {
          itemId: "t2",
          sender: "Emma",
          message: "Um, hi... I guess I am the new marketing person. I've done some social media stuff before, maybe for a few years... I just hope I can help out, and, well, hopefully I won't get in your way.",
          prompt: "Identify the tone of Emma's introduction:",
          options: ["Hesitant and uncertain", "Confident and polished", "Formal and strict"],
          correctIndex: 0,
          explanation: "Emma uses filler words like 'Um', 'I guess', 'maybe', 'just', and 'hopefully', which convey uncertainty."
        }
      ],
      answers: {
        correct: { t1: 1, t2: 0 },
        wrong: { t1: 1, t2: 1 }
      }
    },
    {
      id: "w4d6-listen-tone",
      sequence: 2,
      archetypeId: "LISTEN_TONE",
      widget: "listen_tone",
      sectionLabel: "Listening",
      topic: "Audio self-introductions",
      taskIntro: "Distinguish vocal confidence",
      instructions: "Listen to the presentation and identify key moments of vocal confidence vs. uncertainty.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 4,
      grammarRule: "Confident speakers pace their words evenly, maintain a steady tone, and avoid long hesitations.",
      intros: [
        {
          id: "w4d6_intro_1",
          label: "Speaker A",
          speaker: "David (CONFIDENT)",
          audioScript: "Good morning. I am thrilled to join the team today. Over the past five years, my main passion has been driving growth.",
          audioDurationSeconds: 10
        },
        {
          id: "w4d6_intro_2",
          label: "Speaker B",
          speaker: "Emma (HESITANT)",
          audioScript: "Um, hi... I guess I am the new marketing person. I've done some social media stuff before, maybe for a few years.",
          audioDurationSeconds: 11
        }
      ],
      items: [
        {
          itemId: "lt1",
          prompt: "Which speaker sounds more poised and structured?",
          options: ["Speaker A (David)", "Speaker B (Emma)", "Both sound equally confident"],
          correctIndex: 0,
          explanation: "Speaker A (David) maintains even pacing, a warm tone, and speaks without filler words."
        },
        {
          itemId: "lt2",
          prompt: "What key indicator in Speaker B's recording signals hesitation?",
          options: ["Fast speed of speaking", "Heavy use of filler words like 'Um' and 'I guess'", "Speaking too loudly"],
          correctIndex: 1,
          explanation: "Speaker B uses several fillers ('Um', 'I guess') and speaks with an uneven, halting flow."
        }
      ],
      answers: {
        correct: { lt1: 0, lt2: 1 },
        wrong: { lt1: 0, lt2: 0 }
      }
    },
    {
      id: "w4d6-write-timed",
      sequence: 3,
      archetypeId: "WRITE_TIMED",
      widget: "write_timed",
      sectionLabel: "Writing",
      topic: "3-sentence introduction",
      taskIntro: "Draft your self-introduction",
      instructions: "Write a 3-sentence introduction of yourself. State your name/role, share a key passion, and state your absolute focus. Saturday timed write is intentionally short and focused.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 5,
      grammarRule: "Structure: Sentence 1: Role, Sentence 2: Passion, Sentence 3: Focus. Time limit is 180 seconds.",
      targetWords: ["passion", "thrilled", "focus"],
      writingDurationSeconds: 180,
      prompt: "Write a 3-sentence introduction of yourself using 'thrilled', 'passion', and 'focus'.",
      sampleAnswer: "I am thrilled to join you all as the new lead designer. Design has been my lifelong passion and I love creating intuitive products. In this role, my absolute focus is to deliver outstanding user experiences.",
      answers: {
        correct: [
          {
            itemId: "w1",
            text: "I am thrilled to join the team as a software engineer. Solving complex algorithms has always been my core passion. My primary focus is to build clean, efficient, and scalable web platforms.",
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "w1",
            text: "I am a new worker here. I don't have a passion, but I just hope to focus on doing my job okay.",
            isCorrect: false
          }
        ]
      },
      answerHints: [
        "Mention your name or role.",
        "Share a key passion or interest.",
        "State your absolute focus or goal.",
        "Use all three target words: 'thrilled', 'passion', 'focus'."
      ]
    },
    {
      id: "w4d6-speak-present",
      sequence: 4,
      archetypeId: "SPEAK_PRESENT",
      widget: "speak_present",
      sectionLabel: "Speaking",
      topic: "Structured self-introduction",
      taskIntro: "Deliver a polished self-introduction",
      instructions: "Record a 90-second self-introduction. State your background, your main passion, and your key focus. Poise means taking your time, keeping pauses controlled, and avoiding rush.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 6,
      grammarRule: "Speak with structure and poise. Maintain even pacing, clear transitions, and vocal conviction.",
      targetWords: ["thrilled", "passion", "focus"],
      speakingDurationSeconds: 90,
      visualPromptDescription: "Introduce yourself in three structured parts:\n1. Your current role or background.\n2. Your core passion or driving interest.\n3. Your absolute focus or goal in this position.",
      modelPresentation: "Good morning, everyone. I am absolutely thrilled to join the engineering team today. Over the past five years, my main passion has been developing elegant solutions to complex data problems. In this role, my absolute focus is to improve our system reliability, and I look forward to working closely with all of you.",
      answers: {
        correct: [
          {
            itemId: "s1",
            transcript: "Hello everyone, I am thrilled to join the team as a new engineer. Writing efficient code is my lifelong passion. My primary focus is to build robust systems. I look forward to working together with you all.",
            durationSeconds: 15,
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "s1",
            transcript: "Um, hi... I am a new engineer here. I don't know, I just... write code. I don't really have a big passion or focus yet.",
            durationSeconds: 10,
            isCorrect: false
          }
        ]
      }
    }
  ]
};

const weekFourDaySevenTasks: TaskDayData = {
  dayId: "day_24_04_07",
  tasks: [
    {
      id: "w4d7-read-mcq",
      sequence: 1,
      archetypeId: "READ_COMP_MCQ",
      widget: "read_comp_mcq",
      sectionLabel: "Reading",
      topic: "Overcoming fear of speaking",
      taskIntro: "Inspiring passage on speaking confidence",
      instructions: "Read the story of someone who overcame their fear of speaking, then answer the questions.",
      subSkill: "Comprehension",
      activity: "Read",
      estimatedMinutes: 4,
      passageTitle: "Finding My Voice",
      grammarRule: "Identify narrative markers of growth (e.g. 'For years', 'until one day', 'Inspired by this') to track progression.",
      passage: "For years, the thought of speaking English in public filled me with a quiet dread. Whenever a colleague asked a question in a meeting, my heart would race, and I would stay silent, terrified of making a mistake. I believed that to speak, I had to be flawless. That mindset held me back until one day, a mentor shared a simple truth: 'Fluency is about connection, not perfection.' Inspired by this, I began practicing small. I started by shadowing short audio clips and recording my own voice. In the second week, I pushed myself to speak up in a friendly group chat. Each small step built my confidence. Today, I don't speak flawlessly, but I do speak confidently. I realized that speaking is a journey of growth, and my voice is worth sharing. To anyone still afraid: start small, embrace your mistakes, and trust your progress.",
      items: [
        {
          itemId: "q1",
          prompt: "What originally kept the narrator from speaking in meetings?",
          options: [
            "A lack of interest in the meeting topics",
            "A fear of making mistakes and a desire to be flawless",
            "An inability to understand their colleagues",
            "A lack of time to prepare answers"
          ],
          correctIndex: 1,
          explanation: "The narrator notes they would stay silent because they were 'terrified of making a mistake' and believed they 'had to be flawless'."
        },
        {
          itemId: "q2",
          prompt: "What simple advice from a mentor shifted the narrator's mindset?",
          options: [
            "Fluency is about connection, not perfection",
            "Speak as fast as you possibly can to sound natural",
            "Avoid speaking until you are a perfect expert",
            "Write everything down and read it word-for-word"
          ],
          correctIndex: 0,
          explanation: "The narrator explicitly states their mentor shared: 'Fluency is about connection, not perfection.'"
        },
        {
          itemId: "q3",
          prompt: "What was the narrator's very first step toward building speaking confidence?",
          options: [
            "Giving a massive presentation in front of the whole company",
            "Shadowing short audio clips and recording their own voice",
            "Moving to an English-speaking country",
            "Taking a difficult written grammar exam"
          ],
          correctIndex: 1,
          explanation: "The passage notes: 'I began practicing small. I started by shadowing short audio clips and recording my own voice.'"
        },
        {
          itemId: "q4",
          prompt: "What is the narrator's final encouraging message to others?",
          options: [
            "Only speak when your grammar is 100% flawless",
            "Start small, embrace your mistakes, and trust your progress",
            "Do not listen to mentors or group chats",
            "Public speaking is always a quiet dread"
          ],
          correctIndex: 1,
          explanation: "The narrator closes with: 'To anyone still afraid: start small, embrace your mistakes, and trust your progress.'"
        }
      ],
      answers: {
        correct: { q1: 1, q2: 0, q3: 1, q4: 1 },
        wrong: { q1: 1, q2: 0, q3: 0, q4: 1 }
      }
    },
    {
      id: "w4d7-listen-shadow",
      sequence: 2,
      archetypeId: "LISTEN_SHADOW",
      widget: "listen_shadow",
      sectionLabel: "Listening",
      topic: "Fluent and energetic shadow session",
      taskIntro: "Shadow a confident speaker",
      instructions: "Listen to the speaker talk with confidence and energy about showing growth, then record yourself repeating the passage.",
      subSkill: "Comprehension",
      activity: "Listen",
      estimatedMinutes: 3,
      audioGenre: "Motivational speech",
      audioDurationSeconds: 15,
      audioScript: "My voice is unique, and I am proud of my progress. Every single day, I am speaking with more confidence and energy!",
      grammarRule: "Match the speaker's rising and falling intonation to express energy and confidence.",
      targetWords: ["proud of", "progress", "confidence"],
      textToShadow: "My voice is unique, and I am proud of my progress. Every single day, I am speaking with more confidence and energy!",
      answers: {
        correct: [
          {
            itemId: "shadow",
            transcript: "My voice is unique, and I am proud of my progress. Every single day, I am speaking with more confidence and energy!",
            durationSeconds: 10,
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "shadow",
            transcript: "My voice is unique, and I am proud of progress. Every single day, I speak with confidence.",
            durationSeconds: 8,
            isCorrect: false
          }
        ]
      }
    },
    {
      id: "w4d7-write-timed",
      sequence: 3,
      archetypeId: "WRITE_TIMED",
      widget: "write_timed",
      sectionLabel: "Writing",
      topic: "Reflecting on Cycle 1 growth",
      taskIntro: "Reflect on your speaking growth",
      instructions: "Take 3 minutes to reflect on this question: 'What did you learn about yourself this week?' Write a short, personal reflection on your journey.",
      subSkill: "Expression",
      activity: "Write",
      estimatedMinutes: 4,
      grammarRule: "Use reflective and forward-looking transition markers (e.g. 'I discovered', 'Moreover', 'In the future') to close Cycle 1.",
      targetWords: ["discovered", "moreover", "in the future"],
      writingDurationSeconds: 180,
      prompt: "What did you learn about yourself this week?",
      sampleAnswer: "This week, I discovered that I am much more resilient than I thought. Moreover, I realized that making mistakes is simply part of learning, not a failure. In the future, I will continue speaking up without fear.",
      answers: {
        correct: [
          {
            itemId: "reflection",
            text: "This week, I discovered that I am much more resilient than I thought. Moreover, I realized that making mistakes is simply part of learning, not a failure. In the future, I will continue speaking up without fear.",
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "reflection",
            text: "I learned that I speak better. I don't know what else.",
            isCorrect: false
          }
        ]
      },
      answerHints: [
        "Answer the question directly.",
        "Use at least two target words.",
        "Write at least two sentences."
      ]
    },
    {
      id: "w4d7-speak-debate",
      sequence: 4,
      archetypeId: "SPEAK_DEBATE",
      widget: "speak_debate",
      sectionLabel: "Speaking",
      topic: "Debate: Learn alone vs. with others",
      taskIntro: "Debate with the AI",
      instructions: "Debate the topic: 'Is it better to learn alone or with others?' State your opinion. The AI argues that learning alone is better. Listen to its statement and record your counter-argument.",
      subSkill: "Fluency",
      activity: "Speak",
      estimatedMinutes: 5,
      grammarRule: "Use strong opinion starters ('strongly believe', 'firmly advocate') and transition markers ('however', 'on the other hand') to frame your counter-argument.",
      targetWords: ["strongly believe", "however", "on the other hand"],
      speakingDurationSeconds: 60,
      debateContext: [
        { role: "AI Moderator", text: "Welcome to today's A1 Debate Arena! The topic is: 'Is it better to learn alone or with others?' Let's hear the AI's opening statement.", speaker: "ai" },
        { role: "AI Opponent", text: "I strongly argue that learning alone is far superior. It allows you to focus fully on your own weaknesses without any distractions from others, and you can study at your own pace.", speaker: "ai" },
        { role: "You", text: "While learning alone has benefits, I strongly believe learning with others is better. On the other hand, you can practice speaking with partners. However, group work makes learning much more fun!", speaker: "learner" }
      ],
      answers: {
        correct: [
          {
            itemId: "debate",
            transcript: "While learning alone has benefits, I strongly believe learning with others is better. On the other hand, you can practice speaking with partners. However, group work makes learning much more fun!",
            durationSeconds: 15,
            isCorrect: true
          }
        ],
        wrong: [
          {
            itemId: "debate",
            transcript: "I think learning alone is okay but learning with others is nice. I don't know.",
            durationSeconds: 9,
            isCorrect: false
          }
        ]
      }
    }
  ]
};

const taskDays: Partial<Record<CourseTrack, Record<number, Record<number, TaskDayData>>>> = {
  "24w": {
    1: {
      1: weekOneDayOneTasks,
      2: weekOneDayTwoTasks,
      3: weekOneDayThreeTasks,
      4: weekOneDayFourTasks,
      5: weekOneDayFiveTasks,
      6: weekOneDaySixTasks,
      7: weekOneDaySevenTasks,
    },
    2: {
      1: weekTwoDayOneTasks,
      2: weekTwoDayTwoTasks,
      3: weekTwoDayThreeTasks,
      4: weekTwoDayFourTasks,
      5: weekTwoDayFiveTasks,
      6: weekTwoDaySixTasks,
      7: weekTwoDaySevenTasks,
    },
    3: {
      1: weekThreeDayOneTasks,
      3: weekThreeDayThreeTasks,
      2: weekThreeDayTwoTasks,
      4: weekThreeDayFourTasks,
      5: weekThreeDayFiveTasks,
      6: weekThreeDaySixTasks,
      7: weekThreeDaySevenTasks,
    },
    4: {
      1: weekFourDayOneTasks,
      2: weekFourDayTwoTasks,
      3: weekFourDayThreeTasks,
      4: weekFourDayFourTasks,
      5: weekFourDayFiveTasks,
      6: weekFourDaySixTasks,
      7: weekFourDaySevenTasks,
    },
  },
  "48w": {},
};


export function getTaskDay(
  courseTrack: CourseTrack,
  week: number,
  day: number,
): TaskDayData | null {
  return taskDays[courseTrack]?.[week]?.[day] ?? null;
}
