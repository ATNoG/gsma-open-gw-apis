import { parseISO } from "date-fns";
import { ArrowDownRight } from "lucide-react";
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
    device: {
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
    subscriptionMaxEvents: 5,
    subscriptionExpireTime: "2026-01-17T13:18:23.682Z",
    subscriptionDetail: {
      area: {
        areaType: "CIRCLE",
        center: { latitude: 40.633189926609525, longitude: -8.659489441414976 },
        radius: 75,
      },
      device: {
        networkAccessIdentifier: "69001@domain.com",
      },
    },
  },
};

const latitude = 40.633189926609525;

function App() {
  const [lat, setLat] = useState(latitude);
  const [counter, setCounter] = useState(0);
  const [notifs, setNotifs] = useState<CloudEvent[]>([]);

  const { mutate } = $api.useMutation(
    "post",
    "/geofencing-subscriptions/v0/subscriptions",
  );

  const handleMessage = (data: CloudEvent) => {
    setNotifs((notifs) => [data, ...notifs]);
  };
  useEffect(() => {
    socket.on("data", handleMessage);
    return () => {
      socket.off("data", handleMessage);
    };
  }, []);

  const startGeofencing = () => {
    mutate({ body: req });
  };

  useEffect(() => {
    const timeout = setInterval(() => {
      setLat(latitude + Math.sin(counter) * 0.001);
      setCounter((counter) => counter + Math.PI / 24);
    }, 500);
    return () => clearTimeout(timeout);
  });
  return (
    <main className="container mx-auto my-20 space-y-12">
      <h1 className="text-center text-4xl font-bold">
        Drone Monitoring System
      </h1>

      <Button onClick={startGeofencing}>Geofencing</Button>
      <div className="h-[516px] overflow-hidden rounded-md border-2 border-black">
        <MapContainer
          center={[40.633189926609525, -8.659489441414976]}
          zoom={18}
          scrollWheelZoom={true}
          className="h-full w-full"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Marker position={[40.633189926609525, -8.659489441414976]}>
            <Tooltip>DETI</Tooltip>
          </Marker>
          <Circle
            center={[
              req.config.subscriptionDetail.area.center.latitude,
              req.config.subscriptionDetail.area.center.longitude,
            ]}
            radius={req.config.subscriptionDetail.area.radius}
          ></Circle>
          <Circle
            center={[lat, req.config.subscriptionDetail.area.center.longitude]}
            radius={2}
            fillOpacity={1}
            color="red"
          ></Circle>
        </MapContainer>
      </div>
      <ul className="divide-y">
        {notifs.map((notif) => (
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
