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


const weekOneDayFour: TeachingDayData = {
  dayId: "day_24_01_04",
  courseTrack: "24w",
  week: 1,
  day: 4,
  title: "Articles - A, An, The",
  theme: "Grammar",
  cefr: "A1",
  focus: "Using a, an, and the correctly",
  isAuthored: true,
  messages: [
    {
      id: "teach-w1d4-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Today we are learning about articles: a, an, and the. Use 'a' before words starting with consonant sounds and 'an' before words starting with vowel sounds. Which one do you use before 'apple'?",
    },
    {
      id: "teach-w1d4-user-1",
      role: "you",
      content: "an apple",
    },
    {
      id: "teach-w1d4-ai-2",
      role: "ai",
      content:
        "Correct! 'An apple'. Now, we use 'the' when we talk about a specific thing or when there is only one, like 'the sun'. If you bought a book, and you are talking about that specific book, how would you refer to it?",
    },
    {
      id: "teach-w1d4-user-2",
      role: "you",
      content: "The book.",
    },
    {
      id: "teach-w1d4-ai-3",
      role: "ai",
      content:
        "Exactly. 'I bought a book. The book is interesting.' Ready to practice using a, an, and the?",
      actions: ["Start practice"],
    },
  ],
};

const weekOneDayFive: TeachingDayData = {
  dayId: "day_24_01_05",
  courseTrack: "24w",
  week: 1,
  day: 5,
  title: "Pronouns - Subject, Object, and Possessives",
  theme: "Grammar",
  cefr: "A1",
  focus: "Using subject, object, and possessive pronouns correctly in conversation and writing",
  isAuthored: true,
  messages: [
    {
      id: "teach-w1d5-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Today we are learning about pronouns! We have subject pronouns (I, you, he, she, it, we, they), object pronouns (me, you, him, her, it, us, them), and possessive pronouns (my/mine, your/yours, his, her/hers, our/ours, their/theirs). Subject pronouns do the action, and object pronouns receive it. For example: *She* calls *him*. What is the correct object pronoun to complete this: 'I like Sarah. I gave ___ a gift'?",
    },
    {
      id: "teach-w1d5-user-1",
      role: "you",
      content: "her",
    },
    {
      id: "teach-w1d5-ai-2",
      role: "ai",
      content:
        "Perfect! 'her' is the object pronoun for Sarah. Now, what is the possessive pronoun for 'this book belongs to me'? 'This book is ___'?",
    },
    {
      id: "teach-w1d5-user-2",
      role: "you",
      content: "mine",
    },
    {
      id: "teach-w1d5-ai-3",
      role: "ai",
      content:
        "Excellent! 'mine' shows possession. Ready to start practicing subject, object, and possessive pronouns?",
      actions: ["Start practice"],
    },
  ],
};

const weekOneDaySix: TeachingDayData = {
  dayId: "day_24_01_06",
  courseTrack: "24w",
  week: 1,
  day: 6,
  title: "Possessives - Nouns, Adjectives, and Pronouns",
  theme: "Grammar",
  cefr: "A1",
  focus: "Possessive 's, possessive adjectives (my, your, his, her, its, our, their), and possessive pronouns (mine, yours, his, hers, ours, theirs)",
  isAuthored: true,
  messages: [
    {
      id: "teach-w1d6-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Today we are mastering possessives! We use possessive 's for nouns (e.g. *Maria's* bag), possessive adjectives before a noun (e.g. *my* phone, *her* car), and possessive pronouns to replace a noun (e.g. That book is *mine*, it's *hers*). Complete this: 'This is John's laptop. It is ___ laptop' using a possessive adjective.",
    },
    {
      id: "teach-w1d6-user-1",
      role: "you",
      content: "his",
    },
    {
      id: "teach-w1d6-ai-2",
      role: "ai",
      content:
        "Spot on! 'his laptop'. Now complete this: 'The car belongs to Mary and Steve. The car is ___' using a possessive pronoun.",
    },
    {
      id: "teach-w1d6-user-2",
      role: "you",
      content: "theirs",
    },
    {
      id: "teach-w1d6-ai-3",
      role: "ai",
      content:
        "Perfect! 'theirs' shows ownership. Ready to start practicing possessive forms?",
      actions: ["Start practice"],
    },
  ],
};

