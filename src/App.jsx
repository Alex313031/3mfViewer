import React from "react";

import { ThreeMFLoaderProvider } from "./components/loaders/ThreeMFLoader.jsx";
import { ThemeProvider } from "./contexts/ThemeContext.jsx";
import { parseEmbedConfig } from "./app/embedConfig.js";
import ViewerBootstrap from "./app/ViewerBootstrap.jsx";

export default function App() {
  // In an embed, the host can pin the theme via ?theme=light|dark|auto so the
  // iframe opens matching the embedding page (ThreeMFViewerEmbed `theme` option).
  const { theme: embedTheme } = parseEmbedConfig();
  return (
    <ThemeProvider forcedTheme={embedTheme}>
      <ThreeMFLoaderProvider>
        <ViewerBootstrap />
      </ThreeMFLoaderProvider>
    </ThemeProvider>
  );
}
