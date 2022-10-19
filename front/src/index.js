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

//function setToken(userToken) {
//    sessionStorage.setItem('token', userToken);
//}
//
//function getToken() {
//    const userToken = sessionStorage.getItem('token');
//    return userToken
//}


function App() {
    const { token, setToken } = useToken();



    if(!token) {
        return <Login setToken={setToken} />
    }

    return (
      <Router>
        <Navigation />
        <Routes>
          <Route path="/" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/categories" element={<Categories />} />
          <Route path="/transactions" element={<Transactions token={token} />} />
          <Route path="/login" element={<Login />} />
        </Routes>
        <Footer />
      </Router>
    );
 }

ReactDOM.render(<App />, document.getElementById("root"));

serviceWorker.unregister();