const weekOneDaySeven: TeachingDayData = {
  dayId: "day_24_01_07",
  courseTrack: "24w",
  week: 1,
  day: 7,
  title: "Prepositions - Expressing Place, Time, and Context",
  theme: "Grammar",
  cefr: "A2",
  focus: "Prepositions in context (in, on, at, next to, between) for relationships, space, and confidence",
  isAuthored: true,
  messages: [
    {
      id: "teach-w1d7-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome to Day 7! Today is the final day of our grammar week. Since it's Sunday, we are going to wrap up and boost your confidence with prepositions like *in*, *on*, *at*, *next to*, and *between*. Prepositions can be tricky because they depend heavily on context. For example, do you sit *on* a chair or *in* an armchair? Let's check: which preposition do you use to describe being inside a room?",
    },
    {
      id: "teach-w1d7-user-1",
      role: "you",
      content: "in the room",
    },
    {
      id: "teach-w1d7-ai-2",
      role: "ai",
      content:
        "Exactly! You are *in* the room. And if something is resting on the flat surface of a table, what is the correct preposition?",
    },
    {
      id: "teach-w1d7-user-2",
      role: "you",
      content: "on the table",
    },
    {
      id: "teach-w1d7-ai-3",
      role: "ai",
      content:
        "Spot on! *On* the table. If you want to say something is in the middle of two objects, you use *between*. Now, ready for our confidence-boosting wrap-up tasks? Let's go!",
      actions: ["Start practice"],
    },
  ],
};

const weekTwoDayOne: TeachingDayData = {
  dayId: "day_24_02_01",
  courseTrack: "24w",
  week: 2,
  day: 1,
  title: "Greetings & Introductions",
  theme: "Communication",
  cefr: "A1",
  focus: "Greeting someone naturally, introducing yourself, and asking one simple follow-up question",
  isAuthored: true,
  messages: [
    {
      id: "teach-w2d1-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome to communication week. Today we will practice first meetings: say hello, share your name, and keep the conversation moving with one easy question.",
    },
    {
      id: "teach-w2d1-user-1",
      role: "you",
      content: "Hi, I'm Riya. Nice to meet you.",
    },
    {
      id: "teach-w2d1-ai-2",
      role: "ai",
      content:
        "That sounds natural. A simple introduction can be: Hi, I'm Riya. Nice to meet you. After that, ask one friendly question like 'Are you new here?' or 'What do you do?'",
    },
    {
      id: "teach-w2d1-user-2",
      role: "you",
      content: "Hi, I'm Riya. Nice to meet you. Are you new here?",
    },
    {
      id: "teach-w2d1-ai-3",
      role: "ai",
      content:
        "Excellent. Keep your tone warm and your sentences short. Hello, I'm..., Nice to meet you, and What do you do? are strong first-day phrases.",
    },
    {
      id: "teach-w2d1-ai-4",
      role: "ai",
      content: "Ready to try the practice task?",
      actions: ["Start practice"],
    },
  ],
};

const weekTwoDayTwo: TeachingDayData = {
  dayId: "day_24_02_02",
  courseTrack: "24w",
  week: 2,
  day: 2,
  title: "Asking & Answering Questions",
  theme: "Communication",
  cefr: "A1",
  focus: "Keeping conversations moving with short questions, polite requests, and clear answers",
  isAuthored: true,
  messages: [
    {
      id: "teach-w2d2-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Today we will keep a conversation moving. A good A1 conversation can use short questions like 'Are you free?', 'Can we meet?', and 'What do you like?'",
    },
    {
      id: "teach-w2d2-user-1",
      role: "you",
      content: "Can we meet after class?",
    },
    {
      id: "teach-w2d2-ai-2",
      role: "ai",
      content:
        "Nice. That question is clear and polite. When someone answers, add one simple follow-up question so the conversation does not stop.",
    },
    {
      id: "teach-w2d2-user-2",
      role: "you",
      content: "Sure. Where should we meet?",
    },
    {
      id: "teach-w2d2-ai-3",
      role: "ai",
      content:
        "Exactly. Question, answer, follow-up question. Keep your words short, listen for the speaker's intent, and answer directly.",
    },
    {
      id: "teach-w2d2-ai-4",
      role: "ai",
      content: "Ready to try the practice task?",
      actions: ["Start practice"],
    },
  ],
};

const weekTwoDayThree: TeachingDayData = {
  dayId: "day_24_02_03",
  courseTrack: "24w",
  week: 2,
  day: 3,
  title: "Talking About Daily Life",
  theme: "Communication",
  cefr: "A1",
  focus: "Speak about routines naturally with clear sequence words and short opinions",
  isAuthored: true,
  messages: [
    {
      id: "teach-w2d3-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Today we will talk about daily life in a natural way. A clear routine usually has a beginning, middle, and ending. Tell me one thing you do after you wake up.",
    },
    {
      id: "teach-w2d3-user-1",
      role: "you",
      content: "After I wake up, I drink water and check my phone.",
    },
    {
      id: "teach-w2d3-ai-2",
      role: "ai",
      content:
        "Good. To make a routine sound smooth, use sequence words: first, then, after that, and finally. Write one short routine with two sequence words.",
    },
    {
      id: "teach-w2d3-user-2",
      role: "you",
      content: "First, I brush my teeth. Then I make tea.",
    },
    {
      id: "teach-w2d3-ai-3",
      role: "ai",
      content:
        "Nice. You can also add a simple opinion: I prefer mornings because I feel fresh. Answer this: do you prefer morning or evening?",
    },
    {
      id: "teach-w2d3-user-3",
      role: "you",
      content: "I prefer morning because I feel fresh and calm.",
    },
    {
      id: "teach-w2d3-ai-4",
      role: "ai",
      content: "Ready to try the practice task?",
      actions: ["Start practice"],
    },
  ],
};

