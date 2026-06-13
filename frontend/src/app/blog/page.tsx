import type { Metadata } from "next";
import Link from "next/link";

import {
  ACCENT_HUE,
  CoverArt,
  DotGrid,
  GlassCard,
} from "@/components/blog/BlogVisuals";
import { LandingFooter } from "@/components/layout/LandingFooter";
import { LandingNavbar } from "@/components/layout/LandingNavbar";
import { MarketingCTALink } from "@/components/marketing/MarketingCTALink";
import {
  absolutizeMediaUrl,
  fetchPublishedPosts,
  formatBlogDate,
  type BlogPostListItem,
} from "@/lib/blog-api";

export const metadata: Metadata = {
  title: "Blog — Learn English Smarter with AI | LingosAI",
  description:
    "Insights, communication tips, learning strategies, and updates from the LingosAI team.",
  openGraph: {
    title: "Learn English Smarter with AI",
    description:
      "Insights, communication tips, learning strategies, and updates from the LingosAI team.",
    type: "website",
  },
};

export default async function BlogIndexPage() {
  const posts = await fetchPublishedPosts();
  const [featured, ...rest] = posts;

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
        style={{
          position: "relative",
          padding: "70px 40px 60px",
          textAlign: "center",
          maxWidth: 920,
          margin: "0 auto",
        }}
      >
        <span style={eyebrowStyle}>The LingosAI Blog</span>
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
          Learn English Smarter with AI
        </h1>
        <p
          style={{
            fontSize: 20,
            color: "oklch(40% 0.05 240)",
            lineHeight: 1.6,
            maxWidth: 680,
            margin: "0 auto 36px",
          }}
        >
          Insights, communication tips, learning strategies, and updates from the
          LingosAI team.
        </p>
        <div style={{ display: "flex", justifyContent: "center", gap: 14, flexWrap: "wrap" }}>
          <MarketingCTALink anonLabel="Start Learning" className="blog-btn" style={primaryBtnStyle} />
          <Link href="/pricing" className="blog-btn" style={secondaryBtnStyle}>
            View Pricing
          </Link>
        </div>
      </section>

      {/* CONTENT */}
      <section style={{ padding: "20px 40px 100px" }}>
        <div style={{ maxWidth: 1180, margin: "0 auto" }}>
          {posts.length === 0 ? (
            <GlassCard style={{ padding: 48, textAlign: "center" }}>
              <p style={{ fontSize: 18, color: "oklch(40% 0.05 240)", margin: 0 }}>
                No articles published yet. Check back soon.
              </p>
            </GlassCard>
          ) : (
            <>
              {featured && <FeaturedCard post={featured} />}

              {rest.length > 0 && (
                <>
                  <h2 style={sectionHeadingStyle}>Latest articles</h2>
                  <div className="blog-grid">
                    {rest.map((post) => (
                      <PostCard key={post.id} post={post} />
                    ))}
                  </div>
                </>
              )}
            </>
          )}
        </div>
      </section>

      {/* CTA */}
      <CtaSection />

      <LandingFooter />
    </main>
  );
}

function FeaturedCard({ post }: { post: BlogPostListItem }) {
  return (
    <Link href={`/blog/${post.slug}`} style={{ textDecoration: "none", color: "inherit", display: "block", marginBottom: 56 }}>
      <GlassCard className="blog-card blog-featured" style={{ padding: 0 }}>
        <div style={{ position: "relative", minHeight: 320 }}>
          <CoverArt src={absolutizeMediaUrl(post.cover_image_url)} alt={post.title} radius={0} />
        </div>
        <div style={{ padding: "40px 44px", display: "flex", flexDirection: "column", justifyContent: "center" }}>
          <div style={metaRowStyle}>
            <span style={categoryPillStyle}>{post.category ?? "Article"}</span>
            <span style={dateStyle}>{formatBlogDate(post.published_at)}</span>
          </div>
          <h2 style={{ fontSize: 30, fontWeight: 800, color: "oklch(15% 0.09 245)", lineHeight: 1.18, margin: "16px 0 14px" }}>
            {post.title}
          </h2>
          {post.excerpt && (
            <p style={{ fontSize: 17, lineHeight: 1.65, color: "oklch(40% 0.05 240)", margin: "0 0 22px" }}>
              {post.excerpt}
            </p>
          )}
          <span className="blog-readmore" style={readMoreStyle}>
            Read More <span aria-hidden>→</span>
          </span>
        </div>
      </GlassCard>
    </Link>
  );
}

