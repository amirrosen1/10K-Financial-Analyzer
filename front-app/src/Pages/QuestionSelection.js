import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Button,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  CircularProgress,
} from "@mui/material";
import { useLocation, useNavigate } from "react-router-dom";

const QuestionSelection = () => {
  const [selectedQuestion, setSelectedQuestion] = useState("");
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fetchingQuestions, setFetchingQuestions] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();

  // Ensure session ID is stored properly
  const [sessionId] = useState(location.state?.sessionId || null);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/api/questions");
        const data = await response.json();
        setQuestions(data.questions);
      } catch (error) {
        console.error("Error fetching questions:", error);
      } finally {
        setFetchingQuestions(false);
      }
    };

    fetchQuestions();
  }, []);

  const handleQuestionChange = (event) => {
    setSelectedQuestion(event.target.value);
  };

  const handleProceed = async () => {
    if (!selectedQuestion) {
      alert("Please select a question.");
      return;
    }

    if (!sessionId) {
      console.error("Session ID is missing.");
      alert("Session ID is required to analyze files.");
      return;
    }

    // Show loading spinner immediately
    setLoading(true);

    // Simulate a 5-second delay before sending the backend request
    setTimeout(async () => {
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/analyze/${sessionId}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: selectedQuestion }),
        });

        const data = await response.json();

        if (response.ok) {
          navigate("/results", {
            state: { question: selectedQuestion, insights: data.insights, sessionId }, // Pass sessionId
          });
        } else {
          console.error("Error analyzing files:", data.error);
          alert("Error analyzing files. Please try again.");
        }
      } catch (error) {
        console.error("Unexpected error:", error);
        alert("An unexpected error occurred.");
      } finally {
        setLoading(false);
      }
    }, 5000); // 5-second delay before making the request
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
        paddingTop: "200px"
      }}
    >
      {/* Page Title */}
      <Typography
        variant="h4"
        sx={{
          marginBottom: "20px",
          fontWeight: "bold",
          color: "#333",
          textAlign: "center",
        }}
      >
        Choose a Question to Get Insights
      </Typography>

      {/* Display spinner if questions are still loading */}
      {fetchingQuestions ? (
        <CircularProgress sx={{ color: "#8e44ad", marginBottom: "20px" }} />
      ) : (
        <>
          {/* Dropdown for Question Selection */}
          <FormControl sx={{ minWidth: "300px", marginBottom: "20px" }}>
            <InputLabel id="question-select-label">Select a Question</InputLabel>
            <Select
              labelId="question-select-label"
              value={selectedQuestion}
              onChange={handleQuestionChange}
            >
              {questions.map((question, index) => (
                <MenuItem key={index} value={question}>
                  {question}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Conditionally Render Loading Spinner or Button */}
          {loading ? (
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <CircularProgress
                sx={{
                  color: "#8e44ad",
                  marginBottom: "10px",
                }}
              />
              <Typography
                sx={{
                  color: "#333",
                  fontWeight: "bold",
                  marginTop: "10px",
                }}
              >
                Generating Insights...
              </Typography>
            </Box>
          ) : (
            <Button
              variant="contained"
              onClick={handleProceed}
              sx={{
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
              Generate Insights
            </Button>
          )}
        </>
      )}
    </Box>
  );
};

export default QuestionSelection;