const weekTwoDayFour: TeachingDayData = {
  dayId: "day_24_02_04",
  courseTrack: "24w",
  week: 2,
  day: 4,
  title: "Shopping & Ordering",
  theme: "Communication",
  cefr: "A1",
  focus: "Handle real-world interactions like ordering food and buying items",
  isAuthored: true,
  messages: [
    {
      id: "teach-w2d4-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome to Day 4! Today we will practice shopping and ordering. When ordering, be polite and clear. You can say 'Could I have...' or 'I'd like to get...'. What is a polite way to ask for a coffee?",
    },
    {
      id: "teach-w2d4-user-1",
      role: "you",
      content: "Could I have a coffee, please?",
    },
    {
      id: "teach-w2d4-ai-2",
      role: "ai",
      content:
        "Exactly! 'Could I have...' is very polite. Now try ordering a slice of chocolate cake too.",
    },
    {
      id: "teach-w2d4-user-2",
      role: "you",
      content: "I'd like to get a coffee and a slice of chocolate cake, please.",
    },
    {
      id: "teach-w2d4-ai-3",
      role: "ai",
      content:
        "Perfect. When buying items in a shop, you might also describe what you need. Today we will read a dialogue about shopping, listen to a café order, write a message from a shopping list, and roleplay ordering items!",
    },
    {
      id: "teach-w2d4-ai-4",
      role: "ai",
      content: "Ready to try the practice task?",
      actions: ["Start practice"],
    },
  ],
};

const weekTwoDayFive: TeachingDayData = {
  dayId: "day_24_02_05",
  courseTrack: "24w",
  week: 2,
  day: 5,
  title: "Asking for Help & Directions",
  theme: "Survival communication",
  cefr: "A1",
  focus: "Ask for help, understand simple directions, and describe map locations",
  isAuthored: true,
  messages: [
    {
      id: "teach-w2d5-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Today we will practise survival English for asking for help and directions. Useful phrases are: Excuse me, could you help me?, Where is the station?, go straight, turn left, and it is next to...",
    },
    {
      id: "teach-w2d5-user-1",
      role: "you",
      content: "Excuse me, could you help me?",
    },
    {
      id: "teach-w2d5-ai-2",
      role: "ai",
      content:
        "Good. Now add the place you need: 'Excuse me, could you help me? Where is the station?' This sounds polite and clear.",
    },
    {
      id: "teach-w2d5-user-2",
      role: "you",
      content: "Excuse me, could you help me? Where is the station?",
    },
    {
      id: "teach-w2d5-ai-3",
      role: "ai",
      content:
        "Nice. When someone gives directions, listen for action words and landmarks: go straight, turn left, on your right, next to the pharmacy. Today you will read directions, infer what someone needs, write a help request, and describe a simple map.",
    },
    {
      id: "teach-w2d5-ai-4",
      role: "ai",
      content: "Ready to try the practice task?",
      actions: ["Start practice"],
    },
  ],
};

const weekTwoDaySix: TeachingDayData = {
  dayId: "day_24_02_06",
  courseTrack: "24w",
  week: 2,
  day: 6,
  title: "Phone & Online Conversations",
  theme: "Modern communication",
  cefr: "A1",
  focus: "Identify formal, casual, and urgent tone; rewrite messages; and enjoy casual smalltalk",
  isAuthored: true,
  messages: [
    {
      id: "teach-w2d6-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Today we will use English for phone calls and online messages. The same message can sound formal, casual, or urgent. Read this: 'Could you please call me when you are free?' What tone do you hear?",
    },
    {
      id: "teach-w2d6-user-1",
      role: "you",
      content: "It sounds formal and polite.",
    },
    {
      id: "teach-w2d6-ai-2",
      role: "ai",
      content:
        "Exactly. Now make it casual for a friend: 'Can you call me when you're free?' Shorter words often feel friendlier in chats.",
    },
    {
      id: "teach-w2d6-user-2",
      role: "you",
      content: "Can you call me when you're free?",
    },
    {
      id: "teach-w2d6-ai-3",
      role: "ai",
      content:
        "Good. In phone calls, listen for urgency words like now, quickly, or in five minutes. After that, we will finish with relaxed smalltalk about weather and weekend plans.",
    },
    {
      id: "teach-w2d6-ai-4",
      role: "ai",
      content: "Ready to try the practice task?",
      actions: ["Start practice"],
    },
  ],
};

