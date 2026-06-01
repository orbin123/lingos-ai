import { api } from "./api";
import { blobToWav } from "./audio-utils";
import type { DiagnosisInput } from "./validators/diagnosis";

// Versioned IDs the backend expects
const QUESTION_SET_ID = "diag_fillblank_v1";
const WRITING_PROMPT_ID = "diag_writing_v1";
const READ_ALOUD_PASSAGE_ID = "diag_passage_v1";

// ── Types ──────────────────────────────────────────────────────────────────

/** One word from Azure pronunciation assessment (subset we use). */
export interface PronunciationWord {
  word: string;
  accuracy_score: number;
  error_type: string | null;
  phonemes?: { phoneme: string; accuracy_score: number }[];
}

/** Raw result returned by POST /diagnosis/pronunciation-score (Azure scale 0–100). */
export interface PronunciationScore {
  overall_score: number;
  accuracy_score: number;
  fluency_score: number;
  completeness_score: number;
  prosody_score: number;
  words: PronunciationWord[];
}

/** Read-aloud analysis shown in the result page scorecard (Azure scale 0–100). */
export interface ReadAloudAnalysis {
  overall: number;
  accuracy: number;
  fluency: number;
  completeness: number;
  prosody: number;
  words_to_improve: string[];
}

export interface SkillCallout {
  skill_name: string;
  description: string;
}

export interface FocusCallout {
  title: string;
  description: string;
}

export interface DiagnosisFeedback {
  estimated_level_label: string;
  level_description: string;
  summary: string;
  biggest_weakness: SkillCallout;
  strongest_skill: SkillCallout;
  first_focus: FocusCallout;
}

export interface DiagnosisResult {
  skill_scores: Record<string, number>;
  goal: string;
  feedback: DiagnosisFeedback;
  read_aloud_analysis?: ReadAloudAnalysis | null;
  next_step: string;
}

// ── API calls ──────────────────────────────────────────────────────────────

export const diagnosisApi = {
  start: (): Promise<{ next: string }> =>
    api.post<{ next: string }>("/diagnosis/start").then((r) => r.data),

  /**
   * Score a read-aloud recording with Azure Speech Pronunciation Assessment.
   * Azure does not accept WebM, so we convert the recorded blob to WAV on the
   * client first (same as the main read-aloud task). The canonical reference
   * text is resolved server-side from the passage id.
   */
  scorePronunciation: async (
    audioBlob: Blob,
    passageId: string = READ_ALOUD_PASSAGE_ID,
  ): Promise<PronunciationScore> => {
    const wav = await blobToWav(audioBlob);
    const formData = new FormData();
    formData.append("audio", wav, "recording.wav");
    formData.append("passage_id", passageId);
    return api
      .post<PronunciationScore>("/diagnosis/pronunciation-score", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },

  /**
   * Submit the full diagnosis form.
   * read_aloud sends the Azure pronunciation result (from scorePronunciation()),
   * NOT the audio blob — keeps this endpoint clean JSON.
   */
  submit: (data: DiagnosisInput): Promise<DiagnosisResult> => {
    const payload = {
      self_assessment: data.self_assessment,
      fill_blank: {
        question_set_id: QUESTION_SET_ID,
        answers: data.fill_blank.answers,
      },
      writing: {
        prompt_id: WRITING_PROMPT_ID,
        response_text: data.writing.response_text,
      },
      read_aloud: {
        passage_id: READ_ALOUD_PASSAGE_ID,
        overall_score: data.read_aloud.overall_score,
        accuracy_score: data.read_aloud.accuracy_score,
        fluency_score: data.read_aloud.fluency_score,
        completeness_score: data.read_aloud.completeness_score,
        prosody_score: data.read_aloud.prosody_score,
        words: data.read_aloud.words,
      },
    };
    return api
      .post<DiagnosisResult>("/diagnosis/submit", payload)
      .then((r) => r.data);
  },
};
