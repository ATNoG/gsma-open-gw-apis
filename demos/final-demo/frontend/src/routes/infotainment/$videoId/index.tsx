import { videosById } from "@/data/videos";
import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import YouTube from "react-youtube";

export const Route = createFileRoute("/infotainment/$videoId/")({
  component: RouteComponent,
});

// const YT_EMBED_BASE_URL = "https://www.youtube.com/embed";
//
const aspect = 16 / 9;

function calcDimensions(width: number, height: number) {
  const scaledHeight = height * aspect;
  if (width < scaledHeight) {
    return {
      width,
      height: width / aspect,
    };
  } else if (width > scaledHeight) {
    return {
      height,
      width: scaledHeight,
    };
  } else {
    return { width, height };
  }
}

function RouteComponent() {
  const { videoId } = Route.useParams();
  const video = videosById.get(videoId);
  const [width, setWidth] = useState(window.innerWidth);
  const [height, setHeight] = useState(window.innerHeight);
  useEffect(() => {
    const onResize = () => {
      setWidth(window.innerWidth);
      setHeight(window.innerHeight);
    };
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);
  if (video === undefined) return "Video not found";

  const { width: vidWidth, height: vidHeight } = calcDimensions(width, height);
  return (
    <main className="grid h-screen w-full place-items-center bg-black">
      <YouTube
        style={{ width: `${vidWidth}px`, height: `${vidHeight}px` }}
        iframeClassName="w-full h-full focus:outline-none"
        opts={{ playerVars: { autoplay: 1 } }}
        videoId={videoId}
      />
    </main>
  );
}
