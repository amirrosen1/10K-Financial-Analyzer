import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./Pages/Home";
import Upload from "./Pages/Upload";
import Insights from "./Pages/Insights";
import QuestionSelection from "./Pages/QuestionSelection";
import Results from "./Pages/Results";
import About from "./Pages/About";
import ProcessingPage from "./Pages/ProcessingPage"; // ✅ Import the new component

function App() {
  const [selectedQuestion, setSelectedQuestion] = useState(""); // State to manage the selected question

  // Example data for Insights component
  const exampleData = [
    { label: "Total Pages", value: 25 },
    { label: "Analysis Time", value: "3 minutes" },
    { label: "Extracted Entities", value: 150 },
  ];

  return (
    <Router>
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/processing" element={<ProcessingPage />} />
          <Route path="/insights" element={<Insights data={exampleData} />} />
          <Route
            path="/questions"
            element={
              <QuestionSelection
                setSelectedQuestion={setSelectedQuestion}
              />
            }
          />
          <Route
            path="/results"
            element={<Results selectedQuestion={selectedQuestion} />}
          />
          <Route path="/about" element={<About />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
