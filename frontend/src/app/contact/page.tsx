import type { Metadata } from "next";
import { Clock, type LucideIcon, Mail, MapPin } from "lucide-react";

import { ACCENT_HUE, DotGrid, GlassCard } from "@/components/blog/BlogVisuals";
import { ContactForm } from "@/components/contact/ContactForm";
import { LandingFooter } from "@/components/layout/LandingFooter";
import { LandingNavbar } from "@/components/layout/LandingNavbar";
import { MarketingCTALink } from "@/components/marketing/MarketingCTALink";

export const metadata: Metadata = {
  title: "Contact — We'd Love to Hear From You | LingosAI",
  description:
    "Questions, feedback, partnerships, or support — get in touch with the LingosAI team. We typically reply within 24–48 hours.",
  openGraph: {
    title: "Contact LingosAI",
    description:
      "Questions, feedback, partnerships, or support — our team is here to help.",
    type: "website",
  },
};

const INFO_CARDS: {
  icon: LucideIcon;
  label: string;
  value: string;
  href?: string;
}[] = [
  {
    icon: Mail,
    label: "Email",
    value: "support@lingosai.com",
    href: "mailto:support@lingosai.com",
  },
  { icon: MapPin, label: "Location", value: "Kerala, India" },
  { icon: Clock, label: "Response time", value: "Typically within 24–48 hours" },
];

const FAQS = [
  {
    q: "Is Lingos AI suitable for beginners?",
    a: "Absolutely. Your journey starts with a short diagnosis that places you at the right level, and the curriculum adapts from there — whether you're just starting out or polishing advanced fluency.",
  },
  {
    q: "Do I need speaking experience?",
    a: "No prior experience needed. You'll practice speaking from day one with guided tasks and gentle, specific feedback, so confidence builds naturally as you go.",
  },
  {
    q: "Can I use it for interview preparation?",
    a: "Yes. Many learners use Lingos AI to sharpen professional communication — clear answers, confident delivery, and the vocabulary that interviews demand.",
  },
] as const;