const weekTwoDaySeven: TeachingDayData = {
  dayId: "day_24_02_07",
  courseTrack: "24w",
  week: 2,
  day: 7,
  title: "Small Talk & Social Interaction",
  theme: "Communication",
  cefr: "A1",
  focus: "Build natural fluency with friendly chat, week review, short messages, and a spoken wrap-up",
  isAuthored: true,
  messages: [
    {
      id: "teach-w2d7-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Today is our small-talk wrap-up. Natural fluency does not mean long sentences. It means you can connect ideas, respond warmly, and keep the conversation moving.",
    },
    {
      id: "teach-w2d7-user-1",
      role: "you",
      content: "So I can use short friendly sentences?",
    },
    {
      id: "teach-w2d7-ai-2",
      role: "ai",
      content:
        "Exactly. A good chat can use simple connectors: first, then, also, but, and because. Tell me one good thing from your week and one busy thing.",
    },
    {
      id: "teach-w2d7-user-2",
      role: "you",
      content: "I met my friend, but work was busy.",
    },
    {
      id: "teach-w2d7-ai-3",
      role: "ai",
      content:
        "Nice. That already sounds like real small talk. Today you will read a short chat, retell a casual conversation, write to a friend, and give a low-pressure summary of your week.",
    },
    {
      id: "teach-w2d7-ai-4",
      role: "ai",
      content: "Ready to try the practice task?",
      actions: ["Start practice"],
    },
  ],
};

const weekThreeDayOne: TeachingDayData = {
  dayId: "day_24_03_01",
  courseTrack: "24w",
  week: 3,
  day: 1,
  title: "People & Relationships - Family, Friends & Roles",
  theme: "Vocabulary",
  cefr: "A1",
  focus: "Vocabulary for describing family, friends, colleagues, neighbours, and their roles",
  isAuthored: true,
  messages: [
    {
      id: "teach-w3d1-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome to Week 3! Today we will learn words to describe people in our lives: *family*, *friends*, and *roles*. For example, an *uncle* is your parent's brother, and a *colleague* is someone you work with. Who is someone you work with?",
    },
    {
      id: "teach-user-1",
      role: "you",
      content: "A colleague.",
    },
    {
      id: "teach-ai-2",
      role: "ai",
      content:
        "Perfect! Now, what do you call the person who lives next door to you?",
    },
    {
      id: "teach-user-2",
      role: "you",
      content: "A neighbour.",
    },
    {
      id: "teach-ai-3",
      role: "ai",
      content:
        "Exactly. *Colleague* for work, *neighbour* for where you live, and *uncle* for family. Today we will match people to their definitions, listen to a scenario, transform sentences, and describe a family photo!",
    },
    {
      id: "teach-ai-4",
      role: "ai",
      content: "Ready to try the practice task?",
      actions: ["Start practice"],
    },
  ],
};

const weekThreeDayThree: TeachingDayData = {
  dayId: "day_24_03_03",
  courseTrack: "24w",
  week: 3,
  day: 3,
  title: "Places & Locations - City, Home & Directions",
  theme: "Vocabulary",
  cefr: "A1",
  focus: "Vocabulary for places, city locations, and describing neighbourhoods",
  isAuthored: true,
  messages: [
    {
      id: "teach-w3d3-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome back! Today we are learning about places and locations. A *market* is where you buy fresh food, a *station* is where you catch a train, and a *suburb* is a quiet residential area outside the city centre. Where do you usually go to buy fresh vegetables?",
    },
    {
      id: "teach-w3d3-user-1",
      role: "you",
      content: "I go to the market.",
    },
    {
      id: "teach-w3d3-ai-2",
      role: "ai",
      content:
        "Good! And if you want to travel to another city, where do you go?",
    },
    {
      id: "teach-w3d3-user-2",
      role: "you",
      content: "I go to the station.",
    },
    {
      id: "teach-w3d3-ai-3",
      role: "ai",
      content:
        "Exactly. Today we will match place words, listen to someone describe their neighbourhood, write a short paragraph about your area, and describe a city picture!",
    },
    {
      id: "teach-w3d3-ai-4",
      role: "ai",
      content: "Ready to try the practice task?",
      actions: ["Start practice"],
    },
  ],
};

