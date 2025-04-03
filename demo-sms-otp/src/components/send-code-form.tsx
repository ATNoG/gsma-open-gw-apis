import { $api } from "@/lib/fetch-client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { SubmitHandler, useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "./ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "./ui/form";
import { Input } from "./ui/input";

const formSchema = z.object({
  phoneNumber: z
    .string()
    .min(1, "Can't be empty")
    .regex(/^\+[1-9][0-9]{4,14}$/, "Invalid phone number."),
  message: z
    .string()
    .min(1, "Can't be empty")
    .regex(
      /.*\{\{code\}\}.*/,
      "The label '{{code}}' must be included in the message.",
    )
    .max(160, "Message size must be at most 160 characters."),
});

type FormSchema = z.infer<typeof formSchema>;

export default function SendCodeForm() {
  const form = useForm<FormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      phoneNumber: "",
      message: "",
    },
  });
  const [authId, setAuthId] = useState<string | null>(null);
  const { mutate, isPending } = $api.useMutation(
    "post",
    "/one-time-password-sms/v1/send-code",
    {
      onSuccess(data) {
        setAuthId(data.authenticationId);
      },
    },
  );

  const onSubmit: SubmitHandler<FormSchema> = (data) => {
    mutate({ body: data });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Send Code</CardTitle>
        <CardDescription>
          Send a One-Time-Password to the specified phone number
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <FormField
              control={form.control}
              name="phoneNumber"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Phone Number</FormLabel>
                  <FormControl>
                    <Input placeholder="+346661113334" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="message"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Message</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="{{code}} is your short code to authenticate with Cool App via SMS"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    This is the message that will be sent to the phone number.
                    Make sure to include the <code>{"{{code}}"}</code> label in
                    the message.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" disabled={isPending}>
              Send Code
            </Button>
          </form>
        </Form>
        {authId && <>Authentication ID: {authId}</>}
      </CardContent>
    </Card>
  );
}
