import React, { useEffect, useState } from "react";
import { Box, Typography, CircularProgress } from "@mui/material";
import { useLocation, useNavigate } from "react-router-dom";

const ProcessingPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const sessionId = location.state?.sessionId;
  const [error, setError] = useState(null);

  useEffect(() => {
    const processFiles = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/process/${sessionId}`, {
          method: "POST",
        });

        const data = await response.json();

        if (response.ok) {
          // Navigate to the questions page
          navigate("/questions", { state: { sessionId } });
        } else {
          setError(data.error || "Processing failed.");
        }
      } catch (err) {
        setError("Unexpected error occurred during processing.");
      }
    };

    if (sessionId) {
      processFiles();
    }
  }, [sessionId, navigate]);

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        backgroundImage: "url('/wave-background4.jpeg')",
        backgroundSize: "cover",
        backgroundRepeat: "no-repeat",
        padding: "20px",
      }}
    >
      {error ? (
        <Typography sx={{ color: "red", fontWeight: "bold" }}>{error}</Typography>
      ) : (
        <>
          <CircularProgress sx={{ color: "#8e44ad", mb: 2 }} />
          <Typography variant="h6" sx={{ color: "#333", fontWeight: "bold" }}>
            Analyzing Uploaded Files...
          </Typography>
        </>
      )}
    </Box>
  );
};

export default ProcessingPage;
