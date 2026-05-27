import type { AnswerView } from "../../teaching/source";
import type { SessionTask } from "../../tasks/source";
import type { ActivityEvaluation } from "../source";
import { ReadListenEvaluationWidget } from "./ReadListenEvaluationWidget";
import { WriteSpeakEvaluationWidget } from "./WriteSpeakEvaluationWidget";

export function EvaluationWidgetRenderer({
  task,
  evaluation,
  answerView,
}: {
  task: SessionTask;
  evaluation: ActivityEvaluation;
  answerView: AnswerView;
}) {
  if (task.activity === "Read" || task.activity === "Listen") {
    return <ReadListenEvaluationWidget evaluation={evaluation} answerView={answerView} />;
  }

  return <WriteSpeakEvaluationWidget evaluation={evaluation} answerView={answerView} />;
}
