import { io } from "socket.io-client";
export const socket = io("ws://localhost:5000");

socket.on("connect", () => {
  console.log("WebSocket Connected");
});
