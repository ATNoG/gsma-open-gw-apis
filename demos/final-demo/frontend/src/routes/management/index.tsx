<<<<<<< HEAD
import { $api } from "@/api/client";
import { useNotification } from "@/components/notification-provider";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { createFileRoute, Link } from "@tanstack/react-router";
import {
  CircleX,
  Clock8,
  LoaderCircle,
  Phone,
  Truck,
  Wifi,
  WifiOff,
} from "lucide-react";
import { useEffect, useState } from "react";
=======
import { createFileRoute } from "@tanstack/react-router";
>>>>>>> 1772d87e (demo: changed directory structure)

export const Route = createFileRoute("/management/")({
  component: RouteComponent,
});

<<<<<<< HEAD
type StatusMemory = Record<number, boolean>;

function RouteComponent() {
  const { data, isSuccess, isLoading, isError } = $api.useQuery(
    "get",
    "/trucks",
  );

  const [reachabilityMemory, setReachabilityMemory] = useState<StatusMemory>(
    {},
  );

  const [queuedMemory, setQueuedMemory] = useState<StatusMemory>({});

  const { reachabilityNotification, queueNotification } = useNotification();

  useEffect(() => {
    if (data === undefined) return;
    for (let truck of data) {
      setReachabilityMemory((rm) => {
        return { ...rm, [truck.id]: truck.isReachable };
      });

      setQueuedMemory((qm) => {
        return { ...qm, [truck.id]: truck.isQueued };
      });
    }
  }, [data]);

  useEffect(() => {
    if (reachabilityNotification === null) return;

    setReachabilityMemory((rm) => {
      return {
        ...rm,
        [reachabilityNotification.id]: reachabilityNotification.isReachable,
      };
    });
  }, [reachabilityNotification]);

  useEffect(() => {
    if (queueNotification === null) return;

    setQueuedMemory((qm) => {
      return {
        ...qm,
        [queueNotification.id]: queueNotification.isQueued,
      };
    });
  }, [queueNotification]);

  return (
    <main className="container mx-auto my-20 px-4">
      <h1 className="mb-12 text-center text-3xl font-bold">Fleet Management</h1>
      <p className="text-foreground/80 mb-2 text-xl font-semibold">Trucks:</p>
      {isSuccess && (
        <ul className="grid grid-cols-[auto_auto_1fr_auto_auto] divide-y-2 border-2">
          {data.map((truck) => {
            const isReachable = reachabilityMemory[truck.id];
            const isQueued = queuedMemory[truck.id];
            return (
              <li
                key={truck.id}
                className="col-span-full grid grid-cols-subgrid px-4 py-2 even:bg-black/5"
              >
                <Link
                  className="col-span-full grid grid-cols-subgrid items-center gap-16"
                  to="/management/truck/$truckId"
                  params={{ truckId: truck.id }}
                >
                  <span className="text-foreground/70 font-bold">
                    TRUCK-{truck.id}
                  </span>
                  <span className="text-foreground/60 flex gap-4 font-semibold">
                    <Tooltip>
                      <TooltipTrigger>
                        <Phone />
                      </TooltipTrigger>
                      <TooltipContent>Phone Number</TooltipContent>
                    </Tooltip>
                    {truck.phoneNumber}
                  </span>
                  <div />
                  <span className="text-foreground/60 flex items-center gap-4 font-semibold">
                    <Tooltip>
                      <TooltipTrigger>
                        {isQueued ? (
                          <Clock8 className="text-yellow-600" />
                        ) : (
                          <Truck className="text-blue-600" />
                        )}
                      </TooltipTrigger>
                      <TooltipContent>
                        {isQueued ? "In queue" : "Driving "}
                      </TooltipContent>
                    </Tooltip>
                    {isQueued ? "In queue" : "Driving "}
                  </span>
                  <span className="text-foreground/60 flex items-center gap-4 font-semibold">
                    <Tooltip>
                      <TooltipTrigger>
                        {isReachable ? (
                          <Wifi className="text-green-600" />
                        ) : (
                          <WifiOff className="text-red-600" />
                        )}
                      </TooltipTrigger>
                      <TooltipContent>
                        {isReachable ? "" : "Not "}Reachable
                      </TooltipContent>
                    </Tooltip>
                    {isReachable ? "" : "Not "}Reachable
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
      {isLoading && (
        <>
          <LoaderCircle className="text-foreground/60 h-40 w-full animate-spin" />
          <p className="text-foreground/70 text-center text-3xl font-bold">
            Loading
          </p>
        </>
      )}
      {isError && (
        <>
          <CircleX className="h-40 w-full text-red-600/90" />
          <p className="text-foreground/70 text-center text-3xl font-bold">
            Failed to load trucks
          </p>
        </>
      )}
    </main>
  );
=======
function RouteComponent() {
  return <div>Truck list</div>;
>>>>>>> 1772d87e (demo: changed directory structure)
}
