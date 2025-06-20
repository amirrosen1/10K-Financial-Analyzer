import React from "react";
import { Box, Typography, Paper } from "@mui/material";

const About = () => {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        backgroundImage: "url('/wave-background4.jpeg')", // Updated background image
        backgroundSize: "cover",
        backgroundRepeat: "no-repeat",
        padding: "20px",
      }}
    >
      <Paper
        elevation={5}
        sx={{
          padding: "50px",
          maxWidth: "900px",
          textAlign: "center",
          background: "rgba(255, 255, 255, 0.9)", // Slightly transparent background for better readability
          borderRadius: "20px",
          boxShadow: "0 8px 16px rgba(0, 0, 0, 0.2)", // Add a subtle shadow for a modern look
        }}
      >
        <Typography
          variant="h4"
          sx={{
            fontWeight: "bold",
            color: "#333",
            marginBottom: "20px",
          }}
        >
          About Adaptive Document Analysis
        </Typography>
        <Typography
          variant="body1"
          sx={{
            color: "#555",
            lineHeight: "1.8",
            marginBottom: "20px",
          }}
        >
          Adaptive Document Analysis is an innovative platform designed to
          extract meaningful insights from complex document structures. The
          system leverages advanced algorithms to analyze financial, legal, and
          other structured data, providing users with accurate and actionable
          insights in real time.
        </Typography>
        <Typography
          variant="body1"
          sx={{
            color: "#555",
            lineHeight: "1.8",
            marginBottom: "20px",
          }}
        >
          Our goal is to empower users to make informed decisions by simplifying
          the analysis of large datasets and unstructured documents. Whether
          you're looking to compare net income trends, analyze sector-specific
          performance, or uncover hidden patterns in data, Adaptive Document
          Analysis is your go-to solution.
        </Typography>
      </Paper>
    </Box>
  );
};

export default About;
