import { FileText, MessageCircle, Sparkles } from "lucide-react";
import { EvaluationWidgetRenderer } from "./evaluation/evaluation_widgets/EvaluationWidgetRenderer";
import { FinalScorecardWidget } from "./evaluation/evaluation_widgets/FinalScorecardWidget";
import { getActivityEvaluation, getEvaluationDay } from "./evaluation/source";
import { FeedbackWidgetRenderer } from "./feedback/feedback_widgets/FeedbackWidgetRenderer";
import { RagFeedbackCard } from "./feedback/feedback_widgets/RagFeedbackCard";
import { ReadAloudAssessmentWidget } from "./feedback/feedback_widgets/ReadAloudAssessmentWidget";
import { getActivityFeedback, getFeedbackDay } from "./feedback/source";
import { TaskWidgetRenderer } from "./tasks/task_widgets/TaskWidgetRenderer";
import { getTaskDay } from "./tasks/source";
import { getTeachingDay, type CourseTrack, type SessionPreviewState } from "./teaching/source";
import { TextBlob } from "./teaching/textBlob";

interface ChatSessionOrchestratorProps {
  courseTrack: CourseTrack;
  week: number;
  day: number;
  previewState: SessionPreviewState;
}

export function ChatSessionOrchestrator({
  courseTrack,
  week,
  day,
  previewState,
}: ChatSessionOrchestratorProps) {
  const teachingDay = getTeachingDay(courseTrack, week, day);
  const taskDay = getTaskDay(courseTrack, week, day);
  const evaluationDay = getEvaluationDay(courseTrack, week, day);
  const feedbackDay = getFeedbackDay(courseTrack, week, day);

  if (!teachingDay.isAuthored || !taskDay || !evaluationDay || !feedbackDay) {
    return (
      <>
        <SessionMetaCard
          title={teachingDay.title}
          subtitle={`${teachingDay.courseTrack.toUpperCase()} - Week ${week} Day ${day}`}
          focus={teachingDay.focus}
        />
        <SectionMarker tone="intro" icon={<MessageCircle size={13} />}>
          Preview
        </SectionMarker>
        {teachingDay.messages.map((message) => (
          <TextBlob key={message.id} message={message} />
        ))}
      </>
    );
  }

  return (
    <>
      <SessionMetaCard
        title={teachingDay.title}
        subtitle={`${teachingDay.theme} - ${teachingDay.cefr} - Week ${week} Day ${day}`}
        focus={teachingDay.focus}
      />

      <SectionMarker tone="intro" icon={<MessageCircle size={13} />}>
        Teaching
      </SectionMarker>
      {teachingDay.messages.map((message) => (
        <TextBlob key={message.id} message={message} />
      ))}

      {taskDay.tasks.map((task) => {
        const evaluation = getActivityEvaluation(evaluationDay, task.id);
        const feedback = getActivityFeedback(feedbackDay, task.id);
        const isReadAloud = task.widget === "read_aloud";

        return (
          <div key={task.id}>
            <SectionMarker tone="task" icon={<FileText size={13} />}>
              {task.sequence}. {task.sectionLabel}
            </SectionMarker>
            <TaskWidgetRenderer task={task} previewState={previewState} />

            {previewState !== "default" && isReadAloud && evaluation && (
              <>
                <SectionMarker tone="score" icon={<Sparkles size={13} />}>
                  Read aloud assessment
                </SectionMarker>
                <ReadAloudAssessmentWidget
                  evaluation={evaluation}
                  answerView={previewState}
                />
              </>
            )}

            {previewState !== "default" && isReadAloud && feedback && (
              <>
                <SectionMarker tone="feedback" icon={<Sparkles size={13} />}>
                  Activity feedback
                </SectionMarker>
                <FeedbackWidgetRenderer
                  task={task}
                  feedback={feedback}
                  answerView={previewState}
                />
              </>
            )}

            {previewState !== "default" && !isReadAloud && evaluation && (
              <>
                <SectionMarker tone="score" icon={<Sparkles size={13} />}>
                  Activity score
                </SectionMarker>
                <EvaluationWidgetRenderer
                  task={task}
                  evaluation={evaluation}
                  answerView={previewState}
                />
              </>
            )}

            {previewState !== "default" && !isReadAloud && feedback && (
              <>
                <SectionMarker tone="feedback" icon={<Sparkles size={13} />}>
                  Activity feedback
                </SectionMarker>
                <FeedbackWidgetRenderer
                  task={task}
                  feedback={feedback}
                  answerView={previewState}
                />
              </>
            )}
          </div>
        );
      })}

      {previewState !== "default" && (
        <>
          <SectionMarker tone="score" icon={<Sparkles size={13} />}>
            Final scorecard
          </SectionMarker>
          <FinalScorecardWidget
            scorecard={evaluationDay.overallScorecard}
            answerView={previewState}
          />

          <SectionMarker tone="feedback" icon={<Sparkles size={13} />}>
            RAG feedback
          </SectionMarker>
          <RagFeedbackCard
            ragFeedback={feedbackDay.ragFeedback}
            answerView={previewState}
          />
        </>
      )}
    </>
  );
}

function SessionMetaCard({
  title,
  subtitle,
  focus,
}: {
  title: string;
  subtitle: string;
  focus: string;
}) {
  return (
    <section
      style={{
        borderRadius: 22,
        padding: "18px 20px",
        marginBottom: 18,
        background: "linear-gradient(135deg, rgba(255,255,255,0.96), rgba(238,245,255,0.96))",
        border: "1.5px solid rgba(255,255,255,0.9)",
        boxShadow: "0 8px 32px rgba(80,110,180,0.14)",
      }}
    >
      <div style={{ fontSize: 12, fontWeight: 800, color: "#0070C4", textTransform: "uppercase" }}>
        {subtitle}
      </div>
      <h1
        style={{
          margin: "5px 0 7px",
          fontSize: 22,
          lineHeight: 1.2,
          fontWeight: 800,
          color: "oklch(20% 0.09 245)",
        }}
      >
        {title}
      </h1>
      <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.55, color: "oklch(42% 0.07 240)" }}>
        {focus}
      </p>
    </section>
  );
}

function SectionMarker({
  tone,
  icon,
  children,
}: {
  tone: "intro" | "task" | "score" | "feedback";
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  const colors: Record<"intro" | "task" | "score" | "feedback", string> = {
    intro: "oklch(62% 0.16 240)",
    task: "oklch(70% 0.16 290)",
    score: "oklch(70% 0.16 155)",
    feedback: "oklch(76% 0.15 60)",
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", margin: "10px 0 14px" }}>
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 7,
          padding: "6px 13px",
          borderRadius: 999,
          background: "rgba(255,255,255,0.96)",
          border: "1px solid oklch(85% 0.025 240)",
          fontSize: 12.5,
          fontWeight: 800,
          color: colors[tone],
          boxShadow: "0 2px 8px rgba(80,110,180,0.06)",
          animation: "testChatFadeIn 0.35s ease both",
        }}
      >
        {icon}
        <span>{children}</span>
      </div>
    </div>
  );
}
