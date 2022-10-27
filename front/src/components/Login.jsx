import React, { useState } from "react";
import PropTypes from 'prop-types';
import Alert from "./Alert.jsx";

async function loginUser(credentials) {
console.log(JSON.stringify(credentials))
 return fetch('/api/login', {
   method: 'POST',
   headers: {
     'Content-Type': 'application/json'
   },
   body: JSON.stringify(credentials)
 })
   .then(data => data.json())
}

export default function Login({ setToken }) {
  const [email, setEmail] = useState();
  const [password, setPassword] = useState();
  const [hideErrorbox, setHideErrorbox] = useState(true);
  const [AlertMain, setAlertMain] = useState({'error':{'show': false, 'text': ''}, 'success': {'show': false, 'text': ''}});

  const handleSubmit = async e => {
    e.preventDefault();
    let credentials = {'email': email, 'password': password}
    console.log(JSON.stringify(credentials))

    let result = await fetch('https://money.nezvanov.ru/api/login', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(credentials)})
    let json_data = await result.json()
    if(json_data.status == 'SUCCESS'){
        console.log('Token: ' + json_data.token)
        setAlertMain({'error':{'show': false, 'text': ''}, 'success': {'show': true, 'text': 'Данные для входа верны, происходит авторизация.'}});
        setToken(json_data.token);

    } else {
        setAlertMain({'error':{'show': true, 'text': 'Указаны неверные данные для входа.'}, 'success': {'show': false, 'text': ''}});
        console.log('error logging in')
    }
  }

  return (
    <div className="text-center">
      <main className="form-signin w-100 mt-5 m-auto">

        <form onSubmit={handleSubmit}>
            <h1 className="h3 mb-3 fw-normal">MoneyLogger</h1>
          <div className="form-floating">
            <input type="email" className="form-control" id="InputEmail" onChange={e => setEmail(e.target.value)}/>
            <label htmlFor="InputEmail">Email</label>
          </div>
          <div className="form-floating">
            <input type="password" className="form-control" id="InputPassword" onChange={e => setPassword(e.target.value)}/>
            <label htmlFor="InputPassword">Пароль</label>
          </div>
          <button type="submit" className="btn btn-primary">Войти</button>
          <Alert source={AlertMain} />
        </form>

      </main>
    </div>
  );
}

Login.propTypes = {
  setToken: PropTypes.func.isRequired
}