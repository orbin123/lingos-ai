const fs = require('fs');
const content = fs.readFileSync('/Users/orbin/Documents/GitHub/ai-english-tutor/frontend/src/app/test_chat_session/tasks/source.ts', 'utf8');

// Update TaskWidgetKind
let newContent = content.replace(
  /\| "speak_record";/,
  `| "speak_record"\n  | "read_word_match"\n  | "speak_pic_desc";`
);

// Add Interfaces
const interfaceStr = `
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

export type SessionTask =`;

newContent = newContent.replace(/export type SessionTask =/, interfaceStr);

// Add to SessionTask union
newContent = newContent.replace(
  /\| SpeakRecordTask;/,
  `| SpeakRecordTask\n  | ReadWordMatchTask\n  | SpeakPicDescTask;`
);

fs.writeFileSync('/Users/orbin/Documents/GitHub/ai-english-tutor/frontend/src/app/test_chat_session/tasks/source.ts', newContent);
