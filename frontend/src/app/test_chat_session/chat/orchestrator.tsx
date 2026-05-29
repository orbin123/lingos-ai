import { FileText, MessageCircle, Sparkles } from "lucide-react";
import { LessonMetaCard, SectionMarker } from "@/components/chat/ChatChrome";
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

            {previewState !== "default" && isReadAloud && evaluation && feedback && (
              <>
                <SectionMarker tone="score" icon={<Sparkles size={13} />}>
                  Read aloud assessment
                </SectionMarker>
                <ReadAloudAssessmentWidget
                  task={task}
                  evaluation={evaluation}
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
  return <LessonMetaCard eyebrow={subtitle} title={title} focus={focus} />;
}
