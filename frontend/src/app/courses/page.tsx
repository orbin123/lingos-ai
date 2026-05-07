"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * /courses is no longer used.
 * All plan selection now happens on /pricing.
 * This file exists only to catch any stale links.
 */
export default function CoursesRedirectPage() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/pricing");
  }, [router]);
  return null;
}
