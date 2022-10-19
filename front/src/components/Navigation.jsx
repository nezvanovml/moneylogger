import React from "react";
import { NavLink  } from "react-router-dom";

function Navigation() {

    const clearToken = () => {
        console.log('loging out')
        localStorage.removeItem('token');
        window.location.href = '/';
        return {}
    };

    return (
        <div className="navigation">
          <nav className="navbar navbar-expand navbar-dark bg-dark">
            <div className="container">
              <NavLink className="navbar-brand" to="/">
                MoneyLogger
              </NavLink>
              <div>
                <ul className="navbar-nav ml-auto">
                  <li className="nav-item">
                    <NavLink className="nav-link" to="/">
                      Отчёты
                    </NavLink>
                  </li>
                  <li className="nav-item">
                    <NavLink className="nav-link" to="/transactions">
                      Транзакции
                    </NavLink>
                  </li>
                  <li className="nav-item">
                    <NavLink className="nav-link" to="/categories">
                      Категории
                    </NavLink>
                  </li>
                  <li className="nav-item">
                    <NavLink className="nav-link" to="/settings">
                      Настройки
                    </NavLink>
                  </li>
                  <li className="nav-item">
                    <NavLink className="nav-link" to="#" onClick={() => {clearToken()}}>
                      Выйти
                    </NavLink>
                  </li>
                </ul>
              </div>
            </div>
          </nav>
        </div>
    );
}

export default Navigation;
