import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <main className="container mx-auto my-20 px-4">
      <h1 className="mb-2 text-center text-6xl font-extrabold">Final Demo</h1>
      <p className="text-foreground/65 mb-12 text-center text-lg font-semibold">
        Demo websites for the final presentation
      </p>
      <p className="mb-4 text-3xl font-bold">Available pages:</p>
      <ul className="grid grid-cols-[auto_auto_1fr] divide-y-1 text-lg">
        <li className="text-foreground/70 col-span-3 grid grid-cols-subgrid items-center pb-2">
          <Link
            className={cn(
              buttonVariants({ size: "lg" }),
              "mr-4 text-xl font-semibold",
            )}
            to="/infotainment"
          >
            Infotainment
          </Link>
          -
          <span className="ml-4">
            Website for the video streaming service inside the truck
          </span>
        </li>
        <li className="text-foreground/70 col-span-3 grid grid-cols-subgrid items-center pt-2">
          <Link
            className={cn(
              buttonVariants({ size: "lg" }),
              "mr-4 text-xl font-semibold",
            )}
            to="/management"
          >
            Fleet Management
          </Link>
          -
          <span className="ml-4">
            Website for managemant of the truck fleet
          </span>
        </li>
      </ul>
    </main>
  );
}
