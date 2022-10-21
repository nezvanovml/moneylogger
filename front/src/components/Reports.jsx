import React, { useState, useEffect } from "react";

const subtractMonths = (date, months) => {
      const result = new Date(date);
      result.setMonth(result.getMonth() - months);
      return result;
    };


function Reports({ token }) {
    const [transactions, setTransactions] = useState([]);
    const [categories, setCategories] = useState([]);
    const [categoriesDict, setCategoriesDict] = useState({});
    const [categoriesIncome, setCategoriesIncome] = useState({});
    const [transactionsNumber, setTransactionsNumber] = useState(0);
    const [categoriesNumber, setCategoriesNumber] = useState(0);

    const [startDate, setStartDate] = useState((subtractMonths(new Date(), 6)).toISOString().slice(0, 10));
    const [endDate, setEndDate] = useState(new Date().toISOString().slice(0, 10));
    const [searchCategory, setSearchCategory] = useState(null);

    const [income, setIncome] = useState(0);
    const [spent, setSpent] = useState(0);



    const loadData = (start, end, category) =>{
        fetch('http://192.168.0.222:81/transactions?start_date='+start+'&end_date='+end+'&category='+category, {headers: {'Authorization': token}})
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
                var dictName = {};
                var dictIncome = {};
                data.categories.map((category) => {
                    dictName[category.id] = category.name
                    dictIncome[category.id] = category.income
                });
                setCategories(data.categories);
                setCategoriesDict(dictName);
                setCategoriesIncome(dictIncome);
                setCategoriesNumber(data.count)
             })
             .catch((err) => {
                console.log(err.message);
             });

        let temp_spent = 0;
        let temp_income = 0;

        transactions.map((transaction) => {
                    console.log(transaction.sum)
                    if(categoriesIncome[transaction.category]) temp_income += transaction.sum;
                    else temp_spent += transaction.sum * (-1);
                });

        setSpent(temp_spent)
        setIncome(temp_income)

    };


    useEffect(() => {
        loadData(startDate, endDate, searchCategory);
    }, [startDate, endDate, searchCategory, income, spent]);

  return (
        <div className="container text-end mt-3 mb-3">
              <div className="row">
                    <div className="col text-left">
                          <h1>Сводка</h1>
                          <form className=" ">
                                <select className="form-select form-select-lg mb-3" onChange={e => setSearchCategory(e.target.value)}>
                                      <option selected>Все категории</option>
                                      {Object.entries(categoriesDict).map(([key, value]) => {
                                         return (
                                                <option value={key} key={key}>{value}</option>
                                         );
                                      })}
                                </select>

                                <div className="form-floating mb-3">
                                        <input type="date" className="form-control" id="InputStart" defaultValue={startDate} onChange={e => setStartDate(e.target.value)}/>
                                        <label htmlFor="InputStart">Начало</label>
                                </div>
                                <div className="form-floating mb-3">
                                        <input type="date" className="form-control" id="InputEnd" defaultValue={endDate} onChange={e => setEndDate(e.target.value)}/>
                                        <label htmlFor="InputEnd">Конец</label>
                                </div>
                          </form>
                          <div className="row m-3">
                                <div className="col text-center fs-5">Число транзакций: </div>
                          </div>
                          <div className="row m-3">
                                <div className="col text-center  fs-5">{transactionsNumber}</div>
                          </div>
                          <div className="row m-3">
                                <div className="col text-center fs-5">Доход за период: </div>
                          </div>
                          <div className="row m-3">
                                <div className="col text-center  fs-5">{income.toLocaleString('ru', {style: 'currency', currency: 'RUB'})}</div>
                          </div>
                          <div className="row m-3">
                                <div className="col text-center fs-5">Расход за период: </div>
                          </div>
                          <div className="row m-3">
                                <div className="col text-center  fs-5">{spent.toLocaleString('ru', {style: 'currency', currency: 'RUB'})}</div>
                          </div>
                          <div className="row m-3">
                                <div className="col text-center fs-5">Баланс: </div>
                          </div>
                          <div className="row m-3">
                                <div className="col text-center fs-5">{(income - spent).toLocaleString('ru', {style: 'currency', currency: 'RUB'})}</div>
                          </div>
                    </div>
                    <div className="col">

                    </div>
              </div>
        </div>
  );
}

export default Reports;
