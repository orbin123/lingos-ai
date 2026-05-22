import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import vm from "node:vm";
import ts from "typescript";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const require = createRequire(import.meta.url);

function loadTypeScriptModule(relativePath) {
  const filename = path.join(root, relativePath);
  const source = fs.readFileSync(filename, "utf8");
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2020,
    },
  });
  const cjsModule = { exports: {} };
  vm.runInNewContext(outputText, {
    URLSearchParams,
    encodeURIComponent,
    exports: cjsModule.exports,
    module: cjsModule,
    process: { env: {} },
    require,
  });
  return cjsModule.exports;
}

const authoring = loadTypeScriptModule("src/lib/authoring-chat.ts");
const widgetNormalize = loadTypeScriptModule(
  "src/components/task/task-widgets/normalize.ts",
);
const fillBlanksNormalize = loadTypeScriptModule(
  "src/components/task/task-widgets/fillBlanksNormalize.ts",
);
const listenNormalize = loadTypeScriptModule(
  "src/components/task/task-widgets/listenAndRespondNormalize.ts",
);

test("authoring start path includes week and day query params", () => {
  assert.equal(
    authoring.authoringStartPath({ week: 1, day: 3 }),
    "/api/dev/learning/sessions/start?week=1&day=3",
  );
});

test("authoring websocket omits token and uses dev path", () => {
  assert.equal(
    authoring.learningWebSocketUrl("http://localhost:8000", "abc", {
      authoring: true,
      token: "secret",
    }),
    "ws://localhost:8000/dev/ws/learning/abc",
  );
});

test("production websocket keeps token on production path", () => {
  assert.equal(
    authoring.learningWebSocketUrl("http://localhost:8000", "abc", {
      authoring: false,
      token: "secret",
    }),
    "ws://localhost:8000/ws/learning/abc?token=secret",
  );
});

test("restart path switches in authoring mode", () => {
  assert.equal(
    authoring.learningRestartPath("a/b", true),
    "/api/dev/learning/sessions/a%2Fb/restart",
  );
  assert.equal(
    authoring.learningRestartPath("a/b", false),
    "/api/learning/sessions/a%2Fb/restart",
  );
});

test("widget normalization accepts legacy FillInBlanks name", () => {
  assert.equal(widgetNormalize.normalizeWidgetKey("FillInBlanks"), "fill_in_blanks");
  assert.equal(widgetNormalize.normalizeWidgetKey("fill_in_blanks"), "fill_in_blanks");
});

test("widget normalization keeps open text stable", () => {
  assert.equal(widgetNormalize.normalizeWidgetKey("open_text"), "open_text");
  assert.equal(widgetNormalize.normalizeWidgetKey("OpenTextList"), "open_text");
});

test("widget normalization leaves unknown widgets untouched", () => {
  assert.equal(widgetNormalize.normalizeWidgetKey("MysteryWidget"), "MysteryWidget");
});

test("open text widget supports before and after writing states", () => {
  const source = fs.readFileSync(
    path.join(root, "src/components/task/task-widgets/OpenTextWidget.tsx"),
    "utf8",
  );

  assert.match(source, /items\.map/);
  assert.match(source, /\[it\.item_id\]: next/);
  assert.match(source, /state === "after"/);
  assert.match(source, /Sample answer/);
  assert.match(source, /disabled=\{!allFilled\}/);
});

test("open-ended feedback shows improved version instead of wrong answer styling", () => {
  const source = fs.readFileSync(
    path.join(root, "src/app/task/chat/[sessionId]/page.tsx"),
    "utf8",
  );

  assert.match(source, /function isOpenEndedFeedbackWidget/);
  assert.match(source, /Your version:/);
  assert.match(source, /Improved version:/);
  assert.match(source, /!openEndedFeedback && mistake\.user_wrote/);
});

test("dashboard see results opens the daily scorecard instead of starting chat", () => {
  const source = fs.readFileSync(
    path.join(root, "src/components/dashboard/DailyTaskPanel.tsx"),
    "utf8",
  );

  assert.match(source, /plan\.activities\.every/);
  assert.ok(source.includes("router.push(`/sessions/${plan.session_id}/scorecard`)"));
});

test("fill blanks normalization keeps native items", () => {
  const payload = fillBlanksNormalize.normalizeFillInBlanksPayload({
    widget: "fill_in_blanks",
    instructions: "Use the right verb.",
    items: [
      {
        item_id: "b1",
        sentence_with_blank: "I ___ daily.",
        correct_answer: "work",
        explanation: "I uses the base verb.",
      },
    ],
  });

  assert.equal(payload.total_blanks, 1);
  assert.equal(payload.items[0].blank_id, "b1");
  assert.equal(payload.items[0].correct_answer, "work");
});

test("fill blanks normalization derives items from legacy activity payloads", () => {
  const payload = fillBlanksNormalize.normalizeFillInBlanksPayload({
    widget: "fill_in_blanks",
    instruction: "Fill each blank with the correct form of 'to be'.",
    source: { type: "passage", text: "I ___ ready. She ___ kind." },
    activities: [
      {
        activity_type: "fill_in_the_blanks",
        questions: {
          Q1: "I ___ ready.",
          Q2: "She ___ kind.",
        },
        answers: {
          Q1: "am",
          Q2: "is",
        },
      },
    ],
  });

  assert.equal(
    payload.instructions,
    "Fill each blank with the correct form of 'to be'.",
  );
  assert.equal(payload.passage, "I ___ ready. She ___ kind.");
  assert.equal(payload.total_blanks, 2);
  assert.equal(
    JSON.stringify(payload.items.map((item) => [item.item_id, item.correct_answer])),
    JSON.stringify([
      ["Q1", "am"],
      ["Q2", "is"],
    ]),
  );
});

