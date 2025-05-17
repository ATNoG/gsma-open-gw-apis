import { $api } from "@/lib/fetch-client";
import { cn } from "@/lib/utils";
import { zodResolver } from "@hookform/resolvers/zod";
import { CircleCheckBig, CircleX, LoaderCircle } from "lucide-react";
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
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "./ui/form";
import { Input } from "./ui/input";

const formSchema = z.object({
  authenticationId: z
    .string()
    .min(1, "Can't be empty")
    .max(36, "Authentication ID must not exceed 36 characters."),
  code: z
    .string()
    .min(1, "Can't be empty")
    .max(10, "Code must not exceed 10 characters."),
});

type FormSchema = z.infer<typeof formSchema>;

export default function ValidateCodeForm() {
  const form = useForm<FormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      authenticationId: "",
      code: "",
    },
  });
  const { mutate, isSuccess, isPending, isError } = $api.useMutation(
    "post",
    "/one-time-password-sms/v1/validate-code",
  );

  const onSubmit: SubmitHandler<FormSchema> = (data) => {
    mutate({ body: data });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Validate Code</CardTitle>
        <CardDescription>
          Validate the One-Time-Password sent in the previous form
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <FormField
              control={form.control}
              name="authenticationId"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Authentication ID</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="ea0840f3-3663-4149-bd10-c7c6b8912105"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="code"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Code</FormLabel>
                  <FormControl>
                    <Input placeholder="AJY3" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <span className="space-x-4">
              <Button type="submit" disabled={isPending}>
                Validate Code
              </Button>
              <span className="relative">
                <CircleCheckBig
                  className={cn("inline-block text-green-600", {
                    "opacity-0": !isSuccess,
                  })}
                />
                <LoaderCircle
                  className={cn("absolute inset-0", {
                    "opacity-0": !isPending,
                  })}
                />
                <CircleX
                  className={cn("absolute inset-0 text-red-600", {
                    "opacity-0": !isError,
                  })}
                />
              </span>
            </span>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
