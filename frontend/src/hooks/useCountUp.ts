import { useEffect, useRef, useState } from "react";

/**
 * Animates a numeric value counting up from 0 to `target` over `duration` ms
 * on mount (and whenever `target` changes). Respects prefers-reduced-motion —
 * jumps straight to the target instead of animating.
 */
export function useCountUp(target: number, duration = 800): number {
  const [value, setValue] = useState(0);
  const frameRef = useRef<number | undefined>(undefined);

  useEffect(() => {
    const reduceMotion =
      typeof window !== "undefined" &&
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

    if (reduceMotion || !Number.isFinite(target)) {
      setValue(target);
      return;
    }

    const start = performance.now();
    const from = 0;

    const tick = (now: number) => {
      const elapsed = now - start;
      const t = Math.min(1, elapsed / duration);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - t, 3);
      setValue(from + (target - from) * eased);
      if (t < 1) {
        frameRef.current = requestAnimationFrame(tick);
      } else {
        setValue(target);
      }
    };

    frameRef.current = requestAnimationFrame(tick);
    return () => {
      if (frameRef.current) cancelAnimationFrame(frameRef.current);
    };
  }, [target, duration]);

  return value;
}