test("fill blanks normalization leaves empty payloads without derived blanks", () => {
  const payload = fillBlanksNormalize.normalizeFillInBlanksPayload({
    widget: "fill_in_blanks",
    instructions: "Fill the blanks.",
  });

  assert.equal(payload.items, undefined);
  assert.equal(payload.blanks, undefined);
  assert.equal(payload.total_blanks, undefined);
  assert.equal(fillBlanksNormalize.areFillInBlanksAnswered([], {}), false);
});

test("fill blanks normalization derives blanks from passage markers", () => {
  const payload = fillBlanksNormalize.normalizeFillInBlanksPayload({
    widget: "fill_in_blanks",
    instructions: "Fill each blank with the correct form of 'to be'.",
    passage: "My name ____ John. I ____ a student.",
    answers: {
      blank_1: "is",
      blank_2: "am",
    },
  });

  assert.equal(payload.passage, "My name ___ John. I ___ a student.");
  assert.equal(payload.total_blanks, 2);
  assert.equal(payload.items[0].blank_id, "blank_1");
  assert.equal(payload.items[1].blank_id, "blank_2");
  assert.equal(payload.items[0].correct_answer, "is");
  assert.equal(payload.items[1].correct_answer, "am");
  assert.equal(
    fillBlanksNormalize.areFillInBlanksAnswered(payload.items, {
      blank_1: "is",
      blank_2: "am",
    }),
    true,
  );
});

test("listen response normalization accepts MCQ aliases and guards malformed items", () => {
  const payload = listenNormalize.normalizeListenAndRespondPayload({
    widget: "listen_and_respond",
    inner_widget: "MCQList",
    audio_script: "Mina usually studies after breakfast.",
    audio_url: "/audio/fake.mp3",
    items: [
      {
        item_id: "q1",
        prompt: "When does Mina study?",
        options: ["Before bed", "After breakfast", "At lunch", "Never"],
        correct_index: 1,
        explanation: "The clip says after breakfast.",
      },
      {
        item_id: "bad",
        prompt: "Broken",
        options: ["Only one option"],
        correct_index: 0,
        explanation: "",
      },
    ],
  });

  assert.equal(payload.inner_widget, "mcq");
  assert.equal(payload.items.length, 1);
  assert.equal(payload.items[0].item_id, "q1");
  assert.equal(listenNormalize.isPlayableListeningMCQ(payload), true);
});

test("listen response guards block missing audio or missing MCQ items", () => {
  const missingAudio = listenNormalize.normalizeListenAndRespondPayload({
    widget: "listen_and_respond",
    inner_widget: "mcq",
    audio_script: "Mina studies.",
    audio_url: null,
    items: [
      {
        item_id: "q1",
        prompt: "What does Mina do?",
        options: ["Studies", "Runs", "Sleeps", "Cooks"],
        correct_index: 0,
        explanation: "The clip says studies.",
      },
    ],
  });
  const missingItems = listenNormalize.normalizeListenAndRespondPayload({
    widget: "listen_and_respond",
    inner_widget: "mcq",
    audio_script: "Mina studies.",
    audio_url: "/audio/fake.mp3",
    items: [],
  });

  assert.equal(listenNormalize.isPlayableListeningMCQ(missingAudio), false);
  assert.equal(listenNormalize.isPlayableListeningMCQ(missingItems), false);
});

test("listen response allows browser TTS fallback when server audio is unavailable", () => {
  const payload = listenNormalize.normalizeListenAndRespondPayload({
    widget: "listen_and_respond",
    inner_widget: "mcq",
    audio_script: "Mina studies after breakfast.",
    audio_url: null,
    browser_tts_fallback: true,
    items: [
      {
        item_id: "q1",
        prompt: "When does Mina study?",
        options: ["Before bed", "After breakfast", "At lunch", "Never"],
        correct_index: 1,
        explanation: "The script says after breakfast.",
      },
    ],
  });

  assert.equal(listenNormalize.isPlayableListeningMCQ(payload), true);
});

test("listen response answer helpers preserve submitted MCQ choices", () => {
  const answers = {
    listen_analytics: {
      play_count: 1,
      total_listen_seconds: 12,
      transcript_revealed: true,
    },
    inner_response: {
      widget: "mcq",
      answers: [
        { item_id: "q1", selected_index: 2 },
        { item_id: "q2", selected_index: 0 },
      ],
    },
  };

  assert.equal(
    JSON.stringify(listenNormalize.selectionsFromListenAnswers(answers)),
    JSON.stringify({ q1: 2, q2: 0 }),
  );
  assert.equal(
    JSON.stringify(listenNormalize.analyticsFromListenAnswers(answers)),
    JSON.stringify({
      play_count: 1,
      total_listen_seconds: 12,
      transcript_revealed: true,
    }),
  );
});

test("listen response counts correct MCQ answers for compact score tile", () => {
  const items = [
    {
      item_id: "q1",
      prompt: "When does Mina study?",
      options: ["Before bed", "After breakfast", "At lunch", "Never"],
      correct_index: 1,
      explanation: "The clip says after breakfast.",
    },
    {
      item_id: "q2",
      prompt: "What does Mina do?",
      options: ["Studies", "Runs", "Sleeps", "Cooks"],
      correct_index: 0,
      explanation: "The clip says studies.",
    },
  ];

  assert.equal(
    listenNormalize.countCorrectListeningMCQ(items, { q1: 1, q2: 2 }),
    1,
  );
});
