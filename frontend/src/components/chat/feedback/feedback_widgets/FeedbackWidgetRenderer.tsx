import type { AnswerView } from "../../teaching/source";
import type { SessionTask } from "../../tasks/source";
import type { ActivityFeedback } from "../source";
import { ReadListenFeedbackWidget } from "./ReadListenFeedbackWidget";
import { WriteSpeakFeedbackWidget } from "./WriteSpeakFeedbackWidget";

export function FeedbackWidgetRenderer({
  task,
  feedback,
  answerView,
}: {
  task: SessionTask;
  feedback: ActivityFeedback;
  answerView: AnswerView;
}) {
  if (task.activity === "Read" || task.activity === "Listen") {
    return <ReadListenFeedbackWidget feedback={feedback} answerView={answerView} />;
  }

  return <WriteSpeakFeedbackWidget feedback={feedback} answerView={answerView} />;
}
