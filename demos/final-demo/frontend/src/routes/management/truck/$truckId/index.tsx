import { $api } from "@/api/client";
import { useNotification } from "@/components/notification-provider";
import { Separator } from "@/components/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { createFileRoute, redirect } from "@tanstack/react-router";
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
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import YouTube from "react-youtube";

import { z } from "zod";

const truckDetailsSchema = z.object({
  truckId: z.coerce.number().int().gt(0),
});

export const Route = createFileRoute("/management/truck/$truckId/")({
  component: RouteComponent,
  params: { parse: truckDetailsSchema.parse },
  onError(error) {
    if (error?.routerCode === "PARSE_PARAMS") {
      throw redirect({ to: "/management" });
    }
  },
});

function RouteComponent() {
  const { truckId } = Route.useParams();
  const {
    data: truck,
    isSuccess,
    isLoading,
    isError,
  } = $api.useQuery("get", "/trucks/{truckId}", {
    params: { path: { truckId } },
  });
  const [reachStatus, setReachStatus] = useState<boolean>(null!);
  const [queueStatus, setQueueStatus] = useState<boolean>(null!);

  const { reachabilityNotification, queueNotification } = useNotification();

  useEffect(() => {
    if (truck === undefined) return;

    setReachStatus(truck.isReachable);
    setQueueStatus(truck.isQueued);
  }, [truck]);

  useEffect(() => {
    if (
      reachabilityNotification === null ||
      reachabilityNotification.id !== truckId
    )
      return;

    setReachStatus(reachabilityNotification.isReachable);
  }, [reachabilityNotification]);

  useEffect(() => {
    if (queueNotification === null || queueNotification.id !== truckId) return;

    setQueueStatus(queueNotification.isQueued);
  }, [queueNotification]);

  if (isLoading)
    return (
      <div className="grid h-screen place-items-center">
        <div className="space-y-8">
          <LoaderCircle className="text-foreground/60 h-42 w-full animate-spin" />
          <p className="text-foreground/70 text-3xl font-bold">
            Loading details
          </p>
        </div>
      </div>
    );

  if (isError || !isSuccess) {
    return (
      <div className="grid h-screen place-items-center">
        <div className="space-y-8">
          <CircleX className="h-42 w-full text-red-600" />
          <p className="text-foreground/70 text-3xl font-bold">
            Failed to load truck details
          </p>
        </div>
      </div>
    );
  }
  const position = { lat: truck.coords.latitude, lng: truck.coords.longitude };
  return (
    <main className="relative h-screen">
      <section className="absolute top-4 right-0 left-0 z-10 mx-auto w-fit space-y-2 rounded-md border-2 border-black/30 bg-white px-8 py-4 shadow-lg">
        <p className="text-foreground/80 text-center text-xl font-bold">
          TRUCK-{truck.id}
        </p>
        <div className="flex h-8 gap-8">
          <span className="text-foreground/60 flex items-center gap-4 font-semibold">
            <Tooltip>
              <TooltipTrigger>
                <Phone />
              </TooltipTrigger>
              <TooltipContent>Phone Number</TooltipContent>
            </Tooltip>
            {truck.phoneNumber}
          </span>
          <Separator orientation="vertical" />
          <span className="text-foreground/60 flex items-center gap-4 font-semibold">
            <Tooltip>
              <TooltipTrigger>
                {queueStatus ? (
                  <Clock8 className="text-yellow-600" />
                ) : (
                  <Truck className="text-blue-600" />
                )}
              </TooltipTrigger>
              <TooltipContent>
                {queueStatus ? "Waiting" : "Driving "}
              </TooltipContent>
            </Tooltip>
            {queueStatus ? "In queue" : "Driving "}
          </span>
          <Separator orientation="vertical" />
          <span className="text-foreground/60 flex items-center gap-4 font-semibold">
            <Tooltip>
              <TooltipTrigger>
                {reachStatus ? (
                  <Wifi className="text-green-600" />
                ) : (
                  <WifiOff className="text-red-600" />
                )}
              </TooltipTrigger>
              <TooltipContent>
                {reachStatus ? "" : "Not "}Reachable
              </TooltipContent>
            </Tooltip>
            {reachStatus ? "" : "Not "}Reachable
          </span>
        </div>
      </section>
      <div className="grid h-full grid-cols-2">
        <MapContainer center={position} zoom={16} className="z-0 h-full w-full">
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; OpenStreetMap contributors"
          />
          <Marker position={position}>
            <Popup>
              <p className="text-center text-base font-semibold">
                Truck's Location
              </p>
              <p>
                Lat: {truck.coords.latitude}, Lon: {truck.coords.longitude}
              </p>
            </Popup>
          </Marker>
        </MapContainer>
        <YouTube
          className="h-full w-full"
          iframeClassName="h-full w-full"
          videoId="9cxlCvXE9-4"
          opts={{ playerVars: { controls: 0, autoplay: 1, mute: 1 } }}
        />
      </div>
    </main>
  );
}
