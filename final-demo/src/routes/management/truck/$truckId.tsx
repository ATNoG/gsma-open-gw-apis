import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/management/truck/$truckId")({
  component: RouteComponent,
});

function RouteComponent() {
  return <div>Truck</div>;
}
