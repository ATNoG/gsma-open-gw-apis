import { videoData } from "@/data/videos";
import { createFileRoute, Link, redirect } from "@tanstack/react-router";
import { userStore } from "../infotainment";

export const Route = createFileRoute("/infotainment/")({
  component: RouteComponent,
  beforeLoad() {
    const user = userStore.state;
    if (user === null) {
      throw redirect({ to: "/infotainment/login" });
    }
  },
});
function formatTime(totalSeconds: number): string {
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  const paddedMinutes = minutes.toString().padStart(2, "0");
  const paddedSeconds = seconds.toString().padStart(2, "0");

  if (hours > 0) {
    const paddedHours = hours.toString().padStart(2, "0");
    return `${paddedHours}:${paddedMinutes}:${paddedSeconds}`;
  } else {
    return `${paddedMinutes}:${paddedSeconds}`;
  }
}
function RouteComponent() {
  return (
    <main className="container mx-auto my-20 px-4">
      <h1 className="mb-12 text-center text-3xl font-bold">Videos</h1>
      <ul className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {videoData.map((video) => (
          <li
            key={video.id}
            className="border-foreground/20 hover:bg-foreground/10 group overflow-hidden rounded-md border shadow"
          >
            <Link to="/infotainment/$videoId" params={{ videoId: video.id }}>
              <div className="relative">
                <img
                  className="block aspect-video w-full object-cover object-center"
                  src={`https://img.youtube.com/vi/${video.id}/0.jpg`}
                />
                <div className="text-primary-foreground text-semibold absolute right-2 bottom-2 rounded-sm bg-black px-2 py-1 text-sm">
                  {formatTime(video.duration)}
                </div>
              </div>
              <section className="px-4 py-2">
                <p className="text-sm font-semibold group-hover:underline">
                  {video.title}
                </p>
              </section>
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
