import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <div>
      Final demo
      <ul className="ml-2 list-inside list-disc">
        <li>
          <Link to="/infotainment">Infotainment</Link>
        </li>
        <li>
          <Link to="/management">Fleet Management</Link>
        </li>
      </ul>
    </div>
  );
}
