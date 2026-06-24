import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";

import { RuleCallout } from "@/components/chat/tasks/task_widgets/TaskWidgetFrame";
import { ErrorCorrectionTaskWidget } from "@/components/chat/tasks/task_widgets/ErrorCorrectionTaskWidget";
import type {
  ErrorCorrectionTask,
  LiveTaskController,
} from "@/components/chat/tasks/source";
import { renderWithProviders } from "../../utils/render";

describe("RuleCallout", () => {
  it("renders the label and rule text when given real content", () => {
    const { container } = renderWithProviders(
      <RuleCallout label="Correction rule">
        Use the simple past for finished actions.
      </RuleCallout>,
    );
    expect(screen.getByText("Correction rule")).toBeInTheDocument();
    expect(
      screen.getByText("Use the simple past for finished actions."),
    ).toBeInTheDocument();
    expect(container.querySelector(".tw-rule-callout")).not.toBeNull();
  });

  it("renders nothing when the rule is an empty string", () => {
    const { container } = renderWithProviders(
      <RuleCallout label="Correction rule">{""}</RuleCallout>,
    );
    expect(screen.queryByText("Correction rule")).not.toBeInTheDocument();
    expect(container.querySelector(".tw-rule-callout")).toBeNull();
  });

  it("renders nothing when the rule is whitespace only", () => {
    const { container } = renderWithProviders(
      <RuleCallout label="Correction rule">{"   \n\t"}</RuleCallout>,
    );
    expect(screen.queryByText("Correction rule")).not.toBeInTheDocument();
    expect(container.querySelector(".tw-rule-callout")).toBeNull();
  });

  it("renders nothing for nullish children", () => {
    const { container } = renderWithProviders(
      <RuleCallout label="Correction rule">{null}</RuleCallout>,
    );
    expect(container.querySelector(".tw-rule-callout")).toBeNull();
  });
});

const baseErrorCorrectionTask: ErrorCorrectionTask = {
  id: "task-error-correction-1",
  sequence: 1,
  archetypeId: "WRITE_ERROR_CORR",
  widget: "error_correction",
  sectionLabel: "Practice",
  topic: "Correct simple past tense mistakes",
  taskIntro: "Correct past tense mistakes.",
  instructions: "Rewrite each sentence correctly in the simple past.",
  subSkill: "grammatical_accuracy",
  activity: "write",
  estimatedMinutes: 5,
  grammarRule: "",
  items: [
    {
      itemId: "item-1",
      incorrectSentence: "Yesterday I eated rice for lunch.",
      sampleAnswer: "Yesterday I ate rice for lunch.",
      watchHints: ["tense", "irregular verb"],
    },
  ],
  answers: { correct: [], wrong: [] },
};

const liveController: LiveTaskController = {
  answers: {},
  setAnswers: () => {},
  onSubmit: () => {},
  submitted: false,
};

describe("ErrorCorrectionTaskWidget", () => {
  it("hides the correction-rule card when grammarRule is empty", () => {
    const { container } = renderWithProviders(
      <ErrorCorrectionTaskWidget
        task={baseErrorCorrectionTask}
        previewState="default"
        live={liveController}
      />,
    );
    // The blank orange "CORRECTION RULE" card must not render…
    expect(screen.queryByText("Correction rule")).not.toBeInTheDocument();
    expect(container.querySelector(".tw-rule-callout")).toBeNull();
    // …but the rest of the task still does.
    expect(screen.getByText(/Yesterday I eated rice for lunch\./)).toBeInTheDocument();
  });

  it("shows the correction-rule card when grammarRule is present", () => {
    const task: ErrorCorrectionTask = {
      ...baseErrorCorrectionTask,
      grammarRule: "Use the simple past for finished actions.",
    };
    const { container } = renderWithProviders(
      <ErrorCorrectionTaskWidget
        task={task}
        previewState="default"
        live={liveController}
      />,
    );
    expect(screen.getByText("Correction rule")).toBeInTheDocument();
    expect(
      screen.getByText("Use the simple past for finished actions."),
    ).toBeInTheDocument();
    expect(container.querySelector(".tw-rule-callout")).not.toBeNull();
  });
});