const weekThreeDayTwo: TeachingDayData = {
  dayId: "day_24_03_02",
  courseTrack: "24w",
  week: 3,
  day: 2,
  title: "Food & Eating - Meals, Ingredients & Taste",
  theme: "Vocabulary",
  cefr: "A2",
  focus: "Vocabulary for meals, food ingredients, and describing taste (delicious, flavourful, bland, savoury)",
  isAuthored: true,
  messages: [
    {
      id: "teach-w3d2-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome back! Today we are focusing on *Food & Eating*. We will learn vocabulary for meals, ingredients, and how things taste. For example, *savoury* describes salty or spicy food, while *bland* means lacking flavour. What is a word you would use to describe a dish that has a very rich and pleasant taste?",
    },
    {
      id: "teach-w3d2-user-1",
      role: "you",
      content: "Delicious or flavourful.",
    },
    {
      id: "teach-w3d2-ai-2",
      role: "ai",
      content:
        "Spot on! Both *delicious* and *flavourful* are wonderful words to upgrade from just saying 'good'. Now, when you order food, it's helpful to be very specific about ingredients. Let's see: what are two typical ingredients in a fresh salad?",
    },
    {
      id: "teach-w3d2-user-2",
      role: "you",
      content: "Lettuce and tomatoes.",
    },
    {
      id: "teach-w3d2-ai-3",
      role: "ai",
      content:
        "Excellent. Lettuce and tomatoes are perfect examples of fresh ingredients. Today we'll read a menu passage to infer the meaning of 'savoury', listen to a café order, upgrade simple food descriptions to premium words, and describe your absolute favourite meal in a timed speech!",
    },
    {
      id: "teach-w3d2-ai-4",
      role: "ai",
      content: "Ready to start today's practice?",
      actions: ["Start practice"],
    },
  ],
};

const weekThreeDayFour: TeachingDayData = {
  dayId: "day_24_03_04",
  courseTrack: "24w",
  week: 3,
  day: 4,
  title: "Work & Jobs - Roles, Actions & Workplace",
  theme: "Vocabulary",
  cefr: "A1",
  focus: "Vocabulary for job roles, workplace actions, and describing what people do at work",
  isAuthored: true,
  messages: [
    {
      id: "teach-w3d4-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome back! Today we are learning about *Work & Jobs*. A *manager* is someone who leads a team, while a *receptionist* greets visitors and answers calls. What do you call someone who is *responsible for* a project?",
    },
    {
      id: "teach-w3d4-user-1",
      role: "you",
      content: "A manager or a team leader.",
    },
    {
      id: "teach-w3d4-ai-2",
      role: "ai",
      content:
        "Exactly! 'Responsible for' means the person takes care of that task. And if someone *manages* a team, they organise and lead people. Now, what verb do you use when a person *works in* a place like an office or a hospital?",
    },
    {
      id: "teach-w3d4-user-2",
      role: "you",
      content: "He works in an office.",
    },
    {
      id: "teach-w3d4-ai-3",
      role: "ai",
      content:
        "Perfect. Today we will read a job ad and infer what 'responsible for' means, listen to a short job description and type the key words, rewrite a sentence about work using new vocabulary, and talk about a job you know for 60 seconds!",
    },
    {
      id: "teach-w3d4-ai-4",
      role: "ai",
      content: "Ready to start today's practice?",
      actions: ["Start practice"],
    },
  ],
};

const weekThreeDayFive: TeachingDayData = {
  dayId: "day_24_03_05",
  courseTrack: "24w",
  week: 3,
  day: 5,
  title: "Time & Schedules - Days, Months & Routines",
  theme: "Vocabulary",
  cefr: "A2",
  focus: "Vocabulary for time expressions: fortnightly, quarterly, deadline, daily, weekly, occasionally",
  isAuthored: true,
  messages: [
    {
      id: "teach-w3d5-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome to Friday! Today we are learning vocabulary for time and schedules. Words like *daily*, *weekly*, and *fortnightly* tell us how often something happens. A *deadline* is the latest time you must finish a task. If something happens every two weeks, what word describes it?",
    },
    {
      id: "teach-w3d5-user-1",
      role: "you",
      content: "Fortnightly.",
    },
    {
      id: "teach-w3d5-ai-2",
      role: "ai",
      content:
        "Exactly! *Fortnightly* means every two weeks. And if a company holds a big meeting only four times a year, what time word fits?",
    },
    {
      id: "teach-w3d5-user-2",
      role: "you",
      content: "Quarterly.",
    },
    {
      id: "teach-w3d5-ai-3",
      role: "ai",
      content:
        "Spot on! *Quarterly* means four times a year. Today you will match time words to their meanings, listen to someone plan their week, transform sentences using time adverbs, and describe a weekly planner image. Ready?",
    },
    {
      id: "teach-w3d5-ai-4",
      role: "ai",
      content: "Ready to try the practice task?",
      actions: ["Start practice"],
    },
  ],
};

