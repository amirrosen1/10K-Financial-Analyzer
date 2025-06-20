import React from "react";
import { Box, Typography, Paper, Grid, Button } from "@mui/material";
import { useLocation, useNavigate } from "react-router-dom";

const Results = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { question, insights, sessionId } = location.state || {};

  const handleGoBack = () => {
    navigate("/questions", { state: { sessionId } }); // Ensure sessionId persists
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
        paddingTop: "100px",
      }}
    >
      {/* Page Title */}
      <Typography
        variant="h4"
        sx={{
          fontWeight: "bold",
          color: "#333",
          marginBottom: "10px",
          textAlign: "center",
        }}
      >
        Generated Insights
      </Typography>

      {/* Display the selected question */}
      {question && (
        <Typography
          variant="h6"
          sx={{
            fontStyle: "italic",
            color: "#555",
            marginBottom: "20px",
            textAlign: "center",
          }}
        >
          Selected Question: {question}
        </Typography>
      )}

      {/* Display insights */}
      <Grid
        container
        spacing={3}
        sx={{
          maxWidth: "800px",
          justifyContent: "center",
          alignItems: "center",
          marginTop: "30px",
        }}
      >
        {insights?.map((insight, index) => (
          <Grid item xs={12} sm={6} key={index}>
            <Paper
              elevation={3}
              sx={{
                padding: "20px",
                textAlign: "center",
                background: "white",
                borderRadius: "10px",
                boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
              }}
            >
              <Typography
                variant="h6"
                sx={{
                  fontWeight: "bold",
                  color: "#333",
                  marginBottom: "10px",
                }}
              >
                {insight.title}
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: "#555",
                }}
              >
                {insight.value}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Go Back Button */}
      <Button
        variant="contained"
        onClick={handleGoBack}
        sx={{
          marginTop: "40px",
          background: "linear-gradient(135deg, #8e44ad, #3498db)",
          color: "white",
          borderRadius: "20px",
          padding: "10px 30px",
          fontWeight: "bold",
          "&:hover": {
            background: "linear-gradient(135deg, #8e44ad, #1f78b4)",
          },
        }}
      >
        Select Another Question
      </Button>
    </Box>
  );
};

export default Results;
