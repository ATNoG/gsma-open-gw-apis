import { videosById } from "@/data/videos";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/infotainment/$videoId/")({
  component: RouteComponent,
});

const YT_EMBED_BASE_URL = "https://www.youtube.com/embed";

function RouteComponent() {
  const { videoId } = Route.useParams();
  const video = videosById.get(videoId);
  if (video === undefined) return "Video not found";
  return (
    <main className="grid h-screen items-center bg-black">
      <iframe
        className="aspect-video max-h-full w-full focus:border-none focus:outline-none"
        src={`${YT_EMBED_BASE_URL}/${video.id}?hd=1`}
        title={video.title}
        // allow="accelerometer; clipboard-write; encrypted-media; picture-in-picture"
        referrerPolicy="strict-origin-when-cross-origin"
        allowFullScreen
      />
    </main>
  );
}
