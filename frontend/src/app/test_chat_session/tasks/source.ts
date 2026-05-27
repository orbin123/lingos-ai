import type { AnswerView, CourseTrack } from "../teaching/source";

export type TaskWidgetKind =
  | "error_spotting"
  | "fill_blanks"
  | "listen_cloze"
  | "listen_mcq"
  | "read_comp_mcq"
  | "listen_dictation"
  | "error_correction"
  | "sentence_transform"
  | "open_text"
  | "read_aloud"
  | "speak_record"
  | "read_word_match"
  | "speak_pic_desc";

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

export interface ReadCompMcqTask extends BaseTask {
  widget: "read_comp_mcq";
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

export interface SpeakPicDescTask extends BaseTask {
  widget: "speak_pic_desc";
  imageUrl: string;
  imageAlt: string;
  grammarRule: string;
  speakingDurationSeconds: number;
  answers: Record<AnswerView, SpeakingAnswer[]>;
}

export type SessionTask =
  | ErrorSpottingTask
  | FillBlanksTask
  | ListenClozeTask
  | ListenMcqTask
  | ReadCompMcqTask
  | ListenDictationTask
  | ErrorCorrectionTask
  | SentenceTransformTask
  | OpenTextTask
  | ReadAloudTask
  | SpeakRecordTask
  | ReadWordMatchTask
  | SpeakPicDescTask;

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

const taskDays: Partial<Record<CourseTrack, Record<number, Record<number, TaskDayData>>>> = {
  "24w": {
    1: {
      1: weekOneDayOneTasks,
      2: weekOneDayTwoTasks,
      3: weekOneDayThreeTasks,
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
