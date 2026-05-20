--
-- PostgreSQL database dump
--

\restrict tPcgterT2QtYMZNPbphkvJhlyXcEjAcTOYhjM7tevOK93jRvaLWWTvM3g13uMkv

-- Dumped from database version 16.13
-- Dumped by pg_dump version 18.3 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: activity_attempt_status_enum; Type: TYPE; Schema: public; Owner: coach
--

CREATE TYPE public.activity_attempt_status_enum AS ENUM (
    'pending',
    'submitted',
    'evaluated',
    'skipped'
);


ALTER TYPE public.activity_attempt_status_enum OWNER TO coach;

--
-- Name: challenge_attempt_status_enum; Type: TYPE; Schema: public; Owner: coach
--

CREATE TYPE public.challenge_attempt_status_enum AS ENUM (
    'in_progress',
    'completed',
    'abandoned',
    'timed_out'
);


ALTER TYPE public.challenge_attempt_status_enum OWNER TO coach;

--
-- Name: content_exposure_enum; Type: TYPE; Schema: public; Owner: coach
--

CREATE TYPE public.content_exposure_enum AS ENUM (
    'NONE',
    'LOW',
    'MEDIUM',
    'HIGH'
);


ALTER TYPE public.content_exposure_enum OWNER TO coach;

--
-- Name: core_activity_enum; Type: TYPE; Schema: public; Owner: coach
--

CREATE TYPE public.core_activity_enum AS ENUM (
    'read',
    'write',
    'listen',
    'speak'
);


ALTER TYPE public.core_activity_enum OWNER TO coach;

--
-- Name: course_length_enum; Type: TYPE; Schema: public; Owner: coach
--

CREATE TYPE public.course_length_enum AS ENUM (
    '24w',
    '48w'
);


ALTER TYPE public.course_length_enum OWNER TO coach;

--
-- Name: course_level_enum; Type: TYPE; Schema: public; Owner: coach
--

CREATE TYPE public.course_level_enum AS ENUM (
    'beginner',
    'intermediate',
    'advanced'
);


ALTER TYPE public.course_level_enum OWNER TO coach;

--
-- Name: course_status_enum; Type: TYPE; Schema: public; Owner: coach
--

CREATE TYPE public.course_status_enum AS ENUM (
    'draft',
    'active',
    'archived'
);


ALTER TYPE public.course_status_enum OWNER TO coach;

--
-- Name: curriculum_theme_type_enum; Type: TYPE; Schema: public; Owner: coach
--

CREATE TYPE public.curriculum_theme_type_enum AS ENUM (
    'grammar',
    'communication',
    'vocabulary',
    'confidence'
);


ALTER TYPE public.curriculum_theme_type_enum OWNER TO coach;

--
-- Name: daily_session_status_enum; Type: TYPE; Schema: public; Owner: coach
--

CREATE TYPE public.daily_session_status_enum AS ENUM (
    'in_progress',
    'completed',
    'abandoned'
);


ALTER TYPE public.daily_session_status_enum OWNER TO coach;

--
-- Name: enrollment_status_enum; Type: TYPE; Schema: public; Owner: coach
--

CREATE TYPE public.enrollment_status_enum AS ENUM (
    'active',
    'paused',
    'completed',
    'abandoned'
);


ALTER TYPE public.enrollment_status_enum OWNER TO coach;

--
-- Name: self_assessed_level_enum; Type: TYPE; Schema: public; Owner: coach
--

CREATE TYPE public.self_assessed_level_enum AS ENUM (
    'BEGINNER',
    'INTERMEDIATE',
    'ADVANCED'
);


ALTER TYPE public.self_assessed_level_enum OWNER TO coach;

--
-- Name: task_status_enum; Type: TYPE; Schema: public; Owner: coach
--

CREATE TYPE public.task_status_enum AS ENUM (
    'draft',
    'active',
    'archived'
);


ALTER TYPE public.task_status_enum OWNER TO coach;

--
-- Name: task_type_enum; Type: TYPE; Schema: public; Owner: coach
--

CREATE TYPE public.task_type_enum AS ENUM (
    'reading',
    'writing',
    'speaking',
    'listening',
    'fill_in_blanks',
    'error_spotting',
    'sentence_transformation',
    'voice_conversion',
    'error_correction',
    'speak_with_tense',
    'curriculum_grammar_fill_blanks',
    'curriculum_grammar_open_text',
    'curriculum_grammar_listen_mcq',
    'curriculum_grammar_speak',
    'curriculum_vocab_mcq',
    'curriculum_vocab_open_text',
    'curriculum_vocab_listen_mcq',
    'curriculum_vocab_speak',
    'curriculum_pron_read_aloud',
    'curriculum_pron_phonetic_mcq',
    'curriculum_pron_listen_discriminate',
    'curriculum_pron_speak_drill',
    'curriculum_fluency_speed_read',
    'curriculum_fluency_timed_write',
    'curriculum_fluency_shadow',
    'curriculum_fluency_speak',
    'curriculum_expression_summarize',
    'curriculum_expression_essay',
    'curriculum_expression_listen_structure',
    'curriculum_expression_storyboard',
    'curriculum_comprehension_read_mcq',
    'curriculum_comprehension_write_answers',
    'curriculum_comprehension_listen_mcq',
    'curriculum_comprehension_retell',
    'curriculum_tone_read_mcq',
    'curriculum_tone_rewrite',
    'curriculum_tone_listen_mcq',
    'curriculum_tone_roleplay'
);


ALTER TYPE public.task_type_enum OWNER TO coach;

--
-- Name: user_goal_enum; Type: TYPE; Schema: public; Owner: coach
--

CREATE TYPE public.user_goal_enum AS ENUM (
    'CASUAL',
    'PROFESSIONAL',
    'ACADEMIC'
);


ALTER TYPE public.user_goal_enum OWNER TO coach;

--
-- Name: user_task_status_enum; Type: TYPE; Schema: public; Owner: coach
--

CREATE TYPE public.user_task_status_enum AS ENUM (
    'pending',
    'in_progress',
    'completed',
    'skipped'
);


