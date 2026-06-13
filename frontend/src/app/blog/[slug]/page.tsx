import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import {
  ACCENT_HUE,
  CoverArt,
  DotGrid,
  GlassCard,
} from "@/components/blog/BlogVisuals";
import { MarkdownContent } from "@/components/blog/MarkdownContent";
import { LandingFooter } from "@/components/layout/LandingFooter";
import { LandingNavbar } from "@/components/layout/LandingNavbar";
import {
  absolutizeMediaUrl,
  fetchPostBySlug,
  fetchRelatedPosts,
  formatBlogDate,
  type BlogPostListItem,
} from "@/lib/blog-api";

type PageProps = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const post = await fetchPostBySlug(slug);
  if (!post) {
    return { title: "Article not found — LingosAI" };
  }
  const description =
    post.excerpt ?? `${post.title} — from the LingosAI blog.`;
  const cover = absolutizeMediaUrl(post.cover_image_url);
  return {
    title: `${post.title} — LingosAI`,
    description,
    openGraph: {
      title: post.title,
      description,
      type: "article",
      publishedTime: post.published_at ?? undefined,
      images: cover ? [{ url: cover }] : undefined,
    },
  };
}

export default async function BlogPostPage({ params }: PageProps) {
  const { slug } = await params;
  const post = await fetchPostBySlug(slug);
  if (!post) notFound();

  const related = await fetchRelatedPosts(slug);
  const cover = absolutizeMediaUrl(post.cover_image_url);

  return (
    <main
      style={{
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        minHeight: "100svh",
        background: `radial-gradient(circle at top right, oklch(92% 0.04 ${ACCENT_HUE}) 0%, oklch(96% 0.015 ${
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

      <article style={{ maxWidth: 820, margin: "0 auto", padding: "40px 24px 0" }}>
        <Link href="/blog" style={backLinkStyle}>
          <span aria-hidden>←</span> All articles
        </Link>

        <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", marginTop: 22 }}>
          <span style={categoryPillStyle}>{post.category ?? "Article"}</span>
          <span style={dateStyle}>{formatBlogDate(post.published_at)}</span>
        </div>

        <h1
          style={{
            fontSize: "clamp(30px, 4vw, 46px)",
            fontWeight: 800,
            color: "oklch(15% 0.09 245)",
            lineHeight: 1.15,
            letterSpacing: "-0.8px",
            margin: "18px 0 16px",
          }}
        >
          {post.title}
        </h1>

        <div style={authorRowStyle}>
          <span style={avatarStyle} aria-hidden>
            {post.author_name.slice(0, 1).toUpperCase()}
          </span>
          <span style={{ fontWeight: 600, color: "oklch(30% 0.05 240)" }}>
            By {post.author_name}
          </span>
        </div>

        <div style={{ position: "relative", width: "100%", height: 380, marginTop: 28, marginBottom: 40, borderRadius: 20, overflow: "hidden", boxShadow: "0 12px 40px rgba(80,120,200,0.15)" }}>
          <CoverArt src={cover} alt={post.title} radius={20} />
        </div>

        <div style={{ marginBottom: 56 }}>
          <MarkdownContent>{post.content}</MarkdownContent>
        </div>
      </article>

      {/* RELATED */}
      {related.length > 0 && (
        <section style={{ padding: "0 40px 90px" }}>
          <div style={{ maxWidth: 1180, margin: "0 auto" }}>
            <h2 style={sectionHeadingStyle}>Related articles</h2>
            <div className="blog-grid">
              {related.map((item) => (
                <RelatedCard key={item.id} post={item} />
              ))}
            </div>
          </div>
        </section>
      )}

      {/* CTA */}
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
            <Link href="/register" className="blog-btn" style={ctaBtnStyle}>
              Start Learning Today
            </Link>
          </div>
        </div>
      </section>

      <LandingFooter />
    </main>
  );
}

function RelatedCard({ post }: { post: BlogPostListItem }) {
  return (
    <Link href={`/blog/${post.slug}`} style={{ textDecoration: "none", color: "inherit", display: "block" }}>
      <GlassCard className="blog-card" style={{ padding: 0, overflow: "hidden", height: "100%", display: "flex", flexDirection: "column" }}>
        <div style={{ position: "relative", height: 170 }}>
          <CoverArt src={absolutizeMediaUrl(post.cover_image_url)} alt={post.title} radius={0} />
        </div>
        <div style={{ padding: 22 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
            <span style={categoryPillStyle}>{post.category ?? "Article"}</span>
            <span style={dateStyle}>{formatBlogDate(post.published_at)}</span>
          </div>
          <h3 style={{ fontSize: 18, fontWeight: 700, color: "oklch(18% 0.07 245)", lineHeight: 1.3, margin: "12px 0 0" }}>
            {post.title}
          </h3>
        </div>
      </GlassCard>
    </Link>
  );
}

// ── shared inline styles ────────────────────────────────────────────────────
const backLinkStyle = {
  display: "inline-flex",
  alignItems: "center",
  gap: 7,
  color: `oklch(40% 0.12 ${ACCENT_HUE})`,
  fontWeight: 600,
  fontSize: 14,
  textDecoration: "none",
};

const categoryPillStyle = {
  padding: "4px 12px",
  borderRadius: 50,
  background: `oklch(95% 0.05 ${ACCENT_HUE})`,
  color: `oklch(38% 0.14 ${ACCENT_HUE})`,
  fontSize: 12,
  fontWeight: 700,
};

const dateStyle = {
  fontSize: 13,
  fontWeight: 600,
  color: "oklch(55% 0.04 240)",
};

const authorRowStyle = {
  display: "flex",
  alignItems: "center",
  gap: 11,
  marginTop: 6,
};

const avatarStyle = {
  width: 36,
  height: 36,
  borderRadius: "50%",
  display: "grid",
  placeItems: "center",
  background: `oklch(45% 0.16 ${ACCENT_HUE})`,
  color: "white",
  fontWeight: 800,
  fontSize: 15,
};

const sectionHeadingStyle = {
  fontSize: 24,
  fontWeight: 800,
  color: "oklch(18% 0.07 245)",
  letterSpacing: "-0.3px",
  margin: "0 0 24px",
};

const ctaBtnStyle = {
  display: "inline-block",
  padding: "15px 34px",
  borderRadius: 50,
  background: "white",
  color: "oklch(25% 0.1 240)",
  fontSize: 16,
  fontWeight: 700,
  textDecoration: "none",
  boxShadow: "0 8px 24px rgba(10,20,60,0.25)",
};

const STYLES = `
  .blog-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 26px; }
  .blog-card { transition: transform .18s ease, box-shadow .18s ease; }
  .blog-card:hover { transform: translateY(-4px); box-shadow: 0 14px 44px rgba(80,120,200,0.20); }
  .blog-btn { transition: transform .15s ease, box-shadow .15s ease; }
  .blog-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 30px rgba(10,20,60,0.32); }
`;
