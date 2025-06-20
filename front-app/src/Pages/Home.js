import React from "react";
import { Container, Typography, Button, Box } from "@mui/material";

const Home = () => {
  return (
    <Box
      sx={{
        background: "linear-gradient(135deg, #ff914d, #8e44ad, #3498db)", // Orange-to-purple-to-blue gradient
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        color: "white",
        textAlign: "center",
        padding: "0 20px",
      }}
    >
      <Container>
        {/* App Title */}
        <Typography
          variant="h3"
          gutterBottom
          sx={{
            fontWeight: 700,
            textShadow: "0 4px 10px rgba(0,0,0,0.4)", // Soft text shadow for depth
            fontSize: { xs: "2rem", sm: "3rem", md: "4rem" }, // Responsive font size
          }}
        >
          Adaptive Document Analysis
        </Typography>

        {/* Subtitle */}
        <Typography
          variant="h6"
          paragraph
          sx={{
            fontSize: "1.2rem",
            marginBottom: "2rem",
            color: "rgba(255, 255, 255, 0.85)", // Slightly muted white for subtlety
          }}
        >
          Effortlessly upload your financial documents and gain valuable insights.
        </Typography>

        {/* Call-to-Action Button */}
        <Button
          variant="contained"
          size="large"
          href="/upload"
          sx={{
            background: "linear-gradient(135deg, #ff914d, #ff5722)", // Vibrant orange gradient
            color: "white",
            borderRadius: "30px",
            padding: "10px 40px",
            fontSize: "1.2rem",
            fontWeight: "bold",
            boxShadow: "0 5px 15px rgba(255, 87, 34, 0.3)", // Glow effect
            transition: "all 0.3s ease",
            "&:hover": {
              background: "linear-gradient(135deg, #ff5722, #d84315)", // Darker hover state
              boxShadow: "0 8px 20px rgba(255, 87, 34, 0.5)", // More intense shadow on hover
            },
          }}
        >
          Get Started
        </Button>
      </Container>
    </Box>
  );
};

export default Home;