function PostCard({ post }: { post: BlogPostListItem }) {
  return (
    <Link href={`/blog/${post.slug}`} style={{ textDecoration: "none", color: "inherit", display: "block" }}>
      <GlassCard className="blog-card" style={{ padding: 0, overflow: "hidden", height: "100%", display: "flex", flexDirection: "column" }}>
        <div style={{ position: "relative", height: 200 }}>
          <CoverArt src={absolutizeMediaUrl(post.cover_image_url)} alt={post.title} radius={0} />
        </div>
        <div style={{ padding: 24, display: "flex", flexDirection: "column", flex: 1 }}>
          <div style={metaRowStyle}>
            <span style={categoryPillStyle}>{post.category ?? "Article"}</span>
            <span style={dateStyle}>{formatBlogDate(post.published_at)}</span>
          </div>
          <h3 style={{ fontSize: 20, fontWeight: 700, color: "oklch(18% 0.07 245)", lineHeight: 1.3, margin: "14px 0 10px" }}>
            {post.title}
          </h3>
          {post.excerpt && (
            <p style={{ fontSize: 15, lineHeight: 1.6, color: "oklch(45% 0.05 240)", margin: "0 0 18px", flex: 1 }}>
              {post.excerpt}
            </p>
          )}
          <span className="blog-readmore" style={{ ...readMoreStyle, fontSize: 14 }}>
            Read More <span aria-hidden>→</span>
          </span>
        </div>
      </GlassCard>
    </Link>
  );
}

function CtaSection() {
  return (
    <section style={{ padding: "0 40px 110px" }}>
      <div
        style={{
          maxWidth: 1180,
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
          <h2 style={{ fontSize: "clamp(28px, 3.5vw, 40px)", fontWeight: 800, margin: "0 0 28px", letterSpacing: "-0.5px" }}>
            Ready to improve your English with personalized feedback?
          </h2>
          <MarketingCTALink
            anonLabel="Start Learning Today"
            className="blog-btn"
            style={{ ...primaryBtnStyle, background: "white", color: "oklch(25% 0.1 240)" }}
          />
        </div>
      </div>
    </section>
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

const primaryBtnStyle = {
  display: "inline-block",
  padding: "15px 34px",
  borderRadius: 50,
  background: `oklch(20% 0.09 ${ACCENT_HUE})`,
  color: "white",
  fontSize: 16,
  fontWeight: 700,
  textDecoration: "none",
  boxShadow: "0 8px 24px rgba(20,50,120,0.2)",
};

const secondaryBtnStyle = {
  display: "inline-block",
  padding: "15px 34px",
  borderRadius: 50,
  border: "2px solid rgba(100,140,220,0.35)",
  background: "transparent",
  color: `oklch(25% 0.1 ${ACCENT_HUE})`,
  fontSize: 16,
  fontWeight: 700,
  textDecoration: "none",
};

const sectionHeadingStyle = {
  fontSize: 24,
  fontWeight: 800,
  color: "oklch(18% 0.07 245)",
  letterSpacing: "-0.3px",
  margin: "0 0 24px",
};

const metaRowStyle = {
  display: "flex",
  alignItems: "center",
  gap: 12,
  flexWrap: "wrap" as const,
};

const categoryPillStyle = {
  padding: "4px 12px",
  borderRadius: 50,
  background: `oklch(95% 0.05 ${ACCENT_HUE})`,
  color: `oklch(38% 0.14 ${ACCENT_HUE})`,
  fontSize: 12,
  fontWeight: 700,
  letterSpacing: "0.02em",
};

const dateStyle = {
  fontSize: 13,
  fontWeight: 600,
  color: "oklch(55% 0.04 240)",
};

const readMoreStyle = {
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  color: `oklch(40% 0.14 ${ACCENT_HUE})`,
  fontWeight: 700,
  fontSize: 15,
};

const STYLES = `
  .blog-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 28px; }
  .blog-featured { display: grid; grid-template-columns: 1.05fr 1fr; }
  @media (max-width: 860px) { .blog-featured { grid-template-columns: 1fr; } }
  .blog-card { transition: transform .18s ease, box-shadow .18s ease; }
  .blog-card:hover { transform: translateY(-4px); box-shadow: 0 14px 44px rgba(80,120,200,0.20); }
  .blog-btn { transition: transform .15s ease, box-shadow .15s ease; }
  .blog-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 30px rgba(20,50,120,0.28); }
  .blog-readmore { transition: gap .15s ease; }
  .blog-card:hover .blog-readmore { gap: 11px; }
`;
