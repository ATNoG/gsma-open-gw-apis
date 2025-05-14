import { Button } from "./components/ui/button";
import { components } from "./lib/api";
import { $api } from "./lib/fetch-client";
type Device = {
  phoneNumber?: string | null;
  networkAccessIdentifier?: string | null;
  ipv4Address?: components["schemas"]["DeviceIpv4Addr-Output"] | null;
  ipv6Address?: string | null;
};

const device: Device = {
  phoneNumber: "+2020100000001",
};

const HIGH_SPEED_PROFILE_ID = "fast";

function App() {
  const { mutate } = $api.useMutation(
    "post",
    "/qod-provisioning/v0.2/device-qos",
  );

  const requestBandwidth = () => {
    console.log("Requesting");
    mutate({ body: { device, qosProfile: HIGH_SPEED_PROFILE_ID } });
  };
  return (
    <main className="container mx-auto my-20 space-y-6">
      <h1 className="text-center text-4xl font-bold">
        Video Streaming Platform
      </h1>
      <Button type="button" onClick={requestBandwidth}>
        Request Bandwidth
      </Button>
      <iframe
        className="aspect-video w-full rounded-lg border-2 border-black"
        src="https://www.youtube.com/embed/dQw4w9WgXcQ"
        title="Rick Astley - Never Gonna Give You Up (Official Music Video)"
        allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        referrerPolicy="strict-origin-when-cross-origin"
        allowFullScreen
      />
    </main>
  );
}

export default App;
