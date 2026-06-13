import type { Metadata } from "next";
import { Database, Lock, Mail, Server, Shield, Users } from "lucide-react";

import { LegalPage, type LegalSection } from "@/components/legal/LegalPage";

export const metadata: Metadata = {
  title: "Privacy Policy | LingosAI",
  description:
    "How Lingos AI collects, uses, and protects your information — the data we store, how we use it, and the rights you have over it.",
  openGraph: {
    title: "Privacy Policy | LingosAI",
    description:
      "How Lingos AI collects, uses, and protects your information.",
    type: "website",
  },
};

const SECTIONS: LegalSection[] = [
  {
    icon: Database,
    heading: "Information We Collect",
    body: "To deliver personalized English coaching, we collect only what the product needs to work:",
    bullets: [
      "Account information — your name, email address, and password (stored securely, never in plain text).",
      "Learning preferences — your goals, level, and the choices you make while setting up your plan.",
      "Task responses — the answers, recordings, and messages you submit during lessons so the tutor can evaluate and coach you.",
      "Progress data — scores, streaks, sub-skill points, and history used to power your dashboard.",
    ],
  },
  {
    icon: Shield,
    heading: "How We Use Information",
    body: "Your information is used to run and improve your learning experience — never sold:",
    bullets: [
      "Personalize your learning path and adapt tasks to your level.",
      "Improve the quality and accuracy of AI feedback.",
      "Track your progress and surface insights on your dashboard.",
      "Provide customer support and respond to your requests.",
    ],
  },
  {
    icon: Lock,
    heading: "Data Security",
    body: "We follow industry-standard practices to keep your data safe:",
    bullets: [
      "Communication between your device and our servers is encrypted in transit.",
      "Passwords are hashed, and access to systems is restricted and monitored.",
      "Accounts are protected and payment data is never stored on our servers.",
    ],
  },
  {
    icon: Server,
    heading: "Third-Party Services",
    body: "We rely on trusted providers to deliver parts of the service. Your data is shared with them only as needed for the service to function:",
    bullets: [
      "OpenAI — generating tasks, evaluating answers, and producing feedback.",
      "Resend — sending transactional emails such as verification codes.",
      "Razorpay — securely processing subscription payments.",
      "AWS — hosting and infrastructure.",
    ],
  },
  {
    icon: Users,
    heading: "Your Rights",
    body: "You stay in control of your data. At any time you can:",
    bullets: [
      "Request deletion of your account and associated data.",
      "Update your profile and learning preferences.",
      "Contact support with any privacy questions or concerns.",
    ],
  },
  {
    icon: Mail,
    heading: "Contact",
    body: (
      <>
        Questions about this policy or your data? Email us at{" "}
        <a className="legal-body-link" href="mailto:support@lingosai.com">
          support@lingosai.com
        </a>{" "}
        and we&apos;ll be happy to help.
      </>
    ),
  },
];

export default function PrivacyPolicyPage() {
  return (
    <LegalPage
      eyebrow="Privacy"
      title="Privacy Policy"
      subtitle="How Lingos AI collects, uses, and protects your information."
      lastUpdated="June 2026"
      sections={SECTIONS}
    />
  );
}
