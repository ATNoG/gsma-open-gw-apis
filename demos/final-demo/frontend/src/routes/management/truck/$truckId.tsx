import { createFileRoute, redirect } from "@tanstack/react-router";
import { z } from "zod";

const truckDetailsSchema = z.object({
  truckId: z.coerce.number().int().gt(0),
});

export const Route = createFileRoute("/management/truck/$truckId")({
  component: RouteComponent,
  params: { parse: truckDetailsSchema.parse },
  onError(error) {
    if (error?.routerCode === "PARSE_PARAMS") {
      throw redirect({ to: "/management" });
    }
  },
});

function RouteComponent() {
  return <div>Truck</div>;
}
