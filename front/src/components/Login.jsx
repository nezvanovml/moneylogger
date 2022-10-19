import React, { useState } from "react";
import PropTypes from 'prop-types';

async function loginUser(credentials) {
console.log(JSON.stringify(credentials))
 return fetch('http://localhost:81/login', {
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

  const handleSubmit = async e => {
    e.preventDefault();
    const token = await loginUser({
      email,
      password
    });
    console.log(token)
    if(token.status == 'SUCCESS'){
        console.log('Token: ' + token.token)
        //localStorage.setItem('token', token.token);
        setHideErrorbox(true)
        setToken(token.token);

    } else {
        setHideErrorbox(false)
        console.log('error logging in')
    }
  }

  return (
    <div className="text-center">
      <main className="form-signin w-100 mt-5 m-auto">

        <form onSubmit={handleSubmit}>
            <img className="mb-4" src="https://getbootstrap.com/docs/5.2/assets/brand/bootstrap-logo.svg" alt="" width="72" height="57" />
            <h1 className="h3 mb-3 fw-normal">Войти в систему</h1>
          <div className="form-floating">
            <input type="email" className="form-control" id="InputEmail" onChange={e => setEmail(e.target.value)}/>
            <label htmlFor="InputEmail">Email</label>
          </div>
          <div className="form-floating">
            <input type="password" className="form-control" id="InputPassword" onChange={e => setPassword(e.target.value)}/>
            <label htmlFor="InputPassword">Пароль</label>
          </div>
          <button type="submit" className="btn btn-primary">Войти</button>
          <div className={'alert alert-danger mt-2 ' + (hideErrorbox ? "d-none" : "")}  role="alert">Указаны неверные данные для входа</div>
        </form>

      </main>
    </div>
  );
}

Login.propTypes = {
  setToken: PropTypes.func.isRequired
}