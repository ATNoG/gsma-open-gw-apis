import { useNavigate } from "@tanstack/react-router";
import { Clock8, Truck, Wifi, WifiOff } from "lucide-react";
import { createContext, useContext, useEffect, useState } from "react";
import { io } from "socket.io-client";
import { toast } from "sonner";

interface ReachabilityNotification {
  id: number;
  isReachable: boolean;
}

interface QueueNotification {
  id: number;
  isQueued: boolean;
}

interface NotificationContext {
  reachabilityNotification: ReachabilityNotification | null;
  queueNotification: QueueNotification | null;
}

const NotificationContext = createContext<NotificationContext>(null!);

export function NotificationProvider({
  children,
}: {
  children: Readonly<React.ReactNode>;
}) {
  const [reachabilityNotification, setReachabilityNotification] =
    useState<ReachabilityNotification | null>(null);

  const [queueNotification, setQueueNotification] =
    useState<QueueNotification | null>(null);

  const navigate = useNavigate();

  useEffect(() => {
    const sio = io("ws://localhost:8069");

    sio.on("connect", () => console.log("Connected to socketio"));

    sio.on("reachability", (data) => {
      const notif = JSON.parse(data) as ReachabilityNotification;
      setReachabilityNotification(notif);
      toast(
        <span className="flex items-center gap-4">
          {notif.isReachable ? (
            <Wifi className="text-green-600" />
          ) : (
            <WifiOff className="text-red-600" />
          )}
          <span className="text-foreground/60 text-lg font-bold">
            TRUCK-{notif.id}
          </span>
        </span>,
        {
          duration: 8000,
          description: (
            <span className="text-foreground/70">
              {notif.isReachable
                ? "Truck is now reachable"
                : "Truck is now unreachable"}
            </span>
          ),
          action: {
            label: "See details",
            onClick() {
              navigate({
                to: "/management/truck/$truckId",
                params: { truckId: notif.id },
              });
            },
          },
        },
      );
    });

    sio.on("queue", (data) => {
      const notif = JSON.parse(data) as QueueNotification;
      setQueueNotification(notif);
      toast(
        <span className="flex items-center gap-4">
          {notif.isQueued ? (
            <Clock8 className="text-yellow-600" />
          ) : (
            <Truck className="text-blue-600" />
          )}
          <span className="text-foreground/60 text-lg font-bold">
            TRUCK-{notif.id}
          </span>
        </span>,
        {
          duration: 20000,
          description: (
            <span className="text-foreground/70">
              {notif.isQueued
                ? "Truck is now in queue"
                : "Truck is no longet queued"}
            </span>
          ),
          action: {
            label: "See details",
            onClick() {
              navigate({
                to: "/management/truck/$truckId",
                params: { truckId: notif.id },
              });
            },
          },
        },
      );
    });

    return () => {
      sio.close();
    };
  }, []);

  return (
    <NotificationContext.Provider
      value={{ reachabilityNotification, queueNotification }}
    >
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotification() {
  return useContext(NotificationContext);
}
