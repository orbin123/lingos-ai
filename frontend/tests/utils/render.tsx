import { type ReactElement, type ReactNode } from "react";
import {
  render,
  renderHook,
  type RenderOptions,
  type RenderHookOptions,
} from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

/**
 * A QueryClient tuned for tests:
 * - `retry: false` on BOTH queries and mutations — without it a mocked 4xx/5xx
 *   retries with backoff and blows the test timeout instead of surfacing the
 *   error immediately. (Several hooks set query-level retry:false already, but
 *   the mutations — useSubmitResponse/useDiagnosis/useSubmitActivity — do not.)
 * - `gcTime: 0` + a fresh client per render → no cache bleed between tests
 *   (the session hooks call setQueryData/invalidateQueries).
 */
export function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
        refetchOnWindowFocus: false,
      },
      mutations: { retry: false },
    },
  });
}

interface ProviderOptions extends Omit<RenderOptions, "wrapper"> {
  queryClient?: QueryClient;
}

export function createQueryWrapper(queryClient: QueryClient = createTestQueryClient()) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

/** Render a component inside a fresh QueryClientProvider. Returns the client too. */
export function renderWithProviders(
  ui: ReactElement,
  { queryClient = createTestQueryClient(), ...options }: ProviderOptions = {},
) {
  return {
    queryClient,
    ...render(ui, { wrapper: createQueryWrapper(queryClient), ...options }),
  };
}

/** renderHook variant wrapped in a fresh QueryClientProvider (for TanStack Query hooks). */
export function renderHookWithProviders<TResult, TProps>(
  cb: (props: TProps) => TResult,
  {
    queryClient = createTestQueryClient(),
    ...options
  }: Omit<RenderHookOptions<TProps>, "wrapper"> & { queryClient?: QueryClient } = {},
) {
  return {
    queryClient,
    ...renderHook(cb, { wrapper: createQueryWrapper(queryClient), ...options }),
  };
}
