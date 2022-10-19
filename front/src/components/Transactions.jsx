import React, { useState, useEffect } from "react";

function Transactions({ token }) {
    const [transactions, setTansactions] = useState([]);
    const [categories, setCategories] = useState([]);
    const [transactionsNumber, setTansactionsNumber] = useState(0);
    const [categoriesNumber, setCategoriesNumber] = useState(0);
    useEffect(() => {
      fetch('http://localhost:81/transactions',{headers: {'Authorization': token}})
         .then((response) => response.json())
         .then((data) => {
            console.log(data);
            setTansactions(data.transactions);
            setTansactionsNumber(data.count)
         })
         .catch((err) => {
            console.log(err.message);
         });

      fetch('http://localhost:81/categories',{headers: {'Authorization': token}})
         .then((response) => response.json())
         .then((data) => {
            console.log(data);
            setCategories(data.transactions);
            setTansactionsNumber(data.count)
         })
         .catch((err) => {
            console.log(err.message);
         });
   }, []);

  return (
    <div className="container  text-center">
    <div className="row">
        <div class="col">
        {transactionsNumber}
        </div>
        <div class="col">
        <ul class="list-group m-2 justify-content-between">
                {transactions.map((transaction) => {
                     return (
                            <a href="#" class="list-group-item list-group-item-action " aria-current="true" key={transaction.id}>
                                <div class="d-flex w-100 justify-content-between">
                                  <h5 class="mb-1">{transaction.category}</h5>
                                  <small>{transaction.date}</small>
                                </div>
                                <p class="mb-1"><small>{transaction.comment}</small> {transaction.sum}</p>

                            </a>
    //                        <li className="list-group-item" key={transaction.id}>{transaction.date} {transaction.category} {transaction.sum} {transaction.comment}</li>
                     );
                })}
        </ul>
        </div>
    </div>
    </div>
  );
}

export default Transactions;