export default function ContactPage() {
  return (
    <main
      style={{
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        minHeight: "100svh",
        background: `radial-gradient(circle at top right, oklch(90% 0.05 ${ACCENT_HUE}) 0%, oklch(95% 0.02 ${
          ACCENT_HUE + 10
        }) 40%, #ffffff 100%)`,
        paddingTop: 100,
        color: "oklch(20% 0.05 240)",
      }}
    >
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />
      <style>{STYLES}</style>
      <LandingNavbar showCTA={false} />

      {/* HERO */}
      <section
        className="mkt-section"
        style={{
          position: "relative",
          padding: "70px 40px 50px",
          textAlign: "center",
          maxWidth: 920,
          margin: "0 auto",
        }}
      >
        <span style={eyebrowStyle}>Contact Us</span>
        <h1
          style={{
            fontSize: "clamp(36px, 4.5vw, 60px)",
            fontWeight: 800,
            color: "oklch(15% 0.09 245)",
            lineHeight: 1.12,
            letterSpacing: "-1px",
            margin: "18px 0 20px",
          }}
        >
          We&apos;d Love to Hear From You
        </h1>
        <p
          style={{
            fontSize: 20,
            color: "oklch(40% 0.05 240)",
            lineHeight: 1.6,
            maxWidth: 680,
            margin: "0 auto",
          }}
        >
          Questions, feedback, partnerships, or support — our team is here to help.
        </p>
      </section>

      {/* FORM + INFO */}
      <section className="mkt-section" style={{ padding: "10px 40px 90px" }}>
        <div className="contact-layout" style={{ maxWidth: 1080, margin: "0 auto" }}>
          <div>
            <ContactForm />
          </div>

          <aside style={{ display: "flex", flexDirection: "column", gap: 18 }}>
            {INFO_CARDS.map(({ icon: Icon, label, value, href }) => {
              const body = (
                <GlassCard className="info-card" style={{ padding: "22px 24px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                    <span style={iconBadgeStyle}>
                      <Icon size={20} aria-hidden />
                    </span>
                    <div>
                      <div style={infoLabelStyle}>{label}</div>
                      <div style={infoValueStyle}>{value}</div>
                    </div>
                  </div>
                </GlassCard>
              );
              return href ? (
                <a
                  key={label}
                  href={href}
                  style={{ textDecoration: "none", color: "inherit" }}
                >
                  {body}
                </a>
              ) : (
                <div key={label}>{body}</div>
              );
            })}
          </aside>
        </div>
      </section>

      {/* FAQ */}
      <section className="mkt-section" style={{ padding: "0 40px 90px" }}>
        <div style={{ maxWidth: 820, margin: "0 auto" }}>
          <h2
            style={{
              fontSize: "clamp(26px, 3vw, 36px)",
              fontWeight: 800,
              color: "oklch(15% 0.09 245)",
              letterSpacing: "-0.5px",
              textAlign: "center",
              margin: "0 0 32px",
            }}
          >
            Frequently asked questions
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {FAQS.map((faq) => (
              <details key={faq.q} className="faq-item">
                <summary className="faq-summary">
                  <span>{faq.q}</span>
                  <span className="faq-chevron" aria-hidden>
                    +
                  </span>
                </summary>
                <p className="faq-answer">{faq.a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mkt-section" style={{ padding: "0 40px 110px" }}>
        <div
          style={{
            maxWidth: 1080,
            margin: "0 auto",
            borderRadius: 28,
            padding: "64px 40px",
            textAlign: "center",
            background: `linear-gradient(135deg, oklch(35% 0.15 ${ACCENT_HUE}), oklch(25% 0.1 ${ACCENT_HUE}))`,
            color: "white",
            position: "relative",
            overflow: "hidden",
          }}
        >
          <DotGrid opacity={0.16} />
          <div style={{ position: "relative" }}>
            <h2
              style={{
                fontSize: "clamp(28px, 3.5vw, 40px)",
                fontWeight: 800,
                margin: "0 0 28px",
                letterSpacing: "-0.5px",
              }}
            >
              Start your English improvement journey today.
            </h2>
            <MarketingCTALink
              anonLabel="Get Started"
              className="contact-cta-btn"
              style={{
                display: "inline-block",
                padding: "15px 38px",
                borderRadius: 50,
                background: "white",
                color: "oklch(25% 0.1 240)",
                fontSize: 16,
                fontWeight: 700,
                textDecoration: "none",
                boxShadow: "0 8px 24px rgba(20,50,120,0.2)",
              }}
            />
          </div>
        </div>
      </section>

      <LandingFooter />
    </main>
  );
}

// ── shared inline styles ────────────────────────────────────────────────────
const eyebrowStyle = {
  display: "inline-block",
  padding: "7px 16px",
  background: `oklch(95% 0.04 ${ACCENT_HUE})`,
  borderRadius: 50,
  color: `oklch(40% 0.14 ${ACCENT_HUE})`,
  fontSize: 13,
  fontWeight: 700,
  letterSpacing: "0.04em",
  textTransform: "uppercase" as const,
};

const iconBadgeStyle = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  width: 44,
  height: 44,
  flexShrink: 0,
  borderRadius: 14,
  background: `oklch(94% 0.05 ${ACCENT_HUE})`,
  color: `oklch(40% 0.14 ${ACCENT_HUE})`,
};

const infoLabelStyle = {
  fontSize: 12.5,
  fontWeight: 700,
  letterSpacing: "0.02em",
  textTransform: "uppercase" as const,
  color: "oklch(55% 0.04 240)",
  marginBottom: 3,
};

const infoValueStyle = {
  fontSize: 16,
  fontWeight: 700,
  color: "oklch(20% 0.07 245)",
};

const STYLES = `
  .contact-layout { display: grid; grid-template-columns: 1.5fr 1fr; gap: 28px; align-items: start; }
  @media (max-width: 880px) { .contact-layout { grid-template-columns: 1fr; } }
  .info-card { transition: transform .18s ease, box-shadow .18s ease; }
  .info-card:hover { transform: translateY(-3px); box-shadow: 0 14px 40px rgba(80,120,200,0.18); }
  .contact-cta-btn { transition: transform .15s ease, box-shadow .15s ease; }
  .contact-cta-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 30px rgba(0,0,0,0.18); }

  .faq-item {
    background: rgba(255,255,255,0.6);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1.5px solid rgba(255,255,255,0.88);
    border-radius: 16px;
    box-shadow: 0 4px 32px rgba(100,140,210,0.10);
    overflow: hidden;
  }
  .faq-summary {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 20px 24px;
    cursor: pointer;
    list-style: none;
    font-size: 17px;
    font-weight: 700;
    color: oklch(18% 0.07 245);
  }
  .faq-summary::-webkit-details-marker { display: none; }
  .faq-chevron {
    flex-shrink: 0;
    font-size: 22px;
    font-weight: 600;
    line-height: 1;
    color: oklch(45% 0.14 ${ACCENT_HUE});
    transition: transform .2s ease;
  }
  .faq-item[open] .faq-chevron { transform: rotate(45deg); }
  .faq-answer {
    margin: 0;
    padding: 0 24px 22px;
    font-size: 15.5px;
    line-height: 1.65;
    color: oklch(40% 0.05 240);
  }
`;
