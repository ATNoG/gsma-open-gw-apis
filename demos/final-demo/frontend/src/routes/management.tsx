import { NotificationProvider } from "@/components/notification-provider";
import { Toaster } from "@/components/ui/sonner";
import { createFileRoute, Outlet } from "@tanstack/react-router";

export const Route = createFileRoute("/management")({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <>
      <NotificationProvider>
        <Outlet />
      </NotificationProvider>
      <Toaster />
    </>
  );
}
