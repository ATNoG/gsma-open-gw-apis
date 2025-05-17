import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/infotainment/$videoId/")({
  component: RouteComponent,
});

function RouteComponent() {
  return <div>Video</div>;
}
