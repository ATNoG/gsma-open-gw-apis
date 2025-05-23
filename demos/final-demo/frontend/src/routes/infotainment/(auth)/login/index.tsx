import { $api } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useLocalStorage } from "@/hooks/use-local-storage";
import { TOKEN_KEY, userStore } from "@/routes/infotainment";
import { zodResolver } from "@hookform/resolvers/zod";
import { createFileRoute, Link, redirect } from "@tanstack/react-router";
import { useForm, type SubmitHandler } from "react-hook-form";
import { toast } from "sonner";
import z from "zod";

export const Route = createFileRoute("/infotainment/(auth)/login/")({
  component: RouteComponent,
  beforeLoad() {
    const user = userStore.state;
    if (user !== null) {
      throw redirect({ to: "/infotainment" });
    }
  },
});

const formSchema = z.object({
  username: z.string().min(1, "Username can't be empty"),
  password: z.string().min(1, "Password can't be empty"),
});

type FormSchema = z.infer<typeof formSchema>;

function RouteComponent() {
  const form = useForm<FormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: { username: "", password: "" },
  });

  const navigate = Route.useNavigate();

  const [_token, setToken, _removeToken] = useLocalStorage(TOKEN_KEY, "");
  const { mutate } = $api.useMutation("post", "/auth/login", {
    onSuccess(data) {
      setToken(data.token);
      navigate({ to: "/infotainment" });
    },
    onError() {
      toast.error("Wrong username or password");
    },
  });

  const submitHandler: SubmitHandler<FormSchema> = (data) => {
    mutate({ body: data });
  };

  return (
    <main className="container mx-auto my-20 px-4">
      <Card className="mx-auto max-w-96">
        <CardHeader>
          <CardTitle>Log into account</CardTitle>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form
              onSubmit={form.handleSubmit(submitHandler)}
              className="space-y-4"
            >
              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>* Username</FormLabel>
                    <FormControl>
                      <Input type="text" placeholder="Username" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>* Password</FormLabel>
                    <FormControl>
                      <Input
                        type="password"
                        placeholder="Password"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div>
                <Button className="w-full" type="submit">
                  Login
                </Button>
                <p className="text-center">
                  Don't have an account yet? Register{" "}
                  <Link className="underline" to="/infotainment/register">
                    here
                  </Link>
                  .
                </p>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </main>
  );
}