const weekThreeDaySix: TeachingDayData = {
  dayId: "day_24_03_06",
  courseTrack: "24w",
  week: 3,
  day: 6,
  title: "Feelings & Emotions - Express inner states",
  theme: "Vocabulary",
  cefr: "A2",
  focus: "Vocabulary for expressing feelings and emotions: overwhelmed, content, devastated, disappointed, disheartened",
  isAuthored: true,
  messages: [
    {
      id: "teach-w3d6-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome to Saturday! Today we are focusing on *Feelings & Emotions*. Sometimes 'sad' or 'happy' isn't enough. If you feel peaceful and satisfied, you might say you are *content*. If you have too much to do and feel stressed, what word could you use?",
    },
    {
      id: "teach-w3d6-user-1",
      role: "you",
      content: "Overwhelmed.",
    },
    {
      id: "teach-w3d6-ai-2",
      role: "ai",
      content:
        "Exactly. *Overwhelmed* describes that feeling perfectly. Now, if you are very sad because something didn't happen the way you hoped, you might say you are *disappointed*. What is a stronger word for feeling extremely sad or shocked?",
    },
    {
      id: "teach-w3d6-user-2",
      role: "you",
      content: "Devastated.",
    },
    {
      id: "teach-w3d6-ai-3",
      role: "ai",
      content:
        "Spot on! *Devastated* is a powerful word. Today we will read a diary entry to infer emotions, listen to someone describe how they feel, upgrade simple emotion words in writing, and talk about how you felt this week. Ready?",
    },
    {
      id: "teach-w3d6-ai-4",
      role: "ai",
      content: "Ready to try the practice task?",
      actions: ["Start practice"],
    },
  ],
};

const weekThreeDaySeven: TeachingDayData = {
  dayId: "day_24_03_07",
  courseTrack: "24w",
  week: 3,
  day: 7,
  title: "Review & Word Building - Consolidate the week's vocab",
  theme: "Vocabulary",
  cefr: "A2",
  focus: "Consolidate the week's vocabulary covering People, Food, Places, Work, Time, and Feelings",
  isAuthored: true,
  messages: [
    {
      id: "teach-w3d7-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome to Day 7! Today is our weekly review day. We will consolidate all the vocabulary we've learned this week across six different topics: People, Food, Places, Work, Time, and Feelings. Are you ready for a challenge?",
    },
    {
      id: "teach-w3d7-user-1",
      role: "you",
      content: "Yes, I'm ready!",
    },
    {
      id: "teach-w3d7-ai-2",
      role: "ai",
      content:
        "Great! Reviewing helps move words from your short-term to your long-term memory. We'll start by matching words to their definitions, then listen to a short story. What word did we learn this week that means 'to feel very sad or shocked'?",
    },
    {
      id: "teach-w3d7-user-2",
      role: "you",
      content: "Devastated.",
    },
    {
      id: "teach-w3d7-ai-3",
      role: "ai",
      content:
        "Spot on! Today you'll also write a short paragraph using at least 5 new words, and finish with a 90-second speaking challenge. Let's go!",
    },
    {
      id: "teach-w3d7-ai-4",
      role: "ai",
      content: "Ready to start today's practice?",
      actions: ["Start practice"],
    },
  ],
};

const weekFourDayOne: TeachingDayData = {
  dayId: "day_24_04_01",
  courseTrack: "24w",
  week: 4,
  day: 1,
  title: "Finding your voice - Start speaking without fear",
  theme: "Confidence",
  cefr: "A2",
  focus: "Start speaking without fear: simple motivation stories, shadowing practice, low-stakes transforms, and reading aloud.",
  isAuthored: true,
  messages: [
    {
      id: "teach-w4d1-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome to Week 4 Day 1! This week is all about 'Finding your voice'. Today we will learn to start speaking without fear. Many learners are afraid of making mistakes, but mistakes are just stepping stones to fluency. Let's begin by shifting our mindset: can you say one positive thing about practicing English?",
    },
    {
      id: "teach-w4d1-user-1",
      role: "you",
      content: "It helps me connect with people.",
    },
    {
      id: "teach-w4d1-ai-2",
      role: "ai",
      content:
        "That is beautiful! Yes, practicing English is a bridge to connect with the world. Today, we will read a short motivational story, practice shadowing a confident voice to hear yourself speaking well, rewrite a negative sentence into positive self-expression, and finish by reading a short paragraph aloud. Ready to start?",
    },
    {
      id: "teach-w4d1-user-2",
      role: "you",
      content: "Yes, I am ready to start!",
    },
    {
      id: "teach-w4d1-ai-3",
      role: "ai",
      content: "Awesome! Let's get right into the practice tasks.",
      actions: ["Start practice"],
    },
  ],
};

const weekFourDayTwo: TeachingDayData = {
  dayId: "day_24_04_02",
  courseTrack: "24w",
  week: 4,
  day: 2,
  title: "Sharing opinions - Say what you think clearly",
  theme: "Communication",
  cefr: "B1",
  focus: "State your opinion clearly and confidently, notice the difference between confident and uncertain tone, and write/speak under time pressure.",
  isAuthored: true,
  messages: [
    {
      id: "teach-w4d2-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome to Week 4 Day 2! Today we are learning how to share opinions clearly and confidently. Sharing opinions is not just about what you say, but *how* you say it. Compare these two phrases: 'I'm absolutely convinced that remote work is the future,' vs 'I guess remote work is okay, but I don't know.' Which one sounds more confident to you?",
    },
    {
      id: "teach-w4d2-user-1",
      role: "you",
      content: "The first one sounds much more confident.",
    },
    {
      id: "teach-w4d2-ai-2",
      role: "ai",
      content:
        "Exactly. The first statement uses strong, positive words like *convinced* and *absolutely*. The second statement uses hesitation markers like *guess* and *I don't know*, which make it sound uncertain. Today we'll practice distinguishing confident tones from hesitant ones, and train your brain to write and speak your thoughts clearly without overthinking. Ready to start?",
    },
    {
      id: "teach-w4d2-user-2",
      role: "you",
      content: "Yes, let's start the practice!",
    },
    {
      id: "teach-w4d2-ai-3",
      role: "ai",
      content: "Awesome! Let's get right into the practice tasks.",
      actions: ["Start practice"],
    },
  ],
};

