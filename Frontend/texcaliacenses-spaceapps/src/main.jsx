import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import { createRoot } from "react-dom/client";

import Index from "./pages/index.jsx";
import Report from "./pages/report.jsx";
import Chat from "./pages/chat.jsx";

import "./index.css";

createRoot(document.getElementById("root")).render(
  <Router>
    <Routes>
      <Route path="/" element={<Index />} />
      <Route path="/report/:city/:state/:country" element={<Report />} />
      <Route path="/chat" element={<Chat />} />
    </Routes>
  </Router>
);
