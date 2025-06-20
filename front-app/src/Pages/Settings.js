import React from "react";
import { Container, Typography, TextField, Button } from "@mui/material";

const Settings = () => {
  return (
    <Container>
      <Typography variant="h5">Settings</Typography>
      <TextField label="Query 1" fullWidth margin="normal" />
      <TextField label="Query 2" fullWidth margin="normal" />
      <Button variant="contained" color="primary">
        Save Settings
      </Button>
    </Container>
  );
};

export default Settings;