const weekFourDayThree: TeachingDayData = {
  dayId: "day_24_04_03",
  courseTrack: "24w",
  week: 4,
  day: 3,
  title: "Describing yourself - Talk about who you are",
  theme: "Confidence",
  cefr: "A2",
  focus: "Talk about who you are: build expressive self-identity, distinguish formal vs. casual introductions, and practice safe self-expression through describing others.",
  isAuthored: true,
  messages: [
    {
      id: "teach-w4d3-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome to Week 4 Day 3! Today we are learning how to describe ourselves. Expressing who you are is a powerful way to connect with others. How would you introduce yourself in one simple sentence?",
    },
    {
      id: "teach-w4d3-user-1",
      role: "you",
      content: "I am a student and I love reading books.",
    },
    {
      id: "teach-w4d3-ai-2",
      role: "ai",
      content:
        "Great start! Describing yourself can be formal (for work or interviews) or casual (for meeting friends). For example, 'I am a software engineer' vs 'I build apps'. Today, we'll read a bio passage to see how others introduce themselves, listen to formal vs. casual tones, transform simple sentences into richer descriptions, and describe a person doing an activity to practice indirect expression. Ready to start?",
    },
    {
      id: "teach-w4d3-user-2",
      role: "you",
      content: "Yes, let's begin!",
    },
    {
      id: "teach-w4d3-ai-3",
      role: "ai",
      content: "Wonderful! Let's get right into the practice tasks.",
      actions: ["Start practice"],
    },
  ],
};

const weekFourDayFour: TeachingDayData = {
  dayId: "day_24_04_04",
  courseTrack: "24w",
  week: 4,
  day: 4,
  title: "Handling awkward moments - Recover from mistakes gracefully",
  theme: "Confidence",
  cefr: "B1",
  focus: "Recover from mistakes gracefully: short dialogue tone shift identification, mid-sentence self-correction shadowing, timed reflection write, and unpredictable small talk challenge.",
  isAuthored: true,
  messages: [
    {
      id: "teach-w4d4-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome to Week 4 Day 4! Today we are discussing 'Handling awkward moments' and learning how to 'Recover from mistakes gracefully'. When speaking a second language, making mistakes is completely normal. What is your biggest worry when you make a slip-up while speaking?",
    },
    {
      id: "teach-w4d4-user-1",
      role: "you",
      content: "I'm afraid people will judge me or I'll freeze.",
    },
    {
      id: "teach-w4d4-ai-2",
      role: "ai",
      content:
        "That is very common! But the secret is that people rarely judge slips — they notice how you recover. If you recover smoothly and confidently, the mistake vanishes. Today, we'll read dialogues to see tone shifts after mistakes, listen and shadow mid-sentence corrections, write a timed reflection on mistakes, and challenge ourselves with unpredictable small talk. Ready?",
    },
    {
      id: "teach-w4d4-user-2",
      role: "you",
      content: "Yes, let's start the practice!",
    },
    {
      id: "teach-w4d4-ai-3",
      role: "ai",
      content: "Fantastic! Let's begin today's practice tasks.",
      actions: ["Start practice"],
    },
  ],
};

const weekFourDayFive: TeachingDayData = {
  dayId: "day_24_04_05",
  courseTrack: "24w",
  week: 4,
  day: 5,
  title: "Talking about interests - Express hobbies & passions",
  theme: "Confidence",
  cefr: "A2",
  focus: "Expressing your passions and interests with confidence: light reading about stargazing, enthusiastic gardening monologues, sentence transformation for premium vocabulary, and describing an outdoor hobby scene.",
  isAuthored: true,
  messages: [
    {
      id: "teach-w4d5-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome to Week 4 Day 5! Today is all about expressing our interests, hobbies, and passions. Sharing what you love is one of the easiest ways to build connection and speak with natural confidence and enthusiasm. What is one hobby you really enjoy in your free time?",
    },
    {
      id: "teach-w4d5-user-1",
      role: "you",
      content: "I really love watching movies and reading books.",
    },
    {
      id: "teach-w4d5-ai-2",
      role: "ai",
      content:
        "That sounds wonderful! Movies and books are amazing ways to unwind and stimulate the mind. When we talk about our passions, we naturally sound more expressive. Today we will read a light and relatable story about stargazing, listen to someone enthusiastically describing their gardening hobby, learn to transform basic hobby descriptions into premium expressive statements, and describe a cozy hobby scene. Ready to start?",
    },
    {
      id: "teach-w4d5-user-2",
      role: "you",
      content: "Yes, I am ready to start the practice!",
    },
    {
      id: "teach-w4d5-ai-3",
      role: "ai",
      content: "Awesome! Let's get right into the practice tasks.",
      actions: ["Start practice"],
    },
  ],
};

