"use client";

import React from "react";

interface LogoProps {
  variant?: "brand" | "avatar";
  size?: number;
  borderRadius?: number;
  className?: string;
  style?: React.CSSProperties;
}

export function Logo({ variant = "brand", size = 32, borderRadius: customBorderRadius, className, style }: LogoProps) {
  const borderRadius = customBorderRadius ?? Math.round(size * 0.25);
  const iconSize = Math.round(size * 0.55);

  if (variant === "avatar") {
    return (
      <div
        className={className}
        style={{
          width: size,
          height: size,
          borderRadius: borderRadius,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "oklch(52% 0.18 240)",
          ...style,
        }}
      >
        <svg width={iconSize} height={iconSize} viewBox="0 0 17 17" fill="none">
          <path
            d="M3 13L8.5 4L14 13"
            stroke="white"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M5.2 10h6.6"
            stroke="white"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
        </svg>
      </div>
    );
  }

  // BRAND LOGO (Winged Helmet)
  return (
    <div
      className={className}
      style={{
        width: size,
        height: size,
        borderRadius: borderRadius,
        overflow: "hidden",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        ...style,
      }}
    >
      <img
        src="/lingosai_logo.png"
        alt="LingosAI Logo"
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
        }}
      />
    </div>
  );
}
