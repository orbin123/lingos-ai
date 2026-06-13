import type { Metadata } from "next";
import {
  AlertTriangle,
  BookOpen,
  CreditCard,
  FileText,
  Mail,
  ScrollText,
  ShieldCheck,
  UserCheck,
  Wifi,
} from "lucide-react";

import { LegalPage, type LegalSection } from "@/components/legal/LegalPage";

export const metadata: Metadata = {
  title: "Terms of Service | LingosAI",
  description:
    "The guidelines for using Lingos AI responsibly — your account, acceptable use, payments, availability, and the limits of our liability.",
  openGraph: {
    title: "Terms of Service | LingosAI",
    description: "Guidelines for using Lingos AI responsibly.",
    type: "website",
  },
};

const SECTIONS: LegalSection[] = [
  {
    icon: FileText,
    heading: "Acceptance of Terms",
    body: "By creating an account or using Lingos AI, you agree to these Terms of Service and to our Privacy Policy. If you do not agree, please do not use the service.",
  },
  {
    icon: UserCheck,
    heading: "User Accounts",
    body: "You are responsible for the activity that happens under your account:",
    bullets: [
      "Provide accurate information when you sign up.",
      "Keep your password confidential and your account secure.",
      "Notify us promptly if you suspect any unauthorized use.",
    ],
  },
  {
    icon: ShieldCheck,
    heading: "Acceptable Use",
    body: "To keep Lingos AI safe and useful for everyone, you agree not to:",
    bullets: [
      "Abuse, harass, or harm other users or our team.",
      "Attempt to gain unauthorized access to accounts or systems.",
      "Submit harmful, illegal, or malicious content.",
      "Disrupt, overload, or interfere with the service.",
    ],
  },
  {
    icon: BookOpen,
    heading: "Intellectual Property",
    body: "The Lingos AI platform, including its curriculum, software, branding, and generated content, is owned by Lingos AI and protected by applicable laws. You retain ownership of the responses you submit, and grant us the limited rights needed to evaluate them and deliver feedback.",
  },
  {
    icon: CreditCard,
    heading: "Subscription & Payments",
    body: "Paid plans are billed through our payment provider:",
    bullets: [
      "Subscription fees and trial terms are shown before you purchase.",
      "Payments are processed securely by Razorpay; we never store raw card data.",
      "You can manage or cancel your subscription from your account at any time.",
    ],
  },
  {
    icon: Wifi,
    heading: "Service Availability",
    body: "We work to keep Lingos AI available and reliable, but the service is provided on an “as available” basis. We may update, maintain, or temporarily interrupt the service, and features may change over time.",
  },
  {
    icon: AlertTriangle,
    heading: "Termination",
    body: "You may stop using the service and delete your account at any time. We may suspend or terminate accounts that violate these terms or put the service or other users at risk.",
  },
  {
    icon: ScrollText,
    heading: "Limitation of Liability",
    body: "Lingos AI is a learning tool provided to help you practice English. To the fullest extent permitted by law, we are not liable for indirect or incidental damages arising from your use of the service, and the service is provided without warranties of any kind.",
  },
  {
    icon: Mail,
    heading: "Contact",
    body: (
      <>
        Questions about these terms? Email us at{" "}
        <a className="legal-body-link" href="mailto:support@lingosai.com">
          support@lingosai.com
        </a>
        .
      </>
    ),
  },
];

export default function TermsOfServicePage() {
  return (
    <LegalPage
      eyebrow="Terms"
      title="Terms of Service"
      subtitle="Guidelines for using Lingos AI responsibly."
      lastUpdated="June 2026"
      sections={SECTIONS}
    />
  );
}
