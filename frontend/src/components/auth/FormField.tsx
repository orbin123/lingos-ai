"use client";

import { forwardRef, InputHTMLAttributes, useState, useEffect, useRef } from "react";
import { Eye, EyeOff } from "lucide-react";

interface FormFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  hint?: string;
  rightSlot?: React.ReactNode;
}

export const FormField = forwardRef<HTMLInputElement, FormFieldProps>(
  function FormField({ label, error, hint, rightSlot, id, type, ...rest }, ref) {
    const fieldId =
      id || `field-${label.toLowerCase().replace(/\s+/g, "-")}`;

    const isPasswordType = type === "password";
    const [showPassword, setShowPassword] = useState(false);
    const timeoutRef = useRef<NodeJS.Timeout | null>(null);

    const togglePasswordVisibility = () => {
      if (showPassword) {
        setShowPassword(false);
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
          timeoutRef.current = null;
        }
      } else {
        setShowPassword(true);
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }
        // Auto-hide after 3 seconds
        timeoutRef.current = setTimeout(() => {
          setShowPassword(false);
          timeoutRef.current = null;
        }, 3000);
      }
    };

    // Clean up timeout on unmount
    useEffect(() => {
      return () => {
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }
      };
    }, []);

    return (
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1.5">
          <label
            htmlFor={fieldId}
            className="text-[13px] font-semibold"
            style={{ color: "oklch(25% 0.08 245)" }}
          >
            {label}
          </label>
          {rightSlot}
        </div>

        <div className="relative">
          <input
            ref={ref}
            id={fieldId}
            aria-invalid={!!error}
            aria-describedby={
              error ? `${fieldId}-error` : hint ? `${fieldId}-hint` : undefined
            }
            className={[
              "w-full rounded-lg pl-3.5 py-2 text-[14.5px] bg-white",
              "transition-all outline-none",
              "placeholder:text-slate-400",
              isPasswordType ? "pr-10" : "pr-3.5",
              error
                ? "border-2 border-red-400 focus:border-red-500 focus:ring-2 focus:ring-red-200"
                : "border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200/60",
            ].join(" ")}
            style={{ color: "oklch(18% 0.09 245)" }}
            type={isPasswordType && showPassword ? "text" : type}
            {...rest}
          />
          {isPasswordType && (
            <button
              type="button"
              onClick={togglePasswordVisibility}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-500 transition-colors focus:outline-none cursor-pointer"
              title={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          )}
        </div>

        {error ? (
          <p
            id={`${fieldId}-error`}
            className="mt-1.5 text-[12.5px] font-medium text-red-600"
          >
            {error}
          </p>
        ) : hint ? (
          <p
            id={`${fieldId}-hint`}
            className="mt-1.5 text-[12.5px]"
            style={{ color: "oklch(50% 0.06 240)" }}
          >
            {hint}
          </p>
        ) : null}
      </div>
    );
  }
);
