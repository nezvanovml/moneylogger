import React, {useEffect, useState  } from "react";
import ReactDOM from "react-dom";
import "./index.css";
import * as serviceWorker from "./serviceWorker";
import { BrowserRouter as Router, Route, Routes, useNavigate } from "react-router-dom";
import useToken from './useToken';
import {
  Navigation,
  Footer,
  Reports,
  Settings,
  Categories,
  Transactions,
  Login
} from "./components";

//localStorage.setItem('token', 'hjfhsdkfhjsdf\djf');
//if localStorage.getItem('token')

function setToken(userToken) {
    sessionStorage.setItem('token', userToken);
}

function getToken() {
    const userToken = sessionStorage.getItem('token');
    return userToken
}


function App() {
    const { token, setToken } = useToken();



    if(!token) {
        return <div><Login setToken={setToken} /><Footer /></div>
    }

    return (
      <Router>
        <Navigation />
        <Routes>
          <Route path="/" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/categories" element={<Categories />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/login" element={<Login />} />
        </Routes>
        <Footer />
      </Router>
    );
 }

ReactDOM.render(<App />, document.getElementById("root"));

serviceWorker.unregister();
