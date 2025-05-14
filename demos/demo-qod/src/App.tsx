import { useEffect, useState } from "react";
import { z } from "zod";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { $api } from "./lib/fetch-client";

const availableQoSProfiles = {
  slow: { displayText: "Slow" },
  medium: { displayText: "Medium" },
  fast: { displayText: "Fast" },
} as const;

const profiles = ["slow", "medium", "fast"] as const;

type AvailableQoSProfile = (typeof profiles)[number];

const phoneNumberValidator = z
  .string()
  .regex(/^\+[1-9][0-9]{4,14}$/, "Invalid phone number");

function App() {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const {
    mutate: getQoS,
    data,
    isSuccess,
  } = $api.useMutation("post", "/qod-provisioning/v0.2/retrieve-device-qos");

  const { mutate: deleteQoS } = $api.useMutation(
    "delete",
    "/qod-provisioning/v0.2/device-qos/{provisioningId}",
    {
      onSuccess() {
        getQoS({ body: { device: { phoneNumber } } });
      },
    },
  );

  const { mutate } = $api.useMutation(
    "post",
    "/qod-provisioning/v0.2/device-qos",
    {
      onSuccess() {
        getQoS({ body: { device: { phoneNumber } } });
      },
    },
  );

  useEffect(() => {
    if (errorMessage !== null) return;

    getQoS({ body: { device: { phoneNumber } } });
  }, [phoneNumber]);

  const requestQoS = (qosProfile: AvailableQoSProfile) => {
    mutate({ body: { device: { phoneNumber }, qosProfile } });
  };

  const getQoSInfo = () => {
    const pn = phoneNumberValidator.safeParse(phoneNumber);
    if (pn.success) {
      setErrorMessage(null);
      getQoS({ body: { device: { phoneNumber: pn.data } } });
    } else {
      setErrorMessage(pn.error.errors[0].message);
    }
  };

  const clearQoS = () => {
    if (!isSuccess || data.status === "UNAVAILABLE") return;
    deleteQoS({ params: { path: { provisioningId: data.provisioningId } } });
  };
  return (
    <main className="container mx-auto my-20 space-y-6">
      <h1 className="text-center text-4xl font-bold">
        Video Streaming Platform
      </h1>
      <Label>
        Phone number:{" "}
        <Input
          value={phoneNumber}
          placeholder="Phone number"
          onChange={(e) => {
            setPhoneNumber(e.target.value);
          }}
        />
      </Label>
      {errorMessage !== null && <p className="text-red-600">{errorMessage}</p>}
      <Button type="button" onClick={getQoSInfo}>
        Check Phone Number
      </Button>
      <br />
      {isSuccess && data.status !== "UNAVAILABLE" && (
        <>
          <p>
            Current speed:{" "}
            {
              availableQoSProfiles[data.qosProfile as AvailableQoSProfile]
                .displayText
            }
          </p>
          <Button type="button" onClick={clearQoS} variant="destructive">
            Clear
          </Button>
          <br />
        </>
      )}
      <span className="space-x-2">
        {profiles.map((profile) => (
          <Button
            key={profile}
            type="button"
            onClick={() => requestQoS(profile)}
            disabled={data !== undefined && data.status !== "UNAVAILABLE"}
          >
            {availableQoSProfiles[profile].displayText} Speed
          </Button>
        ))}
      </span>
      <br />
      <iframe
        className="mx-auto aspect-video w-3/4 rounded-lg border-2 border-black"
        src="https://www.youtube.com/embed/07qvZRbhIgI"
        title="Universidade de Aveiro"
        allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        referrerPolicy="strict-origin-when-cross-origin"
        allowFullScreen
      />
    </main>
  );
}

export default App;
