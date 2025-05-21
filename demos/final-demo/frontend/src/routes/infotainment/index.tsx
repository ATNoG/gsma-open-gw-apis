import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/infotainment/")({
  component: RouteComponent,
});

function RouteComponent() {
  return <div>List of videos</div>;
}
