import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { createFileRoute } from "@tanstack/react-router";

// Mock truck data
const truck = {
  id: 123,
  phoneNumber: "+9000000001",
  isQueued: true,
  isReachable: true,
  coords: {
    latitude: 40.64427,
    longitude: -8.64554,
  },
};

// TruckDetails component
function TruckDetails() {
  const position: [number, number] = [truck.coords.latitude, truck.coords.longitude];

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Truck {truck.id}</h1>

      <p>Phone: {truck.phoneNumber}</p>
      <p>Status: {truck.isReachable ? "🟢 Online" : "🔴 Offline"}</p>
      <p>Queue: {truck.isQueued ? "Yes" : "No"}</p>

      <div style={{ marginTop: 20 }}>
        <MapContainer center={position} zoom={13} style={{ height: 300, width: "100%" }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; OpenStreetMap contributors"
          />
          <Marker position={position}>
            <Popup>Truck {truck.id} Location</Popup>
          </Marker>
        </MapContainer>
      </div>
    </div>
  );
}

// Route definition
export const Route = createFileRoute("/management/truck/$truckId/")({
  component: TruckDetails,
});
