import { $api } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { zodResolver } from "@hookform/resolvers/zod";
import { createFileRoute } from "@tanstack/react-router";
import { useForm, type SubmitHandler } from "react-hook-form";
import z from "zod";

export const Route = createFileRoute("/infotainment/(auth)/register/")({
  component: RouteComponent,
});

const formSchema = z.object({
  username: z.string().min(0, "Username can't be empty"),
  password: z.string().min(0, "Password can't be empty"),
  phoneNumber: z
    .string()
    .min(0, "Phone number can't be empty")
    .regex(/^\+[1-9][0-9]{4,14}$/, "Invalid phone format"),
});

type FormSchema = z.infer<typeof formSchema>;

function RouteComponent() {
  const form = useForm<FormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: { username: "", password: "", phoneNumber: "" },
  });

  const { mutate } = $api.useMutation("post", "/auth/register");

  const submitHandler: SubmitHandler<FormSchema> = (data) => {
    mutate({ body: data });
  };

  return (
    <main className="container mx-auto my-20 px-4">
      <Card className="mx-auto max-w-96">
        <CardHeader>
          <CardTitle>Register account</CardTitle>
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
              <FormField
                control={form.control}
                name="phoneNumber"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>* Phone Number</FormLabel>
                    <FormControl>
                      <Input
                        type="text"
                        placeholder="Phone number"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button className="w-full" type="submit">
                Register
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
      <Dialog>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Validate phone number</DialogTitle>
            <DialogDescription>
              An SMS with the validation code was sent to your phone number
            </DialogDescription>
            <DialogContent>TODO</DialogContent>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </main>
  );
}
