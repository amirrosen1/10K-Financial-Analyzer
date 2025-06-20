import React from "react";
import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import { Link, useLocation } from "react-router-dom";

const Navbar = () => {
  const location = useLocation(); // Get the current route

  return (
    <AppBar
      position="sticky"
      sx={{
        background: "linear-gradient(135deg, #ff914d, #8e44ad, #3498db)", // Orange-to-purple-to-blue gradient
        boxShadow: "0 4px 10px rgba(0, 0, 0, 0.2)", // Modern shadow for depth
        padding: "0.5rem",
      }}
    >
      <Toolbar>
        {/* Logo and Title */}
        <Typography
          variant="h6"
          component="div"
          sx={{
            flexGrow: 1,
            display: "flex",
            alignItems: "center",
            fontWeight: "bold",
          }}
        >
          <Box
            component="img"
            src="/bookLogo.png" // Add your logo file here
            alt="Logo"
            sx={{
              height: "40px",
              marginRight: "10px",
              filter: "drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3))", // Soft shadow for the logo
            }}
          />
          Adaptive Document Analysis
        </Typography>

        {/* Navigation Buttons */}
        <Button
          component={Link}
          to="/"
          sx={{
            color: location.pathname === "/" ? "#ffcc80" : "white", // Highlight active link
            fontWeight: "bold",
            textTransform: "uppercase",
            margin: "0 10px",
            "&:hover": {
              color: "#ffcc80", // Add hover effect
              transform: "scale(1.05)", // Slight scaling for interaction
            },
          }}
        >
          Home
        </Button>
        <Button
          component={Link}
          to="/upload"
          sx={{
            color: location.pathname === "/upload" ? "#ffcc80" : "white",
            fontWeight: "bold",
            textTransform: "uppercase",
            margin: "0 10px",
            "&:hover": {
              color: "#ffcc80",
              transform: "scale(1.05)",
            },
          }}
        >
          Upload
        </Button>
        <Button
          component={Link}
          to="/about"
          sx={{
            color: location.pathname === "/about" ? "#ffcc80" : "white",
            fontWeight: "bold",
            textTransform: "uppercase",
            margin: "0 10px",
            "&:hover": {
              color: "#ffcc80",
              transform: "scale(1.05)",
            },
          }}
        >
          About
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
