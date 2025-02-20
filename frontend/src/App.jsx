import { useState } from "react";
import React from "react";
import {
  Navigate,
  Route,
  BrowserRouter as Router,
  Routes,
} from "react-router-dom"; //npm install react-router-dom
import DishSelect from "./components/DishSelect";
import "./App.css";

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <Router>
        <div className="header">저메추</div>
        <DishSelect />
        {/* History창 만들거면? */}
        {/* <Routes>
          <Route path="/history" element={<History />} />
        </Routes> */}
      </Router>
    </>
  );
}

export default App;
