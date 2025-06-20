import React from "react";
import { CircularProgress, Box } from "@mui/material";

const LoadingSpinner = () => {
  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh", // Full-screen height for centered spinner
      }}
    >
      <CircularProgress />
    </Box>
  );
};

export default LoadingSpinner;
