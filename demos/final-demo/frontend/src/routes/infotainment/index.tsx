import { createFileRoute, redirect } from "@tanstack/react-router";
import { userStore } from "../infotainment";

export const Route = createFileRoute("/infotainment/")({
  component: RouteComponent,
  beforeLoad() {
    const user = userStore.state;
    if (user === null) {
      throw redirect({ to: "/infotainment/login" });
    }
  },
});

function RouteComponent() {
  return <div>List of videos</div>;
}