const weekFourDaySix: TeachingDayData = {
  dayId: "day_24_04_06",
  courseTrack: "24w",
  week: 4,
  day: 6,
  title: "Presenting yourself - Speak with structure and poise",
  theme: "Confidence",
  cefr: "B1",
  focus: "Presenting yourself with poise: identify differences between hesitant and polished introductions, train your ear for vocal confidence tone shifts, timed write a 3-sentence self-introduction, and record a structured 90-second personal presentation.",
  isAuthored: true,
  messages: [
    {
      id: "teach-w4d6-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome to Week 4 Day 6! Today, our focus is 'Presenting yourself' and learning how to 'Speak with structure and poise'. When introduced in professional or social settings, a structured and polished introduction makes a world of difference. What do you usually include when introducing yourself to someone new?",
    },
    {
      id: "teach-w4d6-user-1",
      role: "you",
      content: "I usually say my name, where I work, and maybe what I like to do.",
    },
    {
      id: "teach-w4d6-ai-2",
      role: "ai",
      content:
        "That is a great foundation! Adding structure and speaking with poise helps you sound more confident. Today, we will read and compare a hesitant vs. polished self-introduction, listen to moment-by-moment tone shifts to train our ear, write a timed 3-sentence note draft as a scaffold, and then record a robust 90-second self-introduction. Ready to begin?",
    },
    {
      id: "teach-w4d6-user-2",
      role: "you",
      content: "Yes, I am ready to start the practice!",
    },
    {
      id: "teach-w4d6-ai-3",
      role: "ai",
      content: "Excellent! Let's start the practice tasks for today.",
      actions: ["Start practice"],
    },
  ],
};

const weekFourDaySeven: TeachingDayData = {
  dayId: "day_24_04_07",
  courseTrack: "24w",
  week: 4,
  day: 7,
  title: "Full Confidence Showcase",
  theme: "Confidence",
  cefr: "A1/A2",
  focus: "Cycle 1 wrap-up: show your growth with inspiring reading, shadowing, reflective writing, and a friendly debate task.",
  isAuthored: true,
  messages: [
    {
      id: "teach-w4d7-ai-1",
      role: "ai",
      name: "LingosAI",
      content:
        "Welcome to Week 4 Day 7! Today is the final day of Week 4 and the wrap-up of Cycle 1! It is time for a 'Full confidence showcase' to reflect on your incredible journey. Looking back to Day 1, how do you feel about your speaking confidence now?",
    },
    {
      id: "teach-w4d7-user-1",
      role: "you",
      content: "I feel much more comfortable and less afraid of making mistakes!",
    },
    {
      id: "teach-w4d7-ai-2",
      role: "ai",
      content:
        "That is marvelous! That growth is exactly what Cycle 1 is about. Today, you'll read an inspiring passage about someone overcoming speaker anxiety, shadow a confident speaker, write a timed reflection on your personal growth, and finish with a simple debate: 'Is it better to learn alone or with others?' I'll take the opposite side. Ready to show off your growth?",
    },
    {
      id: "teach-w4d7-user-2",
      role: "you",
      content: "Yes, I am ready for the finale!",
    },
    {
      id: "teach-w4d7-ai-3",
      role: "ai",
      content: "Outstanding! Let's launch into your showcase.",
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
      4: weekOneDayFour,
      5: weekOneDayFive,
      6: weekOneDaySix,
      7: weekOneDaySeven,
    },
    2: {
      1: weekTwoDayOne,
      2: weekTwoDayTwo,
      3: weekTwoDayThree,
      4: weekTwoDayFour,
      5: weekTwoDayFive,
      6: weekTwoDaySix,
      7: weekTwoDaySeven,
    },
    3: {
      1: weekThreeDayOne,
      2: weekThreeDayTwo,
      3: weekThreeDayThree,
      4: weekThreeDayFour,
      5: weekThreeDayFive,
      6: weekThreeDaySix,
      7: weekThreeDaySeven,
    },
    4: {
      1: weekFourDayOne,
      2: weekFourDayTwo,
      3: weekFourDayThree,
      4: weekFourDayFour,
      5: weekFourDayFive,
      6: weekFourDaySix,
      7: weekFourDaySeven,
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
