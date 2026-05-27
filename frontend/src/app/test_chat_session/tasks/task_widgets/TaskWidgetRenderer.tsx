"use client";

import type { SessionPreviewState } from "../../teaching/source";
import type { SessionTask } from "../source";
import { ErrorCorrectionTaskWidget } from "./ErrorCorrectionTaskWidget";
import { ErrorSpottingTaskWidget } from "./ErrorSpottingTaskWidget";
import { FillBlanksTaskWidget } from "./FillBlanksTaskWidget";
import { ListenClozeTaskWidget } from "./ListenClozeTaskWidget";
import { ListenDictationTaskWidget } from "./ListenDictationTaskWidget";
import { ListenMcqTaskWidget } from "./ListenMcqTaskWidget";
import { OpenTextTaskWidget } from "./OpenTextTaskWidget";
import { ReadAloudTaskWidget } from "./ReadAloudTaskWidget";
import { ReadCompMcqTaskWidget } from "./ReadCompMcqTaskWidget";
import { SentenceTransformTaskWidget } from "./SentenceTransformTaskWidget";
import { SpeakRecordTaskWidget } from "./SpeakRecordTaskWidget";

export function TaskWidgetRenderer({
  task,
  previewState,
}: {
  task: SessionTask;
  previewState: SessionPreviewState;
}) {
  if (task.widget === "error_spotting") {
    return <ErrorSpottingTaskWidget task={task} previewState={previewState} />;
  }
  if (task.widget === "fill_blanks") {
    return <FillBlanksTaskWidget task={task} previewState={previewState} />;
  }
  if (task.widget === "listen_cloze") {
    return <ListenClozeTaskWidget task={task} previewState={previewState} />;
  }
  if (task.widget === "listen_dictation") {
    return <ListenDictationTaskWidget task={task} previewState={previewState} />;
  }
  if (task.widget === "listen_mcq") {
    return <ListenMcqTaskWidget task={task} previewState={previewState} />;
  }
  if (task.widget === "read_comp_mcq") {
    return <ReadCompMcqTaskWidget task={task} previewState={previewState} />;
  }
  if (task.widget === "error_correction") {
    return <ErrorCorrectionTaskWidget task={task} previewState={previewState} />;
  }
  if (task.widget === "sentence_transform") {
    return <SentenceTransformTaskWidget task={task} previewState={previewState} />;
  }
  if (task.widget === "open_text") {
    return <OpenTextTaskWidget task={task} previewState={previewState} />;
  }
  if (task.widget === "read_aloud") {
    return <ReadAloudTaskWidget task={task} previewState={previewState} />;
  }
  return <SpeakRecordTaskWidget task={task} previewState={previewState} />;
}
