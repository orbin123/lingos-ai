"use client";

import type { SessionPreviewState } from "../../teaching/source";
import type { LiveTaskController, SessionTask } from "../source";
import { ErrorCorrectionTaskWidget } from "./ErrorCorrectionTaskWidget";
import { ErrorSpottingTaskWidget } from "./ErrorSpottingTaskWidget";
import { FillBlanksTaskWidget } from "./FillBlanksTaskWidget";
import { ListenClozeTaskWidget } from "./ListenClozeTaskWidget";
import { ListenDictationTaskWidget } from "./ListenDictationTaskWidget";
import { ListenInferTaskWidget } from "./ListenInferTaskWidget";
import { ListenMcqTaskWidget } from "./ListenMcqTaskWidget";
import { ListenToneTaskWidget } from "./ListenToneTaskWidget";
import { OpenTextTaskWidget } from "./OpenTextTaskWidget";
import { ReadAloudTaskWidget } from "./ReadAloudTaskWidget";
import { ReadCompMcqTaskWidget } from "./ReadCompMcqTaskWidget";
import { ReadContextMcqTaskWidget } from "./ReadContextMcqTaskWidget";
import { ReadStructureTaskWidget } from "./ReadStructureTaskWidget";
import { ReadToneIdTaskWidget } from "./ReadToneIdTaskWidget";
import { ReadWordMatchTaskWidget } from "./ReadWordMatchTaskWidget";
import { SentenceTransformTaskWidget } from "./SentenceTransformTaskWidget";
import { SpeakPicDescTaskWidget } from "./SpeakPicDescTaskWidget";
import { SpeakRecordTaskWidget } from "./SpeakRecordTaskWidget";

import { WriteParagraphTaskWidget } from "./WriteParagraphTaskWidget";
import { SpeakRoleplayTaskWidget } from "./SpeakRoleplayTaskWidget";
import { SpeakInterviewTaskWidget } from "./SpeakInterviewTaskWidget";
import { ReadTfngTaskWidget } from "./ReadTfngTaskWidget";
import { ListenShadowTaskWidget } from "./ListenShadowTaskWidget";
import { WriteEmailTaskWidget } from "./WriteEmailTaskWidget";
import { SpeakSmalltalkTaskWidget } from "./SpeakSmalltalkTaskWidget";
import { ListenRetellTaskWidget } from "./ListenRetellTaskWidget";
import { WriteParaphraseTaskWidget } from "./WriteParaphraseTaskWidget";
import { SpeakPresentTaskWidget } from "./SpeakPresentTaskWidget";
import { WriteBulletsToParaTaskWidget } from "./WriteBulletsToParaTaskWidget";
import { WriteWordUpgradeTaskWidget } from "./WriteWordUpgradeTaskWidget";
import { SpeakTimedTaskWidget } from "./SpeakTimedTaskWidget";
import { WriteTimedTaskWidget } from "./WriteTimedTaskWidget";
import { SpeakDebateTaskWidget } from "./SpeakDebateTaskWidget";

export function TaskWidgetRenderer({
  task,
  previewState,
  live,
}: {
  task: SessionTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  // Widgets converged for live interactive use (M4). Others ignore `live` and
  // stay display-only.
  if (task.widget === "fill_blanks") {
    return <FillBlanksTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "listen_mcq") {
    return <ListenMcqTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "open_text") {
    return <OpenTextTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "speak_timed") {
    return <SpeakTimedTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "speak_debate") {
    return <SpeakDebateTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "listen_tone") {
    return <ListenToneTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "error_spotting") {
    return <ErrorSpottingTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "listen_cloze") {
    return <ListenClozeTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "listen_dictation") {
    return <ListenDictationTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "listen_infer") {
    return <ListenInferTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "read_comp_mcq") {
    return <ReadCompMcqTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "read_context_mcq") {
    return <ReadContextMcqTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "read_tone_id") {
    return <ReadToneIdTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "read_structure") {
    return <ReadStructureTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "error_correction") {
    return <ErrorCorrectionTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "sentence_transform") {
    return <SentenceTransformTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "read_aloud") {
    return <ReadAloudTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "read_word_match") {
    return <ReadWordMatchTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "speak_pic_desc") {
    return <SpeakPicDescTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "write_paragraph") {
    return <WriteParagraphTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "speak_roleplay") {
    return <SpeakRoleplayTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "speak_interview") {
    return <SpeakInterviewTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "read_tfng") {
    return <ReadTfngTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "listen_shadow") {
    return <ListenShadowTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "write_email") {
    return <WriteEmailTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "speak_smalltalk") {
    return <SpeakSmalltalkTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "listen_retell") {
    return <ListenRetellTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "write_paraphrase") {
    return <WriteParaphraseTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "speak_present") {
    return <SpeakPresentTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "write_bullets_to_para") {
    return <WriteBulletsToParaTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "write_word_upgrade") {
    return <WriteWordUpgradeTaskWidget task={task} previewState={previewState} live={live} />;
  }
  if (task.widget === "write_timed") {
    return <WriteTimedTaskWidget task={task} previewState={previewState} live={live} />;
  }
  return <SpeakRecordTaskWidget task={task} previewState={previewState} />;
}
