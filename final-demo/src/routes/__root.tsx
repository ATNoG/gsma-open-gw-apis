import Devtools from "@/utils/devtools";
import { HeadContent, Outlet, createRootRoute } from "@tanstack/react-router";

export const Route = createRootRoute({
  component: RootComponent,
  head: () => ({
    meta: [
      { title: "Final Demo" },
      {
        name: "description",
        content: "Demo for GSMA Open Gateway APIs",
      },
    ],
    links: [{ rel: "icon", href: "" }],
  }),
  notFoundComponent: () => "404 Not Found",
});

function RootComponent() {
  return (
    <>
      <HeadContent />
      <Outlet />
      <Devtools />
    </>
  );
}
