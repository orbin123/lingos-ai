// Presentational blog building blocks. No "use client" — these are pure
// markup and render inside React Server Components. Visual language copied
// verbatim from the marketing pages (src/app/about/page.tsx) so the blog
// feels like the same product.

import type { CSSProperties, ReactNode } from "react";

export const ACCENT_HUE = 240;

export function GlassCard({
  children,
  style,
  className,
}: {
  children: ReactNode;
  style?: CSSProperties;
  className?: string;
}) {
  return (
    <div
      className={className}
      style={{
        background: "rgba(255,255,255,0.6)",
        backdropFilter: "blur(18px)",
        WebkitBackdropFilter: "blur(18px)",
        border: "1.5px solid rgba(255,255,255,0.88)",
        borderRadius: 20,
        boxShadow:
          "0 4px 32px rgba(100,140,210,0.13), 0 1.5px 6px rgba(80,120,200,0.07)",
        ...style,
      }}
    >
      {children}
    </div>
  );
}

export function DotGrid({ opacity = 0.18 }: { opacity?: number }) {
  return (
    <svg
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
      }}
      aria-hidden
    >
      <defs>
        <pattern
          id="blog-dots"
          x="0"
          y="0"
          width="22"
          height="22"
          patternUnits="userSpaceOnUse"
        >
          <circle cx="2" cy="2" r="1.1" fill={`rgba(90,130,210,${opacity})`} />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#blog-dots)" />
    </svg>
  );
}

/** Cover image, or a branded gradient placeholder when none is set. */
export function CoverArt({
  src,
  alt,
  style,
  radius = 16,
}: {
  src: string | null;
  alt: string;
  style?: CSSProperties;
  radius?: number;
}) {
  if (src) {
    return (
      // eslint-disable-next-line @next/next/no-img-element -- backend media is
      // cross-origin and next/image remote patterns aren't configured.
      <img
        src={src}
        alt={alt}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          display: "block",
          borderRadius: radius,
          ...style,
        }}
      />
    );
  }
  return (
    <div
      aria-hidden
      style={{
        width: "100%",
        height: "100%",
        position: "relative",
        overflow: "hidden",
        borderRadius: radius,
        background: `linear-gradient(135deg, oklch(72% 0.12 ${ACCENT_HUE}) 0%, oklch(55% 0.16 ${
          ACCENT_HUE + 18
        }) 100%)`,
        ...style,
      }}
    >
      <DotGrid opacity={0.25} />
    </div>
  );
}
