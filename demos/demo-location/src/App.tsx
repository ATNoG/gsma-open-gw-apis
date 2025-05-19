import { cn } from "@/lib/utils";
import { parseISO } from "date-fns";
import {
  ArrowDownRight,
  CircleCheckBig,
  CircleX,
  LoaderCircle,
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  Circle,
  MapContainer,
  Marker,
  TileLayer,
  Tooltip,
} from "react-leaflet";
import { Button } from "./components/ui/button";
import { components } from "./lib/api";
import { $api } from "./lib/fetch-client";
import { socket } from "./lib/ws-client";
type CloudEvent = {
  id: string;
  source: string;
  type:
    | "org.camaraproject.geofencing-subscriptions.v0.area-entered"
    | "org.camaraproject.geofencing-subscriptions.v0.area-left"
    | "org.camaraproject.geofencing-subscriptions.v0.subscription-ends";
  specversion?: "1.0";
  datacontenttype?: "application/json";
  data: {
    device?: {
      phoneNumber?: string;
      networkAccessIdentifier?: string;
      ipv4Address?: string;
      ipv6Address?: string;
    };
    area: {
      areaType: "CIRCLE";
      center: {
        lat: number;
        lon: number;
      };
      radius: number; // 1 ≤ radius ≤ 200000
    };
    subscriptionId: string;
  };
  time: string; // RFC 3339 timestamp (e.g. "2018-04-05T17:31:00Z")
};

const req: components["schemas"]["SubscriptionRequest"] = {
  protocol: "HTTP",
  sink: "http://localhost:5000/webhook",
  types: ["org.camaraproject.geofencing-subscriptions.v0.area-entered"],
  config: {
    subscriptionExpireTime: "2026-01-17T13:18:23.682Z",
    subscriptionDetail: {
      area: {
        areaType: "CIRCLE",
        center: { latitude: 40.633189926609525, longitude: -8.659489441414976 },
        radius: 75,
      },
      device: {
        phoneNumber: "+2020100000001",
      },
    },
  },
};

const verifyReq: components["schemas"]["VerifyLocationRequest"] = {
  area: {
    areaType: "CIRCLE",
    center: { latitude: 40.633189926609525, longitude: -8.659489441414976 },
    radius: 75,
  },
  device: {
    phoneNumber: "+2020100000001",
  },
};

function App() {
  const [notifs, setNotifs] = useState<CloudEvent[]>([]);

  const { mutate } = $api.useMutation(
    "post",
    "/geofencing-subscriptions/v0.4/subscriptions",
  );

  const { data } = $api.useQuery(
    "post",
    "/location-retrieval/v0.4/retrieve",
    {
      body: {
        device: req.config.subscriptionDetail.device,
        maxAge: 0,
        maxSurface: 100,
      },
    },
    { refetchInterval: 500 },
  );

  const {
    mutate: verifyLocationMutation,
    isPending,
    data: verifyLocationData,
  } = $api.useMutation("post", "/location-verification/v2/verify");

  const handleMessage = (data: CloudEvent) => {
    setNotifs((notifs) => [data, ...notifs]);
  };
  useEffect(() => {
    socket.on("data", handleMessage);
    return () => {
      socket.off("data", handleMessage);
    };
  }, []);

  const verifyLocation = () => {
    verifyLocationMutation({ body: verifyReq });
  };

  const startGeofencing = () => {
    mutate({ body: req });
  };

  return (
    <main className="container mx-auto my-20 space-y-6">
      <h1 className="text-center text-4xl font-bold">
        Drone Monitoring System
      </h1>

      <Button onClick={startGeofencing}>Start Geofencing</Button>
      <span className="mx-4 space-x-4">
        <Button type="submit" disabled={isPending} onClick={verifyLocation}>
          Verify Area
        </Button>
        <span className="relative">
          <CircleCheckBig
            className={cn("inline-block text-green-600", {
              "opacity-0":
                verifyLocationData === undefined ||
                isPending ||
                verifyLocationData?.verificationResult === "FALSE",
            })}
          />
          <LoaderCircle
            className={cn("absolute inset-0", {
              "opacity-0": !isPending,
            })}
          />
          <CircleX
            className={cn("absolute inset-0 text-red-600", {
              "opacity-0":
                verifyLocationData === undefined ||
                isPending ||
                verifyLocationData.verificationResult === "TRUE",
            })}
          />
        </span>
      </span>
      <div className="h-[516px] overflow-hidden rounded-md border-2 border-black">
        <MapContainer
          center={[
            req.config.subscriptionDetail.area.center.latitude,
            req.config.subscriptionDetail.area.center.longitude,
          ]}
          zoom={18}
          scrollWheelZoom={true}
          className="h-full w-full"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Marker
            position={[
              req.config.subscriptionDetail.area.center.latitude,
              req.config.subscriptionDetail.area.center.longitude,
            ]}
          >
            <Tooltip>DETI</Tooltip>
          </Marker>
          <Circle
            center={[
              req.config.subscriptionDetail.area.center.latitude,
              req.config.subscriptionDetail.area.center.longitude,
            ]}
            radius={req.config.subscriptionDetail.area.radius}
          ></Circle>
          {data?.area.areaType === "CIRCLE" && (
            <Circle
              center={[
                (data.area as components["schemas"]["Circle-Output"]).center
                  .latitude,
                (data.area as components["schemas"]["Circle-Output"]).center
                  .longitude,
              ]}
              radius={2}
              fillOpacity={1}
              color="red"
            ></Circle>
          )}
        </MapContainer>
      </div>
      <h2 className="text-xl font-bold">Last drone enter zone:</h2>
      <ul className="divide-y">
        {notifs.length === 0
          ? "No data"
          : notifs.map((notif) => (
              <li className="flex space-x-4 py-2" key={notif.time}>
                <span className="text-lg font-semibold">
                  {parseISO(notif.time).toUTCString()}
                </span>
                <ArrowDownRight className="ml-auto inline-block text-green-600" />
                <span className="text-foreground/70 font-semibold">
                  Area entered
                </span>
              </li>
            ))}
      </ul>
    </main>
  );
}

export default App;
