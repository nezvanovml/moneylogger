import React, { useState, useEffect } from "react";

function Transactions({ token }) {
    const [transactions, setTransactions] = useState([]);
    const [categories, setCategories] = useState({});
    const [transactionsNumber, setTransactionsNumber] = useState(0);
    const [categoriesNumber, setCategoriesNumber] = useState(0);
    useEffect(() => {
      fetch('http://192.168.0.222:81/transactions',{headers: {'Authorization': token}})
         .then((response) => response.json())
         .then((data) => {
            console.log(data);
            setTransactions(data.transactions);
            setTransactionsNumber(data.count)
         })
         .catch((err) => {
            console.log(err.message);
         });

      fetch('http://192.168.0.222:81/categories',{headers: {'Authorization': token}})
         .then((response) => response.json())
         .then((data) => {
            console.log(data);
            var dict = {};
            data.categories.map((category) => {
                dict[category.id] = category.name
            });
            setCategories(dict);
            setCategoriesNumber(data.count)
         })
         .catch((err) => {
            console.log(err.message);
         });
   }, []);

  return (
    <div className="container  text-end">
    <div className="row">
        <div className="col text-left">
            <h1>Транзакции</h1>

            <form className="w-25 me-0">
              <div className="form-floating">
                <input type="date" className="form-control" id="InputStart"/>
                <label htmlFor="InputStart">Начало</label>
              </div>
              <div className="form-floating">
                <input type="date" className="form-control" id="InputEnd" defaultValue={new Date().toISOString().slice(0, 10)}/>
                <label htmlFor="InputEnd">Конец</label>
              </div>
              <button type="submit" className="btn btn-primary">Найти</button>
            </form>
        {transactionsNumber}
        </div>
        <div className="col">
        <ul className="list-group m-2 justify-content-between">
                {transactions.map((transaction) => {
                     return (
                            <li className={'list-group-item list-group-item-action text-dark bg-opacity-50 ' + (transaction.sum >= 0 ? "bg-success" : "bg-danger")}  aria-current="true" key={transaction.id}>
                                <div className="d-flex w-100 justify-content-between">
                                  <small>{categories[transaction.category.toString()]}</small>
                                  <small>{transaction.date}</small>

                                </div>
                                <div className="d-flex w-100 justify-content-between">
                                    <small>{transaction.comment}</small><h5 className="mb-1"> {transaction.sum >= 0 ? transaction.sum : transaction.sum * (-1)} ₽</h5>
                                </div>

                            </li>
                     );
                })}
        </ul>
        </div>
    </div>
    </div>
  );
}

export default Transactions;
