import type * as Preset from "@docusaurus/preset-classic";
import type { Config } from "@docusaurus/types";
import { ScalarOptions } from "@scalar/docusaurus";
import { themes as prismThemes } from "prism-react-renderer";

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: "GSMA Open Gateway APIs",
  tagline: "Unlocking Connectivity",
  favicon: "img/favicon.svg",

  // Set the production url of your site here
  url: "https://atnog.github.io",
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: "/gsma-open-gw-apis/",

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: "pi", // Usually your GitHub org/user name.
  projectName: "gsma-open-gw-apis", // Usually your repo name.

  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "classic",
      {
        docs: {
          sidebarPath: "./sidebars.ts",
          lastVersion: "current",
          versions: {
            current: {
              label: "Current",
            },
          },
        },
        theme: {
          customCss: "./src/css/custom.css",
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    navbar: {
      title: "GSMA Open Gateway APIs",
      items: [
        {
          type: "docsVersionDropdown",
          position: "left",
        },
        {
          type: "docSidebar",
          sidebarId: "documentationSidebar",
          position: "left",
          label: "Documentation",
        },
        { to: "/milestones", label: "Milestones", position: "left" },
        {
          href: "https://github.com/ATNoG/gsma-open-gw-apis",
          label: "GitHub",
          position: "right",
        },
      ],
    },
    footer: {
      style: "dark",
      links: [
        {
          label: "GitHub",
          href: "https://github.com/ATNoG/gsma-open-gw-apis/tree/main/microsite",
          className: "margin--horiz-auto",
        },
      ],
      copyright: `
Projeto em Informática
<br>
GSMA Open Gateway APIs
<br>
Copyright © ${new Date().getFullYear()}. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,

  plugins: [
    [
      "@scalar/docusaurus",
      {
        label: "API Documentation",
        route: "/gsma-open-gw-apis/api/docs",
        configuration: {
          url: "openapi.json",
          hideClientButton: true,
        },
      } as ScalarOptions,
    ],
  ],
};

export default config;
