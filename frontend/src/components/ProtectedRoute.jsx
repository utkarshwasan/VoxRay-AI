import { useUser } from "@stackframe/react";
import { Navigate, Outlet } from "react-router-dom";

export default function ProtectedRoute() {
  const user = useUser();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
