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
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSeparator,
  InputOTPSlot,
} from "@/components/ui/input-otp";
import { userStore } from "@/routes/infotainment";
import { zodResolver } from "@hookform/resolvers/zod";
import { createFileRoute, Link, redirect } from "@tanstack/react-router";
import { useState } from "react";
import { useForm, type SubmitHandler } from "react-hook-form";
import { toast } from "sonner";
import z from "zod";

export const Route = createFileRoute("/infotainment/(auth)/register/")({
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
  phoneNumber: z
    .string()
    .min(1, "Phone number can't be empty")
    .regex(/^\+[1-9][0-9]{4,14}$/, "Invalid phone format"),
});

type FormSchema = z.infer<typeof formSchema>;

function RouteComponent() {
  const form = useForm<FormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: { username: "", password: "", phoneNumber: "" },
  });

  const [isValidating, setIsValidating] = useState(false);

  const { mutate, data } = $api.useMutation("post", "/auth/register");

  const submitHandler: SubmitHandler<FormSchema> = (data) => {
    mutate({ body: data });
    setIsValidating(true);
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
              <div>
                <Button className="w-full" type="submit">
                  Register
                </Button>
                <p className="text-center">
                  Already have an account? Login{" "}
                  <Link className="underline" to="/infotainment/login">
                    here
                  </Link>
                  .
                </p>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
      <Dialog open={isValidating}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Validate phone number</DialogTitle>
            <DialogDescription>
              An SMS with the validation code was sent to your phone number
            </DialogDescription>
          </DialogHeader>
          <OtpForm otpId={data?.id} />
        </DialogContent>
      </Dialog>
    </main>
  );
}

const otpFormSchema = z.object({
  code: z.string().length(6, "Incomplete code"),
});

type OtpFormSchema = z.infer<typeof otpFormSchema>;

function OtpForm({ otpId }: { otpId: number | undefined }) {
  const form = useForm<OtpFormSchema>({
    resolver: zodResolver(otpFormSchema),
    defaultValues: {
      code: "",
    },
  });

  const navigate = Route.useNavigate();
  const { mutate } = $api.useMutation("post", "/auth/verify", {
    onError() {
      toast.error("Try again");
    },
    onSuccess() {
      toast.success("Registered successfully");
      navigate({ to: "/infotainment/login" });
    },
  });

  if (otpId === undefined) return null;
  const submitHandler: SubmitHandler<OtpFormSchema> = (data) => {
    mutate({ body: { ...data, id: otpId } });
  };
  return (
    <Form {...form}>
      <form
        className="space-y-4 text-center"
        onSubmit={form.handleSubmit(submitHandler)}
      >
        <FormField
          control={form.control}
          name="code"
          render={({ field }) => (
            <FormItem className="grid place-items-center">
              <FormLabel>One-Time Password</FormLabel>
              <FormControl>
                <InputOTP maxLength={6} {...field}>
                  <InputOTPGroup>
                    <InputOTPSlot index={0} />
                    <InputOTPSlot index={1} />
                    <InputOTPSlot index={2} />
                  </InputOTPGroup>
                  <InputOTPSeparator />
                  <InputOTPGroup>
                    <InputOTPSlot index={3} />
                    <InputOTPSlot index={4} />
                    <InputOTPSlot index={5} />
                  </InputOTPGroup>
                </InputOTP>
              </FormControl>
            </FormItem>
          )}
        />
        <Button type="submit">Verify</Button>
      </form>
    </Form>
  );
}
