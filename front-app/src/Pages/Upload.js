import React, { useState } from "react";
import { Box, Button, Typography, Card, CardContent, CircularProgress } from "@mui/material";
import { useNavigate } from "react-router-dom";

const Upload = () => {
  const [files, setFiles] = useState([]); // Change from single file to array
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (event) => {
    setFiles([...event.target.files]); // Store multiple selected files
    setError(null);
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file); // Append all files to the formData
    });

    try {
      const response = await fetch("http://127.0.0.1:5000/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        console.log("Files uploaded successfully:", data);
       navigate("/processing", { state: { sessionId: data.session_id } }); // Pass session ID for further use
      } else {
        setError(data.error || "Failed to upload files. Please try again.");
      }
    } catch (err) {
      console.error("Error uploading files:", err);
      setError("An unexpected error occurred.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-start",
        alignItems: "center",
        backgroundImage: "url('/wave-background4.jpeg')",
        backgroundSize: "cover",
        backgroundRepeat: "no-repeat",
        padding: "20px",
        paddingTop: "170px",
      }}
    >
      <Box
        sx={{
          maxWidth: "500px",
          width: "100%",
          borderRadius: "15px",
          padding: "2px",
          background: "linear-gradient(135deg, #ff914d, #8e44ad, #3498db)",
        }}
      >
        <Card
          sx={{
            borderRadius: "13px",
            overflow: "hidden",
            background: "white",
            boxShadow: "0 8px 20px rgba(0, 0, 0, 0.1)",
          }}
        >
          <CardContent sx={{ textAlign: "center", padding: "30px" }}>
            <Typography variant="h5" sx={{ fontWeight: "bold", marginBottom: "20px", color: "#333" }}>
              Upload Your Documents
            </Typography>

            <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "20px" }}>
              <Button
                variant="outlined"
                component="label"
                sx={{
                  borderColor: "#8e44ad",
                  color: "#8e44ad",
                  borderRadius: "20px",
                  padding: "10px 30px",
                  fontWeight: "bold",
                  "&:hover": { background: "#8e44ad", color: "white" },
                }}
              >
                Choose Files
                <input type="file" hidden multiple onChange={handleFileChange} />
              </Button>

              <Typography
                variant="body1"
                sx={{ color: files.length > 0 ? "#4caf50" : "#888", fontStyle: files.length > 0 ? "italic" : "normal" }}
              >
                {files.length > 0 ? `Selected Files: ${files.map((file) => file.name).join(", ")}` : "No files chosen"}
              </Typography>
            </Box>

            {uploading ? (
              <CircularProgress sx={{ color: "#8e44ad", marginTop: "20px" }} />
            ) : (
              <Button
                variant="contained"
                size="large"
                disabled={files.length === 0}
                onClick={handleUpload}
                sx={{
                  background: files.length === 0 ? "rgba(142, 68, 173, 0.5)" : "linear-gradient(135deg, #8e44ad, #3498db)",
                  color: "white",
                  borderRadius: "20px",
                  padding: "10px 30px",
                  marginTop: "20px",
                  fontWeight: "bold",
                  boxShadow: files.length === 0 ? "none" : "0 4px 10px rgba(142, 68, 173, 0.3)",
                  "&:hover": {
                    background: files.length > 0 ? "linear-gradient(135deg, #8e44ad, #1f78b4)" : undefined,
                    boxShadow: files.length > 0 ? "0 6px 15px rgba(142, 68, 173, 0.4)" : "none",
                  },
                }}
              >
                Upload
              </Button>
            )}

            {error && (
              <Typography variant="body2" sx={{ color: "#f44336", marginTop: "20px", fontWeight: "bold" }}>
                {error}
              </Typography>
            )}
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default Upload;