ALTER TYPE public.user_task_status_enum OWNER TO coach;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activity_attempts; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.activity_attempts (
    id integer NOT NULL,
    session_id integer NOT NULL,
    archetype_id character varying(64) NOT NULL,
    activity public.core_activity_enum NOT NULL,
    sequence integer NOT NULL,
    status public.activity_attempt_status_enum DEFAULT 'pending'::public.activity_attempt_status_enum NOT NULL,
    task_content jsonb,
    user_response jsonb,
    submitted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.activity_attempts OWNER TO coach;

--
-- Name: activity_attempts_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.activity_attempts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.activity_attempts_id_seq OWNER TO coach;

--
-- Name: activity_attempts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.activity_attempts_id_seq OWNED BY public.activity_attempts.id;


--
-- Name: activity_evaluations; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.activity_evaluations (
    id integer NOT NULL,
    attempt_id integer NOT NULL,
    raw_score numeric(4,1) NOT NULL,
    rubric_scores jsonb DEFAULT '{}'::jsonb NOT NULL,
    base_reward integer NOT NULL,
    weighted_points jsonb NOT NULL,
    evaluator_notes character varying(2000),
    feedback jsonb,
    ruleset_version character varying(16) DEFAULT '1.0'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.activity_evaluations OWNER TO coach;

--
-- Name: activity_evaluations_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.activity_evaluations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.activity_evaluations_id_seq OWNER TO coach;

--
-- Name: activity_evaluations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.activity_evaluations_id_seq OWNED BY public.activity_evaluations.id;


--
-- Name: admin_audit_logs; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.admin_audit_logs (
    admin_user_id integer,
    action character varying(100) NOT NULL,
    resource_type character varying(100) NOT NULL,
    resource_id character varying(120) NOT NULL,
    old_value jsonb,
    new_value jsonb,
    ip_address character varying(64),
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.admin_audit_logs OWNER TO coach;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.admin_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.admin_audit_logs_id_seq OWNER TO coach;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.admin_audit_logs_id_seq OWNED BY public.admin_audit_logs.id;


--
-- Name: ai_request_logs; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.ai_request_logs (
    user_id integer,
    trace_id character varying(120),
    agent_name character varying(100) NOT NULL,
    model character varying(120) NOT NULL,
    input_tokens integer,
    output_tokens integer,
    latency_ms integer,
    status character varying(30) NOT NULL,
    error_message text,
    prompt_version character varying(120),
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.ai_request_logs OWNER TO coach;

--
-- Name: ai_request_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.ai_request_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ai_request_logs_id_seq OWNER TO coach;

--
-- Name: ai_request_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.ai_request_logs_id_seq OWNED BY public.ai_request_logs.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO coach;

--
-- Name: challenge_attempts; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.challenge_attempts (
    id integer NOT NULL,
    user_id integer NOT NULL,
    challenge_level_id integer NOT NULL,
    status public.challenge_attempt_status_enum NOT NULL,
    started_at timestamp with time zone NOT NULL,
    completed_at timestamp with time zone,
    expires_at timestamp with time zone NOT NULL,
    task_payload jsonb NOT NULL,
    response_payload jsonb,
    overall_score numeric(3,1),
    section_scores jsonb,
    passed boolean,
    evaluation_report jsonb,
    feedback_report jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.challenge_attempts OWNER TO coach;

--
-- Name: challenge_attempts_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.challenge_attempts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.challenge_attempts_id_seq OWNER TO coach;

--
-- Name: challenge_attempts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.challenge_attempts_id_seq OWNED BY public.challenge_attempts.id;


--
-- Name: challenge_levels; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.challenge_levels (
    id integer NOT NULL,
    challenge_id integer NOT NULL,
    level_number integer NOT NULL,
    name character varying(100) NOT NULL,
    time_limit_seconds integer NOT NULL,
    pass_threshold numeric(3,1) NOT NULL,
    config jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.challenge_levels OWNER TO coach;

--
-- Name: challenge_levels_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.challenge_levels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.challenge_levels_id_seq OWNER TO coach;

--
-- Name: challenge_levels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.challenge_levels_id_seq OWNED BY public.challenge_levels.id;


--
-- Name: challenges; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.challenges (
    id integer NOT NULL,
    slug character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    short_description character varying(255) NOT NULL,
    rules_md text NOT NULL,
    icon character varying(50),
    is_active boolean DEFAULT true NOT NULL,
    sort_order integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.challenges OWNER TO coach;

--
-- Name: challenges_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.challenges_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.challenges_id_seq OWNER TO coach;

--
-- Name: challenges_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.challenges_id_seq OWNED BY public.challenges.id;


--
-- Name: courses; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.courses (
    slug character varying(50) NOT NULL,
    title character varying(200) NOT NULL,
    description character varying(500) NOT NULL,
    duration_weeks integer NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    status public.course_status_enum DEFAULT 'active'::public.course_status_enum NOT NULL,
    target_level public.course_level_enum NOT NULL
);


ALTER TABLE public.courses OWNER TO coach;

--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.courses_id_seq OWNER TO coach;

--
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.id;


--
-- Name: curriculum_days; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.curriculum_days (
    id integer NOT NULL,
    week_id integer NOT NULL,
    day_number integer NOT NULL,
    topic character varying(255) NOT NULL,
    explanation_brief character varying(1000) DEFAULT ''::character varying NOT NULL,
    default_activities jsonb DEFAULT '[]'::jsonb NOT NULL,
    mandatory_activities jsonb DEFAULT '[]'::jsonb NOT NULL,
    suggested_archetypes jsonb DEFAULT '{}'::jsonb NOT NULL,
    extra_metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_curriculum_day_number_1_7 CHECK (((day_number >= 1) AND (day_number <= 7)))
);


ALTER TABLE public.curriculum_days OWNER TO coach;

--
-- Name: curriculum_days_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.curriculum_days_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.curriculum_days_id_seq OWNER TO coach;

--
-- Name: curriculum_days_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.curriculum_days_id_seq OWNED BY public.curriculum_days.id;


--
-- Name: curriculum_weeks; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.curriculum_weeks (
    id integer NOT NULL,
    course_length public.course_length_enum NOT NULL,
    week_number integer NOT NULL,
    theme_type public.curriculum_theme_type_enum NOT NULL,
    title character varying(200) NOT NULL,
    cefr_level character varying(16) NOT NULL,
    sub_level_min integer NOT NULL,
    sub_level_max integer NOT NULL,
    learning_goal character varying(500) DEFAULT ''::character varying NOT NULL,
    extra_metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.curriculum_weeks OWNER TO coach;

--
-- Name: curriculum_weeks_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.curriculum_weeks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.curriculum_weeks_id_seq OWNER TO coach;

--
-- Name: curriculum_weeks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.curriculum_weeks_id_seq OWNED BY public.curriculum_weeks.id;


--
-- Name: daily_activities; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.daily_activities (
    id integer NOT NULL,
    user_id integer NOT NULL,
    local_date date NOT NULL,
    activity_count integer DEFAULT 1 NOT NULL,
    last_session_id integer,
    completed_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.daily_activities OWNER TO coach;

--
-- Name: daily_activities_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.daily_activities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.daily_activities_id_seq OWNER TO coach;

--
-- Name: daily_activities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.daily_activities_id_seq OWNED BY public.daily_activities.id;


--
-- Name: daily_plans; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.daily_plans (
    id integer NOT NULL,
    user_id integer NOT NULL,
    course_slug character varying(50) NOT NULL,
    week integer NOT NULL,
    day integer NOT NULL,
    topic_id character varying(16) NOT NULL,
    plan_json jsonb NOT NULL,
    generated_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.daily_plans OWNER TO coach;

--
-- Name: daily_plans_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.daily_plans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.daily_plans_id_seq OWNER TO coach;

--
-- Name: daily_plans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.daily_plans_id_seq OWNED BY public.daily_plans.id;


--
-- Name: daily_sessions; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.daily_sessions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    curriculum_day_id integer NOT NULL,
    course_length public.course_length_enum NOT NULL,
    status public.daily_session_status_enum DEFAULT 'in_progress'::public.daily_session_status_enum NOT NULL,
    started_at timestamp with time zone NOT NULL,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.daily_sessions OWNER TO coach;

--
-- Name: daily_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.daily_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.daily_sessions_id_seq OWNER TO coach;

--
-- Name: daily_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.daily_sessions_id_seq OWNED BY public.daily_sessions.id;


--
-- Name: enrollment_skill_history; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.enrollment_skill_history (
    enrollment_id integer NOT NULL,
    skill_id integer NOT NULL,
    times_practiced integer NOT NULL,
    last_practiced_at timestamp with time zone,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    last_activity_type public.task_type_enum
);


ALTER TABLE public.enrollment_skill_history OWNER TO coach;

--
-- Name: enrollment_skill_history_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.enrollment_skill_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.enrollment_skill_history_id_seq OWNER TO coach;

--
-- Name: enrollment_skill_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.enrollment_skill_history_id_seq OWNED BY public.enrollment_skill_history.id;


--
-- Name: evaluations; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.evaluations (
    response_id integer NOT NULL,
    overall_score numeric(4,2) NOT NULL,
    percentage numeric(5,2) NOT NULL,
    report jsonb NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.evaluations OWNER TO coach;

--
-- Name: evaluations_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.evaluations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.evaluations_id_seq OWNER TO coach;

--
-- Name: evaluations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.evaluations_id_seq OWNED BY public.evaluations.id;


--
-- Name: feedbacks; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.feedbacks (
    evaluation_id integer NOT NULL,
    body jsonb NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    review_status character varying(30) DEFAULT 'pending'::character varying NOT NULL,
    reviewed_by integer,
    reviewed_at timestamp with time zone,
    admin_note text
);


ALTER TABLE public.feedbacks OWNER TO coach;

--
-- Name: feedbacks_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.feedbacks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.feedbacks_id_seq OWNER TO coach;

--
-- Name: feedbacks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.feedbacks_id_seq OWNED BY public.feedbacks.id;


--
-- Name: learning_sessions; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.learning_sessions (
    id integer NOT NULL,
    session_id character varying(64) NOT NULL,
    user_id integer NOT NULL,
    enrollment_id integer NOT NULL,
    phase character varying(32) NOT NULL,
    topic character varying(200) NOT NULL,
    skill_name character varying(50) NOT NULL,
    activity_type character varying(50) NOT NULL,
    task_type character varying(50) NOT NULL,
    user_level integer NOT NULL,
    pre_generated_tasks jsonb NOT NULL,
    current_task_index integer NOT NULL,
    messages jsonb NOT NULL,
    user_submission jsonb,
    evaluation jsonb,
    feedback jsonb,
    understanding_confirmed boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    user_task_id integer,
    task_queue jsonb NOT NULL,
    current_activity_order integer NOT NULL
);


ALTER TABLE public.learning_sessions OWNER TO coach;

--
-- Name: learning_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.learning_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.learning_sessions_id_seq OWNER TO coach;

--
-- Name: learning_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.learning_sessions_id_seq OWNED BY public.learning_sessions.id;


--
-- Name: oauth_accounts; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.oauth_accounts (
    id integer NOT NULL,
    user_id integer NOT NULL,
    provider character varying(50) NOT NULL,
    provider_user_id character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.oauth_accounts OWNER TO coach;

--
-- Name: oauth_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.oauth_accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.oauth_accounts_id_seq OWNER TO coach;

--
-- Name: oauth_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.oauth_accounts_id_seq OWNED BY public.oauth_accounts.id;


--
-- Name: payments; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.payments (
    user_id integer NOT NULL,
    provider character varying(50) NOT NULL,
    provider_payment_id character varying(255),
    amount numeric(10,2) NOT NULL,
    currency character varying(3) NOT NULL,
    status character varying(40) NOT NULL,
    paid_at timestamp with time zone,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.payments OWNER TO coach;

--
-- Name: payments_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payments_id_seq OWNER TO coach;

--
-- Name: payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.payments_id_seq OWNED BY public.payments.id;


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.permissions (
    key character varying(120) NOT NULL,
    description character varying(255) NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.permissions OWNER TO coach;

--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.permissions_id_seq OWNER TO coach;

--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.permissions_id_seq OWNED BY public.permissions.id;


--
-- Name: progress_logs; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.progress_logs (
    user_id integer NOT NULL,
    skill_id integer NOT NULL,
    score numeric(3,1) NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.progress_logs OWNER TO coach;

--
-- Name: progress_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.progress_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.progress_logs_id_seq OWNER TO coach;

--
-- Name: progress_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.progress_logs_id_seq OWNED BY public.progress_logs.id;


--
-- Name: purchases; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.purchases (
    user_id integer NOT NULL,
    plan_id character varying(50) NOT NULL,
    plan_name character varying(120) NOT NULL,
    amount_paid numeric(8,2) NOT NULL,
    currency character varying(3) DEFAULT 'INR'::character varying NOT NULL,
    status character varying(30) DEFAULT 'paid'::character varying NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.purchases OWNER TO coach;

--
-- Name: purchases_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.purchases_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.purchases_id_seq OWNER TO coach;

--
-- Name: purchases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.purchases_id_seq OWNED BY public.purchases.id;


--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.role_permissions (
    role_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.role_permissions OWNER TO coach;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.roles (
    name character varying(50) NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.roles OWNER TO coach;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO coach;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: session_scorecards; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.session_scorecards (
    id integer NOT NULL,
    session_id integer NOT NULL,
    points_earned jsonb NOT NULL,
    subskill_totals_after jsonb NOT NULL,
    dashboard_after jsonb NOT NULL,
    completed_at timestamp with time zone NOT NULL,
    ruleset_version character varying(16) DEFAULT '1.0'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.session_scorecards OWNER TO coach;

--
-- Name: session_scorecards_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.session_scorecards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.session_scorecards_id_seq OWNER TO coach;

--
-- Name: session_scorecards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.session_scorecards_id_seq OWNED BY public.session_scorecards.id;


--
-- Name: skill_point_history; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.skill_point_history (
    id integer NOT NULL,
    user_id integer NOT NULL,
    skill_id integer NOT NULL,
    session_id integer NOT NULL,
    points_delta integer NOT NULL,
    points_after integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.skill_point_history OWNER TO coach;

--
-- Name: skill_point_history_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.skill_point_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.skill_point_history_id_seq OWNER TO coach;

--
-- Name: skill_point_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.skill_point_history_id_seq OWNED BY public.skill_point_history.id;


--
-- Name: skill_points; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.skill_points (
    user_id integer NOT NULL,
    skill_id integer NOT NULL,
    points integer NOT NULL,
    display_score numeric(3,1) NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.skill_points OWNER TO coach;

--
-- Name: skill_points_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.skill_points_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.skill_points_id_seq OWNER TO coach;

--
-- Name: skill_points_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.skill_points_id_seq OWNED BY public.skill_points.id;


--
-- Name: skill_points_logs; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.skill_points_logs (
    user_id integer NOT NULL,
    skill_id integer NOT NULL,
    points_earned integer NOT NULL,
    reason character varying(100) NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.skill_points_logs OWNER TO coach;

--
-- Name: skill_points_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.skill_points_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.skill_points_logs_id_seq OWNER TO coach;

--
-- Name: skill_points_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.skill_points_logs_id_seq OWNED BY public.skill_points_logs.id;


--
-- Name: skills; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.skills (
    name character varying(50) NOT NULL,
    description character varying(255) NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    display_label character varying(60) NOT NULL
);


ALTER TABLE public.skills OWNER TO coach;

--
-- Name: skills_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.skills_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.skills_id_seq OWNER TO coach;

--
-- Name: skills_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.skills_id_seq OWNED BY public.skills.id;


--
-- Name: streak_freeze_usages; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.streak_freeze_usages (
    id integer NOT NULL,
    user_id integer NOT NULL,
    protected_date date NOT NULL,
    used_at timestamp with time zone NOT NULL,
    reason character varying(64) DEFAULT 'auto_missed_day_protection'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.streak_freeze_usages OWNER TO coach;

--
-- Name: streak_freeze_usages_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.streak_freeze_usages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.streak_freeze_usages_id_seq OWNER TO coach;

--
-- Name: streak_freeze_usages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.streak_freeze_usages_id_seq OWNED BY public.streak_freeze_usages.id;


--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.subscriptions (
    user_id integer NOT NULL,
    provider character varying(50) NOT NULL,
    provider_customer_id character varying(255),
    provider_subscription_id character varying(255),
    plan_name character varying(120) NOT NULL,
    status character varying(40) NOT NULL,
    trial_ends_at timestamp with time zone,
    current_period_start timestamp with time zone,
    current_period_end timestamp with time zone,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.subscriptions OWNER TO coach;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subscriptions_id_seq OWNER TO coach;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.subscriptions_id_seq OWNED BY public.subscriptions.id;


--
-- Name: task_archetypes; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.task_archetypes (
    id character varying(64) NOT NULL,
    name character varying(200) NOT NULL,
    core_activity public.core_activity_enum NOT NULL,
    description character varying(1000) DEFAULT ''::character varying NOT NULL,
    ui_widget character varying(64) NOT NULL,
    inner_widget character varying(64),
    input_type character varying(32) NOT NULL,
    themes_supported jsonb DEFAULT '[]'::jsonb NOT NULL,
    cefr_min character varying(8) DEFAULT 'A1'::character varying NOT NULL,
    cefr_max character varying(8) DEFAULT 'C2'::character varying NOT NULL,
    weight_map jsonb NOT NULL,
    rubric jsonb DEFAULT '[]'::jsonb NOT NULL,
    evaluation_prompt_ref character varying(255),
    feedback_prompt_ref character varying(255),
    mvp boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.task_archetypes OWNER TO coach;

--
-- Name: task_skills; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.task_skills (
    task_id integer NOT NULL,
    skill_id integer NOT NULL,
    weight numeric(3,2) NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.task_skills OWNER TO coach;

--
-- Name: task_skills_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.task_skills_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.task_skills_id_seq OWNER TO coach;

--
-- Name: task_skills_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.task_skills_id_seq OWNED BY public.task_skills.id;


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.tasks (
    title character varying(200) NOT NULL,
    difficulty integer NOT NULL,
    content jsonb NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    status public.task_status_enum DEFAULT 'active'::public.task_status_enum NOT NULL,
    task_type public.task_type_enum NOT NULL
);


ALTER TABLE public.tasks OWNER TO coach;

--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tasks_id_seq OWNER TO coach;

--
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- Name: user_course_preferences; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.user_course_preferences (
    id integer NOT NULL,
    user_id integer NOT NULL,
    course_length public.course_length_enum DEFAULT '24w'::public.course_length_enum NOT NULL,
    tasks_per_day integer DEFAULT 2 NOT NULL,
    allow_read boolean DEFAULT true NOT NULL,
    allow_write boolean DEFAULT true NOT NULL,
    allow_listen boolean DEFAULT true NOT NULL,
    allow_speak boolean DEFAULT true NOT NULL,
    current_week integer DEFAULT 1 NOT NULL,
    current_day_in_week integer DEFAULT 1 NOT NULL,
    current_day_started_at timestamp with time zone DEFAULT now() NOT NULL,
    last_completed_on date,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_user_course_preferences_tasks_per_day_2_4 CHECK (((tasks_per_day >= 2) AND (tasks_per_day <= 4)))
);


ALTER TABLE public.user_course_preferences OWNER TO coach;

--
-- Name: user_course_preferences_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.user_course_preferences_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_course_preferences_id_seq OWNER TO coach;

--
-- Name: user_course_preferences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.user_course_preferences_id_seq OWNED BY public.user_course_preferences.id;


--
-- Name: user_enrollments; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.user_enrollments (
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    current_week integer NOT NULL,
    current_day_in_week integer NOT NULL,
    started_at timestamp with time zone,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    tasks_per_day integer DEFAULT 2 NOT NULL,
    status public.enrollment_status_enum DEFAULT 'active'::public.enrollment_status_enum NOT NULL,
    allow_reading boolean DEFAULT true NOT NULL,
    allow_writing boolean DEFAULT true NOT NULL,
    allow_listening boolean DEFAULT true NOT NULL,
    allow_speaking boolean DEFAULT true NOT NULL,
    current_day_started_at timestamp with time zone DEFAULT now() NOT NULL,
    last_completed_on date,
    CONSTRAINT ck_user_enrollments_tasks_per_day_2_4 CHECK (((tasks_per_day >= 2) AND (tasks_per_day <= 4)))
);


ALTER TABLE public.user_enrollments OWNER TO coach;

--
-- Name: user_enrollments_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.user_enrollments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_enrollments_id_seq OWNER TO coach;

--
-- Name: user_enrollments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.user_enrollments_id_seq OWNED BY public.user_enrollments.id;


--
-- Name: user_profiles; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.user_profiles (
    user_id integer NOT NULL,
    self_assessed_level public.self_assessed_level_enum NOT NULL,
    daily_time_minutes integer NOT NULL,
    content_exposure public.content_exposure_enum NOT NULL,
    goal public.user_goal_enum NOT NULL,
    interests character varying(500) NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    diagnosis_completed boolean DEFAULT false NOT NULL,
    phone_number character varying(40),
    country character varying(80),
    native_language character varying(80),
    primary_goals character varying(500) DEFAULT ''::character varying NOT NULL,
    personalisation_context character varying(500) DEFAULT ''::character varying NOT NULL,
    display_name character varying(100),
    daily_practice_reminder boolean DEFAULT true NOT NULL,
    streak_reminder boolean DEFAULT true NOT NULL,
    weekly_progress_email boolean DEFAULT false NOT NULL,
    feature_announcements boolean DEFAULT false NOT NULL,
    structured_personalisation jsonb,
    structured_personalisation_updated_at timestamp with time zone,
    timezone character varying(64) DEFAULT 'Asia/Kolkata'::character varying NOT NULL,
    current_streak integer DEFAULT 0 NOT NULL,
    longest_streak integer DEFAULT 0 NOT NULL,
    last_activity_date date,
    streak_freezes integer DEFAULT 0 NOT NULL,
    last_seen_streak_animation_date date,
    last_animation_type character varying(16)
);


ALTER TABLE public.user_profiles OWNER TO coach;

--
-- Name: user_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.user_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_profiles_id_seq OWNER TO coach;

--
-- Name: user_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.user_profiles_id_seq OWNED BY public.user_profiles.id;


--
-- Name: user_responses; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.user_responses (
    user_task_id integer NOT NULL,
    content jsonb NOT NULL,
    raw_text text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    embedding_status text DEFAULT 'pending'::text NOT NULL,
    pinecone_vector_id text
);


ALTER TABLE public.user_responses OWNER TO coach;

--
-- Name: user_responses_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.user_responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_responses_id_seq OWNER TO coach;

--
-- Name: user_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.user_responses_id_seq OWNED BY public.user_responses.id;


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.user_roles (
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.user_roles OWNER TO coach;

--
-- Name: user_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.user_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_roles_id_seq OWNER TO coach;

--
-- Name: user_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.user_roles_id_seq OWNED BY public.user_roles.id;


--
-- Name: user_skill_scores; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.user_skill_scores (
    user_id integer NOT NULL,
    skill_id integer NOT NULL,
    score numeric(3,1) NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    is_estimated boolean DEFAULT false NOT NULL
);


ALTER TABLE public.user_skill_scores OWNER TO coach;

--
-- Name: user_skill_scores_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.user_skill_scores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_skill_scores_id_seq OWNER TO coach;

--
-- Name: user_skill_scores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.user_skill_scores_id_seq OWNED BY public.user_skill_scores.id;


--
-- Name: user_tasks; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.user_tasks (
    user_id integer NOT NULL,
    task_id integer NOT NULL,
    completed_at timestamp with time zone,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    enrollment_id integer,
    status public.user_task_status_enum DEFAULT 'pending'::public.user_task_status_enum NOT NULL
);


ALTER TABLE public.user_tasks OWNER TO coach;

--
-- Name: user_tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.user_tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_tasks_id_seq OWNER TO coach;

--
-- Name: user_tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.user_tasks_id_seq OWNED BY public.user_tasks.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: coach
--

CREATE TABLE public.users (
    email character varying(255) NOT NULL,
    password_hash character varying(255),
    name character varying(100) NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    is_superuser boolean DEFAULT false NOT NULL,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.users OWNER TO coach;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: coach
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO coach;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coach
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: activity_attempts id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.activity_attempts ALTER COLUMN id SET DEFAULT nextval('public.activity_attempts_id_seq'::regclass);


--
-- Name: activity_evaluations id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.activity_evaluations ALTER COLUMN id SET DEFAULT nextval('public.activity_evaluations_id_seq'::regclass);


--
-- Name: admin_audit_logs id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.admin_audit_logs ALTER COLUMN id SET DEFAULT nextval('public.admin_audit_logs_id_seq'::regclass);


--
-- Name: ai_request_logs id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.ai_request_logs ALTER COLUMN id SET DEFAULT nextval('public.ai_request_logs_id_seq'::regclass);


--
-- Name: challenge_attempts id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.challenge_attempts ALTER COLUMN id SET DEFAULT nextval('public.challenge_attempts_id_seq'::regclass);


--
-- Name: challenge_levels id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.challenge_levels ALTER COLUMN id SET DEFAULT nextval('public.challenge_levels_id_seq'::regclass);


--
-- Name: challenges id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.challenges ALTER COLUMN id SET DEFAULT nextval('public.challenges_id_seq'::regclass);


--
-- Name: courses id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.courses ALTER COLUMN id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- Name: curriculum_days id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.curriculum_days ALTER COLUMN id SET DEFAULT nextval('public.curriculum_days_id_seq'::regclass);


--
-- Name: curriculum_weeks id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.curriculum_weeks ALTER COLUMN id SET DEFAULT nextval('public.curriculum_weeks_id_seq'::regclass);


--
-- Name: daily_activities id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.daily_activities ALTER COLUMN id SET DEFAULT nextval('public.daily_activities_id_seq'::regclass);


--
-- Name: daily_plans id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.daily_plans ALTER COLUMN id SET DEFAULT nextval('public.daily_plans_id_seq'::regclass);


--
-- Name: daily_sessions id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.daily_sessions ALTER COLUMN id SET DEFAULT nextval('public.daily_sessions_id_seq'::regclass);


--
-- Name: enrollment_skill_history id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.enrollment_skill_history ALTER COLUMN id SET DEFAULT nextval('public.enrollment_skill_history_id_seq'::regclass);


--
-- Name: evaluations id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.evaluations ALTER COLUMN id SET DEFAULT nextval('public.evaluations_id_seq'::regclass);


--
-- Name: feedbacks id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.feedbacks ALTER COLUMN id SET DEFAULT nextval('public.feedbacks_id_seq'::regclass);


--
-- Name: learning_sessions id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.learning_sessions ALTER COLUMN id SET DEFAULT nextval('public.learning_sessions_id_seq'::regclass);


--
-- Name: oauth_accounts id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.oauth_accounts ALTER COLUMN id SET DEFAULT nextval('public.oauth_accounts_id_seq'::regclass);


--
-- Name: payments id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.payments ALTER COLUMN id SET DEFAULT nextval('public.payments_id_seq'::regclass);


--
-- Name: permissions id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.permissions ALTER COLUMN id SET DEFAULT nextval('public.permissions_id_seq'::regclass);


--
-- Name: progress_logs id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.progress_logs ALTER COLUMN id SET DEFAULT nextval('public.progress_logs_id_seq'::regclass);


--
-- Name: purchases id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.purchases ALTER COLUMN id SET DEFAULT nextval('public.purchases_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: session_scorecards id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.session_scorecards ALTER COLUMN id SET DEFAULT nextval('public.session_scorecards_id_seq'::regclass);


--
-- Name: skill_point_history id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.skill_point_history ALTER COLUMN id SET DEFAULT nextval('public.skill_point_history_id_seq'::regclass);


--
-- Name: skill_points id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.skill_points ALTER COLUMN id SET DEFAULT nextval('public.skill_points_id_seq'::regclass);


--
-- Name: skill_points_logs id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.skill_points_logs ALTER COLUMN id SET DEFAULT nextval('public.skill_points_logs_id_seq'::regclass);


--
-- Name: skills id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.skills ALTER COLUMN id SET DEFAULT nextval('public.skills_id_seq'::regclass);


--
-- Name: streak_freeze_usages id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.streak_freeze_usages ALTER COLUMN id SET DEFAULT nextval('public.streak_freeze_usages_id_seq'::regclass);


--
-- Name: subscriptions id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.subscriptions ALTER COLUMN id SET DEFAULT nextval('public.subscriptions_id_seq'::regclass);


--
-- Name: task_skills id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.task_skills ALTER COLUMN id SET DEFAULT nextval('public.task_skills_id_seq'::regclass);


--
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- Name: user_course_preferences id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_course_preferences ALTER COLUMN id SET DEFAULT nextval('public.user_course_preferences_id_seq'::regclass);


--
-- Name: user_enrollments id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_enrollments ALTER COLUMN id SET DEFAULT nextval('public.user_enrollments_id_seq'::regclass);


--
-- Name: user_profiles id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_profiles ALTER COLUMN id SET DEFAULT nextval('public.user_profiles_id_seq'::regclass);


--
-- Name: user_responses id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_responses ALTER COLUMN id SET DEFAULT nextval('public.user_responses_id_seq'::regclass);


--
-- Name: user_roles id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_roles ALTER COLUMN id SET DEFAULT nextval('public.user_roles_id_seq'::regclass);


--
-- Name: user_skill_scores id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_skill_scores ALTER COLUMN id SET DEFAULT nextval('public.user_skill_scores_id_seq'::regclass);


--
-- Name: user_tasks id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_tasks ALTER COLUMN id SET DEFAULT nextval('public.user_tasks_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: activity_attempts; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.activity_attempts (id, session_id, archetype_id, activity, sequence, status, task_content, user_response, submitted_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: activity_evaluations; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.activity_evaluations (id, attempt_id, raw_score, rubric_scores, base_reward, weighted_points, evaluator_notes, feedback, ruleset_version, created_at) FROM stdin;
\.


--
-- Data for Name: admin_audit_logs; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.admin_audit_logs (admin_user_id, action, resource_type, resource_id, old_value, new_value, ip_address, id, created_at) FROM stdin;
29	user.roles_update	user	29	{"id": 29, "email": "sarath19@example.com", "roles": ["learner", "super_admin"], "is_superuser": true}	{"id": 29, "email": "sarath19@example.com", "roles": ["admin", "learner", "super_admin"], "is_superuser": true}	127.0.0.1	1	2026-05-15 03:25:25.456921+00
29	user.status_change	user	35	{"id": 35, "email": "orbinsunny7306@gmail.com", "roles": ["learner"], "is_active": true}	{"id": 35, "email": "orbinsunny7306@gmail.com", "roles": ["learner"], "is_active": false}	127.0.0.1	3	2026-05-18 09:10:23.1261+00
29	user.status_change	user	36	{"id": 36, "email": "orbinsunny7983@gmail.com", "roles": ["learner"], "is_active": true}	{"id": 36, "email": "orbinsunny7983@gmail.com", "roles": ["learner"], "is_active": false}	127.0.0.1	4	2026-05-18 09:10:24.960625+00
29	user.status_change	user	36	{"id": 36, "email": "orbinsunny7983@gmail.com", "roles": ["learner"], "is_active": false}	{"id": 36, "email": "orbinsunny7983@gmail.com", "roles": ["learner"], "is_active": true}	127.0.0.1	5	2026-05-18 09:10:37.900255+00
29	user.status_change	user	35	{"id": 35, "email": "orbinsunny7306@gmail.com", "roles": ["learner"], "is_active": false}	{"id": 35, "email": "orbinsunny7306@gmail.com", "roles": ["learner"], "is_active": true}	127.0.0.1	6	2026-05-18 09:10:38.888973+00
\N	payment.recorded	payment	1	null	{"id": 1, "amount": 999.0, "status": "paid", "user_id": 36, "currency": "INR", "provider": "mock", "provider_payment_id": "[REDACTED]"}	\N	2	2026-05-15 06:23:06.093737+00
37	payment.recorded	payment	2	null	{"id": 2, "amount": 1999.0, "status": "paid", "user_id": 37, "currency": "INR", "provider": "mock", "provider_payment_id": "[REDACTED]"}	\N	7	2026-05-18 12:37:26.574745+00
38	payment.recorded	payment	3	null	{"id": 3, "amount": 999.0, "status": "paid", "user_id": 38, "currency": "INR", "provider": "mock", "provider_payment_id": "[REDACTED]"}	\N	8	2026-05-18 16:29:39.730771+00
\.


--
-- Data for Name: ai_request_logs; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.ai_request_logs (user_id, trace_id, agent_name, model, input_tokens, output_tokens, latency_ms, status, error_message, prompt_version, id, created_at) FROM stdin;
29	\N	task_generator	gpt-4o-mini	\N	\N	7923	success	\N	full_vocabulary_read_v1	1	2026-05-15 04:19:50.301517+00
29	\N	task_generator	gpt-4o-mini	\N	\N	10438	success	\N	full_vocabulary_write_v1	2	2026-05-15 04:19:50.301517+00
29	\N	task_generator	gpt-4o-mini	\N	\N	11936	success	\N	full_vocabulary_listen_v1	3	2026-05-15 04:19:50.301517+00
29	\N	task_generator	gpt-4o-mini	\N	\N	4401	success	\N	full_vocabulary_speak_v1	4	2026-05-15 04:19:50.301517+00
\N	\N	task_generator	gpt-4o-mini	\N	\N	11757	success	\N	full_grammar_read_v1	5	2026-05-15 06:23:06.553828+00
\N	\N	task_generator	gpt-4o-mini	\N	\N	11845	success	\N	full_grammar_write_v1	6	2026-05-15 06:23:06.553828+00
37	\N	task_generator	gpt-4o-mini	\N	\N	10722	success	\N	full_grammar_read_v1	7	2026-05-18 12:37:28.229289+00
37	\N	task_generator	gpt-4o-mini	\N	\N	7336	success	\N	full_grammar_write_v1	8	2026-05-18 12:37:28.229289+00
38	\N	task_generator	gpt-4o-mini	\N	\N	12813	success	\N	full_grammar_read_v1	9	2026-05-18 16:29:40.53823+00
38	\N	task_generator	gpt-4o-mini	\N	\N	8277	success	\N	full_grammar_write_v1	10	2026-05-18 16:29:40.53823+00
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.alembic_version (version_num) FROM stdin;
c5d6e7f8a0b1
\.


--
-- Data for Name: challenge_attempts; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.challenge_attempts (id, user_id, challenge_level_id, status, started_at, completed_at, expires_at, task_payload, response_payload, overall_score, section_scores, passed, evaluation_report, feedback_report, created_at) FROM stdin;
1	29	1	in_progress	2026-05-18 05:56:58.135014+00	\N	2026-05-18 06:16:58.135014+00	{"meta": {"phase": 3, "level_name": "Level 1 - Quick Sprint", "level_number": 1, "challenge_name": "IELTS Sprint", "challenge_slug": "ielts"}, "sections": {"reading": {"items": [{"prompt": "What is the main idea of the passage?", "item_id": "r1", "options": ["The definition of biodiversity", "The importance of biodiversity in ecosystems", "Methods to conserve biodiversity", "The effects of pollution on biodiversity"], "explanation": "The passage emphasizes the role of biodiversity in maintaining ecosystem stability and its importance for environmental health.", "correct_index": 1}], "widget": "mcq", "passage": "Biodiversity is crucial for maintaining the balance of ecosystems. It refers to the variety of life forms on Earth, including plants, animals, and microorganisms. Healthy ecosystems provide essential services such as pollination, climate regulation, and water purification. When biodiversity is compromised, the stability of these systems is at risk, leading to dire consequences for the environment and humanity. Conservation efforts are necessary to protect endangered species and preserve the natural habitats that support diverse life forms.", "task_intro": "Read the passage and choose the best answers.", "instructions": "Select one option for each question.", "passage_title": "The Importance of Biodiversity"}, "writing": {"items": [{"prompt": "Some people believe that governments should invest more in public services rather than in the arts. To what extent do you agree or disagree?", "item_id": "w1", "target_word_count": 80}], "widget": "timed_text", "task_intro": "Write an IELTS-style response.", "instructions": "Use the global challenge timer.", "sample_response": "", "target_word_count": 80, "minimum_word_count": 40, "no_editing_allowed": false, "time_limit_seconds": 1200}, "speaking": {"widget": "speak_and_record", "task_intro": "Record a short spoken answer.", "instructions": "Speaking upload and scoring arrive in Phase 6.", "sample_responses": [], "speaking_prompts": ["Describe a skill you improved through practice."], "speaking_duration_seconds": 30}, "listening": {"items": [{"prompt": "What is the speaker mainly discussing?", "item_id": "l1", "options": ["Benefits of learning a new language", "Challenges of learning a new language", "Importance of language in culture", "Methods for learning languages"], "explanation": "The speaker focuses on the various benefits one gains from learning a new language.", "correct_index": 0}], "widget": "listen_and_respond", "audio_url": null, "task_intro": "Listen to the short talk and answer the questions.", "audio_script": "In this talk, we will explore the benefits of learning a new language. Learning a new language can enhance cognitive abilities, improve career prospects, and enable deeper connections with people from different cultures. Many people find that they can learn more about themselves through the process of acquiring a new language. Additionally, it can be an enjoyable and fulfilling experience that opens up a world of opportunities.", "inner_widget": "mcq", "instructions": "Audio generation arrives in Phase 5. For now, read the transcript and questions.", "audio_duration_seconds": 45}}}	null	\N	null	\N	null	null	2026-05-18 05:56:57.995243+00
2	29	1	in_progress	2026-05-18 06:42:44.921867+00	\N	2026-05-18 07:02:44.921867+00	{"meta": {"phase": 3, "level_name": "Level 1 - Quick Sprint", "level_number": 1, "challenge_name": "IELTS Sprint", "challenge_slug": "ielts"}, "sections": {"reading": {"items": [{"prompt": "What is a consequence of lack of sleep?", "item_id": "r1", "options": ["Improved cognitive function", "Increased risk of health issues", "Better mood stability", "Enhanced productivity"], "explanation": "The passage clearly states that lack of sleep can lead to health issues.", "correct_index": 1}, {"prompt": "How many hours of sleep is recommended?", "item_id": "r2", "options": ["5-7 hours", "6-8 hours", "7-9 hours", "8-10 hours"], "explanation": "The passage specifies aiming for 7-9 hours of quality sleep.", "correct_index": 2}, {"prompt": "What function does sleep support according to the passage?", "item_id": "r3", "options": ["Physical strength", "Cognitive functions", "Social interactions", "Creativity levels"], "explanation": "The speaker mentions that sleep is essential for cognitive functions.", "correct_index": 1}, {"prompt": "What health issue is not mentioned as a consequence of lack of sleep?", "item_id": "r4", "options": ["Obesity", "Diabetes", "Mental health problems", "Cardiovascular diseases"], "explanation": "Mental health problems are not mentioned as a consequence in the passage.", "correct_index": 2}], "widget": "mcq", "passage": "Sleep is crucial for overall health and well-being. It allows the body to recover and regenerate. Lack of sleep can lead to various health issues such as obesity, diabetes, and cardiovascular diseases. Moreover, sleep is essential for cognitive functions like memory and problem-solving. Aiming for 7-9 hours of quality sleep each night can enhance productivity and focus during the day.", "task_intro": "Read the passage and choose the best answers.", "instructions": "Select one option for each question.", "passage_title": "The Importance of Sleep"}, "writing": {"items": [{"prompt": "Some people believe that the best way to increase road safety is to increase the number of traffic police on the roads. To what extent do you agree or disagree?", "item_id": "w1", "target_word_count": 80}], "widget": "timed_text", "task_intro": "Write an IELTS-style response.", "instructions": "Use the global challenge timer.", "sample_response": "", "target_word_count": 80, "minimum_word_count": 40, "no_editing_allowed": false, "time_limit_seconds": 1200}, "speaking": {"widget": "speak_and_record", "task_intro": "Record a short spoken answer.", "instructions": "Speaking upload and scoring arrive in Phase 6.", "sample_responses": [], "speaking_prompts": ["What hobbies do you enjoy and why?"], "speaking_duration_seconds": 30}, "listening": {"items": [{"prompt": "What is the main benefit of regular exercise mentioned?", "item_id": "l1", "options": ["Maintaining a healthy weight", "Improving sleep quality", "Reducing stress", "Building muscle"], "explanation": "The speaker emphasizes maintaining a healthy weight as a primary benefit.", "correct_index": 0}], "widget": "listen_and_respond", "audio_url": null, "task_intro": "Listen to the short talk and answer the questions.", "audio_script": "Today, I will talk about the benefits of regular exercise. Regular physical activity can help to maintain a healthy weight, improve mental health, and increase lifespan. It's essential to find an activity you enjoy to stay motivated.", "inner_widget": "mcq", "instructions": "Audio generation arrives in Phase 5. For now, read the transcript and questions.", "audio_duration_seconds": 45}}}	null	\N	null	\N	null	null	2026-05-18 06:42:44.843638+00
\.


--
-- Data for Name: challenge_levels; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.challenge_levels (id, challenge_id, level_number, name, time_limit_seconds, pass_threshold, config, created_at, updated_at) FROM stdin;
1	1	1	Level 1 - Quick Sprint	1200	6.0	{"sections": {"reading": {"num_questions": 4, "passage_word_count": 150}, "writing": {"prompt_count": 1, "target_word_count": 80}, "speaking": {"num_prompts": 1, "response_seconds": 30}, "listening": {"num_clips": 1, "num_questions": 3}}}	2026-05-18 03:38:39.034505+00	2026-05-18 03:38:39.034505+00
2	1	2	Level 2 - Focus Sprint	1800	6.0	{"sections": {"reading": {"num_questions": 6, "passage_word_count": 250}, "writing": {"prompt_count": 1, "target_word_count": 120}, "speaking": {"num_prompts": 2, "response_seconds": 45}, "listening": {"num_clips": 1, "num_questions": 5}}}	2026-05-18 03:38:39.034505+00	2026-05-18 03:38:39.034505+00
3	1	3	Level 3 - Deep Sprint	2400	6.0	{"sections": {"reading": {"num_questions": 8, "passage_word_count": 400}, "writing": {"prompt_count": 2, "target_word_count": 160}, "speaking": {"num_prompts": 2, "response_seconds": 60}, "listening": {"num_clips": 2, "num_questions": 8}}}	2026-05-18 03:38:39.034505+00	2026-05-18 03:38:39.034505+00
\.


--
-- Data for Name: challenges; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.challenges (id, slug, name, short_description, rules_md, icon, is_active, sort_order, created_at, updated_at) FROM stdin;
1	ielts	IELTS Sprint	Timed IELTS-flavored practice across all four sections.	# IELTS Sprint\n\nIELTS Sprint is IELTS-flavored practice, not a full official mock test.\n\n**No pause allowed. Closing the tab will lose your attempt. Timer is strict.**\n\nEach level includes Listening, Reading, Writing, and Speaking. You can retry\nlevels as many times as you want; your best-ever band is kept. Level unlocks\nare sequential and based on a best-ever band of 6.0 or higher.\n	award	t	10	2026-05-18 03:38:39.034505+00	2026-05-18 03:38:39.034505+00
\.


--
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.courses (slug, title, description, duration_weeks, id, created_at, updated_at, status, target_level) FROM stdin;
beginner-24w	Beginner English — 24 Week Foundation	A 24-week structured path covering grammar, vocabulary, expression, comprehension, and tone. Daily practice with rotating activity types.	24	1	2026-04-28 11:59:42.022526+00	2026-04-28 11:59:42.022526+00	active	beginner
beginner-48w	Beginner English — 48 Week Complete Path	A 48-week guided English program for learners who want a slower, deeper path through grammar, vocabulary, expression, comprehension, and tone.	48	2	2026-05-01 07:13:43.476641+00	2026-05-01 07:13:43.476641+00	active	beginner
\.


--
-- Data for Name: curriculum_days; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.curriculum_days (id, week_id, day_number, topic, explanation_brief, default_activities, mandatory_activities, suggested_archetypes, extra_metadata, created_at, updated_at) FROM stdin;
1	1	1	I am / You are / He is / She is		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
2	1	2	My, your, his, her, our, their		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
3	1	3	Simple present (positive): I work, she works		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
4	1	4	This / that / these / those + a / an / the		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
5	1	5	Negative present: I don't, she doesn't		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
6	1	6	Yes/No questions: Do you...? Does she...?		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
7	1	7	Review + light speaking drill		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
8	2	1	Name + age + country + city		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
9	2	2	Job / studies / what you do		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
10	2	3	Family — basic mentions		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
11	2	4	Hobbies — like / love / enjoy		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
12	2	5	Polite greetings & closings		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
13	2	6	Full self-intro practice		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
14	2	7	Roleplay: meeting someone new		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
15	3	1	Home & rooms		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
16	3	2	Food & drink basics		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
17	3	3	Clothes & colors		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
18	3	4	Days, times, numbers		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
19	3	5	Weather & seasons		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
20	3	6	Verbs of daily routine (wake, eat, leave, return)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
21	3	7	Vocabulary consolidation game		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
22	4	1	Reading aloud — short sentences		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
23	4	2	Repeat after audio (shadowing basics)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
24	4	3	Answer simple personal questions		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
25	4	4	Describe a photo in 3 sentences		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
26	4	5	30-second self-intro recording		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
27	4	6	Quick small talk: weather, weekend		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
28	4	7	Speaking confidence reflection + recap		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
29	5	1	Regular past: worked, watched, played		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
30	5	2	Irregular past: went, did, saw, had		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
31	5	3	Past negative + question		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
32	5	4	Future with will		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
33	5	5	Future with going to		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
34	5	6	Mixed time references		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
35	5	7	Past + future review + writing task		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
36	6	1	Information questions (what, where, when, who, why, how)		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
37	6	2	Polite requests: Could you...? Would you mind...?		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
38	6	3	Asking for repetition / clarification		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
39	6	4	At a shop / cafe / station		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
40	6	5	Asking a colleague for help		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
41	6	6	Asking on phone / video call		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
42	6	7	Mixed roleplay practice		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
43	7	1	Office objects, rooms		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
44	7	2	Roles & departments		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
45	7	3	Common workplace verbs (attend, schedule, share, send)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
46	7	4	Email vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
47	7	5	Meeting vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
48	7	6	Time at work (deadline, schedule, shift)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
49	7	7	Workplace small talk vocab		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
50	8	1	30-sec timed speaking		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
51	8	2	Picture description timed		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
52	8	3	Recording voice messages		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
53	8	4	Telephoning basics (hello, hold on, sorry)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
54	8	5	Recording a short voice memo summary		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
55	8	6	Spontaneous topic speaking (3 random prompts)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
56	8	7	Reflection + recording self-comparison		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
57	9	1	Present continuous form		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
58	9	2	Present simple vs continuous		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
59	9	3	Adverbs of frequency (always, usually, often, sometimes, never)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
60	9	4	Stative verbs (know, like, want — not used in continuous)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
61	9	5	Future continuous + future plans		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
62	9	6	Mixed practice		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
63	9	7	Review + speaking task		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
64	10	1	Describe a typical day		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
65	10	2	Describe a typical work / study week		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
66	10	3	Describe today and this week		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
67	10	4	Describe weekend plans		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
68	10	5	Describe a 6-month / 1-year plan		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
69	10	6	Compare two routines (yours vs friend's)		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
70	10	7	Spoken routine description		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
71	11	1	Positive emotions (happy → thrilled, content, satisfied)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
72	11	2	Negative emotions (sad → frustrated, disappointed, anxious)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
73	11	3	Opinion verbs (think, believe, feel, suppose)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
74	11	4	Agreeing / disagreeing softly		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
75	11	5	Strong opinions vs cautious opinions		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
76	11	6	Reactions in conversation (Wow, Really, That's interesting)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
77	11	7	Mixed emotional + opinion writing		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
78	12	1	I think / I believe / In my opinion		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
79	12	2	Reasoning (because, since, that's why)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
80	12	3	Giving examples		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
81	12	4	Disagreeing politely		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
82	12	5	Opinion + reason + example structure		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
83	12	6	1-minute opinion speaking		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
84	12	7	Reflection + recording review		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
85	13	1	Present perfect form (have/has + V3)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
86	13	2	Present perfect vs past simple		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
87	13	3	Time markers: ever, never, already, yet, just, since, for		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
88	13	4	Present perfect continuous		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
89	13	5	Past perfect — narrative use		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
90	13	6	All four tenses contrasted		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
91	13	7	Tense review + writing task		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
92	14	1	Story structure: setting → action → result		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
93	14	2	Sequence words (first, then, after that, finally)		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
94	14	3	Time descriptions in narrative		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
95	14	4	Adding emotion / reaction to stories		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
96	14	5	A funny story / embarrassing moment		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
97	14	6	A challenging professional / school moment		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
98	14	7	A 2-minute personal story recording		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
99	15	1	Transport vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
100	15	2	Accommodation vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
101	15	3	Direction-giving phrases		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
102	15	4	City vs countryside descriptors		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
103	15	5	Tourist + cultural vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
104	15	6	Travel problems (delayed, missed, cancelled)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
105	15	7	Travel story writing + speaking		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
106	16	1	Topic-starters (weather, weekend, news)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
107	16	2	Follow-up questions		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
108	16	3	Active listening sounds (really? oh wow, that's interesting)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
109	16	4	Bridging topics		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
110	16	5	Polite exits from conversation		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
111	16	6	Full simulated small talk (3 minutes)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
112	16	7	Conversation reflection		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
113	17	1	Zero conditional (general truth)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
114	17	2	First conditional (real future)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
115	17	3	Second conditional (unreal present)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
116	17	4	Third conditional (unreal past)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
117	17	5	Mixed conditionals		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
118	17	6	Wish + if only		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
119	17	7	Conditional speaking task		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
120	18	1	Meeting language (let's start, can I add, to summarize)		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
121	18	2	Stating your point clearly		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
122	18	3	Polite disagreement		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
123	18	4	Building on others' points (yes, and...)		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
124	18	5	Clarifying and confirming		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
125	18	6	Suggesting and proposing		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
126	18	7	Full simulated meeting roleplay		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
127	19	1	Tech & software vocab		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
128	19	2	AI / data / digital terms		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
129	19	3	Business processes (budget, deadline, scope, deliverable)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
130	19	4	Corporate hierarchy & roles		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
131	19	5	Numbers in business (growth, percent, increase)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
132	19	6	Business idioms (touch base, ballpark, deep dive)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
133	19	7	Writing a tech-business paragraph		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
134	20	1	Opening lines (today I'll talk about...)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
135	20	2	Signposting (firstly, moving on, finally)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
136	20	3	Highlighting key points		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
137	20	4	Handling a Q&A		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
138	20	5	Confidence in body language phrasing		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
139	20	6	Full 90-sec presentation recording		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
140	20	7	Self-review + improvement plan		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
141	21	1	Ability and possibility modals (can, could, may, might)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
142	21	2	Advice and obligation (should, must, have to, ought to)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
143	21	3	Past modals (could have, should have, must have)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
144	21	4	Passive voice — simple tenses		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
145	21	5	Passive — complex tenses		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
146	21	6	Modal + passive combinations		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
147	21	7	Formal writing task using modals		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
148	22	1	Standard interview questions		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
149	22	2	STAR-method storytelling		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
150	22	3	Salary / scope / deadline negotiation phrases		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
151	22	4	Diplomatic disagreement		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
152	22	5	Asking strong follow-up questions		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
153	22	6	Full simulated interview roleplay		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
154	22	7	Negotiation roleplay		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
155	23	1	Linking words (moreover, however, nevertheless)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
156	23	2	Cause-effect vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
157	23	3	Hedging language (tend to, appear to, seem)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
158	23	4	Critical thinking vocab (assumption, evidence, argument)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
159	23	5	Education / research vocab		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
160	23	6	Abstract concepts (justice, freedom, ethics)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
161	23	7	Academic paragraph writing		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
162	24	1	Debate structure (claim, evidence, conclusion)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
163	24	2	Rebuttal phrases		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
164	24	3	Tone control under disagreement		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
165	24	4	Strong vs reasonable opinions		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
166	24	5	1-minute argument speaking		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
167	24	6	Full 2-minute debate roleplay		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
168	24	7	Final reflection + course completion		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
169	25	1	I am / You are / He is / She is		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
170	25	2	My, your, his, her, our, their		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
171	25	3	Simple present (positive): I work, she works		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
172	25	4	This / that / these / those + a / an / the		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
173	25	5	Negative present: I don't, she doesn't		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
174	25	6	Yes/No questions: Do you...? Does she...?		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
175	25	7	Review + light speaking drill		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
176	26	1	I am / You are / He is / She is		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
177	26	2	My, your, his, her, our, their		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
178	26	3	Simple present (positive): I work, she works		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
179	26	4	This / that / these / those + a / an / the		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
180	26	5	Negative present: I don't, she doesn't		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
181	26	6	Yes/No questions: Do you...? Does she...?		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
182	26	7	Review + light speaking drill		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
183	27	1	Name + age + country + city		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
184	27	2	Job / studies / what you do		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
185	27	3	Family — basic mentions		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
186	27	4	Hobbies — like / love / enjoy		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
187	27	5	Polite greetings & closings		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
188	27	6	Full self-intro practice		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
189	27	7	Roleplay: meeting someone new		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
190	28	1	Name + age + country + city		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
191	28	2	Job / studies / what you do		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
192	28	3	Family — basic mentions		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
193	28	4	Hobbies — like / love / enjoy		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
194	28	5	Polite greetings & closings		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
195	28	6	Full self-intro practice		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
196	28	7	Roleplay: meeting someone new		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
197	29	1	Home & rooms		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
198	29	2	Food & drink basics		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
199	29	3	Clothes & colors		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
200	29	4	Days, times, numbers		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
201	29	5	Weather & seasons		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
202	29	6	Verbs of daily routine (wake, eat, leave, return)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
203	29	7	Vocabulary consolidation game		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
204	30	1	Home & rooms		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
205	30	2	Food & drink basics		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
206	30	3	Clothes & colors		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
207	30	4	Days, times, numbers		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
208	30	5	Weather & seasons		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
209	30	6	Verbs of daily routine (wake, eat, leave, return)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
210	30	7	Vocabulary consolidation game		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
211	31	1	Reading aloud — short sentences		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
212	31	2	Repeat after audio (shadowing basics)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
213	31	3	Answer simple personal questions		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
214	31	4	Describe a photo in 3 sentences		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
215	31	5	30-second self-intro recording		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
216	31	6	Quick small talk: weather, weekend		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
217	31	7	Speaking confidence reflection + recap		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
218	32	1	Reading aloud — short sentences		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
219	32	2	Repeat after audio (shadowing basics)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
220	32	3	Answer simple personal questions		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
221	32	4	Describe a photo in 3 sentences		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
222	32	5	30-second self-intro recording		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
223	32	6	Quick small talk: weather, weekend		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
224	32	7	Speaking confidence reflection + recap		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
225	33	1	Regular past: worked, watched, played		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
226	33	2	Irregular past: went, did, saw, had		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
227	33	3	Past negative + question		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
228	33	4	Future with will		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
229	33	5	Future with going to		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
230	33	6	Mixed time references		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
231	33	7	Past + future review + writing task		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
232	34	1	Regular past: worked, watched, played		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
233	34	2	Irregular past: went, did, saw, had		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
234	34	3	Past negative + question		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
235	34	4	Future with will		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
236	34	5	Future with going to		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
237	34	6	Mixed time references		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
238	34	7	Past + future review + writing task		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
239	35	1	Information questions (what, where, when, who, why, how)		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
240	35	2	Polite requests: Could you...? Would you mind...?		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
241	35	3	Asking for repetition / clarification		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
242	35	4	At a shop / cafe / station		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
243	35	5	Asking a colleague for help		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
244	35	6	Asking on phone / video call		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
245	35	7	Mixed roleplay practice		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
246	36	1	Information questions (what, where, when, who, why, how)		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
247	36	2	Polite requests: Could you...? Would you mind...?		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
248	36	3	Asking for repetition / clarification		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
249	36	4	At a shop / cafe / station		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
250	36	5	Asking a colleague for help		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
251	36	6	Asking on phone / video call		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
252	36	7	Mixed roleplay practice		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
253	37	1	Office objects, rooms		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
254	37	2	Roles & departments		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
255	37	3	Common workplace verbs (attend, schedule, share, send)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
256	37	4	Email vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
257	37	5	Meeting vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
258	37	6	Time at work (deadline, schedule, shift)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
259	37	7	Workplace small talk vocab		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
260	38	1	Office objects, rooms		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
261	38	2	Roles & departments		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
262	38	3	Common workplace verbs (attend, schedule, share, send)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
263	38	4	Email vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
264	38	5	Meeting vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
265	38	6	Time at work (deadline, schedule, shift)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
266	38	7	Workplace small talk vocab		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
267	39	1	30-sec timed speaking		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
268	39	2	Picture description timed		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
269	39	3	Recording voice messages		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
270	39	4	Telephoning basics (hello, hold on, sorry)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
271	39	5	Recording a short voice memo summary		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
272	39	6	Spontaneous topic speaking (3 random prompts)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
273	39	7	Reflection + recording self-comparison		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
274	40	1	30-sec timed speaking		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
275	40	2	Picture description timed		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
276	40	3	Recording voice messages		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
277	40	4	Telephoning basics (hello, hold on, sorry)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
278	40	5	Recording a short voice memo summary		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
279	40	6	Spontaneous topic speaking (3 random prompts)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
280	40	7	Reflection + recording self-comparison		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
281	41	1	Present continuous form		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
282	41	2	Present simple vs continuous		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
283	41	3	Adverbs of frequency (always, usually, often, sometimes, never)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
284	41	4	Stative verbs (know, like, want — not used in continuous)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
285	41	5	Future continuous + future plans		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
286	41	6	Mixed practice		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
287	41	7	Review + speaking task		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
288	42	1	Present continuous form		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
289	42	2	Present simple vs continuous		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
290	42	3	Adverbs of frequency (always, usually, often, sometimes, never)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
291	42	4	Stative verbs (know, like, want — not used in continuous)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
292	42	5	Future continuous + future plans		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
293	42	6	Mixed practice		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
294	42	7	Review + speaking task		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
295	43	1	Describe a typical day		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
296	43	2	Describe a typical work / study week		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
297	43	3	Describe today and this week		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
298	43	4	Describe weekend plans		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
299	43	5	Describe a 6-month / 1-year plan		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
300	43	6	Compare two routines (yours vs friend's)		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
301	43	7	Spoken routine description		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
302	44	1	Describe a typical day		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
303	44	2	Describe a typical work / study week		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
304	44	3	Describe today and this week		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
305	44	4	Describe weekend plans		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
306	44	5	Describe a 6-month / 1-year plan		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
307	44	6	Compare two routines (yours vs friend's)		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
308	44	7	Spoken routine description		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
309	45	1	Positive emotions (happy → thrilled, content, satisfied)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
310	45	2	Negative emotions (sad → frustrated, disappointed, anxious)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
311	45	3	Opinion verbs (think, believe, feel, suppose)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
312	45	4	Agreeing / disagreeing softly		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
313	45	5	Strong opinions vs cautious opinions		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
314	45	6	Reactions in conversation (Wow, Really, That's interesting)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
315	45	7	Mixed emotional + opinion writing		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
316	46	1	Positive emotions (happy → thrilled, content, satisfied)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
317	46	2	Negative emotions (sad → frustrated, disappointed, anxious)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
318	46	3	Opinion verbs (think, believe, feel, suppose)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
319	46	4	Agreeing / disagreeing softly		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
320	46	5	Strong opinions vs cautious opinions		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
321	46	6	Reactions in conversation (Wow, Really, That's interesting)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
322	46	7	Mixed emotional + opinion writing		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
323	47	1	I think / I believe / In my opinion		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
324	47	2	Reasoning (because, since, that's why)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
325	47	3	Giving examples		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
326	47	4	Disagreeing politely		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
327	47	5	Opinion + reason + example structure		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
328	47	6	1-minute opinion speaking		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
329	47	7	Reflection + recording review		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
330	48	1	I think / I believe / In my opinion		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
331	48	2	Reasoning (because, since, that's why)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
332	48	3	Giving examples		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
333	48	4	Disagreeing politely		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
334	48	5	Opinion + reason + example structure		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
335	48	6	1-minute opinion speaking		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
336	48	7	Reflection + recording review		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
337	49	1	Present perfect form (have/has + V3)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
338	49	2	Present perfect vs past simple		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
339	49	3	Time markers: ever, never, already, yet, just, since, for		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
340	49	4	Present perfect continuous		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
341	49	5	Past perfect — narrative use		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
342	49	6	All four tenses contrasted		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
343	49	7	Tense review + writing task		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
344	50	1	Present perfect form (have/has + V3)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
345	50	2	Present perfect vs past simple		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
346	50	3	Time markers: ever, never, already, yet, just, since, for		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
347	50	4	Present perfect continuous		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
348	50	5	Past perfect — narrative use		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
349	50	6	All four tenses contrasted		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
350	50	7	Tense review + writing task		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
351	51	1	Story structure: setting → action → result		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
352	51	2	Sequence words (first, then, after that, finally)		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
353	51	3	Time descriptions in narrative		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
354	51	4	Adding emotion / reaction to stories		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
355	51	5	A funny story / embarrassing moment		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
356	51	6	A challenging professional / school moment		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
357	51	7	A 2-minute personal story recording		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
358	52	1	Story structure: setting → action → result		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
359	52	2	Sequence words (first, then, after that, finally)		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
360	52	3	Time descriptions in narrative		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
361	52	4	Adding emotion / reaction to stories		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
362	52	5	A funny story / embarrassing moment		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
363	52	6	A challenging professional / school moment		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
364	52	7	A 2-minute personal story recording		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
365	53	1	Transport vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
366	53	2	Accommodation vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
367	53	3	Direction-giving phrases		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
368	53	4	City vs countryside descriptors		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
369	53	5	Tourist + cultural vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
370	53	6	Travel problems (delayed, missed, cancelled)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
371	53	7	Travel story writing + speaking		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
372	54	1	Transport vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
373	54	2	Accommodation vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
374	54	3	Direction-giving phrases		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
375	54	4	City vs countryside descriptors		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
376	54	5	Tourist + cultural vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
377	54	6	Travel problems (delayed, missed, cancelled)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
378	54	7	Travel story writing + speaking		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
379	55	1	Topic-starters (weather, weekend, news)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
380	55	2	Follow-up questions		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
381	55	3	Active listening sounds (really? oh wow, that's interesting)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
382	55	4	Bridging topics		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
383	55	5	Polite exits from conversation		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
384	55	6	Full simulated small talk (3 minutes)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
385	55	7	Conversation reflection		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
386	56	1	Topic-starters (weather, weekend, news)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
387	56	2	Follow-up questions		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
388	56	3	Active listening sounds (really? oh wow, that's interesting)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
389	56	4	Bridging topics		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
390	56	5	Polite exits from conversation		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
391	56	6	Full simulated small talk (3 minutes)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
392	56	7	Conversation reflection		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
393	57	1	Zero conditional (general truth)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
394	57	2	First conditional (real future)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
395	57	3	Second conditional (unreal present)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
396	57	4	Third conditional (unreal past)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
397	57	5	Mixed conditionals		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
398	57	6	Wish + if only		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
399	57	7	Conditional speaking task		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
400	58	1	Zero conditional (general truth)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
401	58	2	First conditional (real future)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
402	58	3	Second conditional (unreal present)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
403	58	4	Third conditional (unreal past)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
404	58	5	Mixed conditionals		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
405	58	6	Wish + if only		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
406	58	7	Conditional speaking task		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
407	59	1	Meeting language (let's start, can I add, to summarize)		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
408	59	2	Stating your point clearly		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
409	59	3	Polite disagreement		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
410	59	4	Building on others' points (yes, and...)		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
411	59	5	Clarifying and confirming		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
412	59	6	Suggesting and proposing		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
413	59	7	Full simulated meeting roleplay		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
414	60	1	Meeting language (let's start, can I add, to summarize)		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
415	60	2	Stating your point clearly		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
416	60	3	Polite disagreement		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
417	60	4	Building on others' points (yes, and...)		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
418	60	5	Clarifying and confirming		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
419	60	6	Suggesting and proposing		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
420	60	7	Full simulated meeting roleplay		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
421	61	1	Tech & software vocab		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
422	61	2	AI / data / digital terms		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
423	61	3	Business processes (budget, deadline, scope, deliverable)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
424	61	4	Corporate hierarchy & roles		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
425	61	5	Numbers in business (growth, percent, increase)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
426	61	6	Business idioms (touch base, ballpark, deep dive)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
427	61	7	Writing a tech-business paragraph		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
428	62	1	Tech & software vocab		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
429	62	2	AI / data / digital terms		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
430	62	3	Business processes (budget, deadline, scope, deliverable)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
431	62	4	Corporate hierarchy & roles		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
432	62	5	Numbers in business (growth, percent, increase)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
433	62	6	Business idioms (touch base, ballpark, deep dive)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
434	62	7	Writing a tech-business paragraph		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
435	63	1	Opening lines (today I'll talk about...)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
436	63	2	Signposting (firstly, moving on, finally)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
437	63	3	Highlighting key points		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
438	63	4	Handling a Q&A		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
439	63	5	Confidence in body language phrasing		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
440	63	6	Full 90-sec presentation recording		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
441	63	7	Self-review + improvement plan		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
442	64	1	Opening lines (today I'll talk about...)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
443	64	2	Signposting (firstly, moving on, finally)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
444	64	3	Highlighting key points		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
445	64	4	Handling a Q&A		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
446	64	5	Confidence in body language phrasing		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
447	64	6	Full 90-sec presentation recording		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
448	64	7	Self-review + improvement plan		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
449	65	1	Ability and possibility modals (can, could, may, might)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
450	65	2	Advice and obligation (should, must, have to, ought to)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
451	65	3	Past modals (could have, should have, must have)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
452	65	4	Passive voice — simple tenses		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
453	65	5	Passive — complex tenses		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
454	65	6	Modal + passive combinations		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
455	65	7	Formal writing task using modals		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
456	66	1	Ability and possibility modals (can, could, may, might)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
457	66	2	Advice and obligation (should, must, have to, ought to)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
458	66	3	Past modals (could have, should have, must have)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
459	66	4	Passive voice — simple tenses		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
460	66	5	Passive — complex tenses		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
461	66	6	Modal + passive combinations		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
462	66	7	Formal writing task using modals		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_CLOZE", "READ_ERROR_SPOT"], "speak": ["SPEAK_TIMED", "SPEAK_PRON_DRILL"], "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"], "listen": ["LISTEN_CLOZE", "LISTEN_DICTATION"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
463	67	1	Standard interview questions		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
464	67	2	STAR-method storytelling		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
465	67	3	Salary / scope / deadline negotiation phrases		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
466	67	4	Diplomatic disagreement		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
467	67	5	Asking strong follow-up questions		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
468	67	6	Full simulated interview roleplay		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
469	67	7	Negotiation roleplay		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
470	68	1	Standard interview questions		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
471	68	2	STAR-method storytelling		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
472	68	3	Salary / scope / deadline negotiation phrases		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
473	68	4	Diplomatic disagreement		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
474	68	5	Asking strong follow-up questions		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
475	68	6	Full simulated interview roleplay		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
476	68	7	Negotiation roleplay		["read", "write", "listen", "speak"]	["speak", "write"]	{"read": ["READ_COMP_MCQ", "READ_TFNG"], "speak": ["SPEAK_ROLEPLAY", "SPEAK_INTERVIEW"], "write": ["WRITE_EMAIL", "WRITE_PARA"], "listen": ["LISTEN_MCQ", "LISTEN_INFER"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
477	69	1	Linking words (moreover, however, nevertheless)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
478	69	2	Cause-effect vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
479	69	3	Hedging language (tend to, appear to, seem)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
480	69	4	Critical thinking vocab (assumption, evidence, argument)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
481	69	5	Education / research vocab		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
482	69	6	Abstract concepts (justice, freedom, ethics)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
483	69	7	Academic paragraph writing		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
484	70	1	Linking words (moreover, however, nevertheless)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
485	70	2	Cause-effect vocabulary		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
486	70	3	Hedging language (tend to, appear to, seem)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
487	70	4	Critical thinking vocab (assumption, evidence, argument)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
488	70	5	Education / research vocab		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
489	70	6	Abstract concepts (justice, freedom, ethics)		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
490	70	7	Academic paragraph writing		["read", "write", "listen", "speak"]	["read", "write"]	{"read": ["READ_WORD_MATCH", "READ_CONTEXT_MCQ"], "speak": ["SPEAK_PIC_DESC", "SPEAK_TIMED"], "write": ["WRITE_WORD_UPGRADE", "WRITE_PARAPHRASE"], "listen": ["LISTEN_DICTATION", "LISTEN_MCQ"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
491	71	1	Debate structure (claim, evidence, conclusion)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
492	71	2	Rebuttal phrases		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
493	71	3	Tone control under disagreement		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
494	71	4	Strong vs reasonable opinions		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
495	71	5	1-minute argument speaking		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
496	71	6	Full 2-minute debate roleplay		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
497	71	7	Final reflection + course completion		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
498	72	1	Debate structure (claim, evidence, conclusion)		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
499	72	2	Rebuttal phrases		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
500	72	3	Tone control under disagreement		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
501	72	4	Strong vs reasonable opinions		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
502	72	5	1-minute argument speaking		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
503	72	6	Full 2-minute debate roleplay		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
504	72	7	Final reflection + course completion		["read", "write", "listen", "speak"]	["speak", "listen"]	{"read": ["READ_TONE_ID", "READ_STRUCTURE_ID"], "speak": ["SPEAK_OPINION", "SPEAK_PRESENT"], "write": ["WRITE_IDEA_PARA", "WRITE_BULLETS_TO_PARA"], "listen": ["LISTEN_TONE", "LISTEN_SHADOW"]}	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
\.


--
-- Data for Name: curriculum_weeks; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.curriculum_weeks (id, course_length, week_number, theme_type, title, cefr_level, sub_level_min, sub_level_max, learning_goal, extra_metadata, created_at, updated_at) FROM stdin;
1	24w	1	grammar	Being and Belonging	A1	1	1	Master 'to be' + possessives + simple present (affirmative).	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
2	24w	2	communication	Introducing Yourself	A1	1	2	Introduce yourself in 4–5 sentences in any setting.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
3	24w	3	vocabulary	Daily Life Words	A1	2	2	80–100 high-frequency words for daily routines.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
4	24w	4	confidence	Saying Your First Sentences Out Loud	A1	2	2	Kill the freeze response when speaking simple English.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
5	24w	5	grammar	What I Did and What I'll Do	A2	3	3	Past simple + future (will / going to).	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
6	24w	6	communication	Asking for Things	A2	3	3	Ask questions, make requests, ask for clarification.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
7	24w	7	vocabulary	Workplace Basics	A2	3	3	100 work-context words even non-office learners can use.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
8	24w	8	confidence	Speaking Without Pausing Too Long	A2	3	3	Produce 60 seconds of speech without freezing.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
9	24w	9	grammar	Now, Always, Sometimes	B1	4	4	Present continuous, present simple distinction, adverbs of frequency.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
10	24w	10	communication	Describing Routines and Plans	B1	4	4	Explain what you do, what you're doing, what you'll do.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
11	24w	11	vocabulary	Emotions and Opinions	B1	5	5	80+ words for feeling and thinking.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
12	24w	12	confidence	Expressing What You Think	B1	5	5	State and defend an opinion in 1 minute.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
13	24w	13	grammar	Already, Yet, Still	B1+	5	5	Present perfect, past perfect, time markers.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
14	24w	14	communication	Telling Stories	B2	5	6	Narrate a real or imagined event with structure.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
15	24w	15	vocabulary	Travel and Movement	B2	6	6	Travel, transport, directions, descriptions of places.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
16	24w	16	confidence	Advanced Small Talk	B2	6	6	Sustain a 3-minute casual conversation.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
17	24w	17	grammar	If This, Then That	B2	6	6	All four conditional forms.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
18	24w	18	communication	Meetings and Disagreement	B2	7	7	Contribute professionally to meeting conversations.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
19	24w	19	vocabulary	Technology and Business	B2	7	7	100+ words for modern professional contexts.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
20	24w	20	confidence	Presenting an Idea	B2	7	7	Deliver a 90-second structured mini-presentation.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
21	24w	21	grammar	Can, Should, Must, Be Done	C1	8	8	Full modal system + passive voice.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
22	24w	22	communication	Interviews and Negotiation	C1	8	8	Navigate professional high-stakes conversations.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
23	24w	23	vocabulary	Abstract and Academic	C1	8	8	80+ abstract/academic words for nuanced expression.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
24	24w	24	confidence	Debate and Defending an Idea	C1	8	8	Argue a point under pressure with structure and tone control.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
25	48w	1	grammar	Being and Belonging — Introduce	A1	1	1	Introduce: Master 'to be' + possessives + simple present (affirmative).	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
26	48w	2	grammar	Being and Belonging — Extend	A1	1	1	Extend & apply: Master 'to be' + possessives + simple present (affirmative).	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
27	48w	3	communication	Introducing Yourself — Introduce	A1	1	2	Introduce: Introduce yourself in 4–5 sentences in any setting.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
28	48w	4	communication	Introducing Yourself — Extend	A1	1	2	Extend & apply: Introduce yourself in 4–5 sentences in any setting.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
29	48w	5	vocabulary	Daily Life Words — Introduce	A1	2	2	Introduce: 80–100 high-frequency words for daily routines.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
30	48w	6	vocabulary	Daily Life Words — Extend	A1	2	2	Extend & apply: 80–100 high-frequency words for daily routines.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
31	48w	7	confidence	Saying Your First Sentences Out Loud — Introduce	A1	2	2	Introduce: Kill the freeze response when speaking simple English.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
32	48w	8	confidence	Saying Your First Sentences Out Loud — Extend	A1	2	2	Extend & apply: Kill the freeze response when speaking simple English.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
33	48w	9	grammar	What I Did and What I'll Do — Introduce	A2	3	3	Introduce: Past simple + future (will / going to).	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
34	48w	10	grammar	What I Did and What I'll Do — Extend	A2	3	3	Extend & apply: Past simple + future (will / going to).	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
35	48w	11	communication	Asking for Things — Introduce	A2	3	3	Introduce: Ask questions, make requests, ask for clarification.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
36	48w	12	communication	Asking for Things — Extend	A2	3	3	Extend & apply: Ask questions, make requests, ask for clarification.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
37	48w	13	vocabulary	Workplace Basics — Introduce	A2	3	3	Introduce: 100 work-context words even non-office learners can use.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
38	48w	14	vocabulary	Workplace Basics — Extend	A2	3	3	Extend & apply: 100 work-context words even non-office learners can use.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
39	48w	15	confidence	Speaking Without Pausing Too Long — Introduce	A2	3	3	Introduce: Produce 60 seconds of speech without freezing.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
40	48w	16	confidence	Speaking Without Pausing Too Long — Extend	A2	3	3	Extend & apply: Produce 60 seconds of speech without freezing.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
41	48w	17	grammar	Now, Always, Sometimes — Introduce	B1	4	4	Introduce: Present continuous, present simple distinction, adverbs of frequency.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
42	48w	18	grammar	Now, Always, Sometimes — Extend	B1	4	4	Extend & apply: Present continuous, present simple distinction, adverbs of frequency.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
43	48w	19	communication	Describing Routines and Plans — Introduce	B1	4	4	Introduce: Explain what you do, what you're doing, what you'll do.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
44	48w	20	communication	Describing Routines and Plans — Extend	B1	4	4	Extend & apply: Explain what you do, what you're doing, what you'll do.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
45	48w	21	vocabulary	Emotions and Opinions — Introduce	B1	5	5	Introduce: 80+ words for feeling and thinking.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
46	48w	22	vocabulary	Emotions and Opinions — Extend	B1	5	5	Extend & apply: 80+ words for feeling and thinking.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
47	48w	23	confidence	Expressing What You Think — Introduce	B1	5	5	Introduce: State and defend an opinion in 1 minute.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
48	48w	24	confidence	Expressing What You Think — Extend	B1	5	5	Extend & apply: State and defend an opinion in 1 minute.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
49	48w	25	grammar	Already, Yet, Still — Introduce	B1+	5	5	Introduce: Present perfect, past perfect, time markers.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
50	48w	26	grammar	Already, Yet, Still — Extend	B1+	5	5	Extend & apply: Present perfect, past perfect, time markers.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
51	48w	27	communication	Telling Stories — Introduce	B2	5	6	Introduce: Narrate a real or imagined event with structure.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
52	48w	28	communication	Telling Stories — Extend	B2	5	6	Extend & apply: Narrate a real or imagined event with structure.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
53	48w	29	vocabulary	Travel and Movement — Introduce	B2	6	6	Introduce: Travel, transport, directions, descriptions of places.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
54	48w	30	vocabulary	Travel and Movement — Extend	B2	6	6	Extend & apply: Travel, transport, directions, descriptions of places.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
55	48w	31	confidence	Advanced Small Talk — Introduce	B2	6	6	Introduce: Sustain a 3-minute casual conversation.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
56	48w	32	confidence	Advanced Small Talk — Extend	B2	6	6	Extend & apply: Sustain a 3-minute casual conversation.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
57	48w	33	grammar	If This, Then That — Introduce	B2	6	6	Introduce: All four conditional forms.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
58	48w	34	grammar	If This, Then That — Extend	B2	6	6	Extend & apply: All four conditional forms.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
59	48w	35	communication	Meetings and Disagreement — Introduce	B2	7	7	Introduce: Contribute professionally to meeting conversations.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
60	48w	36	communication	Meetings and Disagreement — Extend	B2	7	7	Extend & apply: Contribute professionally to meeting conversations.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
61	48w	37	vocabulary	Technology and Business — Introduce	B2	7	7	Introduce: 100+ words for modern professional contexts.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
62	48w	38	vocabulary	Technology and Business — Extend	B2	7	7	Extend & apply: 100+ words for modern professional contexts.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
63	48w	39	confidence	Presenting an Idea — Introduce	B2	7	7	Introduce: Deliver a 90-second structured mini-presentation.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
64	48w	40	confidence	Presenting an Idea — Extend	B2	7	7	Extend & apply: Deliver a 90-second structured mini-presentation.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
65	48w	41	grammar	Can, Should, Must, Be Done — Introduce	C1	8	8	Introduce: Full modal system + passive voice.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
66	48w	42	grammar	Can, Should, Must, Be Done — Extend	C1	8	8	Extend & apply: Full modal system + passive voice.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
67	48w	43	communication	Interviews and Negotiation — Introduce	C1	8	8	Introduce: Navigate professional high-stakes conversations.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
68	48w	44	communication	Interviews and Negotiation — Extend	C1	8	8	Extend & apply: Navigate professional high-stakes conversations.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
69	48w	45	vocabulary	Abstract and Academic — Introduce	C1	8	8	Introduce: 80+ abstract/academic words for nuanced expression.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
70	48w	46	vocabulary	Abstract and Academic — Extend	C1	8	8	Extend & apply: 80+ abstract/academic words for nuanced expression.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
71	48w	47	confidence	Debate and Defending an Idea — Introduce	C1	8	8	Introduce: Argue a point under pressure with structure and tone control.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
72	48w	48	confidence	Debate and Defending an Idea — Extend	C1	8	8	Extend & apply: Argue a point under pressure with structure and tone control.	{}	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
\.


--
-- Data for Name: daily_activities; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.daily_activities (id, user_id, local_date, activity_count, last_session_id, completed_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: daily_plans; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.daily_plans (id, user_id, course_slug, week, day, topic_id, plan_json, generated_at, created_at, updated_at) FROM stdin;
8	38	beginner-24w	1	1	1:1	{"day": 1, "week": 1, "user_id": 38, "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "activities": [{"order": 1, "widget": "fill_in_blanks", "activity": "read", "template_id": "full_grammar_read_v1", "evaluation_focus": {"level_note": "Assess understanding of simple sentences and the present simple affirmative.", "focus_areas": ["reading comprehension", "sentence structure", "vocabulary usage"], "scoring_instruction": "1 point for each correct answer, total out of 3."}, "evaluation_method": "rule_exact_match"}, {"order": 2, "widget": "open_text", "activity": "write", "template_id": "full_grammar_write_v1", "evaluation_focus": {"level_note": "Look for correct use of present simple affirmative in self-introductions.", "focus_areas": ["sentence formation", "grammar accuracy", "clarity"], "scoring_instruction": "1 point for each correct sentence, total out of 3."}, "evaluation_method": "llm_open_writing"}, {"order": 3, "widget": "listen_and_respond", "activity": "listen", "template_id": "full_grammar_listen_v1", "evaluation_focus": {"level_note": "Evaluate ability to understand and respond to simple introductions.", "focus_areas": ["listening comprehension", "key information", "response accuracy"], "scoring_instruction": "1 point for each correct response, total out of 3."}, "evaluation_method": "rule_exact_match"}, {"order": 4, "widget": "speak_and_record", "activity": "speak", "template_id": "full_grammar_speak_v1", "evaluation_focus": {"level_note": "Focus on clear pronunciation of simple sentences and overall fluency.", "focus_areas": ["pronunciation", "fluency", "confidence"], "scoring_instruction": "1 point for clear pronunciation and 1 point for fluency, total out of 2."}, "evaluation_method": "llm_speaking_grammar"}], "topic_name": "introduce yourself in everyday situations — present simple — affirmative (I/you/we/they + base verb)", "course_slug": "beginner-24w", "generated_at": "2026-05-18T16:30:16.494407+00:00", "language_focus": "present simple — affirmative (I/you/we/they + base verb)", "communication_goal": "introduce yourself in everyday situations", "teacher_instructions": {"do_not_reveal": "The answers to the self-introduction task.", "learning_goal": "Learners will be able to introduce themselves using the present simple affirmative.", "lesson_context": "a casual gathering where people introduce themselves", "words_to_cover": ["I am", "You are", "We are", "They are", "My name is", "I like", "I play", "I live"], "sub_skill_context": "grammar introduction", "teaching_approach": "Use simple sentences to demonstrate the present simple affirmative. Keep sentences short (5-7 words). Focus on subject pronouns and base verbs. Avoid complex structures or vocabulary.", "vocabulary_domain": "general", "conversation_style": "neutral", "concept_check_focus": "Can you tell me your name and one thing you like?"}}	2026-05-18 16:30:16.520302+00	2026-05-18 16:30:11.065302+00	2026-05-18 16:30:11.065302+00
9	37	beginner-48w	1	1	1:1	{"day": 1, "week": 1, "user_id": 37, "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "activities": [{"order": 1, "widget": "fill_in_blanks", "activity": "read", "template_id": "full_grammar_read_v1", "evaluation_focus": {"level_note": "Look for understanding of simple sentences and correct verb forms.", "focus_areas": ["reading comprehension", "sentence structure", "verb usage"], "scoring_instruction": "1 point for each correct identification of a sentence structure."}, "evaluation_method": "rule_exact_match"}, {"order": 2, "widget": "open_text", "activity": "write", "template_id": "full_grammar_write_v1", "evaluation_focus": {"level_note": "Focus on using 'I', 'you', 'we', 'they' correctly in sentences.", "focus_areas": ["sentence creation", "grammar accuracy", "clarity"], "scoring_instruction": "1 point for each grammatically correct sentence up to 3 points."}, "evaluation_method": "llm_open_writing"}, {"order": 3, "widget": "listen_and_respond", "activity": "listen", "template_id": "full_grammar_listen_v1", "evaluation_focus": {"level_note": "Assess the ability to understand and respond using present simple.", "focus_areas": ["listening comprehension", "response accuracy", "verb usage"], "scoring_instruction": "1 point for each correct response to questions about the self-introduction."}, "evaluation_method": "rule_exact_match"}, {"order": 4, "widget": "speak_and_record", "activity": "speak", "template_id": "full_grammar_speak_v1", "evaluation_focus": {"level_note": "Evaluate the use of present simple and clarity of speech.", "focus_areas": ["speaking clarity", "grammar usage", "confidence"], "scoring_instruction": "1 point for each correct use of 'I', 'you', 'we', 'they' in sentences."}, "evaluation_method": "llm_speaking_grammar"}], "topic_name": "introduce yourself using I/you/we/they — present simple — statements (I, you, we, they + base verb)", "course_slug": "beginner-48w", "generated_at": "2026-05-19T03:59:33.298653+00:00", "language_focus": "present simple — statements (I, you, we, they + base verb)", "communication_goal": "introduce yourself using I/you/we/they", "teacher_instructions": {"do_not_reveal": "Do not give away specific answers or examples before the task.", "learning_goal": "Learner will be able to introduce themselves using I/you/we/they with base verbs.", "lesson_context": "first-day-on-campus self-introduction", "words_to_cover": [], "sub_skill_context": "grammar introduction", "teaching_approach": "Focus on simple present statements. Use short sentences (max 6 words). Demonstrate with examples like 'I am a student.' Avoid complex structures and vocabulary.", "vocabulary_domain": "general", "conversation_style": "neutral", "concept_check_focus": "Can you tell me who you are using 'I', 'you', 'we', or 'they'?"}}	2026-05-19 03:59:33.334439+00	2026-05-19 03:59:25.424964+00	2026-05-19 03:59:25.424964+00
\.


--
-- Data for Name: daily_sessions; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.daily_sessions (id, user_id, curriculum_day_id, course_length, status, started_at, completed_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: enrollment_skill_history; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.enrollment_skill_history (enrollment_id, skill_id, times_practiced, last_practiced_at, id, created_at, updated_at, last_activity_type) FROM stdin;
9	1	5	2026-05-14 15:24:05.845388+00	9	2026-05-04 05:15:05.649433+00	2026-05-14 15:23:47.642198+00	speaking
9	2	4	2026-05-15 04:20:25.409378+00	17	2026-05-15 04:19:50.301517+00	2026-05-15 04:19:50.301517+00	speaking
18	1	2	2026-05-18 12:37:48.03594+00	19	2026-05-18 12:37:28.229289+00	2026-05-18 12:37:28.229289+00	writing
19	1	2	2026-05-18 16:30:02.055477+00	20	2026-05-18 16:29:40.53823+00	2026-05-18 16:29:40.53823+00	writing
\.


--
-- Data for Name: evaluations; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.evaluations (response_id, overall_score, percentage, report, id, created_at) FROM stdin;
22	7.50	75.00	{"total": 4, "questions": {"Q1": {"correct": true, "error_type": "correct", "user_answer": "is", "correct_answer": "is"}, "Q2": {"correct": true, "error_type": "correct", "user_answer": "wakes", "correct_answer": "wakes"}, "Q3": {"correct": false, "error_type": "wrong_answer", "user_answer": "likes", "correct_answer": "like"}, "Q4": {"correct": true, "error_type": "correct", "user_answer": "smiles", "correct_answer": "smiles"}}, "task_type": "fill_in_the_blanks", "percentage": 75.0, "correct_count": 3}	21	2026-05-05 04:54:01.977081+00
23	5.00	50.00	{"total": 4, "questions": {"Q1": {"correct": true, "error_type": "correct", "user_answer": "is", "correct_answer": "is"}, "Q2": {"correct": true, "error_type": "correct", "user_answer": "wakes", "correct_answer": "wakes"}, "Q3": {"correct": false, "error_type": "wrong_answer", "user_answer": "likes", "correct_answer": "like"}, "Q4": {"correct": false, "error_type": "wrong_answer", "user_answer": "smile", "correct_answer": "smiles"}}, "task_type": "fill_in_the_blanks", "percentage": 50.0, "correct_count": 2}	22	2026-05-05 06:03:45.127614+00
47	8.00	80.00	{"total": 5, "questions": {"1": {"correct": true, "sentence": "Sarah ___ (wake) up early.", "error_type": "correct", "user_answer": "wakes", "grammar_rule": "In the present simple tense, use the base form of the verb for plural subjects, and add 's' for third person singular subjects.", "correct_answer": "wakes"}, "2": {"correct": true, "sentence": "She ___ (make) breakfast for her family.", "error_type": "correct", "user_answer": "makes", "grammar_rule": "In the present simple tense, use the base form of the verb for plural subjects, and add 's' for third person singular subjects.", "correct_answer": "makes"}, "3": {"correct": false, "sentence": "Her children ___ (go) to school.", "error_type": "wrong_answer", "user_answer": "goes", "grammar_rule": "In the present simple tense, use the base form of the verb for plural subjects, and add 's' for third person singular subjects.", "correct_answer": "go"}, "4": {"correct": true, "sentence": "Sarah ___ (take) a walk in the park.", "error_type": "correct", "user_answer": "takes", "grammar_rule": "In the present simple tense, use the base form of the verb for plural subjects, and add 's' for third person singular subjects.", "correct_answer": "takes"}, "5": {"correct": true, "sentence": "She ___ (cook) dinner and they all eat together.", "error_type": "correct", "user_answer": "cooks", "grammar_rule": "In the present simple tense, use the base form of the verb for plural subjects, and add 's' for third person singular subjects.", "correct_answer": "cooks"}}, "task_type": "fill_in_blanks", "percentage": 80.0, "correct_count": 4}	46	2026-05-15 03:31:46.214411+00
48	10.00	100.00	{"total": 4, "questions": {"1": {"score": 1.0, "prompt": "Write 3 sentences about your daily routine using Present Simple Tense — Basics.", "correct": true, "mistakes": [], "error_type": "correct", "user_answer": "I wake up at 7:00 AM every morning. I drink a glass of water before I start my work. I study new programming concepts for two hours every day.", "correct_answer": "I wake up at 7 AM. I eat breakfast at 8 AM. I go to work at 9 AM."}, "2": {"score": 1.0, "prompt": "Describe your best friend using 5 sentences with Present Simple Tense — Basics.", "correct": true, "mistakes": [], "error_type": "correct", "user_answer": "My best friend is a very kind and helpful person. He lives in the same city as I do. We talk about technology and life almost every evening. He works as a software engineer at a local firm. He always encourages me to work hard on my projects.", "correct_answer": "My best friend lives in the same neighborhood. He plays soccer every weekend. He loves to read books. He helps me with my homework. We watch movies together."}, "3": {"score": 1.0, "prompt": "Write 4 sentences about your favorite hobbies using Present Simple Tense — Basics.", "correct": true, "mistakes": [], "error_type": "correct", "user_answer": "I write clean code for open-source projects in my free time. I listen to music while I design new application interfaces. I read technical blogs to stay updated with the latest AI trends. I also enjoy building physical landscape models as a creative outlet.", "correct_answer": "I like painting and drawing. I play guitar in my free time. I enjoy cooking new recipes. I visit the museum every month."}, "4": {"score": 1.0, "prompt": "Make 3 sentences about what you do every weekend using Present Simple Tense — Basics.", "correct": true, "mistakes": [], "error_type": "correct", "user_answer": "I visit my local library to find books on computer science. I spend time with my family and help around the house. I plan my schedule for the upcoming week every Sunday evening.", "correct_answer": "I go hiking every Saturday. I clean my house on Sundays. I meet my friends for lunch."}}, "task_type": "curriculum_grammar_open_text", "percentage": 100.0, "correct_count": 4, "main_mistakes": [], "overall_level": "excellent", "answered_count": 4, "subskill_score": 10}	47	2026-05-15 03:33:31.199461+00
49	10.00	100.00	{"total": 4, "questions": {"1": {"prompt": "What does the speaker do every morning?", "correct": true, "error_type": "correct", "explanation": "The speaker clearly states that he wakes up early and eats breakfast.", "user_answer": "He wakes up early and eats breakfast.", "correct_index": 2, "correct_answer": "He wakes up early and eats breakfast.", "selected_index": 2}, "2": {"prompt": "Which drink does the speaker mention in his routine?", "correct": true, "error_type": "correct", "explanation": "The speaker specifically mentions drinking coffee in the morning.", "user_answer": "Coffee", "correct_index": 2, "correct_answer": "Coffee", "selected_index": 2}, "3": {"prompt": "What action does the speaker take after breakfast?", "correct": true, "error_type": "correct", "explanation": "The speaker says that he goes to work after having breakfast.", "user_answer": "He goes to work.", "correct_index": 0, "correct_answer": "He goes to work.", "selected_index": 0}, "4": {"prompt": "How does the speaker feel about his job?", "correct": true, "error_type": "correct", "explanation": "The speaker expresses that he loves his job because he helps people every day.", "user_answer": "He loves it.", "correct_index": 2, "correct_answer": "He loves it.", "selected_index": 2}}, "task_type": "curriculum_grammar_listen_mcq", "percentage": 100.0, "correct_count": 4, "listen_analytics": {"play_count": 1, "transcript_revealed": false, "total_listen_seconds": 17}}	48	2026-05-15 03:35:05.546395+00
50	3.00	30.00	{"total": 3, "questions": {"prompt_1": {"score": 0.0, "prompt": "Describe your daily routine. What do you do every day?", "correct": false, "mistakes": ["Used future tense 'will come back' instead of present simple", "Used 'take a shower' without a subject", "Incorrect structure with multiple 'then' phrases"], "audio_url": "/audio/user-recordings/1a1cc332fc7f2697.webm", "error_type": "needs_review", "user_answer": "Hi, my daily routine includes, I wake up early in the morning, then I eat my breakfast at 7.30, then I go to work and work until afternoon, I will come back at 6 and I take a shower, then I will prepare a meal for dinner and eat it at 7.30.", "correct_answer": "Every day, I wake up at 7 AM. I eat breakfast and then I go to work. After work, I exercise and have dinner with my family.", "duration_seconds": 45, "grammar_rule_used": false, "grammar_rule_to_practice": "present simple tense"}, "prompt_2": {"score": 1.0, "prompt": "What hobbies do you have? How often do you practice them?", "correct": true, "mistakes": [], "audio_url": "/audio/user-recordings/df04f65d69ee2bde.webm", "error_type": "correct", "user_answer": "I read books every night before going to bed. This is a habit that I built to calm down my stress before sleeping.", "correct_answer": "I have several hobbies. I play soccer every weekend and I read books in the evenings. I also enjoy painting when I have free time.", "duration_seconds": 45, "grammar_rule_used": true, "grammar_rule_to_practice": "present simple tense"}, "prompt_3": {"score": 1.0, "prompt": "Tell me about your family. What do they do for a living?", "correct": true, "mistakes": ["Used present continuous 'is sitting' instead of present simple", "Incorrect structure with 'without doing nothing'"], "audio_url": "/audio/user-recordings/cf9c30b20adcdbe7.webm", "error_type": "correct", "user_answer": "My father farms rubber and other crops, my mother is a housekeeper and my brother studies in a university and my grandfather sits simply at home without doing nothing.", "correct_answer": "My father is a teacher. He teaches math at a high school. My mother is a nurse, and she works at the local hospital.", "duration_seconds": 40, "grammar_rule_used": true, "grammar_rule_to_practice": "present simple tense"}}, "task_type": "curriculum_grammar_speak", "percentage": 30.0, "correct_count": 2, "main_mistakes": ["Failure to consistently use present simple tense", "Incorrect sentence structure", "Use of future tense instead of present simple"], "overall_level": "needs_work", "subskill_score": 3}	49	2026-05-15 03:39:27.588629+00
\.


--
-- Data for Name: feedbacks; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.feedbacks (evaluation_id, body, id, created_at, review_status, reviewed_by, reviewed_at, admin_note) FROM stdin;
21	{"score": 75, "errors": [{"rule": "When the subject is plural, do not add 's' to the verb in the present tense.", "why_wrong": "You should use 'like' instead of 'likes' because the subject 'students' is plural.", "error_type": "wrong_answer", "memory_tip": "Remember: plural subjects don't take 's' in the present tense verbs.", "question_id": "Q3", "user_answer": "likes", "correct_answer": "like"}], "overall_level": "okay", "overall_message": "You have done well overall, but there is one important mistake to correct. Make sure to pay attention to subject-verb agreement in sentences.", "practice_suggestion": "Write 5 sentences using plural subjects and make sure to use the correct verb forms."}	20	2026-05-05 04:54:01.992833+00	pending	\N	\N	\N
22	{"score": 50, "errors": [{"rule": "When the subject is plural, use the base form of the verb without 's'.", "why_wrong": "You used 'likes' instead of 'like'. 'Students' is plural, so the verb should also be plural.", "error_type": "wrong_answer", "memory_tip": "Remember: plural subjects do not take 's' at the end of the verb.", "question_id": "Q3", "user_answer": "likes", "correct_answer": "like"}, {"rule": "For singular subjects, add 's' to the verb in the present tense.", "why_wrong": "You wrote 'smile' instead of 'smiles'. The subject 'she' is singular, so the verb must have 's'.", "error_type": "wrong_answer", "memory_tip": "Singular subjects need 's' in the present tense verbs.", "question_id": "Q4", "user_answer": "smile", "correct_answer": "smiles"}], "overall_level": "okay", "overall_message": "You have a good understanding of the present tense, but there are some mistakes in subject-verb agreement. Focus on how verbs change with different subjects next time.", "practice_suggestion": "Write 5 sentences using different subjects (singular and plural) and the correct verb forms."}	21	2026-05-05 06:03:45.148764+00	pending	\N	\N	\N
46	{"score": 80, "errors": [{"rule": "In the present simple tense, use the base form of the verb for plural subjects, and add 's' for third person singular subjects.", "why_wrong": "You added 's' to the verb 'go' for a plural subject. In the present simple tense, we use the base form 'go' for plural subjects like 'children'.", "correction": "go", "error_type": "wrong_answer", "memory_tip": "Remember: plural subjects go bare, no 's'! Just think of it as 'no extra luggage' for plural verbs.", "question_id": "Item 3", "user_answer": "goes", "correct_answer": "go"}], "overall_level": "okay", "overall_message": "You did well with most of the answers, but you made a mistake with one. Remember that plural subjects do not take an 's'.", "practice_suggestion": "Write 5 sentences using the present simple tense with both singular and plural subjects."}	45	2026-05-15 03:31:46.214411+00	pending	\N	\N	\N
47	{"score": 100, "errors": [], "overall_level": "excellent", "overall_message": "Your sentences are all correct and well-structured. However, to elevate your writing, focus on using more varied vocabulary and sentence structures.", "practice_suggestion": "Write a short paragraph about your ideal weekend, using at least five different verbs in the present simple tense."}	46	2026-05-15 03:33:31.199461+00	pending	\N	\N	\N
48	{"score": 100, "errors": [], "overall_level": "excellent", "overall_message": "You answered all questions correctly, which shows a good understanding of the material! To further improve, focus on listening for details in longer passages.", "practice_suggestion": "Try summarizing the audio in a few sentences to practice your listening comprehension."}	47	2026-05-15 03:35:05.546395+00	pending	\N	\N	\N
49	{"score": 30, "errors": [{"rule": "Use present simple tense for daily routines. For example, say 'I take a shower' instead of 'I will take a shower'.", "why_wrong": "You used future tense with 'will come back' and 'will prepare' instead of present simple. Also, 'take a shower' needs a subject like 'I'.", "correction": "Hi, my daily routine is to wake up early in the morning, then I eat breakfast at 7:30, then I go to work and work until the afternoon. I come back at 6, take a shower, prepare a meal for dinner, and eat at 7:30.", "error_type": "needs_review", "memory_tip": "Remember to use 'I' for actions you're doing now and not 'will' for daily activities.", "question_id": "prompt_1", "user_answer": "Hi, my daily routine includes, I wake up early in the morning, then I eat my breakfast at 7.30, then I go to work and work until afternoon, I will come back at 6 and I take a shower, then I will prepare a meal for dinner and eat it at 7.30.", "correct_answer": "Every day, I wake up at 7 AM. I eat breakfast and then I go to work. After work, I exercise and have dinner with my family."}, {"rule": "Use simple present tense for actions. Avoid double negatives like 'without doing nothing'.", "why_wrong": "You used 'sits simply' which is incorrect structure. Also, 'without doing nothing' is a double negative.", "correction": "My father farms rubber and other crops, my mother is a housekeeper, my brother studies at a university, and my grandfather sits at home doing nothing.", "error_type": "correct", "memory_tip": "In English, avoid using two negatives together. Just say 'doing nothing'.", "question_id": "prompt_3", "user_answer": "My father farms rubber and other crops, my mother is a housekeeper and my brother studies in a university and my grandfather sits simply at home without doing nothing.", "correct_answer": "My father is a teacher. He teaches math at a high school. My mother is a nurse, and she works at the local hospital."}], "overall_level": "needs_work", "overall_message": "You showed understanding in some areas, but you need to focus on using the present simple tense consistently. Your main mistakes were using future tense and incorrect sentence structures.", "practice_suggestion": "Practice rewriting sentences in the present simple tense. Write 5 sentences about your daily routine using 'I' and the present simple."}	48	2026-05-15 03:39:27.588629+00	pending	\N	\N	\N
\.


--
-- Data for Name: learning_sessions; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.learning_sessions (id, session_id, user_id, enrollment_id, phase, topic, skill_name, activity_type, task_type, user_level, pre_generated_tasks, current_task_index, messages, user_submission, evaluation, feedback, understanding_confirmed, created_at, updated_at, user_task_id, task_queue, current_activity_order) FROM stdin;
34	15f3c3022dac415ab3729758f8d55d88	38	19	teaching	introduce yourself in everyday situations — present simple — affirmative (I/you/we/they + base verb)	grammar	read	curriculum_grammar_fill_blanks	1	{"items": [{"item_id": "1", "base_verb": "be", "explanation": "The correct form of 'to be' for 'I' is 'am'.", "correct_answer": "am", "sentence_with_blank": "My name is John, and I ___ (1) a teacher."}, {"item_id": "2", "base_verb": "live", "explanation": "The base verb 'live' is used here in the present simple.", "correct_answer": "live", "sentence_with_blank": "I ___ (2) in a small town."}, {"item_id": "3", "base_verb": "be", "explanation": "The correct form of 'to be' for 'they' is 'are'.", "correct_answer": "are", "sentence_with_blank": "My friends ___ (3) nice and supportive."}, {"item_id": "4", "base_verb": "do", "explanation": "The verb 'do' is used in the present simple for 'we'.", "correct_answer": "do", "sentence_with_blank": "We ___ (4) many activities together."}, {"item_id": "5", "base_verb": "be", "explanation": "The correct form of 'to be' for 'I' is 'am.'", "correct_answer": "am", "sentence_with_blank": "I ___ (5) happy to meet new people."}], "widget": "fill_in_blanks", "passage": "Hello! My name is John, and I ___ (1) a teacher. I ___ (2) in a small town. My friends ___ (3) nice and supportive. We ___ (4) many activities together. I ___ (5) happy to meet new people.", "activity": "read", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice introducing ourselves in simple sentences! Fill in the blanks with the correct form of the verb.", "topic_name": "introduce yourself in everyday situations — present simple — affirmative (I/you/we/they + base verb)", "instructions": "Read the paragraph and type the numbered answers into the blanks.", "estimated_time_minutes": 4, "grammar_rule_explained": "In the present simple tense, we use 'am' for 'I', 'are' for 'you/we/they', and 'is' for 'he/she/it'."}	0	[{"role": "ai", "type": "chat", "content": "Imagine you're at a casual gathering and someone asks you about yourself. You might say, \\"My name is Alex. I like soccer.\\" This simple structure helps you introduce yourself clearly. How would you introduce yourself to someone new at this gathering?"}, {"role": "user", "type": "chat", "content": "Hi my name is Orbin Sunny. I am student at Brototype"}, {"role": "ai", "type": "chat", "content": "Great introduction, Orbin! You could say, \\"I am a student.\\" This keeps it simple and clear. If someone asks you what you like, how would you respond?"}, {"role": "user", "type": "chat", "content": "I like swimming, going out with my friends and trekking"}, {"role": "ai", "type": "chat", "content": "At a casual gathering, someone might ask you what you enjoy doing. You could say, \\"I like swimming.\\" This simple structure helps you share your interests clearly. How would you say this to someone who asks what you like to do for fun?"}, {"role": "user", "type": "chat", "content": "I like to swim and practice skateboard"}, {"role": "ai", "type": "chat", "content": "At the gathering, when someone asks about your hobbies, you can say, \\"I like to swim.\\" It’s a great way to introduce your interests simply. If someone asks you what you do on weekends, how would you respond?"}, {"role": "user", "type": "chat", "content": "In weekends, I swim or go out with my friends"}, {"role": "ai", "type": "chat", "content": "You have practiced the main idea for introduce yourself in everyday situations — present simple — affirmative (I/you/we/they + base verb): find the subject, look for time or frequency clues, and choose the verb form. Does this feel clear enough to start the practice task?"}]	\N	\N	\N	f	2026-05-18 16:30:09.424679+00	2026-05-18 16:42:04.879084+00	134	[{"title": "Subskill.Grammar - Activity.Read - Uiwidget.Fill In Blanks", "status": "in_progress", "task_id": 103, "task_type": "curriculum_grammar_fill_blanks", "completed_at": null, "user_task_id": 134, "sequence_index": 0}, {"title": "Subskill.Grammar - Activity.Write - Uiwidget.Open Text", "status": "pending", "task_id": 104, "task_type": "curriculum_grammar_open_text", "completed_at": null, "user_task_id": 135, "sequence_index": 1}]	1
35	0f5ece0a162842b49e76fdd5501e5b07	37	18	teaching	introduce yourself using I/you/we/they — present simple — statements (I, you, we, they + base verb)	grammar	read	curriculum_grammar_fill_blanks	1	{"items": [{"item_id": "1", "base_verb": "be", "explanation": "This sentence uses 'I' with the verb 'to be' in the present simple form.", "correct_answer": "am", "sentence_with_blank": "I ___ a student at the local school."}, {"item_id": "2", "base_verb": "come", "explanation": "Here, 'John' is a singular subject, so we add 's' to the base verb 'come'.", "correct_answer": "comes", "sentence_with_blank": "My friend, John, ___ from Canada."}, {"item_id": "3", "base_verb": "be", "explanation": "In this sentence, 'we' requires the verb 'to be' in its plural form.", "correct_answer": "are", "sentence_with_blank": "We ___ in the same class."}, {"item_id": "4", "base_verb": "be", "explanation": "The subject 'you' takes the verb 'to be' in its present simple form.", "correct_answer": "are", "sentence_with_blank": "You ___ very friendly, and we often study together."}, {"item_id": "5", "base_verb": "be", "explanation": "In this sentence, 'they' requires the verb 'to be' in its plural form.", "correct_answer": "are", "sentence_with_blank": "They ___ great at helping others, too!"}], "widget": "fill_in_blanks", "passage": "Hello! My name is Sarah. I ___ a student at the local school. My friend, John, ___ from Canada. We ___ in the same class. You ___ very friendly, and we often study together. They ___ great at helping others, too!", "activity": "read", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice introducing ourselves using the present simple tense! Fill in the blanks with the correct form of the verb.", "topic_name": "introduce yourself using I/you/we/they — present simple — statements (I, you, we, they + base verb)", "instructions": "Read the paragraph and type the numbered answers into the blanks.", "estimated_time_minutes": 4, "grammar_rule_explained": "Use 'I', 'you', 'we', and 'they' with the present simple form of verbs to make statements about who we are and what we do."}	0	[{"role": "ai", "type": "chat", "content": "Imagine it's your first day on campus, and you need to introduce yourself. You can say something simple like, \\"I am a student.\\" How would you introduce yourself to a new classmate using \\"I,\\" \\"you,\\" or \\"we\\"?"}, {"role": "user", "type": "chat", "content": "I am the class leader of this class."}, {"role": "ai", "type": "chat", "content": "It's your first day on campus, and you want to make a good impression. You can say something like, \\"I love movies.\\" How would you introduce yourself to your classmates using \\"they\\" or \\"we\\"?"}]	\N	\N	\N	f	2026-05-19 03:59:24.056982+00	2026-05-19 04:00:35.244381+00	132	[{"title": "Subskill.Grammar - Activity.Read - Uiwidget.Fill In Blanks", "status": "pending", "task_id": 101, "task_type": "curriculum_grammar_fill_blanks", "completed_at": null, "user_task_id": 132, "sequence_index": 0}, {"title": "Subskill.Grammar - Activity.Write - Uiwidget.Open Text", "status": "pending", "task_id": 102, "task_type": "curriculum_grammar_open_text", "completed_at": null, "user_task_id": 133, "sequence_index": 1}]	1
31	05dc4ab0253345ea9da91ae1ac933407	29	9	feedback	Present Simple Tense — Basics	grammar	speak	curriculum_grammar_speak	1	{"widget": "speak_and_record", "activity": "speak", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice using the Present Simple Tense! Speak about your daily activities and routines.", "topic_name": "Present Simple Tense — Basics", "instructions": "Use the prompts below to practice speaking in the present simple tense. Record your answers and make sure to use correct sentence structure.", "sample_responses": ["Every day, I wake up at 7 AM. I eat breakfast and then I go to work. After work, I exercise and have dinner with my family.", "I have several hobbies. I play soccer every weekend and I read books in the evenings. I also enjoy painting when I have free time.", "My father is a teacher. He teaches math at a high school. My mother is a nurse, and she works at the local hospital."], "speaking_prompts": ["Describe your daily routine. What do you do every day?", "What hobbies do you have? How often do you practice them?", "Tell me about your family. What do they do for a living?"], "estimated_time_minutes": 6, "grammar_rule_to_practice": "present simple tense", "speaking_duration_seconds": 45}	3	[{"role": "ai", "type": "chat", "content": "The Present Simple tense helps us talk about habits and routines, like things we do every day. When you fill in the blanks, look for the subject first, then think about the verb form. Can you tell me something you do every day?"}, {"role": "user", "type": "chat", "content": "I walk"}, {"role": "ai", "type": "chat", "content": "Great! \\"I walk\\" is a good example of using the base verb. Remember, when we use \\"I,\\" \\"you,\\" \\"we,\\" or \\"they,\\" we just use the base form of the verb. Can you think of another sentence with \\"you\\" or \\"they\\"?"}, {"role": "user", "type": "chat", "content": "they talk about others all the time"}, {"role": "ai", "type": "chat", "content": "That's a nice sentence! When we talk about \\"he,\\" \\"she,\\" or \\"it,\\" we need to add an \\"s\\" or \\"es\\" to the verb. For example, \\"he walks\\" or \\"she watches.\\" Can you think of a sentence using \\"he\\" or \\"she\\"?"}, {"role": "user", "type": "chat", "content": "he sings well"}, {"role": "ai", "type": "chat", "content": "Great job with \\"he sings well\\"! Now, let’s talk about frequency words like \\"always,\\" \\"often,\\" and \\"usually.\\" These words help us describe how often we do something. For example, you could say, \\"He usually sings well.\\" Can you think of a frequency word to use with a sentence about something you do?"}, {"role": "user", "type": "chat", "content": "He sings for the church every morning"}, {"role": "ai", "type": "chat", "content": "You have practiced the main idea for Present Simple Tense — Basics: find the subject, look for time or frequency clues, and choose the verb form. Does this feel clear enough to start the practice task?"}, {"role": "user", "type": "chat", "content": "okay"}, {"role": "ai", "type": "chat", "content": "Great! Here is activity 1 of 4."}, {"role": "ai", "type": "ui_event", "content": "[task delivered: curriculum_grammar_fill_blanks]"}, {"role": "ai", "type": "ui_event", "content": "[scorecard delivered: 80%]"}, {"role": "ai", "type": "ui_event", "content": "[feedback card delivered]"}, {"role": "ai", "type": "chat", "content": "You did well with most of the answers, but you made a mistake with one. Remember that plural subjects do not take an 's'."}, {"role": "user", "type": "chat", "content": "Next activity"}, {"role": "ai", "type": "chat", "content": "Great! Here is activity 2 of 4."}, {"role": "ai", "type": "ui_event", "content": "[task delivered: curriculum_grammar_open_text]"}, {"role": "ai", "type": "ui_event", "content": "[scorecard delivered: 100%]"}, {"role": "ai", "type": "ui_event", "content": "[feedback card delivered]"}, {"role": "ai", "type": "chat", "content": "Your sentences are all correct and well-structured. However, to elevate your writing, focus on using more varied vocabulary and sentence structures."}, {"role": "user", "type": "chat", "content": "Next activity"}, {"role": "ai", "type": "chat", "content": "Great! Here is activity 3 of 4."}, {"role": "ai", "type": "ui_event", "content": "[task delivered: curriculum_grammar_listen_mcq]"}, {"role": "ai", "type": "ui_event", "content": "[scorecard delivered: 100%]"}, {"role": "ai", "type": "ui_event", "content": "[feedback card delivered]"}, {"role": "ai", "type": "chat", "content": "You answered all questions correctly, which shows a good understanding of the material! To further improve, focus on listening for details in longer passages."}, {"role": "user", "type": "chat", "content": "Next activity"}, {"role": "ai", "type": "chat", "content": "Great! Here is activity 4 of 4."}, {"role": "ai", "type": "ui_event", "content": "[task delivered: curriculum_grammar_speak]"}, {"role": "ai", "type": "ui_event", "content": "[scorecard delivered: 30%]"}, {"role": "ai", "type": "ui_event", "content": "[feedback card delivered]"}, {"role": "ai", "type": "chat", "content": "You showed understanding in some areas, but you need to focus on using the present simple tense consistently. Your main mistakes were using future tense and incorrect sentence structures."}]	{"recordings": [{"item_id": "prompt_1", "transcript": "Hi, my daily routine includes, I wake up early in the morning, then I eat my breakfast at 7.30, then I go to work and work until afternoon, I will come back at 6 and I take a shower, then I will prepare a meal for dinner and eat it at 7.30.", "attempt_number": 1, "audio_blob_url": "/audio/user-recordings/1a1cc332fc7f2697.webm", "duration_seconds": 45}, {"item_id": "prompt_2", "transcript": "I read books every night before going to bed. This is a habit that I built to calm down my stress before sleeping.", "attempt_number": 2, "audio_blob_url": "/audio/user-recordings/df04f65d69ee2bde.webm", "duration_seconds": 45}, {"item_id": "prompt_3", "transcript": "My father farms rubber and other crops, my mother is a housekeeper and my brother studies in a university and my grandfather sits simply at home without doing nothing.", "attempt_number": 1, "audio_blob_url": "/audio/user-recordings/cf9c30b20adcdbe7.webm", "duration_seconds": 40}], "time_spent_seconds": 242}	{"total": 3, "questions": {"prompt_1": {"score": 0.0, "prompt": "Describe your daily routine. What do you do every day?", "correct": false, "mistakes": ["Used future tense 'will come back' instead of present simple", "Used 'take a shower' without a subject", "Incorrect structure with multiple 'then' phrases"], "audio_url": "/audio/user-recordings/1a1cc332fc7f2697.webm", "error_type": "needs_review", "user_answer": "Hi, my daily routine includes, I wake up early in the morning, then I eat my breakfast at 7.30, then I go to work and work until afternoon, I will come back at 6 and I take a shower, then I will prepare a meal for dinner and eat it at 7.30.", "correct_answer": "Every day, I wake up at 7 AM. I eat breakfast and then I go to work. After work, I exercise and have dinner with my family.", "duration_seconds": 45, "grammar_rule_used": false, "grammar_rule_to_practice": "present simple tense"}, "prompt_2": {"score": 1.0, "prompt": "What hobbies do you have? How often do you practice them?", "correct": true, "mistakes": [], "audio_url": "/audio/user-recordings/df04f65d69ee2bde.webm", "error_type": "correct", "user_answer": "I read books every night before going to bed. This is a habit that I built to calm down my stress before sleeping.", "correct_answer": "I have several hobbies. I play soccer every weekend and I read books in the evenings. I also enjoy painting when I have free time.", "duration_seconds": 45, "grammar_rule_used": true, "grammar_rule_to_practice": "present simple tense"}, "prompt_3": {"score": 1.0, "prompt": "Tell me about your family. What do they do for a living?", "correct": true, "mistakes": ["Used present continuous 'is sitting' instead of present simple", "Incorrect structure with 'without doing nothing'"], "audio_url": "/audio/user-recordings/cf9c30b20adcdbe7.webm", "error_type": "correct", "user_answer": "My father farms rubber and other crops, my mother is a housekeeper and my brother studies in a university and my grandfather sits simply at home without doing nothing.", "correct_answer": "My father is a teacher. He teaches math at a high school. My mother is a nurse, and she works at the local hospital.", "duration_seconds": 40, "grammar_rule_used": true, "grammar_rule_to_practice": "present simple tense"}}, "task_type": "curriculum_grammar_speak", "percentage": 30.0, "correct_count": 2, "main_mistakes": ["Failure to consistently use present simple tense", "Incorrect sentence structure", "Use of future tense instead of present simple"], "overall_level": "needs_work", "subskill_score": 3}	{"score": 30, "errors": [{"rule": "Use present simple tense for daily routines. For example, say 'I take a shower' instead of 'I will take a shower'.", "why_wrong": "You used future tense with 'will come back' and 'will prepare' instead of present simple. Also, 'take a shower' needs a subject like 'I'.", "correction": "Hi, my daily routine is to wake up early in the morning, then I eat breakfast at 7:30, then I go to work and work until the afternoon. I come back at 6, take a shower, prepare a meal for dinner, and eat at 7:30.", "error_type": "needs_review", "memory_tip": "Remember to use 'I' for actions you're doing now and not 'will' for daily activities.", "question_id": "prompt_1", "user_answer": "Hi, my daily routine includes, I wake up early in the morning, then I eat my breakfast at 7.30, then I go to work and work until afternoon, I will come back at 6 and I take a shower, then I will prepare a meal for dinner and eat it at 7.30.", "correct_answer": "Every day, I wake up at 7 AM. I eat breakfast and then I go to work. After work, I exercise and have dinner with my family."}, {"rule": "Use simple present tense for actions. Avoid double negatives like 'without doing nothing'.", "why_wrong": "You used 'sits simply' which is incorrect structure. Also, 'without doing nothing' is a double negative.", "correction": "My father farms rubber and other crops, my mother is a housekeeper, my brother studies at a university, and my grandfather sits at home doing nothing.", "error_type": "correct", "memory_tip": "In English, avoid using two negatives together. Just say 'doing nothing'.", "question_id": "prompt_3", "user_answer": "My father farms rubber and other crops, my mother is a housekeeper and my brother studies in a university and my grandfather sits simply at home without doing nothing.", "correct_answer": "My father is a teacher. He teaches math at a high school. My mother is a nurse, and she works at the local hospital."}], "overall_level": "needs_work", "overall_message": "You showed understanding in some areas, but you need to focus on using the present simple tense consistently. Your main mistakes were using future tense and incorrect sentence structures.", "practice_suggestion": "Practice rewriting sentences in the present simple tense. Write 5 sentences about your daily routine using 'I' and the present simple."}	t	2026-05-15 03:27:51.188867+00	2026-05-15 03:39:44.942325+00	125	[{"title": "Subskill.Grammar - Activity.Read - Uiwidget.Fill In Blanks", "status": "completed", "task_id": 91, "task_type": "curriculum_grammar_fill_blanks", "completed_at": "2026-05-15T03:31:51.467223+00:00", "user_task_id": 122, "sequence_index": 0}, {"title": "Subskill.Grammar - Activity.Write - Uiwidget.Open Text", "status": "completed", "task_id": 92, "task_type": "curriculum_grammar_open_text", "completed_at": "2026-05-15T03:33:37.879005+00:00", "user_task_id": 123, "sequence_index": 1}, {"title": "Subskill.Grammar - Activity.Listen - Uiwidget.Listen And Respond", "status": "completed", "task_id": 93, "task_type": "curriculum_grammar_listen_mcq", "completed_at": "2026-05-15T03:35:09.155321+00:00", "user_task_id": 124, "sequence_index": 2}, {"title": "Subskill.Grammar - Activity.Speak - Uiwidget.Speak And Record", "status": "completed", "task_id": 94, "task_type": "curriculum_grammar_speak", "completed_at": "2026-05-15T03:39:44.949512+00:00", "user_task_id": 125, "sequence_index": 3}]	1
32	5ed41feea82c418ba2fa6e381709e251	29	9	practice_task	Everyday Words — Family & Home	vocabulary	read	curriculum_vocab_mcq	1	{"items": [{"prompt": "What does 'mother' mean?", "item_id": "1", "options": ["A male parent", "A female parent", "A sibling", "A grandparent"], "explanation": "'Mother' refers to a female parent.", "correct_index": 1}, {"prompt": "What does 'brother' mean?", "item_id": "2", "options": ["A male sibling", "A female sibling", "A parent", "A child"], "explanation": "'Brother' refers to a male sibling.", "correct_index": 0}, {"prompt": "Pick the word that best fits the sentence: My ___ is very kind to me. ___ can refer to a sibling or a female relative.", "item_id": "3", "options": ["sister", "father", "mother", "friend"], "explanation": "'Sister' is a female sibling.", "correct_index": 0}, {"prompt": "Pick the word that best fits the sentence: I love my home because it is cozy and warm. ___ is where one lives.", "item_id": "4", "options": ["House", "Car", "School", "Park"], "explanation": "'Home' refers to the place where one lives.", "correct_index": 0}], "widget": "mcq", "activity": "read", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's learn some important words related to family and home! Choose the correct answers for each question.", "topic_name": "Everyday Words — Family & Home", "instructions": "Read each question carefully and select the correct answer from the options provided.", "target_words": ["mother", "brother", "home", "sister"], "estimated_time_minutes": 4}	0	[{"role": "ai", "type": "chat", "content": "Let’s think about family words. A \\"mother\\" is a woman who has children. Can you tell me, what is a father?"}, {"role": "user", "type": "chat", "content": "a male parent"}, {"role": "ai", "type": "chat", "content": "Great! A father is indeed a male parent. Now, when we talk about family vocabulary, we often use words like mother, father, sister, and brother. In the practice task, you'll see sentences with blanks, and you need to choose the right family word. Can you think of a family member you can name?"}, {"role": "user", "type": "chat", "content": "my brother name is Austin"}, {"role": "ai", "type": "chat", "content": "That's right! Austin is your brother. When you're filling in the blanks, remember that words like \\"sister\\" and \\"brother\\" are different. A sister is a female sibling, and a brother is a male sibling. Can you think of a sentence using one of these family words?"}, {"role": "user", "type": "chat", "content": "My father is a farmer"}, {"role": "ai", "type": "chat", "content": "You have practiced the main idea for Everyday Words — Family & Home: find the subject, look for time or frequency clues, and choose the verb form. Does this feel clear enough to start the practice task?"}, {"role": "user", "type": "chat", "content": "yes"}, {"role": "ai", "type": "chat", "content": "Great! Here is activity 1 of 4."}, {"role": "ai", "type": "ui_event", "content": "[task delivered: curriculum_vocab_mcq]"}]	\N	\N	\N	t	2026-05-15 04:20:35.10709+00	2026-05-16 08:10:14.987704+00	126	[{"title": "Subskill.Vocabulary - Activity.Read - Uiwidget.Mcq", "status": "in_progress", "task_id": 95, "task_type": "curriculum_vocab_mcq", "completed_at": null, "user_task_id": 126, "sequence_index": 0}, {"title": "Subskill.Vocabulary - Activity.Write - Uiwidget.Open Text", "status": "pending", "task_id": 96, "task_type": "curriculum_vocab_open_text", "completed_at": null, "user_task_id": 127, "sequence_index": 1}, {"title": "Subskill.Vocabulary - Activity.Listen - Uiwidget.Listen And Respond", "status": "pending", "task_id": 97, "task_type": "curriculum_vocab_listen_mcq", "completed_at": null, "user_task_id": 128, "sequence_index": 2}, {"title": "Subskill.Vocabulary - Activity.Speak - Uiwidget.Speak And Record", "status": "pending", "task_id": 98, "task_type": "curriculum_vocab_speak", "completed_at": null, "user_task_id": 129, "sequence_index": 3}]	1
\.


--
-- Data for Name: oauth_accounts; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.oauth_accounts (id, user_id, provider, provider_user_id, created_at, updated_at) FROM stdin;
4	38	google	108738025989322532922	2026-05-18 16:28:01.893366+00	2026-05-18 16:28:01.893366+00
\.


--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.payments (user_id, provider, provider_payment_id, amount, currency, status, paid_at, id, created_at) FROM stdin;
37	mock	mock_8_f7c8636f92e545b8a7e3279c75addd8d	1999.00	INR	paid	2026-05-18 12:37:26.648095+00	2	2026-05-18 12:37:26.574745+00
38	mock	mock_9_c4bf8cecd3f9449f886917cd264fa0bc	999.00	INR	paid	2026-05-18 16:29:39.844705+00	3	2026-05-18 16:29:39.730771+00
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.permissions (key, description, id, created_at) FROM stdin;
users.read	View user accounts in the admin console.	1	2026-05-15 03:21:59.792571+00
users.update_status	Activate or deactivate user accounts.	2	2026-05-15 03:21:59.792571+00
users.view_progress	View learner progress and task history.	3	2026-05-15 03:21:59.792571+00
task_templates.read	View task templates.	4	2026-05-15 03:21:59.792571+00
task_templates.create	Create task templates.	5	2026-05-15 03:21:59.792571+00
task_templates.update	Update task templates.	6	2026-05-15 03:21:59.792571+00
task_templates.archive	Archive task templates.	7	2026-05-15 03:21:59.792571+00
feedback_logs.read	View feedback review queues and logs.	8	2026-05-15 03:21:59.792571+00
feedback_quality.review	Review and annotate AI feedback quality.	9	2026-05-15 03:21:59.792571+00
ai_logs.read	View AI request logs.	10	2026-05-15 03:21:59.792571+00
ai_costs.read	View AI usage and cost information.	11	2026-05-15 03:21:59.792571+00
payments.read	View limited payment and billing information.	12	2026-05-15 03:21:59.792571+00
subscriptions.manage	Manage subscription status and periods.	13	2026-05-15 03:21:59.792571+00
audit_logs.read	View admin audit logs.	14	2026-05-15 03:21:59.792571+00
admins.manage	Assign or remove administrator roles.	15	2026-05-15 03:21:59.792571+00
roles.manage	Update role permission grants.	16	2026-05-15 03:21:59.792571+00
\.


--
-- Data for Name: progress_logs; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.progress_logs (user_id, skill_id, score, id, created_at) FROM stdin;
29	1	3.3	35	2026-05-04 05:15:58.146975+00
29	6	2.5	36	2026-05-04 05:15:58.146975+00
29	1	3.6	37	2026-05-05 04:53:37.263013+00
29	6	2.6	38	2026-05-05 04:53:37.263013+00
29	1	4.2	39	2026-05-05 04:54:05.113521+00
29	6	2.8	40	2026-05-05 04:54:05.113521+00
29	1	4.3	41	2026-05-05 06:03:50.94682+00
29	6	2.9	42	2026-05-05 06:03:50.94682+00
29	1	5.4	43	2026-05-05 06:07:47.83668+00
29	1	5.7	44	2026-05-05 07:19:44.0067+00
29	1	6.6	45	2026-05-06 13:06:33.455366+00
29	1	7.3	46	2026-05-06 13:14:27.415103+00
29	1	6.8	47	2026-05-06 13:40:22.728788+00
29	1	7.4	48	2026-05-06 13:42:22.174736+00
29	1	7.7	49	2026-05-06 13:53:10.084599+00
29	1	7.6	51	2026-05-06 14:40:58.110184+00
29	1	8.1	53	2026-05-06 15:15:38.29022+00
29	1	7.8	54	2026-05-06 15:34:33.383032+00
29	1	7.8	66	2026-05-15 03:31:46.214411+00
29	1	8.2	67	2026-05-15 03:33:31.199461+00
29	1	8.6	68	2026-05-15 03:35:05.546395+00
29	1	7.5	69	2026-05-15 03:39:27.588629+00
\.


--
-- Data for Name: purchases; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.purchases (user_id, plan_id, plan_name, amount_paid, currency, status, id, created_at, updated_at) FROM stdin;
37	beginner-48w	48-Week Plan	1999.00	INR	paid	8	2026-05-18 12:37:26.574745+00	2026-05-18 12:37:26.574745+00
38	beginner-24w	24-Week Foundation	999.00	INR	paid	9	2026-05-18 16:29:39.730771+00	2026-05-18 16:29:39.730771+00
\.


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.role_permissions (role_id, permission_id) FROM stdin;
2	1
2	2
2	3
2	4
2	5
2	6
2	7
2	8
2	9
2	10
2	11
2	12
2	14
3	1
3	2
3	3
3	4
3	5
3	6
3	7
3	8
3	9
3	10
3	11
3	12
3	13
3	14
3	15
3	16
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.roles (name, id, created_at) FROM stdin;
learner	1	2026-05-14 14:48:07.277127+00
admin	2	2026-05-14 14:48:07.277127+00
super_admin	3	2026-05-14 14:48:07.277127+00
\.


--
-- Data for Name: session_scorecards; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.session_scorecards (id, session_id, points_earned, subskill_totals_after, dashboard_after, completed_at, ruleset_version, created_at) FROM stdin;
\.


--
-- Data for Name: skill_point_history; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.skill_point_history (id, user_id, skill_id, session_id, points_delta, points_after, created_at) FROM stdin;
\.


--
-- Data for Name: skill_points; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.skill_points (user_id, skill_id, points, display_score, id, created_at, updated_at) FROM stdin;
29	1	3175	3.2	4	2026-05-15 03:31:51.424034+00	2026-05-15 03:39:44.912692+00
37	1	2500	2.5	12	2026-05-18 13:02:12.847961+00	2026-05-18 13:02:12.847961+00
37	2	2070	2.1	13	2026-05-18 13:02:12.847961+00	2026-05-18 13:02:12.847961+00
37	3	2000	2.0	14	2026-05-18 13:02:12.847961+00	2026-05-18 13:02:12.847961+00
37	4	2240	2.2	15	2026-05-18 13:02:12.847961+00	2026-05-18 13:02:12.847961+00
37	5	1890	1.9	16	2026-05-18 13:02:12.847961+00	2026-05-18 13:02:12.847961+00
37	7	1570	1.6	17	2026-05-18 13:02:12.847961+00	2026-05-18 13:02:12.847961+00
37	6	2290	2.3	18	2026-05-18 13:02:12.847961+00	2026-05-18 13:02:12.847961+00
38	1	1250	1.3	19	2026-05-18 16:29:04.252811+00	2026-05-18 16:29:04.252811+00
38	2	1400	1.4	20	2026-05-18 16:29:04.252811+00	2026-05-18 16:29:04.252811+00
38	3	1250	1.3	21	2026-05-18 16:29:04.252811+00	2026-05-18 16:29:04.252811+00
38	4	1960	2.0	22	2026-05-18 16:29:04.252811+00	2026-05-18 16:29:04.252811+00
38	5	1560	1.6	23	2026-05-18 16:29:04.252811+00	2026-05-18 16:29:04.252811+00
38	7	1400	1.4	24	2026-05-18 16:29:04.252811+00	2026-05-18 16:29:04.252811+00
38	6	1320	1.3	25	2026-05-18 16:29:04.252811+00	2026-05-18 16:29:04.252811+00
\.


--
-- Data for Name: skill_points_logs; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.skill_points_logs (user_id, skill_id, points_earned, reason, id, created_at) FROM stdin;
29	1	55	excellent_task_24w	12	2026-05-15 03:31:51.424034+00
29	1	55	excellent_task_24w	13	2026-05-15 03:33:37.851607+00
29	1	55	excellent_task_24w	14	2026-05-15 03:35:09.131286+00
29	1	10	poor_task_24w	15	2026-05-15 03:39:44.912692+00
\.


--
-- Data for Name: skills; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.skills (name, description, id, created_at, display_label) FROM stdin;
grammar	Grammar & Sentence Construction	1	2026-04-25 05:45:07.622467+00	Grammar
vocabulary	Vocabulary & Word Choice	2	2026-04-25 05:45:07.622467+00	Vocabulary
pronunciation	Pronunciation & Speech Clarity	3	2026-04-25 05:45:07.622467+00	Pronunciation
fluency	Fluency & Spontaneity	4	2026-04-25 05:45:07.622467+00	Fluency
expression	Thought Organization & Expression	5	2026-04-25 05:45:07.622467+00	Thought Organization
comprehension	Listening & Reading Comprehension	6	2026-04-25 05:45:07.622467+00	Listening
tone	Tone & Social Awareness	7	2026-04-25 05:45:07.622467+00	Tone & Social
\.


--
-- Data for Name: streak_freeze_usages; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.streak_freeze_usages (id, user_id, protected_date, used_at, reason, created_at) FROM stdin;
\.


--
-- Data for Name: subscriptions; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.subscriptions (user_id, provider, provider_customer_id, provider_subscription_id, plan_name, status, trial_ends_at, current_period_start, current_period_end, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: task_archetypes; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.task_archetypes (id, name, core_activity, description, ui_widget, inner_widget, input_type, themes_supported, cefr_min, cefr_max, weight_map, rubric, evaluation_prompt_ref, feedback_prompt_ref, mvp, created_at, updated_at) FROM stdin;
READ_COMP_MCQ	Reading Comprehension MCQ	read	Passage + 4–5 MCQs probing main idea + details.	mcq_list	\N	mcq	["grammar", "communication", "vocabulary", "confidence"]	A1	C2	{"grammar": 0.25, "expression": 0.35, "vocabulary": 0.4}	["accuracy", "vocabulary_inference", "comprehension_depth", "structural_understanding"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
READ_TFNG	True / False / Not Given	read	Passage + 4–6 statements judged True / False / Not Given.	true_false_not_given	\N	choice	["grammar", "communication", "vocabulary", "confidence"]	A2	C2	{"grammar": 0.2, "expression": 0.5, "vocabulary": 0.3}	["accuracy", "vocabulary_inference", "comprehension_depth", "structural_understanding"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
READ_ERROR_SPOT	Error Spotting	read	Sentences with possible grammar errors — learner flags them.	error_spotting	\N	choice	["grammar"]	A2	C1	{"grammar": 0.7, "vocabulary": 0.3}	["grammatical_accuracy", "vocabulary_range"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
READ_CLOZE	Cloze (Fill-in-blanks, MCQ options)	read	Paragraph with blanks; each blank has 3–4 option choices.	fill_in_blanks_mcq	\N	choice	["grammar", "vocabulary"]	A1	C1	{"grammar": 0.5, "expression": 0.15, "vocabulary": 0.35}	["accuracy", "vocabulary_inference", "comprehension_depth", "structural_understanding"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
READ_WORD_MATCH	Word ↔ Meaning Match	read	Match each vocab word to one of 4 candidate meanings.	mcq_list	\N	mcq	["vocabulary"]	A1	C2	{"vocabulary": 1.0}	["vocabulary_range", "accuracy"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
READ_CONTEXT_MCQ	Contextual Vocabulary	read	Short context + meaning-of-word MCQ.	mcq_list	\N	mcq	["vocabulary", "communication"]	A2	C2	{"grammar": 0.1, "expression": 0.2, "vocabulary": 0.7}	["accuracy", "vocabulary_inference", "comprehension_depth", "structural_understanding"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
READ_TONE_ID	Tone Identification	read	Passage + tone-of-voice MCQ.	mcq_list	\N	mcq	["confidence", "communication"]	B1	C2	{"tone": 0.7, "vocabulary": 0.3}	["comprehension_depth", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
READ_STRUCTURE_ID	Structure Identification	read	Label sections of a passage (intro / body / conclusion).	open_text_list	\N	text	["confidence", "communication"]	B1	C2	{"expression": 0.8, "vocabulary": 0.2}	["structural_understanding", "coherence"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
WRITE_SENT_TRANS	Sentence Transformation	write	Rewrite each sentence into the target form.	sentence_transform	\N	text	["grammar"]	A2	C1	{"grammar": 0.7, "expression": 0.1, "vocabulary": 0.2}	["grammatical_accuracy", "task_completion"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
WRITE_ERROR_CORR	Error Correction	write	Rewrite a wrong sentence into a corrected version.	error_correction	\N	text	["grammar"]	A1	C2	{"grammar": 0.8, "vocabulary": 0.2}	["grammatical_accuracy", "vocabulary_range"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
WRITE_PARA	Paragraph Writing	write	Write a paragraph on a topic (80–150 words).	open_text_list	\N	text	["communication", "vocabulary", "confidence"]	A2	C2	{"grammar": 0.35, "expression": 0.4, "vocabulary": 0.25}	["grammatical_accuracy", "vocabulary_range", "coherence", "task_completion", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
WRITE_ESSAY	Structured Essay	write	Multi-section essay with intro/body/conclusion.	structured_essay	\N	text	["communication", "confidence"]	B1	C2	{"grammar": 0.25, "expression": 0.45, "vocabulary": 0.3}	["grammatical_accuracy", "vocabulary_range", "coherence", "task_completion", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
WRITE_EMAIL	Email Writing	write	Compose a scenario email (80–200 words).	open_text_list	\N	text	["communication"]	A2	C2	{"tone": 0.4, "grammar": 0.25, "expression": 0.15, "vocabulary": 0.2}	["grammatical_accuracy", "vocabulary_range", "coherence", "task_completion", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
WRITE_CONCISE	Conciseness Rewrite	write	Trim a wordy sentence into a shorter version.	error_correction	\N	text	["grammar", "vocabulary"]	B1	C2	{"grammar": 0.3, "expression": 0.3, "vocabulary": 0.4}	["task_completion", "vocabulary_range", "coherence"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
WRITE_WORD_UPGRADE	Word Upgrade	write	Replace simple words with more advanced equivalents.	open_text_list	\N	text	["vocabulary"]	B1	C2	{"grammar": 0.2, "vocabulary": 0.8}	["vocabulary_range", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
WRITE_PARAPHRASE	Paraphrasing	write	Re-express the same idea in your own words.	open_text_list	\N	text	["vocabulary", "communication"]	B1	C2	{"grammar": 0.2, "expression": 0.4, "vocabulary": 0.4}	["grammatical_accuracy", "vocabulary_range", "coherence", "task_completion", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
WRITE_REGISTER	Register Conversion	write	Rewrite a sentence in a target register (formal ↔ casual).	error_correction	\N	text	["communication", "confidence"]	B1	C2	{"tone": 0.6, "grammar": 0.15, "vocabulary": 0.25}	["register", "vocabulary_range", "grammatical_accuracy"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
WRITE_IDEA_PARA	Idea Paraphrasing	write	Restate the concept (not just the words) in your own form.	open_text_list	\N	text	["communication", "confidence"]	B2	C2	{"grammar": 0.1, "expression": 0.6, "vocabulary": 0.3}	["coherence", "task_completion", "vocabulary_range"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
WRITE_SUMMARY	Passage Summary	write	Summarize a passage in a given word limit.	passage_summary	\N	text	["communication", "confidence"]	B1	C2	{"grammar": 0.2, "expression": 0.5, "vocabulary": 0.3}	["grammatical_accuracy", "vocabulary_range", "coherence", "task_completion", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
WRITE_TIMED	Timed Writing	write	Write fast against a timer — no editing.	timed_writing	\N	text	["confidence", "vocabulary"]	A2	C2	{"fluency": 0.3, "grammar": 0.2, "expression": 0.25, "vocabulary": 0.25}	["task_completion", "coherence", "vocabulary_range"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
WRITE_VOICE_CONV	Active ↔ Passive Voice	write	Convert sentence between active and passive voice.	sentence_transform	\N	text	["grammar"]	B1	C1	{"grammar": 0.8, "vocabulary": 0.2}	["grammatical_accuracy"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
WRITE_BULLETS_TO_PARA	Bullets → Paragraph	write	Convert a bullet list into flowing prose.	open_text_list	\N	text	["communication", "confidence"]	B1	C2	{"grammar": 0.2, "expression": 0.6, "vocabulary": 0.2}	["coherence", "task_completion", "grammatical_accuracy"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
LISTEN_MCQ	Audio MCQ	listen	Audio + 4-option comprehension questions.	listen_and_answer	mcq_list	mcq	["communication", "vocabulary", "grammar", "confidence"]	A1	C2	{"expression": 0.15, "vocabulary": 0.25, "comprehension": 0.6}	["detail_accuracy", "main_idea", "inference", "vocabulary_recognition"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
LISTEN_CLOZE	Cloze Listening	listen	Audio + transcript with blanks the learner fills.	listen_and_answer	fill_in_blanks_mcq	choice	["grammar", "vocabulary"]	A2	C1	{"grammar": 0.3, "vocabulary": 0.2, "comprehension": 0.5}	["detail_accuracy", "main_idea", "inference", "vocabulary_recognition"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
LISTEN_DICTATION	Dictation	listen	Type the sentence you hear.	listen_and_answer	open_text_list	text	["grammar", "vocabulary"]	A1	C1	{"grammar": 0.3, "vocabulary": 0.2, "comprehension": 0.5}	["detail_accuracy", "grammatical_accuracy"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
LISTEN_INFER	Inference Listening	listen	Audio + interpretive (implied-meaning) questions.	listen_and_answer	mcq_list	mcq	["communication", "confidence"]	B1	C2	{"expression": 0.35, "vocabulary": 0.15, "comprehension": 0.5}	["detail_accuracy", "main_idea", "inference", "vocabulary_recognition"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
LISTEN_RETELL	Retell What You Heard	listen	Listen, then speak a short summary back.	listen_and_answer	speak_and_record	audio	["communication", "confidence"]	B1	C2	{"fluency": 0.2, "expression": 0.3, "vocabulary": 0.2, "comprehension": 0.3}	["pronunciation", "fluency", "grammatical_control", "vocabulary_use", "thought_organization", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
LISTEN_SHADOW	Shadow Speaking	listen	Repeat audio out loud, matching rhythm + intonation.	listen_and_answer	speak_and_record	audio	["confidence"]	A1	C2	{"fluency": 0.25, "comprehension": 0.3, "pronunciation": 0.45}	["pronunciation", "fluency", "detail_accuracy"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
LISTEN_TONE	Detect Speaker Tone	listen	Identify the emotional register or attitude in the audio.	listen_and_answer	mcq_list	mcq	["confidence", "communication"]	B1	C2	{"tone": 0.55, "comprehension": 0.45}	["inference", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
SPEAK_READ_ALOUD	Read Aloud	speak	Read a passage aloud.	speak_and_record	\N	audio	["confidence"]	A1	C1	{"fluency": 0.2, "grammar": 0.1, "pronunciation": 0.7}	["pronunciation", "fluency"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
SPEAK_PIC_DESC	Picture Description	speak	Describe an image in 30–60 seconds.	speak_and_record	\N	audio	["confidence", "vocabulary"]	A1	C2	{"fluency": 0.3, "grammar": 0.2, "expression": 0.2, "vocabulary": 0.3}	["pronunciation", "fluency", "grammatical_control", "vocabulary_use", "thought_organization", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
SPEAK_TIMED	Timed Speaking	speak	Speak on a prompt against a timer — no long pauses.	speak_and_record	\N	audio	["confidence"]	A2	C2	{"fluency": 0.5, "grammar": 0.1, "expression": 0.25, "vocabulary": 0.15}	["fluency", "thought_organization"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
SPEAK_STORYBOARD	Storyboard Narration	speak	Narrate a sequence of generated images.	storyboard	\N	audio	["confidence", "communication"]	B1	C2	{"fluency": 0.25, "grammar": 0.2, "expression": 0.35, "vocabulary": 0.2}	["pronunciation", "fluency", "grammatical_control", "vocabulary_use", "thought_organization", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
SPEAK_INTERVIEW	Interview Response	speak	Answer interview-style questions out loud.	speak_and_record	\N	audio	["communication", "confidence"]	B1	C2	{"tone": 0.1, "fluency": 0.3, "grammar": 0.15, "expression": 0.25, "vocabulary": 0.2}	["pronunciation", "fluency", "grammatical_control", "vocabulary_use", "thought_organization", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
SPEAK_ROLEPLAY	Roleplay	speak	Multi-turn voice roleplay against an AI partner.	speak_and_record	\N	audio	["communication", "confidence"]	A2	C2	{"tone": 0.3, "fluency": 0.25, "grammar": 0.15, "vocabulary": 0.2, "pronunciation": 0.1}	["pronunciation", "fluency", "grammatical_control", "vocabulary_use", "thought_organization", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
SPEAK_OPINION	Opinion Speaking	speak	Defend a position out loud in 60–90 seconds.	speak_and_record	\N	audio	["confidence", "communication"]	B1	C2	{"fluency": 0.3, "grammar": 0.15, "expression": 0.35, "vocabulary": 0.2}	["pronunciation", "fluency", "grammatical_control", "vocabulary_use", "thought_organization", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
SPEAK_SMALLTALK	Small Talk Simulation	speak	Sustain casual back-and-forth with a persona.	speak_and_record	\N	audio	["confidence", "communication"]	A2	C2	{"tone": 0.35, "fluency": 0.3, "grammar": 0.15, "vocabulary": 0.2}	["pronunciation", "fluency", "grammatical_control", "vocabulary_use", "thought_organization", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
SPEAK_DEBATE	Debate Response	speak	Argue + rebut against an opposing claim.	speak_and_record	\N	audio	["confidence", "communication"]	B2	C2	{"tone": 0.1, "fluency": 0.25, "grammar": 0.15, "expression": 0.3, "vocabulary": 0.2}	["pronunciation", "fluency", "grammatical_control", "vocabulary_use", "thought_organization", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
SPEAK_PRON_DRILL	Pronunciation Drill	speak	Repeat target sounds + words for clarity.	speak_and_record	\N	audio	["confidence"]	A1	C2	{"fluency": 0.15, "pronunciation": 0.85}	["pronunciation"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
SPEAK_PRESENT	Presentation Practice	speak	Deliver a 60–90 second mini-presentation.	speak_and_record	\N	audio	["confidence", "communication"]	B2	C2	{"tone": 0.1, "fluency": 0.3, "expression": 0.25, "vocabulary": 0.2, "pronunciation": 0.15}	["pronunciation", "fluency", "grammatical_control", "vocabulary_use", "thought_organization", "register"]	\N	\N	t	2026-05-17 09:36:33.035788+00	2026-05-17 09:36:33.035788+00
\.


--
-- Data for Name: task_skills; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.task_skills (task_id, skill_id, weight, id) FROM stdin;
1	1	0.70	1
1	2	0.30	2
2	1	0.80	3
2	6	0.20	4
3	1	0.70	5
3	6	0.30	6
4	1	1.00	7
5	1	0.70	8
5	6	0.30	9
7	1	0.80	10
7	6	0.20	11
8	1	0.80	12
8	6	0.20	13
9	1	0.80	14
9	6	0.20	15
10	1	0.80	16
10	6	0.20	17
11	1	0.80	18
11	6	0.20	19
13	1	0.80	20
13	6	0.20	21
14	1	0.70	22
14	5	0.30	23
15	1	0.80	24
15	5	0.20	25
53	1	1.00	63
54	1	1.00	64
55	1	1.00	65
56	1	1.00	66
57	1	1.00	67
58	1	1.00	68
59	1	1.00	69
60	1	1.00	70
61	2	1.00	71
62	2	1.00	72
63	2	1.00	73
64	2	1.00	74
65	2	1.00	75
66	2	1.00	76
67	2	1.00	77
68	2	1.00	78
69	2	1.00	79
70	2	1.00	80
71	2	1.00	81
72	2	1.00	82
73	2	1.00	83
74	2	1.00	84
75	2	1.00	85
76	2	1.00	86
77	2	1.00	87
78	2	1.00	88
79	2	1.00	89
80	2	1.00	90
81	2	1.00	91
82	2	1.00	92
83	2	1.00	93
84	2	1.00	94
85	1	1.00	95
86	1	1.00	96
87	1	1.00	97
88	1	1.00	98
89	1	1.00	99
90	1	1.00	100
91	1	1.00	101
92	1	1.00	102
93	1	1.00	103
94	1	1.00	104
95	2	1.00	105
96	2	1.00	106
97	2	1.00	107
98	2	1.00	108
99	1	1.00	109
100	1	1.00	110
101	1	1.00	111
102	1	1.00	112
103	1	1.00	113
104	1	1.00	114
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.tasks (title, difficulty, content, id, created_at, updated_at, status, task_type) FROM stdin;
S13 test task	1	{"activities": [], "instruction": "test"}	7	2026-04-30 05:36:52.031213+00	2026-04-30 05:36:52.031213+00	active	writing
Test fill-in-the-blank	3	{"answer": "goes", "passage": "Maria ___ to school every day."}	1	2026-04-25 06:08:49.800525+00	2026-04-25 06:08:49.800525+00	active	reading
Daily Routine — Present Tense	1	{"source": {"text": "Maria is a school teacher. Every morning, she wakes up at six o'clock. She makes a cup of tea and reads the newspaper. After breakfast, she walks to school. Her students like her because she always smiles.", "type": "passage"}, "activities": [{"answers": {"Q1": "is", "Q2": "wakes", "Q3": "like", "Q4": "smiles"}, "questions": {"Q1": "Maria ___ (be) a school teacher.", "Q2": "She ___ (wake) up at six o'clock every morning.", "Q3": "Her students ___ (like) her.", "Q4": "She always ___ (smile) at them."}, "activity_id": "fib_1", "instruction": "Use the correct present tense form of the verb in brackets.", "activity_type": "fill_in_the_blanks"}], "instruction": "Read the passage and fill in the blanks with the correct verb form."}	2	2026-04-27 15:26:42.778317+00	2026-04-27 15:26:42.778317+00	active	reading
S12 test task	1	{"activities": [{"answers": {"Q1": "went", "Q2": "has"}, "questions": {"Q1": "Yesterday I ___ (go) to the market.", "Q2": "She ___ (have) breakfast every day."}, "activity_id": "fib_1", "activity_type": "fill_in_the_blanks"}], "instruction": "Fill in the blanks with the correct verb form."}	6	2026-04-30 05:03:53.459656+00	2026-04-30 05:03:53.459656+00	active	writing
S14 full-loop test	1	{"activities": [{"answers": {"Q1": "went", "Q2": "has"}, "questions": {"Q1": "Yesterday I ___ (go) to the market.", "Q2": "She ___ (have) breakfast every day."}, "activity_id": "fib_1", "activity_type": "fill_in_the_blanks"}], "instruction": "Fill in the blanks with the correct verb form."}	8	2026-04-30 06:16:58.628272+00	2026-04-30 06:16:58.628272+00	active	writing
The Job Interview — Past Tense	2	{"source": {"text": "Yesterday, Ahmed went to a job interview at a software company. While he was waiting in the lobby, he reviewed his notes. The interviewer arrived ten minutes late and apologized politely. Ahmed answered every question carefully. After the interview, he felt confident but tired.", "type": "passage"}, "activities": [{"answers": {"Q1": "went", "Q2": "was waiting", "Q3": "arrived", "Q4": "felt"}, "questions": {"Q1": "Yesterday, Ahmed ___ (go) to a job interview.", "Q2": "While he ___ (wait) in the lobby, he reviewed his notes.", "Q3": "The interviewer ___ (arrive) ten minutes late.", "Q4": "After the interview, he ___ (feel) tired."}, "activity_id": "fib_1", "instruction": "Fill in the correct past tense form.", "activity_type": "fill_in_the_blanks"}, {"answers": {"Q1": "A", "Q2": "B"}, "questions": {"Q1": {"prompt": "Why did the interviewer apologize?", "options": {"A": "He arrived late.", "B": "He asked a wrong question.", "C": "He forgot Ahmed's name."}}, "Q2": {"prompt": "Which sentence uses past continuous correctly?", "options": {"A": "He was reviewed his notes.", "B": "He was reviewing his notes.", "C": "He were reviewing his notes."}}}, "activity_id": "mcq_1", "instruction": "Choose the best answer based on the passage.", "activity_type": "mcq"}], "instruction": "Read the passage. Then complete both activities below."}	3	2026-04-27 15:26:42.778317+00	2026-04-27 15:26:42.778317+00	active	reading
S14 full-loop test	1	{"activities": [{"answers": {"Q1": "went", "Q2": "has"}, "questions": {"Q1": "Yesterday I ___ (go) to the market.", "Q2": "She ___ (have) breakfast every day."}, "activity_id": "fib_1", "activity_type": "fill_in_the_blanks"}], "instruction": "Fill in the blanks with the correct verb form."}	9	2026-04-30 06:18:06.104087+00	2026-04-30 06:18:06.104087+00	active	writing
S14 full-loop test	1	{"activities": [{"answers": {"Q1": "went", "Q2": "has"}, "questions": {"Q1": "Yesterday I ___ (go) to the market.", "Q2": "She ___ (have) breakfast every day."}, "activity_id": "fib_1", "activity_type": "fill_in_the_blanks"}], "instruction": "Fill in the blanks with the correct verb form."}	10	2026-05-01 09:43:49.399286+00	2026-05-01 09:43:49.399286+00	active	writing
Subject-Verb Agreement Drill	3	{"source": {"text": "Subject-verb agreement is one of the most common grammar issues for English learners. The verb must agree with the subject in number — singular subject takes singular verb, plural subject takes plural verb. Be careful with tricky cases like 'each', 'everyone', 'a group of', and 'neither/nor'.", "type": "passage"}, "activities": [{"answers": {"Q1": "B", "Q2": "B", "Q3": "B", "Q4": "B"}, "questions": {"Q1": {"prompt": "Which is correct?", "options": {"A": "Each of the students have a book.", "B": "Each of the students has a book.", "C": "Each of the students having a book."}}, "Q2": {"prompt": "Which is correct?", "options": {"A": "Neither John nor his friends is coming.", "B": "Neither John nor his friends are coming.", "C": "Neither John nor his friends am coming."}}, "Q3": {"prompt": "Which is correct?", "options": {"A": "The team are winning the match.", "B": "The team is winning the match.", "C": "The team be winning the match."}}, "Q4": {"prompt": "Which is correct?", "options": {"A": "Everyone in the office are happy today.", "B": "Everyone in the office is happy today.", "C": "Everyone in the office be happy today."}}}, "activity_id": "mcq_1", "instruction": "Pick the sentence with correct subject-verb agreement.", "activity_type": "mcq"}], "instruction": "Choose the grammatically correct sentence for each question."}	4	2026-04-27 15:26:42.778317+00	2026-04-27 15:26:42.778317+00	active	reading
S12 test task	1	{"activities": [{"answers": {"Q1": "went", "Q2": "has"}, "questions": {"Q1": "Yesterday I ___ (go) to the market.", "Q2": "She ___ (have) breakfast every day."}, "activity_id": "fib_1", "activity_type": "fill_in_the_blanks"}], "instruction": "Fill in the blanks with the correct verb form."}	12	2026-05-01 14:31:02.613446+00	2026-05-01 14:31:02.613446+00	active	writing
S14 full-loop test	1	{"activities": [{"answers": {"Q1": "went", "Q2": "has"}, "questions": {"Q1": "Yesterday I ___ (go) to the market.", "Q2": "She ___ (have) breakfast every day."}, "activity_id": "fib_1", "activity_type": "fill_in_the_blanks"}], "instruction": "Fill in the blanks with the correct verb form."}	13	2026-05-01 14:37:30.980461+00	2026-05-01 14:37:30.980461+00	active	writing
Project Deadline — Mixed Tenses	4	{"source": {"text": "Priya has been working on the project for three weeks. Last Monday, her manager told her that the deadline had been moved up by five days. Since then, she has skipped lunch twice and stayed late every evening. If she finishes the report by Friday, she will get a small bonus. She hopes she will not have to work over the weekend.", "type": "passage"}, "activities": [{"answers": {"Q1": "has been working", "Q2": "told", "Q3": "finishes", "Q4": "will not have"}, "questions": {"Q1": "Priya ___ (work) on the project for three weeks.", "Q2": "Last Monday, her manager ___ (tell) her about the new deadline.", "Q3": "If she ___ (finish) the report by Friday, she will get a bonus.", "Q4": "She hopes she ___ (not have) to work over the weekend."}, "activity_id": "fib_1", "instruction": "Fill in the correct verb form.", "activity_type": "fill_in_the_blanks"}, {"answers": {"A": "2", "B": "3", "C": "4", "D": "1"}, "section_a": {"A": "Priya has been working", "B": "Her manager told her", "C": "She has skipped lunch", "D": "She will get a bonus"}, "section_b": {"1": "if she finishes by Friday.", "2": "on the project for three weeks.", "3": "that the deadline was moved up.", "4": "twice since Monday."}, "activity_id": "mtf_1", "instruction": "Match each sentence start in Section A with the correct ending in Section B.", "activity_type": "match_the_following"}], "instruction": "Read the passage carefully. Then complete the fill-in-the-blanks and the matching activity."}	5	2026-04-27 15:26:42.778317+00	2026-04-27 15:26:42.778317+00	active	reading
S14 full-loop test	1	{"activities": [{"answers": {"Q1": "went", "Q2": "has"}, "questions": {"Q1": "Yesterday I ___ (go) to the market.", "Q2": "She ___ (have) breakfast every day."}, "activity_id": "fib_1", "activity_type": "fill_in_the_blanks"}], "instruction": "Fill in the blanks with the correct verb form."}	11	2026-05-01 09:45:52.796676+00	2026-05-01 09:45:52.796676+00	active	writing
Workplace Email — Paraphrasing Basics	2	{"source": {"text": "These are common workplace sentences. Practice rewriting them in a different way.", "type": "passage"}, "activities": [{"min_words": 5, "questions": {"Q1": "I am very busy today because I have many meetings.", "Q2": "She arrived late to the office because of heavy traffic.", "Q3": "We need to finish the report before Friday.", "Q4": "The manager was happy with the team's performance."}, "activity_id": "para_1", "instruction": "Rewrite each sentence. Use different words but keep the same meaning. Each answer should be a full sentence.", "activity_type": "paraphrasing", "reference_answers": {"Q1": "Today is very hectic for me as I have several meetings scheduled.", "Q2": "Heavy traffic caused her to be late to the office.", "Q3": "The report must be completed by Friday.", "Q4": "The team's performance pleased the manager."}}], "instruction": "Read each sentence and rewrite it in your own words. Keep the meaning the same, but change the wording."}	14	2026-05-01 15:20:58.869348+00	2026-05-01 15:20:58.869348+00	active	writing
Build the Sentence — Word Order Practice	2	{"source": {"text": "Pay attention to word order, capitalization, and the final punctuation mark.", "type": "passage"}, "activities": [{"answers": {"Q1": "She went to the market yesterday.", "Q2": "My name is Ahmed.", "Q3": "I drink coffee every morning.", "Q4": "They have been friends since childhood."}, "questions": {"Q1": {"words": ["went", "she", "yesterday", "to", "the", "market"]}, "Q2": {"words": ["my", "is", "name", "Ahmed"]}, "Q3": {"words": ["coffee", "every", "I", "morning", "drink"]}, "Q4": {"words": ["been", "have", "they", "friends", "since", "childhood"]}}, "activity_id": "seng_1", "instruction": "Use ALL the given words to form one correct sentence. The final answer should end with a period.", "activity_type": "sentence_engineering"}], "instruction": "Each question gives you a set of words. Tap them in the correct order to form a complete sentence."}	15	2026-05-01 15:20:58.869348+00	2026-05-01 15:20:58.869348+00	active	writing
Present Simple Tense — Basics — Reading	1	{"items": [{"item_id": "1", "distractors": ["go", "goed", "going"], "explanation": "We use 'goes' for he, she, and it in the present simple tense.", "correct_answer": "goes", "sentence_with_blank": "She ___ to the store every Saturday."}, {"item_id": "2", "distractors": ["plays", "played", "playing"], "explanation": "'Play' is the base form used for I, you, we, and they in the present simple tense.", "correct_answer": "play", "sentence_with_blank": "They ___ soccer in the park every weekend."}, {"item_id": "3", "distractors": ["do", "doing", "done"], "explanation": "We use 'does' with he, she, and it in the present simple tense.", "correct_answer": "does", "sentence_with_blank": "He ___ his homework after dinner."}, {"item_id": "4", "distractors": ["brushing", "brushed", "brushes"], "explanation": "'Brush' is used in the present simple tense for I, you, we, and they.", "correct_answer": "brush", "sentence_with_blank": "I ___ my teeth every morning."}], "widget": "fill_in_blanks", "passage": "Every day, I wake up early. I eat breakfast and get ready for school. At school, I learn new things and play with my friends. I enjoy my classes and like to study. After school, I do my homework and help my parents. This is my daily routine.", "activity": "read", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice the Present Simple Tense! Fill in the blanks with the correct form of the verb.", "topic_name": "Present Simple Tense — Basics", "instructions": "Complete the sentences by filling in the blanks with the correct form of the verb.", "estimated_time_minutes": 4, "grammar_rule_explained": "The Present Simple Tense is used to describe habits, routines, and facts. We often add 's' or 'es' to the verb for he, she, and it."}	53	2026-05-09 07:48:20.035536+00	2026-05-09 07:48:20.035536+00	active	curriculum_grammar_fill_blanks
Present Simple Tense — Basics — Writing	1	{"items": [{"prompt": "Write 3 sentences about your daily routine using Present Simple Tense — Basics.", "item_id": "1", "answer_hints": ["Use 'I', 'you', 'he', 'she', 'it', 'we', 'they' as subjects.", "Remember to use the base form of the verb for Present Simple."], "sample_answer": "I wake up at 7 AM. I eat breakfast at 8 AM. I go to work at 9 AM."}, {"prompt": "Describe your favorite hobby using Present Simple Tense — Basics.", "item_id": "2", "answer_hints": ["Think about what you do regularly.", "Use action verbs in their base form."], "sample_answer": "I play soccer on weekends. I enjoy reading books in my free time. I often go hiking with my friends."}, {"prompt": "Write about your family members and what they do using Present Simple Tense — Basics.", "item_id": "3", "answer_hints": ["Use third person singular forms for he/she/it."], "sample_answer": "My brother plays guitar. My sister studies at university. My parents work in a hospital."}, {"prompt": "Explain your job or school life using Present Simple Tense — Basics.", "item_id": "4", "answer_hints": ["Recall the structure of Present Simple for describing jobs."], "sample_answer": "I work as a teacher. I teach English to students. I help them learn grammar and vocabulary."}], "widget": "open_text", "activity": "write", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice the Present Simple Tense! You'll learn how to use it correctly in your sentences.", "topic_name": "Present Simple Tense — Basics", "instructions": "Use the Present Simple Tense to complete the prompts below.", "common_mistakes": ["Using the wrong verb form for third person singular (e.g., 'He go' instead of 'He goes').", "Omitting the 's' or 'es' ending in third person singular.", "Using the present continuous form instead of the simple present for routine actions."], "estimated_time_minutes": 8, "grammar_rule_explained": "The Present Simple Tense is used to describe habits, routines, and general truths. It is formed using the base form of the verb for all subjects except for the third person singular (he, she, it), which adds 's' or 'es' to the verb."}	54	2026-05-09 07:48:20.035536+00	2026-05-09 07:48:20.035536+00	active	curriculum_grammar_open_text
Present Simple Tense — Basics — Speaking	1	{"widget": "speak_and_record", "activity": "speak", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice using the Present Simple tense! Speak your answers to the prompts below.", "topic_name": "Present Simple Tense — Basics", "instructions": "Answer the following prompts using the Present Simple tense.", "sample_responses": ["I wake up at 7 AM every day. After that, I eat breakfast and go to work. I usually finish my work around 5 PM.", "On weekends, I like to go to the park with my friends. We play soccer and sometimes have a picnic. I also enjoy reading books and watching movies.", "My mother is a teacher, and she teaches at a local school. My father works as a doctor. My sister studies at university, and my brother is in high school."], "speaking_prompts": ["Describe your daily routine.", "What do you like to do on weekends?", "Tell me about your family members and what they do."], "estimated_time_minutes": 6, "grammar_rule_to_practice": "present simple tense", "speaking_duration_seconds": 45}	56	2026-05-09 07:48:20.035536+00	2026-05-09 07:48:20.035536+00	active	curriculum_grammar_speak
Present Simple Tense — Basics — Listening	1	{"items": [{"prompt": "What time does the speaker usually wake up?", "item_id": "1", "options": ["At 6 AM", "At 7 AM", "At 8 AM", "At 9 AM"], "explanation": "The speaker mentioned they usually wake up at 7 AM.", "correct_index": 1}, {"prompt": "Which activity does the speaker do after waking up?", "item_id": "2", "options": ["Goes for a walk", "Eats breakfast", "Reads a book", "Goes back to sleep"], "explanation": "The speaker states that after waking up, they eat breakfast.", "correct_index": 1}, {"prompt": "Does the speaker enjoy their mornings?", "item_id": "3", "options": ["Yes, they enjoy them", "No, they do not enjoy them", "They are indifferent", "They hate mornings"], "explanation": "The speaker expresses that they enjoy their mornings because they are quiet.", "correct_index": 0}, {"prompt": "What does the speaker do before starting work?", "item_id": "4", "options": ["Watches TV", "Goes for a walk", "Checks emails", "Meets friends"], "explanation": "The speaker mentions that they often go for a short walk before starting work.", "correct_index": 1}], "widget": "listen_and_respond", "activity": "listen", "topic_id": "1:1", "audio_url": "/audio/77/771c09d07db4ca78.mp3", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice the present simple tense! Listen carefully to the audio and answer the questions that follow.", "topic_name": "Present Simple Tense — Basics", "audio_script": "Hi there! I usually wake up at 7 AM. After that, I eat breakfast and read the news. I enjoy my mornings because they are quiet. I often go for a short walk before I start working. How do you spend your mornings?", "inner_widget": "mcq", "instructions": "Listen to the audio and answer the multiple-choice questions based on what you hear.", "audio_duration_seconds": 12.59, "estimated_time_minutes": 5}	55	2026-05-09 07:48:20.035536+00	2026-05-09 07:48:20.035536+00	active	curriculum_grammar_listen_mcq
Subskill.Vocabulary - Activity.Speak - Uiwidget.Speak And Record	1	{"widget": "speak_and_record", "activity": "speak", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's practice speaking about family and home! Use the target words in your response.", "topic_name": "Everyday Words — Family & Home", "instructions": "Speak for 45 seconds about your family and home using all the target words provided.", "target_words": ["mother", "father", "home", "family", "sibling"], "sample_response": "My mother is a wonderful cook, and my father loves to spend time with us at home. We are a close-knit family, and I really enjoy playing games with my sibling in our cozy living room.", "speaking_prompt": "Talk about your family and home using these words: mother, father, home, family, sibling.", "minimum_words_used": 3, "estimated_time_minutes": 5, "speaking_duration_seconds": 45}	75	2026-05-13 15:16:43.066439+00	2026-05-13 15:16:43.066439+00	active	curriculum_vocab_speak
Present Simple Tense — Basics — Reading	1	{"items": [{"item_id": "1", "explanation": "Use 'go' to indicate a regular action that happens every day.", "correct_answer": "go", "sentence_with_blank": "Sarah ___ (go) to school at 8 AM."}, {"item_id": "2", "explanation": "Use 'studies' for the third-person singular subject in the present simple tense.", "correct_answer": "studies", "sentence_with_blank": "She ___ (study) math and science in her classes."}, {"item_id": "3", "explanation": "Use 'meets' for the third-person singular subject in the present simple tense.", "correct_answer": "meets", "sentence_with_blank": "She usually ___ (meet) her friends at the park."}, {"item_id": "4", "explanation": "Use 'play' for the plural subject in the present simple tense.", "correct_answer": "play", "sentence_with_blank": "They often ___ (play) soccer together."}, {"item_id": "5", "explanation": "Use 'wants' for the third-person singular subject in the present simple tense.", "correct_answer": "wants", "sentence_with_blank": "Sarah ___ (want) to be a doctor one day."}], "widget": "fill_in_blanks", "passage": "Every day, Sarah ___ (go) to school at 8 AM. She ___ (study) math and science in her classes. After school, she usually ___ (meet) her friends at the park. They often ___ (play) soccer together. Sarah ___ (want) to be a doctor one day.", "activity": "read", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice the Present Simple Tense! Fill in the blanks with the correct forms of the verbs.", "topic_name": "Present Simple Tense — Basics", "instructions": "Read the paragraph and type the numbered answers into the blanks.", "estimated_time_minutes": 4, "grammar_rule_explained": "In the present simple tense, we use the base form of the verb for most subjects, but add 's' or 'es' for third-person singular."}	57	2026-05-09 10:51:01.235401+00	2026-05-09 10:51:01.235401+00	active	curriculum_grammar_fill_blanks
Present Simple Tense — Basics — Writing	1	{"items": [{"prompt": "Write 3 sentences about your daily routine using Present Simple Tense — Basics.", "item_id": "item1", "answer_hints": ["Use 'I' or 'he/she/it' for daily routines.", "Remember to use the base form of the verb with 'I', 'you', 'we', 'they'.", "Use 's' or 'es' with 'he', 'she', 'it'."], "sample_answer": "I wake up at 7 AM. I eat breakfast at 8 AM. I go to work at 9 AM."}, {"prompt": "Describe 2 things you do every week using Present Simple Tense — Basics.", "item_id": "item2", "answer_hints": ["Think about your weekly habits.", "Use simple statements with a subject and verb."], "sample_answer": "I play soccer every Saturday. I visit my grandmother every Sunday."}, {"prompt": "Write 4 sentences about what you like to do in your free time using Present Simple Tense — Basics.", "item_id": "item3", "answer_hints": ["Use 'I' for your preferences.", "Make sure each sentence is clear and simple."], "sample_answer": "I read books. I watch movies. I go for walks. I play video games."}, {"prompt": "Write 3 sentences about your family using Present Simple Tense — Basics.", "item_id": "item4", "answer_hints": ["Use present simple to describe routines or facts about your family.", "Include subjects like 'my brother', 'my sister', etc."], "sample_answer": "My brother plays guitar. My sister studies biology. My parents work in an office."}], "widget": "open_text", "activity": "write", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice using the Present Simple Tense! This will help you express facts and habits in English.", "topic_name": "Present Simple Tense — Basics", "instructions": "Read the grammar rule and answer the prompts by writing complete sentences in the Present Simple Tense.", "common_mistakes": ["Forgetting to add 's' or 'es' in the third person singular.", "Using the wrong verb form (e.g., 'I goes' instead of 'I go').", "Omitting the subject of the sentence.", "Confusing present simple with present continuous."], "estimated_time_minutes": 8, "grammar_rule_explained": "The Present Simple Tense is used to describe habits, routines, and general truths. It is formed using the base form of the verb for all subjects except for third-person singular, where you add 's' or 'es' to the verb."}	58	2026-05-09 10:51:01.235401+00	2026-05-09 10:51:01.235401+00	active	curriculum_grammar_open_text
Present Simple Tense — Basics — Speaking	1	{"widget": "speak_and_record", "activity": "speak", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice using the Present Simple Tense! Speak clearly and use complete sentences.", "topic_name": "Present Simple Tense — Basics", "instructions": "Respond to the prompts using the Present Simple Tense.", "sample_responses": ["I wake up every day at 7 AM. After that, I eat breakfast and brush my teeth. Then, I go to school by bus.", "In my free time, I like to read books and play video games. I also enjoy going for walks in the park.", "I usually take the bus to school. It takes about 30 minutes to get there, and I enjoy listening to music during the ride."], "speaking_prompts": ["Describe your daily routine.", "Tell me what you like to do in your free time.", "Explain how you usually get to school or work."], "estimated_time_minutes": 6, "grammar_rule_to_practice": "present simple tense", "speaking_duration_seconds": 45}	60	2026-05-09 14:47:26.845138+00	2026-05-09 14:47:26.845138+00	active	curriculum_grammar_speak
Subskill.Vocabulary - Activity.Listen - Uiwidget.Listen And Respond	1	{"items": [{"prompt": "What word did the speaker use to mean 'place where you live'?", "item_id": "1", "options": ["family", "home", "kitchen", "study"], "explanation": "The speaker used 'home' to refer to the place where they live.", "correct_index": 1}, {"prompt": "Which target word did the speaker NOT use?", "item_id": "2", "options": ["living room", "bathroom", "kitchen", "bedroom"], "explanation": "The speaker did not mention 'bathroom' in the audio.", "correct_index": 1}, {"prompt": "From context, what does the word 'study' mean?", "item_id": "3", "options": ["a room for cooking", "a room for reading", "a room for playing", "a room for sleeping"], "explanation": "In the audio, 'study' refers to a room where the dad enjoys reading.", "correct_index": 1}, {"prompt": "What word did the speaker use to mean 'a space for relaxation and gathering'?", "item_id": "4", "options": ["kitchen", "living room", "bedroom", "study"], "explanation": "The speaker mentioned 'living room' as the space for relaxation and gathering.", "correct_index": 1}], "widget": "listen_and_respond", "activity": "listen", "topic_id": "1:2", "audio_url": "/audio/38/38041ab2f996ab1f.mp3", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's practice everyday words related to family and home! Listen carefully to the audio and answer the questions.", "topic_name": "Everyday Words — Family & Home", "audio_script": "Welcome to my home! This is my family. I live with my parents and my sister. We have a cozy living room where we spend time together. In the kitchen, my mom cooks delicious meals. My dad enjoys reading in the study, and my sister loves playing games in her bedroom.", "inner_widget": "mcq", "instructions": "Listen to the audio and then answer the questions that follow.", "target_words_in_audio": ["home", "family", "kitchen", "living room", "bedroom", "study"], "audio_duration_seconds": 15.57, "estimated_time_minutes": 5}	97	2026-05-15 04:19:50.301517+00	2026-05-15 04:19:50.301517+00	active	curriculum_vocab_listen_mcq
Subskill.Vocabulary - Activity.Speak - Uiwidget.Speak And Record	1	{"widget": "speak_and_record", "activity": "speak", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's practice speaking about your family and home! Use the target words in your description.", "topic_name": "Everyday Words — Family & Home", "instructions": "Talk for 45 seconds about your family using all the target words provided.", "target_words": ["mother", "father", "sister", "brother", "home"], "sample_response": "In my home, I live with my mother and father. I also have a sister and a brother. We all enjoy spending time together in our cozy home, where we share meals and talk about our day.", "speaking_prompt": "Describe your family and home using these words: mother, father, sister, brother, home.", "minimum_words_used": 3, "estimated_time_minutes": 5, "speaking_duration_seconds": 45}	98	2026-05-15 04:19:50.301517+00	2026-05-15 04:19:50.301517+00	active	curriculum_vocab_speak
Present Simple Tense — Basics — Listening	1	{"items": [{"prompt": "What time does the speaker usually wake up?", "item_id": "1", "options": ["6 AM", "7 AM", "8 AM", "9 AM"], "explanation": "The speaker said, 'I usually wake up at 7 AM.'", "correct_index": 1}, {"prompt": "What does the speaker do after work?", "item_id": "2", "options": ["Goes to bed", "Goes to the gym", "Relaxes and reads a book", "Watches TV"], "explanation": "The speaker mentioned, 'After work, I relax and read a book.'", "correct_index": 2}, {"prompt": "How does the speaker feel about their job?", "item_id": "3", "options": ["They dislike it", "They are indifferent", "They like it", "They hate it"], "explanation": "The speaker said, 'I like my job because I help people.'", "correct_index": 2}, {"prompt": "What does the speaker do every Saturday?", "item_id": "4", "options": ["Works", "Visits friends", "Cleans the house", "Studies"], "explanation": "The speaker stated, 'Every Saturday, I visit my friends.'", "correct_index": 1}], "widget": "listen_and_respond", "activity": "listen", "topic_id": "1:1", "audio_url": "/audio/17/176d6535e955a53c.mp3", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Listen carefully to the audio about the Present Simple Tense. Answer the questions based on what you hear!", "topic_name": "Present Simple Tense — Basics", "audio_script": "Hello! I want to tell you about my daily routine. I usually wake up at 7 AM. I eat breakfast and then go to work. I like my job because I help people. After work, I relax and read a book. Every Saturday, I visit my friends. What do you do during the week?", "inner_widget": "mcq", "instructions": "Listen to the audio and answer the following questions about the Present Simple Tense.", "audio_duration_seconds": 14.27, "estimated_time_minutes": 5}	59	2026-05-09 14:47:26.845138+00	2026-05-09 14:47:26.845138+00	active	curriculum_grammar_listen_mcq
Everyday Words — Family & Home — Reading	1	{"items": [{"prompt": "What does 'mother' mean?", "item_id": "1", "options": ["A female parent", "A male parent", "A sibling", "A grandparent"], "explanation": "'Mother' refers to a female parent.", "correct_index": 0}, {"prompt": "What does 'brother' mean?", "item_id": "2", "options": ["A female sibling", "A male sibling", "A cousin", "An aunt"], "explanation": "'Brother' refers to a male sibling.", "correct_index": 1}, {"prompt": "Pick the word that best fits the sentence: 'I live in a nice ___.'", "item_id": "3", "options": ["brother", "home", "sister", "uncle"], "explanation": "'Home' is the correct word that fits the sentence.", "correct_index": 1}, {"prompt": "Pick the word that best fits the sentence: 'My ___ is very kind.'", "item_id": "4", "options": ["mother", "home", "brother", "sister"], "explanation": "'Sister' is the appropriate word to complete the sentence.", "correct_index": 3}], "widget": "mcq", "activity": "read", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's learn some everyday words related to family and home! Choose the correct answers for each question.", "topic_name": "Everyday Words — Family & Home", "instructions": "Select the correct answer for each question about family and home vocabulary.", "target_words": ["mother", "brother", "home", "sister"], "estimated_time_minutes": 4}	61	2026-05-11 07:45:59.397288+00	2026-05-11 07:45:59.397288+00	active	curriculum_vocab_mcq
Everyday Words — Family & Home — Writing	1	{"items": [{"prompt": "Write a short paragraph about your family using the words 'mother' and 'brother'.", "item_id": "1", "answer_hints": ["Think about what your mother likes to do.", "Include a description of your brother's personality."], "sample_answer": "My mother is a wonderful cook, and my brother loves to help her in the kitchen. Together, they make delicious meals for our family."}, {"prompt": "Describe your home using the words 'home' and 'family'.", "item_id": "2", "answer_hints": ["Consider what makes your home special for your family.", "Mention activities you do together at home."], "sample_answer": "My home is a cozy place where my family loves to gather. We spend time together in the living room playing games and laughing."}, {"prompt": "Use the word 'family' in a sentence that describes a family tradition.", "item_id": "3", "answer_hints": ["Think of a special event your family celebrates together.", "What do you usually do on that day?"], "sample_answer": "Every year, my family has a tradition of gathering for a big dinner on Thanksgiving."}, {"prompt": "Write about a favorite memory with your 'mother' and 'brother'.", "item_id": "4", "answer_hints": ["Recall a specific day you spent with them.", "What activities did you do together?"], "sample_answer": "One of my favorite memories is when my mother took my brother and me to the park for a picnic. We had so much fun playing games and eating sandwiches."}], "widget": "open_text", "activity": "write", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's practice using everyday words related to family and home!", "topic_name": "Everyday Words — Family & Home", "instructions": "Use the target words in your answers to complete the prompts below.", "target_words": ["family", "home", "mother", "brother"], "estimated_time_minutes": 7, "minimum_target_words_used": 3}	62	2026-05-11 07:45:59.397288+00	2026-05-11 07:45:59.397288+00	active	curriculum_vocab_open_text
Everyday Words — Family & Home — Speaking	1	{"widget": "speak_and_record", "activity": "speak", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's talk about your family and home! Use the words provided to create a short talk.", "topic_name": "Everyday Words — Family & Home", "instructions": "Speak for 45 seconds about your family and home using all the target words.", "target_words": ["mother", "father", "brother", "sister", "home"], "sample_response": "My mother is a great cook, and my father loves to garden. I have a brother who plays soccer and a sister who enjoys painting. Our home is filled with laughter and love, and we all spend time together in the living room.", "speaking_prompt": "Describe your family and home using these words: mother, father, brother, sister, home.", "minimum_words_used": 3, "estimated_time_minutes": 5, "speaking_duration_seconds": 45}	63	2026-05-11 07:45:59.397288+00	2026-05-11 07:45:59.397288+00	active	curriculum_vocab_speak
Everyday Words — Family & Home — Reading	1	{"items": [{"prompt": "What does 'mother' mean?", "item_id": "1", "options": ["A male parent", "A female parent", "A sibling", "A child"], "explanation": "'Mother' refers to a female parent.", "correct_index": 1}, {"prompt": "What does 'father' mean?", "item_id": "2", "options": ["A male parent", "A female parent", "A sibling", "A child"], "explanation": "'Father' refers to a male parent.", "correct_index": 0}, {"prompt": "Pick the word that best fits the sentence: My ___ is my best friend.", "item_id": "3", "options": ["mother", "brother", "car", "tree"], "explanation": "'Brother' fits the sentence as a family member who can be a best friend.", "correct_index": 1}, {"prompt": "Pick the word that best fits the sentence: My ___ makes dinner every night.", "item_id": "4", "options": ["sister", "dog", "book", "table"], "explanation": "'Sister' is a family member who can prepare dinner.", "correct_index": 0}], "widget": "mcq", "activity": "read", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's learn some everyday words related to family and home! Choose the correct answers so you can improve your vocabulary.", "topic_name": "Everyday Words — Family & Home", "instructions": "For each question, select the correct answer from the options provided.", "target_words": ["mother", "father", "sister", "brother"], "estimated_time_minutes": 4}	64	2026-05-11 07:45:59.397288+00	2026-05-11 07:45:59.397288+00	active	curriculum_vocab_mcq
Everyday Words — Family & Home — Reading	1	{"items": [{"prompt": "What does 'mother' mean?", "item_id": "1", "options": ["A female parent", "A male parent", "A child", "A grandparent"], "explanation": "'Mother' refers to a female parent.", "correct_index": 0}, {"prompt": "What does 'brother' mean?", "item_id": "2", "options": ["A male sibling", "A female sibling", "A cousin", "An aunt"], "explanation": "'Brother' refers to a male sibling.", "correct_index": 0}, {"prompt": "Pick the word that best fits the sentence: My ___ is very kind.", "item_id": "3", "options": ["mother", "teacher", "friend", "car"], "explanation": "The word 'mother' fits the sentence as it refers to a family member.", "correct_index": 0}, {"prompt": "Pick the word that best fits the sentence: I live in a big ___.", "item_id": "4", "options": ["home", "car", "book", "tree"], "explanation": "'Home' fits the sentence as it refers to the place where someone lives.", "correct_index": 0}], "widget": "mcq", "activity": "read", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's explore some everyday words related to family and home! Choose the correct answers to the questions below.", "topic_name": "Everyday Words — Family & Home", "instructions": "Select the correct answer for each question.", "target_words": ["mother", "brother", "home", "sister"], "estimated_time_minutes": 4}	65	2026-05-13 14:32:35.702292+00	2026-05-13 14:32:35.702292+00	active	curriculum_vocab_mcq
Everyday Words — Family & Home — Writing	1	{"items": [{"prompt": "Write a paragraph describing your home using the words 'home' and 'family'.", "item_id": "1", "answer_hints": ["Use descriptive language about your home.", "Include activities that your family does together."], "sample_answer": "My home is a warm place where my family gathers after a long day. We enjoy cooking together and sharing stories in our cozy living room."}, {"prompt": "Describe a special moment you had with your brother using the word 'brother'.", "item_id": "2", "answer_hints": ["Think of an activity you and your brother enjoy.", "What makes your relationship special?"], "sample_answer": "One sunny afternoon, my brother and I built a treehouse in the backyard. It became our secret hideout where we shared countless adventures."}, {"prompt": "Write a short story about a family gathering using the words 'sister' and 'family'.", "item_id": "3", "answer_hints": ["Consider a specific family gathering or holiday.", "Include details about the people and activities."], "sample_answer": "During the holidays, my sister and family come together to celebrate. We play games, eat delicious food, and laugh until our bellies hurt."}, {"prompt": "Create a dialogue between a brother and sister discussing their favorite things about home using the words 'home' and 'sister'.", "item_id": "4", "answer_hints": ["Think about what makes your home special.", "Include both characters' perspectives."], "sample_answer": "Brother: What do you like most about our home?  \\nSister: I love how we can always find each other here. It feels safe and happy!"}], "widget": "open_text", "activity": "write", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's practice using words related to family and home!", "topic_name": "Everyday Words — Family & Home", "instructions": "Use the target words in your responses to complete the prompts below.", "target_words": ["family", "home", "brother", "sister"], "estimated_time_minutes": 7, "minimum_target_words_used": 3}	66	2026-05-13 14:32:35.702292+00	2026-05-13 14:32:35.702292+00	active	curriculum_vocab_open_text
Everyday Words — Family & Home — Speaking	1	{"widget": "speak_and_record", "activity": "speak", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's practice speaking about your family and home! Use the words provided to create a short description.", "topic_name": "Everyday Words — Family & Home", "instructions": "Speak for 45 seconds using all of the target words provided.", "target_words": ["mother", "father", "kitchen", "home", "brother"], "sample_response": "My mother is a great cook and spends a lot of time in the kitchen. My father enjoys helping her with meals. We love spending time at home together, especially on weekends. I have a younger brother who likes to play games with me in the living room.", "speaking_prompt": "Talk about your family and home using these words: mother, father, kitchen, home, brother.", "minimum_words_used": 3, "estimated_time_minutes": 5, "speaking_duration_seconds": 45}	67	2026-05-13 14:32:35.702292+00	2026-05-13 14:32:35.702292+00	active	curriculum_vocab_speak
Everyday Words — Family & Home — Reading	1	{"items": [{"prompt": "What does 'mother' mean?", "item_id": "1", "options": ["A female parent", "A male parent", "A sibling", "A grandparent"], "explanation": "'Mother' refers to a female parent.", "correct_index": 0}, {"prompt": "What does 'brother' mean?", "item_id": "2", "options": ["A female sibling", "A male sibling", "A parent", "A child"], "explanation": "'Brother' means a male sibling.", "correct_index": 1}, {"prompt": "Pick the word that best fits the sentence: 'I live in a ___.'", "item_id": "3", "options": ["home", "brother", "sister", "mother"], "explanation": "'Home' is the correct word that fits the sentence.", "correct_index": 0}, {"prompt": "Pick the word that best fits the sentence: 'My ___ is my best friend.'", "item_id": "4", "options": ["sister", "mother", "home", "brother"], "explanation": "'Sister' is the word that fits best in this context.", "correct_index": 0}], "widget": "mcq", "activity": "read", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's learn some everyday words related to family and home! Choose the correct answers for each question.", "topic_name": "Everyday Words — Family & Home", "instructions": "Select the correct answer for each question about family and home words.", "target_words": ["mother", "brother", "home", "sister"], "estimated_time_minutes": 4}	68	2026-05-13 14:32:35.702292+00	2026-05-13 14:32:35.702292+00	active	curriculum_vocab_mcq
Subskill.Vocabulary - Activity.Read - Uiwidget.Mcq	1	{"items": [{"prompt": "What does 'mother' mean?", "item_id": "1", "options": ["A male parent", "A female parent", "A sibling", "A grandparent"], "explanation": "'Mother' refers to a female parent.", "correct_index": 1}, {"prompt": "What does 'brother' mean?", "item_id": "2", "options": ["A female sibling", "A male sibling", "A parent", "A child"], "explanation": "'Brother' refers to a male sibling.", "correct_index": 1}, {"prompt": "Pick the word that best fits the sentence: My _____ is very kind.", "item_id": "3", "options": ["sister", "tree", "car", "dog"], "explanation": "The correct word is 'sister', as it refers to a female sibling.", "correct_index": 0}, {"prompt": "Pick the word that best fits the sentence: I love my home because it is cozy.", "item_id": "4", "options": ["house", "sister", "brother", "friend"], "explanation": "The word 'home' refers to a place where one lives, which is often cozy.", "correct_index": 0}], "widget": "mcq", "activity": "read", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's learn some everyday words related to family and home! Choose the correct meanings or fit the words into the sentences.", "topic_name": "Everyday Words — Family & Home", "instructions": "Select the correct answer for each question based on the vocabulary about family and home.", "target_words": ["mother", "brother", "home", "sister"], "estimated_time_minutes": 4}	69	2026-05-13 15:15:18.598608+00	2026-05-13 15:15:18.598608+00	active	curriculum_vocab_mcq
Subskill.Vocabulary - Activity.Write - Uiwidget.Open Text	1	{"items": [{"prompt": "Write a short paragraph about your family using the words 'family', 'brother', and 'sister'.", "item_id": "1", "answer_hints": ["Think about your family members and their activities.", "Include how you feel about your family."], "sample_answer": "My family is very important to me. I have a brother who loves to play soccer and a sister who enjoys painting. Together, we have fun at home."}, {"prompt": "Describe what makes a house a home using the words 'home' and 'family'.", "item_id": "2", "answer_hints": ["Consider what activities you do at home with your family.", "What emotions do you associate with your home?"], "sample_answer": "A house becomes a home when it is filled with love and laughter from my family. It is where we share our meals and create memories together."}, {"prompt": "Write about your favorite activity to do with your brother or sister using those words.", "item_id": "3", "answer_hints": ["Think of a specific game or activity.", "How does this activity strengthen your bond?"], "sample_answer": "My favorite activity with my brother is playing video games. We both enjoy competing against each other and laughing at our funny moments."}, {"prompt": "Create a dialogue between a brother and sister discussing their family plans for the weekend using the words 'brother', 'sister', and 'family'.", "item_id": "4", "answer_hints": ["Use conversational language.", "Think about what your family enjoys doing together."], "sample_answer": "Brother: What do you want to do this weekend?  Sister: I think we should plan a family picnic. It would be fun to spend time together!"}], "widget": "open_text", "activity": "write", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's practice using words related to family and home!", "topic_name": "Everyday Words — Family & Home", "instructions": "Use the target words in your responses to the prompts below.", "target_words": ["family", "home", "brother", "sister"], "estimated_time_minutes": 7, "minimum_target_words_used": 3}	70	2026-05-13 15:15:18.598608+00	2026-05-13 15:15:18.598608+00	active	curriculum_vocab_open_text
Subskill.Vocabulary - Activity.Speak - Uiwidget.Speak And Record	1	{"widget": "speak_and_record", "activity": "speak", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's practice speaking about your family and home! Use the target words to describe your life.", "topic_name": "Everyday Words — Family & Home", "instructions": "Talk for 45 seconds about your family using all the target words below.", "target_words": ["mother", "brother", "house", "kitchen", "family"], "sample_response": "In my family, my mother is the one who cooks every day in our kitchen. I have a younger brother who loves to play games at home. We all enjoy spending time together as a family in our house, especially during dinner when we share stories.", "speaking_prompt": "Describe your family and home using these words: mother, brother, house, kitchen, family.", "minimum_words_used": 3, "estimated_time_minutes": 5, "speaking_duration_seconds": 45}	71	2026-05-13 15:15:18.598608+00	2026-05-13 15:15:18.598608+00	active	curriculum_vocab_speak
Subskill.Vocabulary - Activity.Read - Uiwidget.Mcq	1	{"items": [{"prompt": "What does mother mean?", "item_id": "1", "options": ["A female parent", "A male parent", "A sibling", "A grandparent"], "explanation": "'Mother' means a female parent.", "correct_index": 0}, {"prompt": "What does brother mean?", "item_id": "2", "options": ["A female sibling", "A male sibling", "A parent", "A child"], "explanation": "'Brother' refers to a male sibling.", "correct_index": 1}, {"prompt": "Pick the word that best fits the sentence: My ___ is very cozy.", "item_id": "3", "options": ["sister", "home", "uncle", "friend"], "explanation": "'Home' is the word that fits best in the sentence.", "correct_index": 1}, {"prompt": "Pick the word that best fits the sentence: My ___ is always there for me.", "item_id": "4", "options": ["mother", "table", "car", "dog"], "explanation": "'Mother' fits best as someone who is always there for you.", "correct_index": 0}], "widget": "mcq", "activity": "read", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's learn some everyday words related to family and home! Test your knowledge with these questions.", "topic_name": "Everyday Words — Family & Home", "instructions": "Choose the correct answer for each question about family and home vocabulary.", "target_words": ["mother", "brother", "home", "sister"], "estimated_time_minutes": 4}	72	2026-05-13 15:15:18.598608+00	2026-05-13 15:15:18.598608+00	active	curriculum_vocab_mcq
Subskill.Vocabulary - Activity.Read - Uiwidget.Mcq	1	{"items": [{"prompt": "What does 'mother' mean?", "item_id": "1", "options": ["A male parent", "A female parent", "A sibling", "An aunt"], "explanation": "'Mother' refers to a female parent.", "correct_index": 1}, {"prompt": "Pick the word that best fits the sentence: 'My ___ takes care of me every day.'", "item_id": "2", "options": ["father", "friend", "neighbor", "teacher"], "explanation": "In this context, 'father' is the best fit as a family member who takes care of someone.", "correct_index": 0}, {"prompt": "What does 'sister' mean?", "item_id": "3", "options": ["A female sibling", "A male sibling", "A grandparent", "An uncle"], "explanation": "'Sister' refers to a female sibling.", "correct_index": 0}, {"prompt": "Pick the word that best fits the sentence: 'He has one ___ who plays with him.'", "item_id": "4", "options": ["sister", "grandma", "cousin", "neighbor"], "explanation": "In this context, 'sister' is the best fit as a sibling who plays with someone.", "correct_index": 0}], "widget": "mcq", "activity": "read", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's explore some everyday words related to family and home! Test your knowledge with these fun questions.", "topic_name": "Everyday Words — Family & Home", "instructions": "Choose the correct answer for each question based on the words related to family and home.", "target_words": ["mother", "father", "sister", "brother"], "estimated_time_minutes": 4}	73	2026-05-13 15:16:43.066439+00	2026-05-13 15:16:43.066439+00	active	curriculum_vocab_mcq
Subskill.Vocabulary - Activity.Write - Uiwidget.Open Text	1	{"items": [{"prompt": "Write a short paragraph about your family using the words 'family', 'brother', and 'sister'.", "item_id": "1", "answer_hints": ["Make sure to mention your family members.", "Describe a fun activity you do together."], "sample_answer": "In my family, I have a brother and a sister. We all get along very well and enjoy spending time together at home."}, {"prompt": "Describe what home means to you, using 'home' and 'family' in your answer.", "item_id": "2", "answer_hints": ["Think about your feelings when you're at home.", "You can include activities that make home enjoyable."], "sample_answer": "Home is where my family is. It is a place filled with love and support, making it special to me."}, {"prompt": "Write about a memorable event with your brother, using 'brother' and 'home'.", "item_id": "3", "answer_hints": ["Focus on a specific event that was fun.", "Use descriptive language to convey your feelings."], "sample_answer": "One memorable event with my brother was our family game night at home. We laughed and played games all evening."}, {"prompt": "Explain how your sister contributes to the family dynamic, using 'sister' and 'family'.", "item_id": "4", "answer_hints": ["Think about her personality traits.", "Mention specific examples of her contributions."], "sample_answer": "My sister plays an important role in our family by always making us laugh and keeping the atmosphere joyful."}], "widget": "open_text", "activity": "write", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's practice using words related to family and home!", "topic_name": "Everyday Words — Family & Home", "instructions": "Use the target words in your responses to complete each prompt.", "target_words": ["family", "home", "brother", "sister"], "estimated_time_minutes": 7, "minimum_target_words_used": 3}	74	2026-05-13 15:16:43.066439+00	2026-05-13 15:16:43.066439+00	active	curriculum_vocab_open_text
Subskill.Vocabulary - Activity.Read - Uiwidget.Mcq	1	{"items": [{"prompt": "What does mother mean?", "item_id": "1", "options": ["A female parent", "A male parent", "A sibling", "A grandparent"], "explanation": "'Mother' refers to a female parent in a family.", "correct_index": 0}, {"prompt": "What does father mean?", "item_id": "2", "options": ["A male parent", "A female parent", "A sibling", "An aunt"], "explanation": "'Father' refers to a male parent in a family.", "correct_index": 0}, {"prompt": "Pick the word that best fits the sentence: My ___ is my best friend.", "item_id": "3", "options": ["mother", "brother", "sister", "father"], "explanation": "In this context, 'sister' is a common term used to refer to a female sibling.", "correct_index": 2}, {"prompt": "Pick the word that best fits the sentence: My ___ loves to play soccer.", "item_id": "4", "options": ["sister", "mother", "uncle", "aunt"], "explanation": "In this context, 'sister' is a suitable word to describe a sibling who enjoys playing soccer.", "correct_index": 0}], "widget": "mcq", "activity": "read", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's learn some essential family and home words! Choose the correct answers for each question.", "topic_name": "Everyday Words — Family & Home", "instructions": "Select the correct answer for each question based on family and home words.", "target_words": ["mother", "father", "sister", "brother"], "estimated_time_minutes": 4}	76	2026-05-13 15:16:43.066439+00	2026-05-13 15:16:43.066439+00	active	curriculum_vocab_mcq
Subskill.Vocabulary - Activity.Read - Uiwidget.Mcq	1	{"items": [{"prompt": "What does 'mother' mean?", "item_id": "1", "options": ["A male parent", "A female parent", "A child", "A grandparent"], "explanation": "'Mother' refers to a female parent.", "correct_index": 1}, {"prompt": "What does 'father' mean?", "item_id": "2", "options": ["A male parent", "A female parent", "An aunt", "A niece"], "explanation": "'Father' refers to a male parent.", "correct_index": 0}, {"prompt": "Pick the word that best fits the sentence: My ___ is my best friend.", "item_id": "3", "options": ["mother", "teacher", "uncle", "brother"], "explanation": "'Brother' fits best as it refers to a male sibling.", "correct_index": 3}, {"prompt": "Pick the word that best fits the sentence: My ___ helps me with my homework.", "item_id": "4", "options": ["sister", "pet", "neighbor", "friend"], "explanation": "'Sister' fits best as it refers to a female sibling who may help with homework.", "correct_index": 0}], "widget": "mcq", "activity": "read", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's learn some everyday words related to family and home! Choose the correct answers for the questions below.", "topic_name": "Everyday Words — Family & Home", "instructions": "Select the correct answer for each question about family and home words.", "target_words": ["mother", "father", "sister", "brother"], "estimated_time_minutes": 4}	77	2026-05-13 15:43:13.27607+00	2026-05-13 15:43:13.27607+00	active	curriculum_vocab_mcq
Subskill.Vocabulary - Activity.Write - Uiwidget.Open Text	1	{"items": [{"prompt": "Write a sentence about your family that includes the word 'family'.", "item_id": "1", "answer_hints": ["Think about your family members.", "Describe what your family does together."], "sample_answer": "My family is very supportive and always there for me."}, {"prompt": "Describe your home using the word 'home'.", "item_id": "2", "answer_hints": ["Consider what makes your home special.", "Include details about your home environment."], "sample_answer": "My home is a cozy place where I feel safe and happy."}, {"prompt": "Write a short paragraph about your brother, including the word 'brother'.", "item_id": "3", "answer_hints": ["Think about your brother's personality.", "Mention activities you do with him."], "sample_answer": "My brother is my best friend. He always makes me laugh and we play games together."}, {"prompt": "Write a few sentences about your sister using the word 'sister'.", "item_id": "4", "answer_hints": ["Consider your sister's hobbies.", "Include how you feel about your sister."], "sample_answer": "My sister is very talented. She loves to draw and often shares her art with me."}], "widget": "open_text", "activity": "write", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's practice using vocabulary related to family and home!", "topic_name": "Everyday Words — Family & Home", "instructions": "Use the target words in your responses to the prompts below.", "target_words": ["family", "home", "brother", "sister"], "estimated_time_minutes": 7, "minimum_target_words_used": 3}	78	2026-05-13 15:43:13.27607+00	2026-05-13 15:43:13.27607+00	active	curriculum_vocab_open_text
Subskill.Vocabulary - Activity.Listen - Uiwidget.Listen And Respond	1	{"items": [{"prompt": "What word did the speaker use to mean 'a female sibling'?", "item_id": "1", "options": ["brother", "sister", "parent", "child"], "explanation": "The speaker used 'sister' to refer to a female sibling.", "correct_index": 1}, {"prompt": "Which target word did the speaker NOT use?", "item_id": "2", "options": ["kitchen", "home", "garden", "dining table"], "explanation": "The speaker did not mention the word 'garden'.", "correct_index": 2}, {"prompt": "From context, what does the word 'dining table' mean?", "item_id": "3", "options": ["a place to sleep", "a place to eat", "a place to play", "a place to study"], "explanation": "In context, 'dining table' refers to a place where meals are eaten.", "correct_index": 1}, {"prompt": "What word did the speaker use to mean 'a male sibling'?", "item_id": "4", "options": ["sister", "brother", "uncle", "father"], "explanation": "The speaker used 'brother' to refer to a male sibling.", "correct_index": 1}], "widget": "listen_and_respond", "activity": "listen", "topic_id": "1:2", "audio_url": "/audio/0e/0e6ae96807275b29.mp3", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's listen and respond to some words related to family and home!", "topic_name": "Everyday Words — Family & Home", "audio_script": "Today, I want to talk about my family. My sister loves to cook in our kitchen, while my brother enjoys playing games in the living room. We often gather around the dining table for dinner. Our home is filled with laughter and happiness. Family is everything to me!", "inner_widget": "mcq", "instructions": "Listen to the audio and then answer the questions based on what you hear.", "target_words_in_audio": ["sister", "kitchen", "brother", "dining table", "home"], "audio_duration_seconds": 13.82, "estimated_time_minutes": 5}	79	2026-05-13 15:43:13.27607+00	2026-05-13 15:43:13.27607+00	active	curriculum_vocab_listen_mcq
Subskill.Vocabulary - Activity.Speak - Uiwidget.Speak And Record	1	{"widget": "speak_and_record", "activity": "speak", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's practice speaking about your family and home! Use the target words to describe your experience.", "topic_name": "Everyday Words — Family & Home", "instructions": "Talk for 45 seconds about your family and home using all the target words provided.", "target_words": ["mother", "father", "house", "brother", "sister"], "sample_response": "In my house, I live with my mother, father, brother, and sister. My mother is a great cook, and she makes delicious meals for us. My father works hard to provide for the family. I share a room with my brother, and my sister has her own room. We all love spending time together at home.", "speaking_prompt": "Describe your family and home using these words: mother, father, house, brother, sister.", "minimum_words_used": 3, "estimated_time_minutes": 5, "speaking_duration_seconds": 45}	80	2026-05-13 15:43:13.27607+00	2026-05-13 15:43:13.27607+00	active	curriculum_vocab_speak
Subskill.Vocabulary - Activity.Read - Uiwidget.Mcq	1	{"items": [{"prompt": "What does 'mother' mean?", "item_id": "1", "options": ["A female parent", "A male parent", "A child's friend", "A family pet"], "explanation": "'Mother' refers to a female parent.", "correct_index": 0}, {"prompt": "What does 'father' mean?", "item_id": "2", "options": ["A male parent", "A female relative", "A type of food", "A family neighbor"], "explanation": "'Father' refers to a male parent.", "correct_index": 0}, {"prompt": "Pick the word that best fits the sentence: My sister is a great cook, and she makes dinner at ___ every night.", "item_id": "3", "options": ["school", "home", "park", "office"], "explanation": "The best fit is 'home' as it refers to where one lives.", "correct_index": 1}, {"prompt": "Pick the word that best fits the sentence: My ___ is my best friend and we play together every day.", "item_id": "4", "options": ["mother", "sister", "father", "brother"], "explanation": "The best fit is 'sister' as it refers to a female sibling.", "correct_index": 1}], "widget": "mcq", "activity": "read", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's learn some everyday words related to family and home! Choose the correct answers for each question.", "topic_name": "Everyday Words — Family & Home", "instructions": "Read each question carefully and select the best answer from the options provided.", "target_words": ["mother", "father", "home", "sister"], "estimated_time_minutes": 4}	81	2026-05-13 15:49:46.263579+00	2026-05-13 15:49:46.263579+00	active	curriculum_vocab_mcq
Subskill.Vocabulary - Activity.Write - Uiwidget.Open Text	1	{"items": [{"prompt": "Write a short paragraph about your favorite room in your house. Use the word 'kitchen' and describe why you like it.", "item_id": "1", "answer_hints": ["Think about the activities you do in the kitchen.", "Describe what makes the kitchen special for you."], "sample_answer": "My favorite room in my house is the kitchen. I love cooking with my family there. It is always filled with delicious smells and laughter, making it a warm and happy place."}, {"prompt": "Describe your relationship with your brother. Use the word 'brother' at least twice in your description.", "item_id": "2", "answer_hints": ["Mention activities you do with your brother.", "Share a special memory you have with him."], "sample_answer": "My brother is my best friend. We play games together, and he always makes me laugh. I enjoy spending time with my brother because he understands me well."}, {"prompt": "Write about what 'home' means to you. Include the word 'home' in your response.", "item_id": "3", "answer_hints": ["Think about what makes your home special.", "Consider the feelings you associate with home."], "sample_answer": "Home is a place where I feel safe and loved. It is not just a building; it is where my family gathers and shares special moments. Home means comfort and happiness to me."}, {"prompt": "Explain what family means to you using the word 'family' in your answer.", "item_id": "4", "answer_hints": ["Reflect on your family dynamics.", "Include any traditions or activities you enjoy together."], "sample_answer": "Family is the most important part of my life. It includes my parents, my brother, and our pets. We support and care for each other, making our bond strong and special."}], "widget": "open_text", "activity": "write", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's explore some words related to family and home! Use the target words to complete the prompts below.", "topic_name": "Everyday Words — Family & Home", "instructions": "Use the target words in your answers to the prompts.", "target_words": ["kitchen", "brother", "home", "family"], "estimated_time_minutes": 7, "minimum_target_words_used": 3}	82	2026-05-13 15:49:46.263579+00	2026-05-13 15:49:46.263579+00	active	curriculum_vocab_open_text
Subskill.Vocabulary - Activity.Listen - Uiwidget.Listen And Respond	1	{"items": [{"prompt": "What word did the speaker use to mean 'a place where we live'?", "item_id": "1", "options": ["family", "home", "brother", "sister"], "explanation": "The speaker used the word 'home' to refer to a place where they live.", "correct_index": 1}, {"prompt": "Which target word did the speaker NOT use?", "item_id": "2", "options": ["dining table", "living room", "kitchen", "brother"], "explanation": "The speaker did not mention the word 'kitchen' in the audio.", "correct_index": 2}, {"prompt": "From context, what does the word 'dinner' mean?", "item_id": "3", "options": ["a meal at night", "a family gathering", "a type of food", "a time for games"], "explanation": "In context, 'dinner' refers to a meal that is eaten at night.", "correct_index": 0}, {"prompt": "What word did the speaker use to refer to a male sibling?", "item_id": "4", "options": ["sister", "brother", "friend", "cousin"], "explanation": "The word 'brother' was used by the speaker to refer to a male sibling.", "correct_index": 1}], "widget": "listen_and_respond", "activity": "listen", "topic_id": "1:2", "audio_url": "/audio/56/56e3f41df0b33a84.mp3", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Listen carefully to the audio and respond to the questions about family and home words.", "topic_name": "Everyday Words — Family & Home", "audio_script": "In my family home, we have a cozy living room where we gather. My brother loves to play games there, while my sister enjoys reading in her bedroom. We often have dinner together at the dining table, sharing stories and laughter. Family time is important to us, and our home is where we feel safe and happy.", "inner_widget": "mcq", "instructions": "Listen to the audio and then answer the questions based on what you heard.", "target_words_in_audio": ["family", "home", "living room", "dining table", "brother", "sister"], "audio_duration_seconds": 16.19, "estimated_time_minutes": 5}	83	2026-05-13 15:49:46.263579+00	2026-05-13 15:49:46.263579+00	active	curriculum_vocab_listen_mcq
Subskill.Vocabulary - Activity.Speak - Uiwidget.Speak And Record	1	{"widget": "speak_and_record", "activity": "speak", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's practice using words related to family and home! Talk about your family and home life using the words provided.", "topic_name": "Everyday Words — Family & Home", "instructions": "Use all the target words in your response, and try to speak for at least 45 seconds.", "target_words": ["family", "home", "brother", "sister", "mother"], "sample_response": "My family is very important to me. I have a brother and a sister who I love spending time with. Our home is cozy and filled with love. My mother cooks delicious meals for us. We enjoy playing games together in our living room and having fun as a family.", "speaking_prompt": "Talk about your family and what your home is like using these words: family, home, brother, sister, mother.", "minimum_words_used": 3, "estimated_time_minutes": 5, "speaking_duration_seconds": 45}	84	2026-05-13 15:49:46.263579+00	2026-05-13 15:49:46.263579+00	active	curriculum_vocab_speak
Subskill.Grammar - Activity.Read - Uiwidget.Fill In Blanks	1	{"items": [{"item_id": "1", "base_verb": "go", "explanation": "Use 'goes' for he/she/it in the present simple.", "correct_answer": "goes", "sentence_with_blank": "Sarah ___ (1) to school by bus."}, {"item_id": "2", "base_verb": "do", "explanation": "Use 'does' for he/she/it in the present simple.", "correct_answer": "does", "sentence_with_blank": "She ___ (2) her homework during the bus ride."}, {"item_id": "3", "base_verb": "sit", "explanation": "Use 'sits' for he/she/it in the present simple.", "correct_answer": "sits", "sentence_with_blank": "She ___ (3) in her math class and learns many new things."}, {"item_id": "4", "base_verb": "play", "explanation": "Use 'plays' for he/she/it in the present simple.", "correct_answer": "plays", "sentence_with_blank": "After school, she ___ (4) with her friends at the park."}, {"item_id": "5", "base_verb": "play", "explanation": "Use 'play' for I/you/we/they in the present simple.", "correct_answer": "play", "sentence_with_blank": "They often ___ (5) soccer and have fun together."}], "widget": "fill_in_blanks", "passage": "Every day, Sarah ___ (1) to school by bus. She ___ (2) her homework during the bus ride. At school, she ___ (3) in her math class and learns many new things. After school, she ___ (4) with her friends at the park. They often ___ (5) soccer and have fun together.", "activity": "read", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice the present simple tense! Fill in the blanks as you read the passage.", "topic_name": "Present Simple Tense — Basics", "instructions": "Read the paragraph and type the numbered answers into the blanks.", "estimated_time_minutes": 4, "grammar_rule_explained": "In the present simple tense, we use 's' or 'es' with he, she, or it for verbs."}	85	2026-05-14 04:12:44.266442+00	2026-05-14 04:12:44.266442+00	active	curriculum_grammar_fill_blanks
Subskill.Grammar - Activity.Write - Uiwidget.Open Text	1	{"items": [{"prompt": "Write 3 sentences about your daily routine using Present Simple Tense — Basics.", "item_id": "1", "answer_hints": ["Think about what you do every day.", "Use 'I', 'you', 'he', 'she', or 'they' as subjects."], "sample_answer": "I wake up at 7 AM. I eat breakfast at 8 AM. I go to school at 9 AM."}, {"prompt": "Describe your best friend using 5 sentences in Present Simple Tense — Basics.", "item_id": "2", "answer_hints": ["Use characteristics and activities in your sentences.", "Make sure to use the correct form of the verb."], "sample_answer": "My best friend is funny. She loves to play soccer. He studies hard for his exams. She helps me with my homework. We go to the park together."}, {"prompt": "Write 4 sentences about your favorite food using Present Simple Tense — Basics.", "item_id": "3", "answer_hints": ["Think about your preferences.", "Use action verbs to describe what happens."], "sample_answer": "I like pizza. It tastes delicious. My mom makes it every Friday. I eat it with my family."}, {"prompt": "List 5 things you do on weekends using Present Simple Tense — Basics.", "item_id": "4", "answer_hints": ["Consider your typical weekend activities.", "Use present simple verbs like 'do', 'go', 'watch'."], "sample_answer": "I sleep late on weekends. I watch movies with my family. I read books. I go shopping. I relax at home."}], "widget": "open_text", "activity": "write", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice using the Present Simple Tense! You'll explain the rule and create sentences to show your understanding.", "topic_name": "Present Simple Tense — Basics", "instructions": "First, explain the Present Simple Tense rule in your own words. Then, complete the prompts to create sentences using this tense.", "common_mistakes": ["Omitting the 's' in third person singular (e.g., he go instead of he goes).", "Confusing present simple with present continuous (e.g., I am going instead of I go).", "Using the wrong verb form for different subjects (e.g., I goes instead of I go).", "Forgetting to use the base form of the verb after 'do' or 'does' (e.g., I do plays instead of I do play)."], "estimated_time_minutes": 8, "grammar_rule_explained": "The Present Simple Tense is used to describe actions that happen regularly or facts that are always true. For example, we use it to talk about routines, habits, and general truths."}	86	2026-05-14 04:12:44.266442+00	2026-05-14 04:12:44.266442+00	active	curriculum_grammar_open_text
Subskill.Grammar - Activity.Listen - Uiwidget.Listen And Respond	1	{"items": [{"prompt": "What time does the speaker wake up?", "item_id": "1", "options": ["At 6 AM", "At 7 AM", "At 8 AM", "At 9 AM"], "explanation": "The speaker clearly states that they wake up at 7 AM.", "correct_index": 1}, {"prompt": "What does the speaker usually have for breakfast?", "item_id": "2", "options": ["Cereal", "Pancakes", "Eggs and toast", "Fruit"], "explanation": "The audio mentions that the speaker usually has eggs and toast for breakfast.", "correct_index": 2}, {"prompt": "Does the speaker love their job?", "item_id": "3", "options": ["Yes, they love it", "No, they hate it", "They are indifferent", "They are unsure"], "explanation": "The speaker expresses that they love their job.", "correct_index": 0}, {"prompt": "What tense is used to describe the speaker's daily routines?", "item_id": "4", "options": ["Past simple", "Present continuous", "Present simple", "Future simple"], "explanation": "The speaker describes their daily routines using the present simple tense.", "correct_index": 2}], "widget": "listen_and_respond", "activity": "listen", "topic_id": "1:1", "audio_url": "/audio/a6/a6b0e64c05ea0953.mp3", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice the Present Simple Tense! Listen carefully and answer the questions about what you hear.", "topic_name": "Present Simple Tense — Basics", "audio_script": "Hello! I wake up every morning at 7 AM. I brush my teeth and eat breakfast. I usually have eggs and toast. After breakfast, I leave for work. I love my job and I enjoy working with my team. We often have meetings in the afternoon.", "inner_widget": "mcq", "instructions": "Listen to the audio and then answer the questions that follow.", "audio_duration_seconds": 14.36, "estimated_time_minutes": 5}	87	2026-05-14 04:13:54.94539+00	2026-05-14 04:13:54.94539+00	active	curriculum_grammar_listen_mcq
Subskill.Grammar - Activity.Listen - Uiwidget.Listen And Respond	1	{"items": [{"prompt": "What time does the speaker wake up?", "item_id": "1", "options": ["At 6 AM", "At 7 AM", "At 8 AM", "At 9 AM"], "explanation": "The speaker clearly states, 'I wake up every morning at 7 AM.'", "correct_index": 1}, {"prompt": "What does Sarah do?", "item_id": "2", "options": ["She works in an office", "She works at a bakery", "She is a teacher", "She is a doctor"], "explanation": "The speaker mentions that 'My friend Sarah works at a bakery.'", "correct_index": 1}, {"prompt": "How often does the speaker meet Sarah for lunch?", "item_id": "3", "options": ["Sometimes", "Rarely", "Always", "Never"], "explanation": "The speaker says, 'We always meet for lunch at noon.'", "correct_index": 2}, {"prompt": "What tense is used when talking about daily activities?", "item_id": "4", "options": ["Past simple", "Present continuous", "Present simple", "Future simple"], "explanation": "The conversation uses the present simple tense to describe regular actions.", "correct_index": 2}], "widget": "listen_and_respond", "activity": "listen", "topic_id": "1:1", "audio_url": "/audio/ef/ef4e7b7d0b0c2b4e.mp3", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Listen carefully to the conversation about daily activities. Pay attention to how the present simple tense is used!", "topic_name": "Present Simple Tense — Basics", "audio_script": "Hi there! I wake up every morning at 7 AM. I eat breakfast and then I go to work. My friend Sarah works at a bakery. She makes delicious bread every day. We always meet for lunch at noon. It’s a lovely routine!", "inner_widget": "mcq", "instructions": "Listen to the audio and answer the questions based on what you hear about the present simple tense.", "audio_duration_seconds": 12.27, "estimated_time_minutes": 5}	88	2026-05-14 04:13:57.801414+00	2026-05-14 04:13:57.801414+00	active	curriculum_grammar_listen_mcq
Subskill.Grammar - Activity.Speak - Uiwidget.Speak And Record	1	{"widget": "speak_and_record", "activity": "speak", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice using the Present Simple tense! Share your daily routines and habits by speaking.", "topic_name": "Present Simple Tense — Basics", "instructions": "Respond to each prompt using the Present Simple tense. Speak clearly and use full sentences.", "sample_responses": ["On weekends, I usually go to the park and play soccer with my friends. I also like to watch movies and read books. Sometimes, I visit my family and we have dinner together.", "Every day, I wake up at 7 AM. I eat breakfast and then I go to school. After school, I do my homework and play video games.", "My best friend likes to play basketball and listen to music. He often goes to the gym and spends time with his family."], "speaking_prompts": ["What do you usually do on weekends?", "Describe your daily routine.", "What does your best friend like to do in their free time?"], "estimated_time_minutes": 6, "grammar_rule_to_practice": "present simple tense", "speaking_duration_seconds": 45}	89	2026-05-14 04:13:54.94539+00	2026-05-14 04:13:54.94539+00	active	curriculum_grammar_speak
Subskill.Grammar - Activity.Speak - Uiwidget.Speak And Record	1	{"widget": "speak_and_record", "activity": "speak", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice using the Present Simple Tense! Respond to the prompts and focus on your sentence structure.", "topic_name": "Present Simple Tense — Basics", "instructions": "Use the Present Simple Tense to respond to the following prompts. Speak clearly and try to use complete sentences.", "sample_responses": ["In the morning, I usually wake up at 7 AM. I eat breakfast and then I go for a walk. After that, I take a shower and get ready for the day.", "I love painting. I paint every weekend because it relaxes me. My friends often admire my artwork and encourage me to keep going.", "My best friend plays soccer every Saturday. He enjoys it a lot and practices regularly to improve his skills."], "speaking_prompts": ["What do you usually do in the morning?", "How do you feel about your favorite hobby?", "What does your best friend do for fun?"], "estimated_time_minutes": 6, "grammar_rule_to_practice": "present simple tense", "speaking_duration_seconds": 45}	90	2026-05-14 04:13:57.801414+00	2026-05-14 04:13:57.801414+00	active	curriculum_grammar_speak
Subskill.Grammar - Activity.Read - Uiwidget.Fill In Blanks	1	{"items": [{"item_id": "1", "base_verb": "wake", "explanation": "In the present simple tense, we add 's' to the verb for third person singular subjects like Sarah.", "correct_answer": "wakes", "sentence_with_blank": "Sarah ___ (wake) up early."}, {"item_id": "2", "base_verb": "make", "explanation": "For third person singular, the verb 'make' becomes 'makes' in the present simple tense.", "correct_answer": "makes", "sentence_with_blank": "She ___ (make) breakfast for her family."}, {"item_id": "3", "base_verb": "go", "explanation": "The verb 'go' does not change in the present simple tense for plural subjects like children.", "correct_answer": "go", "sentence_with_blank": "Her children ___ (go) to school."}, {"item_id": "4", "base_verb": "take", "explanation": "In the present simple tense, we add 's' to the verb for third person singular subjects like Sarah.", "correct_answer": "takes", "sentence_with_blank": "Sarah ___ (take) a walk in the park."}, {"item_id": "5", "base_verb": "cook", "explanation": "The verb 'cook' changes to 'cooks' when used with third person singular subjects in the present simple tense.", "correct_answer": "cooks", "sentence_with_blank": "She ___ (cook) dinner and they all eat together."}], "widget": "fill_in_blanks", "passage": "Every day, Sarah ___ (wake) up early. She ___ (make) breakfast for her family. After breakfast, her children ___ (go) to school. Sarah ___ (take) a walk in the park. In the evening, she ___ (cook) dinner and they all eat together.", "activity": "read", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice the Present Simple Tense! Fill in the blanks as you read the passage.", "topic_name": "Present Simple Tense — Basics", "instructions": "Read the paragraph and type the numbered answers into the blanks.", "estimated_time_minutes": 4, "grammar_rule_explained": "In the present simple tense, use the base form of the verb for plural subjects, and add 's' for third person singular subjects."}	91	2026-05-14 15:19:21.116302+00	2026-05-14 15:19:21.116302+00	active	curriculum_grammar_fill_blanks
Subskill.Grammar - Activity.Write - Uiwidget.Open Text	1	{"items": [{"prompt": "Write 3 sentences about your daily routine using Present Simple Tense — Basics.", "item_id": "1", "answer_hints": ["Use the structure: Subject + base verb + object", "Think about your typical day", "Remember to use 's' for third person singular when needed"], "sample_answer": "I wake up at 7 AM. I eat breakfast at 8 AM. I go to work at 9 AM."}, {"prompt": "Describe your best friend using 5 sentences with Present Simple Tense — Basics.", "item_id": "2", "answer_hints": ["Use 'lives', 'plays', 'loves', 'helps', and 'watches'", "Make sure to use correct verb forms for he/she/it"], "sample_answer": "My best friend lives in the same neighborhood. He plays soccer every weekend. He loves to read books. He helps me with my homework. We watch movies together."}, {"prompt": "Write 4 sentences about your favorite hobbies using Present Simple Tense — Basics.", "item_id": "3", "answer_hints": ["Use 'like', 'play', 'enjoy', and 'visit' in the present simple form", "Think about what you do regularly"], "sample_answer": "I like painting and drawing. I play guitar in my free time. I enjoy cooking new recipes. I visit the museum every month."}, {"prompt": "Make 3 sentences about what you do every weekend using Present Simple Tense — Basics.", "item_id": "4", "answer_hints": ["Use 'go', 'clean', and 'meet' in your sentences", "Focus on activities that are part of your routine"], "sample_answer": "I go hiking every Saturday. I clean my house on Sundays. I meet my friends for lunch."}], "widget": "open_text", "activity": "write", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice the Present Simple Tense! You'll learn how to express routine actions and habits.", "topic_name": "Present Simple Tense — Basics", "instructions": "Use the Present Simple Tense to complete the following prompts.", "common_mistakes": ["Forgetting to add 's' for third person singular (he, she, it)", "Using the past tense form instead of the present", "Omitting the subject in sentences", "Confusing the present simple with the present continuous (e.g., 'I am going' instead of 'I go')"], "estimated_time_minutes": 8, "grammar_rule_explained": "The Present Simple Tense is used to describe habits, routines, and general truths. It is formed by using the base form of the verb for most subjects, and adding 's' or 'es' for the third person singular (he, she, it)."}	92	2026-05-14 15:19:21.116302+00	2026-05-14 15:19:21.116302+00	active	curriculum_grammar_open_text
Subskill.Grammar - Activity.Listen - Uiwidget.Listen And Respond	1	{"items": [{"prompt": "What does the speaker do every morning?", "item_id": "1", "options": ["He wakes up late.", "He goes to bed early.", "He wakes up early and eats breakfast.", "He skips breakfast."], "explanation": "The speaker clearly states that he wakes up early and eats breakfast.", "correct_index": 2}, {"prompt": "Which drink does the speaker mention in his routine?", "item_id": "2", "options": ["Tea", "Juice", "Coffee", "Milk"], "explanation": "The speaker specifically mentions drinking coffee in the morning.", "correct_index": 2}, {"prompt": "What action does the speaker take after breakfast?", "item_id": "3", "options": ["He goes to work.", "He goes for a walk.", "He reads a book.", "He visits friends."], "explanation": "The speaker says that he goes to work after having breakfast.", "correct_index": 0}, {"prompt": "How does the speaker feel about his job?", "item_id": "4", "options": ["He dislikes it.", "He is indifferent.", "He loves it.", "He wants to change it."], "explanation": "The speaker expresses that he loves his job because he helps people every day.", "correct_index": 2}], "widget": "listen_and_respond", "activity": "listen", "topic_id": "1:1", "audio_url": "/audio/e8/e84ad7fbfa924380.mp3", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Listen carefully to the audio and then answer the questions based on what you heard!", "topic_name": "Present Simple Tense — Basics", "audio_script": "Hi there! I want to tell you about my daily routine. Every morning, I wake up early and eat breakfast. I usually drink coffee and read the news. After that, I go to work. I love my job because I help people every day. What do you do in the mornings?", "inner_widget": "mcq", "instructions": "Listen to the audio and answer the multiple-choice questions based on the content.", "audio_duration_seconds": 14.68, "estimated_time_minutes": 5}	93	2026-05-14 15:23:47.642198+00	2026-05-14 15:23:47.642198+00	active	curriculum_grammar_listen_mcq
Subskill.Grammar - Activity.Speak - Uiwidget.Speak And Record	1	{"widget": "speak_and_record", "activity": "speak", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice using the Present Simple Tense! Speak about your daily activities and routines.", "topic_name": "Present Simple Tense — Basics", "instructions": "Use the prompts below to practice speaking in the present simple tense. Record your answers and make sure to use correct sentence structure.", "sample_responses": ["Every day, I wake up at 7 AM. I eat breakfast and then I go to work. After work, I exercise and have dinner with my family.", "I have several hobbies. I play soccer every weekend and I read books in the evenings. I also enjoy painting when I have free time.", "My father is a teacher. He teaches math at a high school. My mother is a nurse, and she works at the local hospital."], "speaking_prompts": ["Describe your daily routine. What do you do every day?", "What hobbies do you have? How often do you practice them?", "Tell me about your family. What do they do for a living?"], "estimated_time_minutes": 6, "grammar_rule_to_practice": "present simple tense", "speaking_duration_seconds": 45}	94	2026-05-14 15:23:47.642198+00	2026-05-14 15:23:47.642198+00	active	curriculum_grammar_speak
Subskill.Vocabulary - Activity.Read - Uiwidget.Mcq	1	{"items": [{"prompt": "What does 'mother' mean?", "item_id": "1", "options": ["A male parent", "A female parent", "A sibling", "A grandparent"], "explanation": "'Mother' refers to a female parent.", "correct_index": 1}, {"prompt": "What does 'brother' mean?", "item_id": "2", "options": ["A male sibling", "A female sibling", "A parent", "A child"], "explanation": "'Brother' refers to a male sibling.", "correct_index": 0}, {"prompt": "Pick the word that best fits the sentence: My ___ is very kind to me. ___ can refer to a sibling or a female relative.", "item_id": "3", "options": ["sister", "father", "mother", "friend"], "explanation": "'Sister' is a female sibling.", "correct_index": 0}, {"prompt": "Pick the word that best fits the sentence: I love my home because it is cozy and warm. ___ is where one lives.", "item_id": "4", "options": ["House", "Car", "School", "Park"], "explanation": "'Home' refers to the place where one lives.", "correct_index": 0}], "widget": "mcq", "activity": "read", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's learn some important words related to family and home! Choose the correct answers for each question.", "topic_name": "Everyday Words — Family & Home", "instructions": "Read each question carefully and select the correct answer from the options provided.", "target_words": ["mother", "brother", "home", "sister"], "estimated_time_minutes": 4}	95	2026-05-15 04:19:50.301517+00	2026-05-15 04:19:50.301517+00	active	curriculum_vocab_mcq
Subskill.Vocabulary - Activity.Write - Uiwidget.Open Text	1	{"items": [{"prompt": "Write a sentence about your family using the words 'brother' and 'sister'.", "item_id": "1", "answer_hints": ["Think about your siblings.", "Include details about what they help you with."], "sample_answer": "My brother and sister always help me with my homework at home."}, {"prompt": "Describe what makes your home special using the word 'home'.", "item_id": "2", "answer_hints": ["Consider what makes a place feel like home.", "Mention specific feelings or activities."], "sample_answer": "My home is special because it is filled with love and laughter."}, {"prompt": "Write a short paragraph about a family gathering that includes the word 'family'.", "item_id": "3", "answer_hints": ["Think about your favorite family traditions.", "Include details about the gathering."], "sample_answer": "Every Sunday, my family gathers for dinner, and we share stories and laughter around the table."}, {"prompt": "Create a sentence that describes your relationship with your brother using the word 'brother'.", "item_id": "4", "answer_hints": ["Think about how you interact with your brother.", "Include feelings or experiences."], "sample_answer": "My brother is not only my sibling but also my best friend who I can talk to about anything."}], "widget": "open_text", "activity": "write", "topic_id": "1:2", "sub_level": 1, "sub_skill": "vocabulary", "task_intro": "Let's practice using words related to family and home!", "topic_name": "Everyday Words — Family & Home", "instructions": "Use the target words in your responses to the prompts below.", "target_words": ["family", "home", "brother", "sister"], "estimated_time_minutes": 7, "minimum_target_words_used": 3}	96	2026-05-15 04:19:50.301517+00	2026-05-15 04:19:50.301517+00	active	curriculum_vocab_open_text
Subskill.Grammar - Activity.Read - Uiwidget.Fill In Blanks	1	{"items": [{"item_id": "1", "base_verb": "be", "explanation": "The correct form of 'to be' for 'I' is 'am.'", "correct_answer": "am", "sentence_with_blank": "I ___ a student at the local university."}, {"item_id": "2", "base_verb": "be", "explanation": "The correct form of 'to be' for 'I' is 'am.'", "correct_answer": "am", "sentence_with_blank": "I ___ from Canada, and I ___ 20 years old."}, {"item_id": "3", "base_verb": "be", "explanation": "The correct form of 'to be' for 'they' is 'are.'", "correct_answer": "are", "sentence_with_blank": "My friends ___ very important to me."}, {"item_id": "4", "base_verb": "like", "explanation": "The verb 'like' stays the same for 'we.'", "correct_answer": "like", "sentence_with_blank": "We ___ like to hang out at the park on weekends."}, {"item_id": "5", "base_verb": "be", "explanation": "The correct form of 'to be' for 'I' is 'am.'", "correct_answer": "am", "sentence_with_blank": "I ___ a student at the local university."}], "widget": "fill_in_blanks", "passage": "Hello! My name is John. I ___ a student at the local university. I ___ from Canada, and I ___ 20 years old. My friends ___ very important to me. We ___ like to hang out at the park on weekends.", "activity": "read", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice introducing ourselves! Fill in the blanks as you read the passage.", "topic_name": "introduce yourself in everyday situations — present simple — affirmative (I/you/we/they + base verb)", "instructions": "Read the paragraph and type the numbered answers into the blanks.", "estimated_time_minutes": 4, "grammar_rule_explained": "Use the present simple tense to talk about habits, facts, or things that are always true."}	99	2026-05-15 06:23:06.553828+00	2026-05-15 06:23:06.553828+00	active	curriculum_grammar_fill_blanks
Subskill.Grammar - Activity.Write - Uiwidget.Open Text	1	{"items": [{"prompt": "Write 3 sentences about yourself using the present simple affirmative form (I/you/we/they + base verb).", "item_id": "1", "answer_hints": ["Use 'I' to talk about yourself.", "Remember to use the base form of the verb.", "Think about what you do regularly."], "sample_answer": "I am a student. I like to read books. I live in New York."}, {"prompt": "Write sentences to introduce your friends using the present simple affirmative form (I/you/we/they + base verb).", "item_id": "2", "answer_hints": ["Use 'they' to talk about your friends.", "Think about their hobbies or what they do."], "sample_answer": "They are my friends. They play soccer every weekend. They enjoy movies."}, {"prompt": "Introduce your family members using the present simple affirmative form (I/you/we/they + base verb).", "item_id": "3", "answer_hints": ["Use 'we' to talk about your family.", "Think about what your family enjoys doing together."], "sample_answer": "We are a family of four. We love to travel. We often cook together."}, {"prompt": "Write a few sentences about your daily routine using the present simple affirmative form (I/you/we/they + base verb).", "item_id": "4", "answer_hints": ["Use 'I' to describe your daily actions.", "Think about what you do every day."], "sample_answer": "I wake up at 7 AM. I go to school. I do my homework in the evening."}], "widget": "open_text", "activity": "write", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice introducing ourselves using the present simple tense!", "topic_name": "introduce yourself in everyday situations — present simple — affirmative (I/you/we/they + base verb)", "instructions": "Use the present simple tense to introduce yourself and others in everyday situations.", "common_mistakes": ["Incorrect verb forms (e.g., using 'plays' with 'I')", "Omitting the subject (e.g., just writing 'like to read')", "Using the wrong tense (e.g., writing in past or future instead of present)", "Not using the base form of the verb correctly."], "estimated_time_minutes": 8, "grammar_rule_explained": "In the present simple tense, we use the base form of the verb for all subjects except for 'he', 'she', and 'it', where we add 's' or 'es'. For example: 'I play', 'You play', 'He plays'."}	100	2026-05-15 06:23:06.553828+00	2026-05-15 06:23:06.553828+00	active	curriculum_grammar_open_text
Subskill.Grammar - Activity.Read - Uiwidget.Fill In Blanks	1	{"items": [{"item_id": "1", "base_verb": "be", "explanation": "This sentence uses 'I' with the verb 'to be' in the present simple form.", "correct_answer": "am", "sentence_with_blank": "I ___ a student at the local school."}, {"item_id": "2", "base_verb": "come", "explanation": "Here, 'John' is a singular subject, so we add 's' to the base verb 'come'.", "correct_answer": "comes", "sentence_with_blank": "My friend, John, ___ from Canada."}, {"item_id": "3", "base_verb": "be", "explanation": "In this sentence, 'we' requires the verb 'to be' in its plural form.", "correct_answer": "are", "sentence_with_blank": "We ___ in the same class."}, {"item_id": "4", "base_verb": "be", "explanation": "The subject 'you' takes the verb 'to be' in its present simple form.", "correct_answer": "are", "sentence_with_blank": "You ___ very friendly, and we often study together."}, {"item_id": "5", "base_verb": "be", "explanation": "In this sentence, 'they' requires the verb 'to be' in its plural form.", "correct_answer": "are", "sentence_with_blank": "They ___ great at helping others, too!"}], "widget": "fill_in_blanks", "passage": "Hello! My name is Sarah. I ___ a student at the local school. My friend, John, ___ from Canada. We ___ in the same class. You ___ very friendly, and we often study together. They ___ great at helping others, too!", "activity": "read", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice introducing ourselves using the present simple tense! Fill in the blanks with the correct form of the verb.", "topic_name": "introduce yourself using I/you/we/they — present simple — statements (I, you, we, they + base verb)", "instructions": "Read the paragraph and type the numbered answers into the blanks.", "estimated_time_minutes": 4, "grammar_rule_explained": "Use 'I', 'you', 'we', and 'they' with the present simple form of verbs to make statements about who we are and what we do."}	101	2026-05-18 12:37:28.229289+00	2026-05-18 12:37:28.229289+00	active	curriculum_grammar_fill_blanks
Subskill.Grammar - Activity.Write - Uiwidget.Open Text	1	{"items": [{"prompt": "Write 3 sentences introducing yourself using 'I' and the present simple tense.", "item_id": "1", "answer_hints": ["Use 'I' followed by a base verb.", "Think about your hobbies or interests."], "sample_answer": "I am a student. I like to read books. I enjoy playing soccer."}, {"prompt": "Write 2 sentences about your friend using 'he' or 'she' in the present simple tense.", "item_id": "2", "answer_hints": ["Use 'he' or 'she' followed by a base verb.", "Consider what your friend does or likes."], "sample_answer": "He is a teacher. She loves to cook."}, {"prompt": "Write 2 sentences about your family using 'we' in the present simple tense.", "item_id": "3", "answer_hints": ["Use 'we' followed by a base verb.", "Think about activities you do together as a family."], "sample_answer": "We enjoy going to the park. We are a happy family."}, {"prompt": "Write 3 sentences about your new classmates using 'they' in the present simple tense.", "item_id": "4", "answer_hints": ["Use 'they' followed by a base verb.", "Think about what your classmates do or how they are."], "sample_answer": "They are friendly. They play basketball after school. They like to study together."}], "widget": "open_text", "activity": "write", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice introducing ourselves using the present simple tense!", "topic_name": "introduce yourself using I/you/we/they — present simple — statements (I, you, we, they + base verb)", "instructions": "Use the prompts below to write sentences introducing yourself and others using the present simple tense. Make sure to use the correct subject pronouns and base verbs.", "common_mistakes": ["Using the wrong subject pronoun (e.g., using 'he' when referring to 'I').", "Not using the base form of the verb (e.g., saying 'I am going to school' instead of 'I go to school').", "Forgetting to use the correct verb forms for he/she/it (e.g., saying 'He like soccer' instead of 'He likes soccer').", "Using present continuous instead of present simple when not needed (e.g., saying 'I am a student' instead of 'I am a student')."], "estimated_time_minutes": 8, "grammar_rule_explained": "In English, we use the present simple tense to talk about things that are true now or things we do regularly. When introducing yourself or others, we start with a subject pronoun like 'I', 'you', 'we', or 'they', followed by the base form of the verb."}	102	2026-05-18 12:37:28.229289+00	2026-05-18 12:37:28.229289+00	active	curriculum_grammar_open_text
Subskill.Grammar - Activity.Read - Uiwidget.Fill In Blanks	1	{"items": [{"item_id": "1", "base_verb": "be", "explanation": "The correct form of 'to be' for 'I' is 'am'.", "correct_answer": "am", "sentence_with_blank": "My name is John, and I ___ (1) a teacher."}, {"item_id": "2", "base_verb": "live", "explanation": "The base verb 'live' is used here in the present simple.", "correct_answer": "live", "sentence_with_blank": "I ___ (2) in a small town."}, {"item_id": "3", "base_verb": "be", "explanation": "The correct form of 'to be' for 'they' is 'are'.", "correct_answer": "are", "sentence_with_blank": "My friends ___ (3) nice and supportive."}, {"item_id": "4", "base_verb": "do", "explanation": "The verb 'do' is used in the present simple for 'we'.", "correct_answer": "do", "sentence_with_blank": "We ___ (4) many activities together."}, {"item_id": "5", "base_verb": "be", "explanation": "The correct form of 'to be' for 'I' is 'am.'", "correct_answer": "am", "sentence_with_blank": "I ___ (5) happy to meet new people."}], "widget": "fill_in_blanks", "passage": "Hello! My name is John, and I ___ (1) a teacher. I ___ (2) in a small town. My friends ___ (3) nice and supportive. We ___ (4) many activities together. I ___ (5) happy to meet new people.", "activity": "read", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice introducing ourselves in simple sentences! Fill in the blanks with the correct form of the verb.", "topic_name": "introduce yourself in everyday situations — present simple — affirmative (I/you/we/they + base verb)", "instructions": "Read the paragraph and type the numbered answers into the blanks.", "estimated_time_minutes": 4, "grammar_rule_explained": "In the present simple tense, we use 'am' for 'I', 'are' for 'you/we/they', and 'is' for 'he/she/it'."}	103	2026-05-18 16:29:40.53823+00	2026-05-18 16:29:40.53823+00	active	curriculum_grammar_fill_blanks
Subskill.Grammar - Activity.Write - Uiwidget.Open Text	1	{"items": [{"prompt": "Write 3 sentences about yourself using the present simple tense. For example, 'I work at a school.'", "item_id": "1", "answer_hints": ["Use 'I' + base verb format.", "Include your daily activities."], "sample_answer": "I am a student. I live in New York. I enjoy reading books."}, {"prompt": "Describe your family using the present simple tense. For example, 'They like to travel.'", "item_id": "2", "answer_hints": ["Use 'they' + base verb.", "Mention different family members."], "sample_answer": "They are my parents. They work in a hospital. They love to cook."}, {"prompt": "Write 3 sentences about your friends using the present simple tense. For example, 'We play soccer on weekends.'", "item_id": "3", "answer_hints": ["Use 'we' + base verb.", "Talk about activities you do together."], "sample_answer": "We study together. We go to the park. We enjoy watching movies."}, {"prompt": "Introduce your favorite hobby using the present simple tense. For example, 'I play the guitar.'", "item_id": "4", "answer_hints": ["Use 'I' + base verb.", "Describe what you like to do in your free time."], "sample_answer": "I like painting. I play basketball. I enjoy cooking."}], "widget": "open_text", "activity": "write", "topic_id": "1:1", "sub_level": 1, "sub_skill": "grammar", "task_intro": "Let's practice introducing yourself using the present simple tense! This will help you communicate more effectively in everyday situations.", "topic_name": "introduce yourself in everyday situations — present simple — affirmative (I/you/we/they + base verb)", "instructions": "Use the present simple tense to introduce yourself and provide information about your daily life.", "common_mistakes": ["Using the wrong verb form (e.g., 'I eats').", "Omitting the subject (e.g., 'Like to swim').", "Using present continuous instead of present simple (e.g., 'I am playing football').", "Incorrect subject-verb agreement (e.g., 'He go to school')."], "estimated_time_minutes": 8, "grammar_rule_explained": "The present simple tense is used to describe habits, routines, and facts. In affirmative sentences, it follows the structure: subject + base verb. For example, 'I eat', 'You play', 'They work.'"}	104	2026-05-18 16:29:40.53823+00	2026-05-18 16:29:40.53823+00	active	curriculum_grammar_open_text
\.


--
-- Data for Name: user_course_preferences; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.user_course_preferences (id, user_id, course_length, tasks_per_day, allow_read, allow_write, allow_listen, allow_speak, current_week, current_day_in_week, current_day_started_at, last_completed_on, created_at, updated_at) FROM stdin;
1	29	24w	4	t	t	t	t	1	2	2026-05-15 04:19:50.21028+00	2026-05-15	2026-05-19 09:24:10.258829+00	2026-05-19 09:24:10.258829+00
2	37	48w	2	t	t	t	t	1	1	2026-05-18 12:37:26.617282+00	\N	2026-05-19 09:24:10.258829+00	2026-05-19 09:24:10.258829+00
3	38	24w	2	t	t	t	t	1	1	2026-05-18 16:29:39.779723+00	\N	2026-05-19 09:24:10.258829+00	2026-05-19 09:24:10.258829+00
\.


--
-- Data for Name: user_enrollments; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.user_enrollments (user_id, course_id, current_week, current_day_in_week, started_at, id, created_at, updated_at, tasks_per_day, status, allow_reading, allow_writing, allow_listening, allow_speaking, current_day_started_at, last_completed_on) FROM stdin;
29	1	1	2	2026-05-04 05:14:56.341678+00	9	2026-05-04 05:14:56.323333+00	2026-05-15 04:19:50.172169+00	4	active	t	t	t	t	2026-05-15 04:19:50.21028+00	2026-05-15
37	2	1	1	2026-05-18 12:37:26.617282+00	18	2026-05-18 12:37:26.574745+00	2026-05-18 12:37:26.574745+00	2	active	t	t	t	t	2026-05-18 12:37:26.617282+00	\N
38	1	1	1	2026-05-18 16:29:39.779723+00	19	2026-05-18 16:29:39.730771+00	2026-05-19 11:22:15.585709+00	4	active	t	t	t	t	2026-05-18 16:29:39.779723+00	\N
\.


--
-- Data for Name: user_profiles; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.user_profiles (user_id, self_assessed_level, daily_time_minutes, content_exposure, goal, interests, id, created_at, updated_at, diagnosis_completed, phone_number, country, native_language, primary_goals, personalisation_context, display_name, daily_practice_reminder, streak_reminder, weekly_progress_email, feature_announcements, structured_personalisation, structured_personalisation_updated_at, timezone, current_streak, longest_streak, last_activity_date, streak_freezes, last_seen_streak_animation_date, last_animation_type) FROM stdin;
29	BEGINNER	15	LOW	PROFESSIONAL	movies,sports,travel	26	2026-05-04 04:15:43.420175+00	2026-05-15 05:03:47.895369+00	t	\N	\N	\N		I am aspiring Machine laenaing engineering who is planning to get into tech industry. preparing for interviews now.	\N	t	t	t	t	\N	\N	Asia/Kolkata	0	0	\N	0	\N	\N
37	BEGINNER	15	LOW	PROFESSIONAL	movies,sports,travel	33	2026-05-18 12:37:11.265937+00	2026-05-18 13:02:13.088684+00	t	\N	\N	\N			\N	t	t	f	f	{"domain": "general", "pain_points": [], "extracted_at": "2026-05-18T13:02:15.128905+00:00", "priority_skills": [], "tone_preference": "neutral", "extraction_source": "llm", "communication_contexts": []}	2026-05-18 13:02:15.154919+00	Asia/Kolkata	0	0	\N	0	\N	\N
38	BEGINNER	15	LOW	PROFESSIONAL	sports,travel,movies	34	2026-05-18 16:28:01.893366+00	2026-05-18 16:29:04.503287+00	t	\N	\N	\N			\N	t	t	f	f	{"domain": "general", "pain_points": [], "extracted_at": "2026-05-18T16:29:07.262778+00:00", "priority_skills": [], "tone_preference": "neutral", "extraction_source": "llm", "communication_contexts": []}	2026-05-18 16:29:07.281414+00	Asia/Kolkata	0	0	\N	0	\N	\N
\.


--
-- Data for Name: user_responses; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.user_responses (user_task_id, content, raw_text, id, created_at, embedding_status, pinecone_vector_id) FROM stdin;
30	{"Q1": "is", "Q2": "wakes", "Q3": "likes", "Q4": "smiles"}	\N	22	2026-05-05 04:54:01.927017+00	skipped	\N
29	{"Q1": "is", "Q2": "wakes", "Q3": "likes", "Q4": "smile"}	\N	23	2026-05-05 06:03:45.035949+00	skipped	\N
122	{"1": "wakes", "2": "makes", "3": "goes", "4": "takes", "5": "cooks", "time_spent_seconds": 83}	\N	47	2026-05-15 03:31:46.214411+00	pending	\N
123	{"1": "I wake up at 7:00 AM every morning. I drink a glass of water before I start my work. I study new programming concepts for two hours every day.", "2": "My best friend is a very kind and helpful person. He lives in the same city as I do. We talk about technology and life almost every evening. He works as a software engineer at a local firm. He always encourages me to work hard on my projects.", "3": "I write clean code for open-source projects in my free time. I listen to music while I design new application interfaces. I read technical blogs to stay updated with the latest AI trends. I also enjoy building physical landscape models as a creative outlet.", "4": "I visit my local library to find books on computer science. I spend time with my family and help around the house. I plan my schedule for the upcoming week every Sunday evening.", "time_spent_seconds": 78}	\N	48	2026-05-15 03:33:31.199461+00	pending	\N
124	{"inner_response": {"widget": "mcq", "answers": [{"item_id": "1", "selected_index": 2}, {"item_id": "2", "selected_index": 2}, {"item_id": "3", "selected_index": 0}, {"item_id": "4", "selected_index": 2}]}, "listen_analytics": {"play_count": 1, "transcript_revealed": false, "total_listen_seconds": 17}, "time_spent_seconds": 57}	\N	49	2026-05-15 03:35:05.546395+00	pending	\N
125	{"recordings": [{"item_id": "prompt_1", "transcript": "Hi, my daily routine includes, I wake up early in the morning, then I eat my breakfast at 7.30, then I go to work and work until afternoon, I will come back at 6 and I take a shower, then I will prepare a meal for dinner and eat it at 7.30.", "attempt_number": 1, "audio_blob_url": "/audio/user-recordings/1a1cc332fc7f2697.webm", "duration_seconds": 45}, {"item_id": "prompt_2", "transcript": "I read books every night before going to bed. This is a habit that I built to calm down my stress before sleeping.", "attempt_number": 2, "audio_blob_url": "/audio/user-recordings/df04f65d69ee2bde.webm", "duration_seconds": 45}, {"item_id": "prompt_3", "transcript": "My father farms rubber and other crops, my mother is a housekeeper and my brother studies in a university and my grandfather sits simply at home without doing nothing.", "attempt_number": 1, "audio_blob_url": "/audio/user-recordings/cf9c30b20adcdbe7.webm", "duration_seconds": 40}], "time_spent_seconds": 242}	\N	50	2026-05-15 03:39:27.588629+00	pending	\N
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.user_roles (user_id, role_id, id, created_at) FROM stdin;
29	2	28	2026-05-15 03:25:25.456921+00
29	1	29	2026-05-15 03:25:25.456921+00
29	3	30	2026-05-15 03:25:25.456921+00
37	1	32	2026-05-18 12:37:11.265937+00
38	1	33	2026-05-18 16:28:01.893366+00
\.


--
-- Data for Name: user_skill_scores; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.user_skill_scores (user_id, skill_id, score, id, created_at, updated_at, is_estimated) FROM stdin;
37	1	2.5	122	2026-05-18 13:02:12.847961+00	2026-05-18 13:02:12.847961+00	f
37	2	2.1	123	2026-05-18 13:02:12.847961+00	2026-05-18 13:02:12.847961+00	f
37	3	2.0	124	2026-05-18 13:02:12.847961+00	2026-05-18 13:02:12.847961+00	t
37	4	2.2	125	2026-05-18 13:02:12.847961+00	2026-05-18 13:02:12.847961+00	f
37	5	1.9	126	2026-05-18 13:02:12.847961+00	2026-05-18 13:02:12.847961+00	f
37	7	1.6	127	2026-05-18 13:02:12.847961+00	2026-05-18 13:02:12.847961+00	t
37	6	2.3	128	2026-05-18 13:02:12.847961+00	2026-05-18 13:02:12.847961+00	f
38	1	1.3	129	2026-05-18 16:29:04.252811+00	2026-05-18 16:29:04.252811+00	f
38	2	1.4	130	2026-05-18 16:29:04.252811+00	2026-05-18 16:29:04.252811+00	f
38	3	1.3	131	2026-05-18 16:29:04.252811+00	2026-05-18 16:29:04.252811+00	t
38	4	2.0	132	2026-05-18 16:29:04.252811+00	2026-05-18 16:29:04.252811+00	f
38	5	1.6	133	2026-05-18 16:29:04.252811+00	2026-05-18 16:29:04.252811+00	f
38	7	1.4	134	2026-05-18 16:29:04.252811+00	2026-05-18 16:29:04.252811+00	t
38	6	1.3	135	2026-05-18 16:29:04.252811+00	2026-05-18 16:29:04.252811+00	f
29	2	2.1	73	2026-05-04 05:14:14.523495+00	2026-05-04 05:14:14.523495+00	f
29	3	1.7	74	2026-05-04 05:14:14.523495+00	2026-05-04 05:14:14.523495+00	t
29	4	1.6	75	2026-05-04 05:14:14.523495+00	2026-05-04 05:14:14.523495+00	f
29	5	1.9	76	2026-05-04 05:14:14.523495+00	2026-05-04 05:14:14.523495+00	f
29	7	1.6	77	2026-05-04 05:14:14.523495+00	2026-05-04 05:14:14.523495+00	t
29	6	2.9	78	2026-05-04 05:14:14.523495+00	2026-05-05 06:03:50.94682+00	f
29	1	7.5	72	2026-05-04 05:14:14.523495+00	2026-05-15 03:39:27.588629+00	f
\.


--
-- Data for Name: user_tasks; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.user_tasks (user_id, task_id, completed_at, id, created_at, updated_at, enrollment_id, status) FROM stdin;
37	102	\N	133	2026-05-18 12:37:28.229289+00	2026-05-18 12:37:28.229289+00	18	pending
38	104	\N	135	2026-05-18 16:29:40.53823+00	2026-05-18 16:29:40.53823+00	19	pending
38	103	\N	134	2026-05-18 16:29:40.53823+00	2026-05-18 16:30:09.424679+00	19	in_progress
37	101	\N	132	2026-05-18 12:37:28.229289+00	2026-05-19 03:59:24.056982+00	18	in_progress
29	2	\N	31	2026-05-04 05:15:26.876181+00	2026-05-04 05:15:26.876181+00	9	pending
29	2	\N	32	2026-05-04 05:15:30.959217+00	2026-05-04 05:15:30.959217+00	9	pending
29	2	\N	29	2026-05-04 05:15:04.801022+00	2026-05-04 05:15:52.572778+00	9	in_progress
29	2	\N	33	2026-05-04 05:16:17.754058+00	2026-05-04 05:16:17.754058+00	9	pending
29	2	\N	34	2026-05-04 05:16:27.182036+00	2026-05-04 05:16:27.182036+00	9	pending
29	3	\N	35	2026-05-04 05:16:29.629575+00	2026-05-04 05:16:29.629575+00	9	pending
29	3	\N	36	2026-05-04 05:16:34.038372+00	2026-05-04 05:16:34.038372+00	9	pending
29	2	\N	37	2026-05-04 05:16:42.617672+00	2026-05-04 05:16:42.617672+00	9	pending
29	2	\N	38	2026-05-04 11:52:04.388598+00	2026-05-04 11:52:04.388598+00	9	pending
29	2	\N	30	2026-05-04 05:15:05.649433+00	2026-05-05 04:54:01.927017+00	9	in_progress
29	2	\N	39	2026-05-05 04:55:25.284491+00	2026-05-05 04:55:25.284491+00	9	pending
29	91	2026-05-15 03:31:51.467223+00	122	2026-05-14 15:19:21.116302+00	2026-05-15 03:31:51.45433+00	9	completed
29	2	\N	42	2026-05-05 04:58:46.53784+00	2026-05-05 04:58:46.53784+00	9	pending
29	2	\N	44	2026-05-05 06:08:02.059609+00	2026-05-05 06:08:02.059609+00	9	pending
29	1	\N	46	2026-05-05 06:08:48.647473+00	2026-05-05 06:08:48.647473+00	9	pending
29	1	\N	47	2026-05-05 06:09:19.466654+00	2026-05-05 06:09:19.466654+00	9	pending
29	92	2026-05-15 03:33:37.879005+00	123	2026-05-14 15:19:21.116302+00	2026-05-15 03:33:37.872856+00	9	completed
29	5	\N	49	2026-05-05 06:12:50.168074+00	2026-05-05 06:12:50.168074+00	9	pending
29	2	\N	50	2026-05-05 07:04:27.16041+00	2026-05-05 07:04:27.16041+00	9	pending
29	93	2026-05-15 03:35:09.155321+00	124	2026-05-14 15:23:47.642198+00	2026-05-15 03:35:09.150068+00	9	completed
29	94	2026-05-15 03:39:44.949512+00	125	2026-05-14 15:23:47.642198+00	2026-05-15 03:39:44.942325+00	9	completed
29	96	\N	127	2026-05-15 04:19:50.301517+00	2026-05-15 04:19:50.301517+00	9	pending
29	97	\N	128	2026-05-15 04:19:50.301517+00	2026-05-15 04:19:50.301517+00	9	pending
29	98	\N	129	2026-05-15 04:19:50.301517+00	2026-05-15 04:19:50.301517+00	9	pending
29	95	\N	126	2026-05-15 04:19:50.301517+00	2026-05-15 04:20:35.10709+00	9	in_progress
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: coach
--

COPY public.users (email, password_hash, name, id, created_at, updated_at, is_superuser, is_active) FROM stdin;
sarath19@example.com	$2b$12$V9ZrrPCYU1hFCwfs83GJ6.7g7gOWEAviwd2qV0BpHI6vi8x/j0KgC	Sarath	29	2026-05-04 04:15:43.420175+00	2026-05-04 04:15:43.420175+00	t	t
orbin1@example.com	$2b$12$MUkejEKt8PFQ6bJPCCdI8.Z3nVkNSyGeBweUHpuVox6xrI1gvdubi	Orbin	37	2026-05-18 12:37:11.265937+00	2026-05-18 12:37:11.265937+00	f	t
orbinsunny@gmail.com	\N	Orbin BCR70	38	2026-05-18 16:28:01.893366+00	2026-05-18 16:28:01.893366+00	f	t
\.


--
-- Name: activity_attempts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.activity_attempts_id_seq', 1, false);


--
-- Name: activity_evaluations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.activity_evaluations_id_seq', 1, false);


--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.admin_audit_logs_id_seq', 8, true);


--
-- Name: ai_request_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.ai_request_logs_id_seq', 10, true);


--
-- Name: challenge_attempts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.challenge_attempts_id_seq', 3, true);


--
-- Name: challenge_levels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.challenge_levels_id_seq', 3, true);


--
-- Name: challenges_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.challenges_id_seq', 1, true);


--
-- Name: courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.courses_id_seq', 3, true);


--
-- Name: curriculum_days_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.curriculum_days_id_seq', 504, true);


--
-- Name: curriculum_weeks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.curriculum_weeks_id_seq', 72, true);


--
-- Name: daily_activities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.daily_activities_id_seq', 1, false);


--
-- Name: daily_plans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.daily_plans_id_seq', 9, true);


--
-- Name: daily_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.daily_sessions_id_seq', 1, false);


--
-- Name: enrollment_skill_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.enrollment_skill_history_id_seq', 20, true);


--
-- Name: evaluations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.evaluations_id_seq', 50, true);


--
-- Name: feedbacks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.feedbacks_id_seq', 49, true);


--
-- Name: learning_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.learning_sessions_id_seq', 35, true);


--
-- Name: oauth_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.oauth_accounts_id_seq', 4, true);


--
-- Name: payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.payments_id_seq', 3, true);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.permissions_id_seq', 16, true);


--
-- Name: progress_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.progress_logs_id_seq', 70, true);


--
-- Name: purchases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.purchases_id_seq', 9, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.roles_id_seq', 3, true);


--
-- Name: session_scorecards_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.session_scorecards_id_seq', 1, false);


--
-- Name: skill_point_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.skill_point_history_id_seq', 1, false);


--
-- Name: skill_points_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.skill_points_id_seq', 25, true);


--
-- Name: skill_points_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.skill_points_logs_id_seq', 16, true);


--
-- Name: skills_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.skills_id_seq', 7, true);


--
-- Name: streak_freeze_usages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.streak_freeze_usages_id_seq', 1, false);


--
-- Name: subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.subscriptions_id_seq', 1, false);


--
-- Name: task_skills_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.task_skills_id_seq', 114, true);


--
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.tasks_id_seq', 104, true);


--
-- Name: user_course_preferences_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.user_course_preferences_id_seq', 3, true);


--
-- Name: user_enrollments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.user_enrollments_id_seq', 19, true);


--
-- Name: user_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.user_profiles_id_seq', 34, true);


--
-- Name: user_responses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.user_responses_id_seq', 51, true);


--
-- Name: user_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.user_roles_id_seq', 33, true);


--
-- Name: user_skill_scores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.user_skill_scores_id_seq', 135, true);


--
-- Name: user_tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.user_tasks_id_seq', 135, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coach
--

SELECT pg_catalog.setval('public.users_id_seq', 38, true);


--
-- Name: activity_attempts activity_attempts_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.activity_attempts
    ADD CONSTRAINT activity_attempts_pkey PRIMARY KEY (id);


--
-- Name: activity_evaluations activity_evaluations_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.activity_evaluations
    ADD CONSTRAINT activity_evaluations_pkey PRIMARY KEY (id);


--
-- Name: admin_audit_logs admin_audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.admin_audit_logs
    ADD CONSTRAINT admin_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: ai_request_logs ai_request_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.ai_request_logs
    ADD CONSTRAINT ai_request_logs_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: challenge_attempts challenge_attempts_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.challenge_attempts
    ADD CONSTRAINT challenge_attempts_pkey PRIMARY KEY (id);


--
-- Name: challenge_levels challenge_levels_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.challenge_levels
    ADD CONSTRAINT challenge_levels_pkey PRIMARY KEY (id);


--
-- Name: challenges challenges_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.challenges
    ADD CONSTRAINT challenges_pkey PRIMARY KEY (id);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- Name: curriculum_days curriculum_days_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.curriculum_days
    ADD CONSTRAINT curriculum_days_pkey PRIMARY KEY (id);


--
-- Name: curriculum_weeks curriculum_weeks_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.curriculum_weeks
    ADD CONSTRAINT curriculum_weeks_pkey PRIMARY KEY (id);


--
-- Name: daily_activities daily_activities_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.daily_activities
    ADD CONSTRAINT daily_activities_pkey PRIMARY KEY (id);


--
-- Name: daily_plans daily_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.daily_plans
    ADD CONSTRAINT daily_plans_pkey PRIMARY KEY (id);


--
-- Name: daily_sessions daily_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.daily_sessions
    ADD CONSTRAINT daily_sessions_pkey PRIMARY KEY (id);


--
-- Name: enrollment_skill_history enrollment_skill_history_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.enrollment_skill_history
    ADD CONSTRAINT enrollment_skill_history_pkey PRIMARY KEY (id);


--
-- Name: evaluations evaluations_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.evaluations
    ADD CONSTRAINT evaluations_pkey PRIMARY KEY (id);


--
-- Name: feedbacks feedbacks_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.feedbacks
    ADD CONSTRAINT feedbacks_pkey PRIMARY KEY (id);


--
-- Name: learning_sessions learning_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.learning_sessions
    ADD CONSTRAINT learning_sessions_pkey PRIMARY KEY (id);


--
-- Name: oauth_accounts oauth_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.oauth_accounts
    ADD CONSTRAINT oauth_accounts_pkey PRIMARY KEY (id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: progress_logs progress_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.progress_logs
    ADD CONSTRAINT progress_logs_pkey PRIMARY KEY (id);


--
-- Name: purchases purchases_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_pkey PRIMARY KEY (id);


--
-- Name: purchases purchases_user_id_key; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_user_id_key UNIQUE (user_id);


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (role_id, permission_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: session_scorecards session_scorecards_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.session_scorecards
    ADD CONSTRAINT session_scorecards_pkey PRIMARY KEY (id);


--
-- Name: skill_point_history skill_point_history_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.skill_point_history
    ADD CONSTRAINT skill_point_history_pkey PRIMARY KEY (id);


--
-- Name: skill_points_logs skill_points_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.skill_points_logs
    ADD CONSTRAINT skill_points_logs_pkey PRIMARY KEY (id);


--
-- Name: skill_points skill_points_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.skill_points
    ADD CONSTRAINT skill_points_pkey PRIMARY KEY (id);


--
-- Name: skills skills_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.skills
    ADD CONSTRAINT skills_pkey PRIMARY KEY (id);


--
-- Name: streak_freeze_usages streak_freeze_usages_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.streak_freeze_usages
    ADD CONSTRAINT streak_freeze_usages_pkey PRIMARY KEY (id);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- Name: task_archetypes task_archetypes_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.task_archetypes
    ADD CONSTRAINT task_archetypes_pkey PRIMARY KEY (id);


--
-- Name: task_skills task_skills_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.task_skills
    ADD CONSTRAINT task_skills_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: activity_attempts uq_activity_attempt_sequence; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.activity_attempts
    ADD CONSTRAINT uq_activity_attempt_sequence UNIQUE (session_id, sequence);


--
-- Name: challenge_levels uq_challenge_levels_challenge_level; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.challenge_levels
    ADD CONSTRAINT uq_challenge_levels_challenge_level UNIQUE (challenge_id, level_number);


--
-- Name: curriculum_days uq_curriculum_day; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.curriculum_days
    ADD CONSTRAINT uq_curriculum_day UNIQUE (week_id, day_number);


--
-- Name: curriculum_weeks uq_curriculum_week; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.curriculum_weeks
    ADD CONSTRAINT uq_curriculum_week UNIQUE (course_length, week_number);


--
-- Name: daily_activities uq_daily_activities_user_date; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.daily_activities
    ADD CONSTRAINT uq_daily_activities_user_date UNIQUE (user_id, local_date);


--
-- Name: daily_plans uq_daily_plan_user_day; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.daily_plans
    ADD CONSTRAINT uq_daily_plan_user_day UNIQUE (user_id, course_slug, week, day);


--
-- Name: enrollment_skill_history uq_enrollment_skill; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.enrollment_skill_history
    ADD CONSTRAINT uq_enrollment_skill UNIQUE (enrollment_id, skill_id);


--
-- Name: oauth_accounts uq_oauth_provider_user; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.oauth_accounts
    ADD CONSTRAINT uq_oauth_provider_user UNIQUE (provider, provider_user_id);


--
-- Name: user_course_preferences uq_user_course_preferences_user; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_course_preferences
    ADD CONSTRAINT uq_user_course_preferences_user UNIQUE (user_id);


--
-- Name: user_roles uq_user_roles_user_role; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT uq_user_roles_user_role UNIQUE (user_id, role_id);


--
-- Name: user_skill_scores uq_user_skill; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_skill_scores
    ADD CONSTRAINT uq_user_skill UNIQUE (user_id, skill_id);


--
-- Name: skill_points uq_user_skill_points; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.skill_points
    ADD CONSTRAINT uq_user_skill_points UNIQUE (user_id, skill_id);


--
-- Name: user_course_preferences user_course_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_course_preferences
    ADD CONSTRAINT user_course_preferences_pkey PRIMARY KEY (id);


--
-- Name: user_enrollments user_enrollments_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_enrollments
    ADD CONSTRAINT user_enrollments_pkey PRIMARY KEY (id);


--
-- Name: user_profiles user_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_pkey PRIMARY KEY (id);


--
-- Name: user_profiles user_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_user_id_key UNIQUE (user_id);


--
-- Name: user_responses user_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_responses
    ADD CONSTRAINT user_responses_pkey PRIMARY KEY (id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (id);


--
-- Name: user_skill_scores user_skill_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_skill_scores
    ADD CONSTRAINT user_skill_scores_pkey PRIMARY KEY (id);


--
-- Name: user_tasks user_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_tasks
    ADD CONSTRAINT user_tasks_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_activity_attempts_archetype_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_activity_attempts_archetype_id ON public.activity_attempts USING btree (archetype_id);


--
-- Name: ix_activity_attempts_session_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_activity_attempts_session_id ON public.activity_attempts USING btree (session_id);


--
-- Name: ix_activity_evaluations_attempt_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE UNIQUE INDEX ix_activity_evaluations_attempt_id ON public.activity_evaluations USING btree (attempt_id);


--
-- Name: ix_admin_audit_logs_action; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_admin_audit_logs_action ON public.admin_audit_logs USING btree (action);


--
-- Name: ix_admin_audit_logs_admin_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_admin_audit_logs_admin_user_id ON public.admin_audit_logs USING btree (admin_user_id);


--
-- Name: ix_admin_audit_logs_resource_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_admin_audit_logs_resource_id ON public.admin_audit_logs USING btree (resource_id);


--
-- Name: ix_admin_audit_logs_resource_type; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_admin_audit_logs_resource_type ON public.admin_audit_logs USING btree (resource_type);


--
-- Name: ix_ai_request_logs_agent_name; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_ai_request_logs_agent_name ON public.ai_request_logs USING btree (agent_name);


--
-- Name: ix_ai_request_logs_status; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_ai_request_logs_status ON public.ai_request_logs USING btree (status);


--
-- Name: ix_ai_request_logs_trace_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_ai_request_logs_trace_id ON public.ai_request_logs USING btree (trace_id);


--
-- Name: ix_ai_request_logs_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_ai_request_logs_user_id ON public.ai_request_logs USING btree (user_id);


--
-- Name: ix_challenge_attempts_challenge_level_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_challenge_attempts_challenge_level_id ON public.challenge_attempts USING btree (challenge_level_id);


--
-- Name: ix_challenge_attempts_expires_at; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_challenge_attempts_expires_at ON public.challenge_attempts USING btree (expires_at);


--
-- Name: ix_challenge_attempts_status; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_challenge_attempts_status ON public.challenge_attempts USING btree (status);


--
-- Name: ix_challenge_attempts_user_created_at; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_challenge_attempts_user_created_at ON public.challenge_attempts USING btree (user_id, created_at);


--
-- Name: ix_challenge_attempts_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_challenge_attempts_user_id ON public.challenge_attempts USING btree (user_id);


--
-- Name: ix_challenge_attempts_user_level_status; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_challenge_attempts_user_level_status ON public.challenge_attempts USING btree (user_id, challenge_level_id, status);


--
-- Name: ix_challenge_levels_challenge_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_challenge_levels_challenge_id ON public.challenge_levels USING btree (challenge_id);


--
-- Name: ix_challenges_active_sort; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_challenges_active_sort ON public.challenges USING btree (is_active, sort_order);


--
-- Name: ix_challenges_slug; Type: INDEX; Schema: public; Owner: coach
--

CREATE UNIQUE INDEX ix_challenges_slug ON public.challenges USING btree (slug);


--
-- Name: ix_courses_slug; Type: INDEX; Schema: public; Owner: coach
--

CREATE UNIQUE INDEX ix_courses_slug ON public.courses USING btree (slug);


--
-- Name: ix_curriculum_days_week_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_curriculum_days_week_id ON public.curriculum_days USING btree (week_id);


--
-- Name: ix_curriculum_week_lookup; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_curriculum_week_lookup ON public.curriculum_weeks USING btree (course_length, week_number);


--
-- Name: ix_curriculum_weeks_theme_type; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_curriculum_weeks_theme_type ON public.curriculum_weeks USING btree (theme_type);


--
-- Name: ix_daily_activities_user_date; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_daily_activities_user_date ON public.daily_activities USING btree (user_id, local_date);


--
-- Name: ix_daily_activities_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_daily_activities_user_id ON public.daily_activities USING btree (user_id);


--
-- Name: ix_daily_plan_lookup; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_daily_plan_lookup ON public.daily_plans USING btree (user_id, course_slug, week, day);


--
-- Name: ix_daily_plans_course_slug; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_daily_plans_course_slug ON public.daily_plans USING btree (course_slug);


--
-- Name: ix_daily_plans_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_daily_plans_user_id ON public.daily_plans USING btree (user_id);


--
-- Name: ix_daily_sessions_curriculum_day_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_daily_sessions_curriculum_day_id ON public.daily_sessions USING btree (curriculum_day_id);


--
-- Name: ix_daily_sessions_status; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_daily_sessions_status ON public.daily_sessions USING btree (status);


--
-- Name: ix_daily_sessions_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_daily_sessions_user_id ON public.daily_sessions USING btree (user_id);


--
-- Name: ix_daily_sessions_user_status; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_daily_sessions_user_status ON public.daily_sessions USING btree (user_id, status);


--
-- Name: ix_enrollment_skill_history_enrollment_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_enrollment_skill_history_enrollment_id ON public.enrollment_skill_history USING btree (enrollment_id);


--
-- Name: ix_enrollment_skill_history_skill_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_enrollment_skill_history_skill_id ON public.enrollment_skill_history USING btree (skill_id);


--
-- Name: ix_evaluations_response_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE UNIQUE INDEX ix_evaluations_response_id ON public.evaluations USING btree (response_id);


--
-- Name: ix_feedbacks_evaluation_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE UNIQUE INDEX ix_feedbacks_evaluation_id ON public.feedbacks USING btree (evaluation_id);


--
-- Name: ix_feedbacks_review_status; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_feedbacks_review_status ON public.feedbacks USING btree (review_status);


--
-- Name: ix_feedbacks_reviewed_by; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_feedbacks_reviewed_by ON public.feedbacks USING btree (reviewed_by);


--
-- Name: ix_learning_sessions_enrollment_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_learning_sessions_enrollment_id ON public.learning_sessions USING btree (enrollment_id);


--
-- Name: ix_learning_sessions_session_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE UNIQUE INDEX ix_learning_sessions_session_id ON public.learning_sessions USING btree (session_id);


--
-- Name: ix_learning_sessions_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_learning_sessions_user_id ON public.learning_sessions USING btree (user_id);


--
-- Name: ix_learning_sessions_user_task_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_learning_sessions_user_task_id ON public.learning_sessions USING btree (user_task_id);


--
-- Name: ix_oauth_accounts_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_oauth_accounts_user_id ON public.oauth_accounts USING btree (user_id);


--
-- Name: ix_payments_paid_at; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_payments_paid_at ON public.payments USING btree (paid_at);


--
-- Name: ix_payments_provider; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_payments_provider ON public.payments USING btree (provider);


--
-- Name: ix_payments_provider_payment_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE UNIQUE INDEX ix_payments_provider_payment_id ON public.payments USING btree (provider_payment_id);


--
-- Name: ix_payments_status; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_payments_status ON public.payments USING btree (status);


--
-- Name: ix_payments_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_payments_user_id ON public.payments USING btree (user_id);


--
-- Name: ix_permissions_key; Type: INDEX; Schema: public; Owner: coach
--

CREATE UNIQUE INDEX ix_permissions_key ON public.permissions USING btree (key);


--
-- Name: ix_progress_logs_skill_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_progress_logs_skill_id ON public.progress_logs USING btree (skill_id);


--
-- Name: ix_progress_logs_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_progress_logs_user_id ON public.progress_logs USING btree (user_id);


--
-- Name: ix_purchases_plan_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_purchases_plan_id ON public.purchases USING btree (plan_id);


--
-- Name: ix_purchases_status; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_purchases_status ON public.purchases USING btree (status);


--
-- Name: ix_purchases_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_purchases_user_id ON public.purchases USING btree (user_id);


--
-- Name: ix_role_permissions_permission_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_role_permissions_permission_id ON public.role_permissions USING btree (permission_id);


--
-- Name: ix_role_permissions_role_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_role_permissions_role_id ON public.role_permissions USING btree (role_id);


--
-- Name: ix_roles_name; Type: INDEX; Schema: public; Owner: coach
--

CREATE UNIQUE INDEX ix_roles_name ON public.roles USING btree (name);


--
-- Name: ix_session_scorecards_session_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE UNIQUE INDEX ix_session_scorecards_session_id ON public.session_scorecards USING btree (session_id);


--
-- Name: ix_skill_point_history_session_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_skill_point_history_session_id ON public.skill_point_history USING btree (session_id);


--
-- Name: ix_skill_point_history_skill_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_skill_point_history_skill_id ON public.skill_point_history USING btree (skill_id);


--
-- Name: ix_skill_point_history_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_skill_point_history_user_id ON public.skill_point_history USING btree (user_id);


--
-- Name: ix_skill_point_history_user_skill; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_skill_point_history_user_skill ON public.skill_point_history USING btree (user_id, skill_id);


--
-- Name: ix_skill_points_logs_skill_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_skill_points_logs_skill_id ON public.skill_points_logs USING btree (skill_id);


--
-- Name: ix_skill_points_logs_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_skill_points_logs_user_id ON public.skill_points_logs USING btree (user_id);


--
-- Name: ix_skill_points_skill_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_skill_points_skill_id ON public.skill_points USING btree (skill_id);


--
-- Name: ix_skill_points_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_skill_points_user_id ON public.skill_points USING btree (user_id);


--
-- Name: ix_skills_name; Type: INDEX; Schema: public; Owner: coach
--

CREATE UNIQUE INDEX ix_skills_name ON public.skills USING btree (name);


--
-- Name: ix_streak_freeze_usages_user_date; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_streak_freeze_usages_user_date ON public.streak_freeze_usages USING btree (user_id, protected_date);


--
-- Name: ix_streak_freeze_usages_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_streak_freeze_usages_user_id ON public.streak_freeze_usages USING btree (user_id);


--
-- Name: ix_subscriptions_current_period_end; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_subscriptions_current_period_end ON public.subscriptions USING btree (current_period_end);


--
-- Name: ix_subscriptions_provider; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_subscriptions_provider ON public.subscriptions USING btree (provider);


--
-- Name: ix_subscriptions_provider_customer_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_subscriptions_provider_customer_id ON public.subscriptions USING btree (provider_customer_id);


--
-- Name: ix_subscriptions_provider_subscription_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE UNIQUE INDEX ix_subscriptions_provider_subscription_id ON public.subscriptions USING btree (provider_subscription_id);


--
-- Name: ix_subscriptions_status; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_subscriptions_status ON public.subscriptions USING btree (status);


--
-- Name: ix_subscriptions_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_subscriptions_user_id ON public.subscriptions USING btree (user_id);


--
-- Name: ix_task_archetypes_core_activity; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_task_archetypes_core_activity ON public.task_archetypes USING btree (core_activity);


--
-- Name: ix_task_skills_skill_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_task_skills_skill_id ON public.task_skills USING btree (skill_id);


--
-- Name: ix_task_skills_task_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_task_skills_task_id ON public.task_skills USING btree (task_id);


--
-- Name: ix_user_course_preferences_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_user_course_preferences_user_id ON public.user_course_preferences USING btree (user_id);


--
-- Name: ix_user_enrollments_course_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_user_enrollments_course_id ON public.user_enrollments USING btree (course_id);


--
-- Name: ix_user_enrollments_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE UNIQUE INDEX ix_user_enrollments_user_id ON public.user_enrollments USING btree (user_id);


--
-- Name: ix_user_responses_embedding_status; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_user_responses_embedding_status ON public.user_responses USING btree (embedding_status);


--
-- Name: ix_user_responses_user_task_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE UNIQUE INDEX ix_user_responses_user_task_id ON public.user_responses USING btree (user_task_id);


--
-- Name: ix_user_roles_role_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_user_roles_role_id ON public.user_roles USING btree (role_id);


--
-- Name: ix_user_roles_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_user_roles_user_id ON public.user_roles USING btree (user_id);


--
-- Name: ix_user_skill_scores_skill_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_user_skill_scores_skill_id ON public.user_skill_scores USING btree (skill_id);


--
-- Name: ix_user_skill_scores_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_user_skill_scores_user_id ON public.user_skill_scores USING btree (user_id);


--
-- Name: ix_user_tasks_enrollment_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_user_tasks_enrollment_id ON public.user_tasks USING btree (enrollment_id);


--
-- Name: ix_user_tasks_task_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_user_tasks_task_id ON public.user_tasks USING btree (task_id);


--
-- Name: ix_user_tasks_user_id; Type: INDEX; Schema: public; Owner: coach
--

CREATE INDEX ix_user_tasks_user_id ON public.user_tasks USING btree (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: coach
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: activity_attempts activity_attempts_archetype_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.activity_attempts
    ADD CONSTRAINT activity_attempts_archetype_id_fkey FOREIGN KEY (archetype_id) REFERENCES public.task_archetypes(id) ON DELETE RESTRICT;


--
-- Name: activity_attempts activity_attempts_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.activity_attempts
    ADD CONSTRAINT activity_attempts_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.daily_sessions(id) ON DELETE CASCADE;


--
-- Name: activity_evaluations activity_evaluations_attempt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.activity_evaluations
    ADD CONSTRAINT activity_evaluations_attempt_id_fkey FOREIGN KEY (attempt_id) REFERENCES public.activity_attempts(id) ON DELETE CASCADE;


--
-- Name: admin_audit_logs admin_audit_logs_admin_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.admin_audit_logs
    ADD CONSTRAINT admin_audit_logs_admin_user_id_fkey FOREIGN KEY (admin_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: ai_request_logs ai_request_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.ai_request_logs
    ADD CONSTRAINT ai_request_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: challenge_attempts challenge_attempts_challenge_level_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.challenge_attempts
    ADD CONSTRAINT challenge_attempts_challenge_level_id_fkey FOREIGN KEY (challenge_level_id) REFERENCES public.challenge_levels(id) ON DELETE CASCADE;


--
-- Name: challenge_attempts challenge_attempts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.challenge_attempts
    ADD CONSTRAINT challenge_attempts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: challenge_levels challenge_levels_challenge_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.challenge_levels
    ADD CONSTRAINT challenge_levels_challenge_id_fkey FOREIGN KEY (challenge_id) REFERENCES public.challenges(id) ON DELETE CASCADE;


--
-- Name: curriculum_days curriculum_days_week_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.curriculum_days
    ADD CONSTRAINT curriculum_days_week_id_fkey FOREIGN KEY (week_id) REFERENCES public.curriculum_weeks(id) ON DELETE CASCADE;


--
-- Name: daily_activities daily_activities_last_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.daily_activities
    ADD CONSTRAINT daily_activities_last_session_id_fkey FOREIGN KEY (last_session_id) REFERENCES public.daily_sessions(id) ON DELETE SET NULL;


--
-- Name: daily_activities daily_activities_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.daily_activities
    ADD CONSTRAINT daily_activities_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: daily_plans daily_plans_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.daily_plans
    ADD CONSTRAINT daily_plans_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: daily_sessions daily_sessions_curriculum_day_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.daily_sessions
    ADD CONSTRAINT daily_sessions_curriculum_day_id_fkey FOREIGN KEY (curriculum_day_id) REFERENCES public.curriculum_days(id) ON DELETE RESTRICT;


--
-- Name: daily_sessions daily_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.daily_sessions
    ADD CONSTRAINT daily_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: enrollment_skill_history enrollment_skill_history_enrollment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.enrollment_skill_history
    ADD CONSTRAINT enrollment_skill_history_enrollment_id_fkey FOREIGN KEY (enrollment_id) REFERENCES public.user_enrollments(id) ON DELETE CASCADE;


--
-- Name: enrollment_skill_history enrollment_skill_history_skill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.enrollment_skill_history
    ADD CONSTRAINT enrollment_skill_history_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.skills(id) ON DELETE CASCADE;


--
-- Name: evaluations evaluations_response_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.evaluations
    ADD CONSTRAINT evaluations_response_id_fkey FOREIGN KEY (response_id) REFERENCES public.user_responses(id) ON DELETE CASCADE;


--
-- Name: feedbacks feedbacks_evaluation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.feedbacks
    ADD CONSTRAINT feedbacks_evaluation_id_fkey FOREIGN KEY (evaluation_id) REFERENCES public.evaluations(id) ON DELETE CASCADE;


--
-- Name: feedbacks fk_feedbacks_reviewed_by_users; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.feedbacks
    ADD CONSTRAINT fk_feedbacks_reviewed_by_users FOREIGN KEY (reviewed_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: learning_sessions fk_learning_sessions_user_task_id_user_tasks; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.learning_sessions
    ADD CONSTRAINT fk_learning_sessions_user_task_id_user_tasks FOREIGN KEY (user_task_id) REFERENCES public.user_tasks(id) ON DELETE SET NULL;


--
-- Name: user_tasks fk_user_tasks_enrollment_id; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_tasks
    ADD CONSTRAINT fk_user_tasks_enrollment_id FOREIGN KEY (enrollment_id) REFERENCES public.user_enrollments(id) ON DELETE SET NULL;


--
-- Name: learning_sessions learning_sessions_enrollment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.learning_sessions
    ADD CONSTRAINT learning_sessions_enrollment_id_fkey FOREIGN KEY (enrollment_id) REFERENCES public.user_enrollments(id) ON DELETE CASCADE;


--
-- Name: learning_sessions learning_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.learning_sessions
    ADD CONSTRAINT learning_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: oauth_accounts oauth_accounts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.oauth_accounts
    ADD CONSTRAINT oauth_accounts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: payments payments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: progress_logs progress_logs_skill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.progress_logs
    ADD CONSTRAINT progress_logs_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.skills(id) ON DELETE CASCADE;


--
-- Name: progress_logs progress_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.progress_logs
    ADD CONSTRAINT progress_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: purchases purchases_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: session_scorecards session_scorecards_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.session_scorecards
    ADD CONSTRAINT session_scorecards_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.daily_sessions(id) ON DELETE CASCADE;


--
-- Name: skill_point_history skill_point_history_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.skill_point_history
    ADD CONSTRAINT skill_point_history_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.daily_sessions(id) ON DELETE CASCADE;


--
-- Name: skill_point_history skill_point_history_skill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.skill_point_history
    ADD CONSTRAINT skill_point_history_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.skills(id) ON DELETE CASCADE;


--
-- Name: skill_point_history skill_point_history_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.skill_point_history
    ADD CONSTRAINT skill_point_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: skill_points_logs skill_points_logs_skill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.skill_points_logs
    ADD CONSTRAINT skill_points_logs_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.skills(id) ON DELETE CASCADE;


--
-- Name: skill_points_logs skill_points_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.skill_points_logs
    ADD CONSTRAINT skill_points_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: skill_points skill_points_skill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.skill_points
    ADD CONSTRAINT skill_points_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.skills(id) ON DELETE CASCADE;


--
-- Name: skill_points skill_points_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.skill_points
    ADD CONSTRAINT skill_points_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: streak_freeze_usages streak_freeze_usages_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.streak_freeze_usages
    ADD CONSTRAINT streak_freeze_usages_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: subscriptions subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: task_skills task_skills_skill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.task_skills
    ADD CONSTRAINT task_skills_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.skills(id) ON DELETE CASCADE;


--
-- Name: task_skills task_skills_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.task_skills
    ADD CONSTRAINT task_skills_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id) ON DELETE CASCADE;


--
-- Name: user_course_preferences user_course_preferences_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_course_preferences
    ADD CONSTRAINT user_course_preferences_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_enrollments user_enrollments_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_enrollments
    ADD CONSTRAINT user_enrollments_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE CASCADE;


--
-- Name: user_enrollments user_enrollments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_enrollments
    ADD CONSTRAINT user_enrollments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_profiles user_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_responses user_responses_user_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_responses
    ADD CONSTRAINT user_responses_user_task_id_fkey FOREIGN KEY (user_task_id) REFERENCES public.user_tasks(id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_skill_scores user_skill_scores_skill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_skill_scores
    ADD CONSTRAINT user_skill_scores_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.skills(id) ON DELETE CASCADE;


--
-- Name: user_skill_scores user_skill_scores_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_skill_scores
    ADD CONSTRAINT user_skill_scores_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_tasks user_tasks_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_tasks
    ADD CONSTRAINT user_tasks_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id) ON DELETE CASCADE;


--
-- Name: user_tasks user_tasks_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: coach
--

ALTER TABLE ONLY public.user_tasks
    ADD CONSTRAINT user_tasks_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict tPcgterT2QtYMZNPbphkvJhlyXcEjAcTOYhjM7tevOK93jRvaLWWTvM3g13uMkv

