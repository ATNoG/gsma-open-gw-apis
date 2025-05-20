import { videoData } from "@/data/videos";
import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/infotainment/")({
  component: RouteComponent,
});

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
                  {video.duration}
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
