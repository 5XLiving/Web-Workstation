import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ClientRoomPage from "./pages/ClientRoomPage";
import HomePage from "./pages/HomePage";
import AdminPage from "./pages/AdminPage";
import ReviewRoomPage from "./pages/ReviewRoomPage";
import WorkstationPage from "./pages/WorkstationPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/admin" element={<AdminPage />} />
        <Route path="/client-room" element={<ClientRoomPage />} />
        <Route path="/dev-room" element={<Navigate to="/admin" replace />} />
        <Route path="/review-room" element={<ReviewRoomPage />} />
        <Route path="/workstation" element={<WorkstationPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
