import { StackClientApp } from "@stackframe/react";

export const stackApp = new StackClientApp({
  publishableClientKey: import.meta.env.VITE_STACK_PUBLISHABLE_CLIENT_KEY,
  projectId: import.meta.env.VITE_STACK_PROJECT_ID,
  tokenStore: "cookie",
  handlerUrl: "http://localhost:5173/handler",
});
