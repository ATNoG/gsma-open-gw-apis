import createFetchClient from "openapi-fetch";
import createClient from "openapi-react-query";
import type { paths } from "./types";

export const fetchClient = createFetchClient<paths>({
  baseUrl: "http://localhost:8069",
});

export const $api = createClient(fetchClient);
