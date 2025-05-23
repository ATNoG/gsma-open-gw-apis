import { $api, fetchClient } from "@/api/client";
import { Toaster } from "@/components/ui/sonner";
import { useLocalStorage } from "@/hooks/use-local-storage";
import { createFileRoute, Outlet } from "@tanstack/react-router";
import { Store } from "@tanstack/react-store";
import { useEffect } from "react";

export const userStore = new Store<User | null>(null);
export const TOKEN_KEY = "login-token" as const;

export const Route = createFileRoute("/infotainment")({
  component: RouteComponent,
  async beforeLoad() {
    const item = localStorage.getItem(TOKEN_KEY);
    if (item === null) {
      userStore.setState(() => null);
      return;
    }
    const token = JSON.parse(item);
    const res = await fetchClient.POST("/auth/me", { body: { token } });
    userStore.setState(() => {
      if (res.data === undefined) return null;
      return { ...res.data, token };
    });
  },
});

interface User {
  username: string;
  phoneNumber: string;
  token: string;
}

function RouteComponent() {
  const [token, _setToken, _remove] = useLocalStorage<string>(TOKEN_KEY, "");
  const { data, isLoading, isSuccess, isError, refetch } = $api.useQuery(
    "post",
    "/auth/me",
    {
      body: { token },
    },
    { retry: false },
  );
  useEffect(() => {
    console.log("called");
    if (isSuccess) {
      userStore.setState(() => {
        return {
          username: data.username,
          phoneNumber: data.phoneNumber,
          token,
        };
      });
    }
    if (isError) {
      userStore.setState(() => null);
    }
  }, [data]);

  useEffect(() => {
    refetch();
  }, [token]);

  if (isLoading) return null;

  return (
    <>
      <Outlet />
      <Toaster richColors />
    </>
  );
}
